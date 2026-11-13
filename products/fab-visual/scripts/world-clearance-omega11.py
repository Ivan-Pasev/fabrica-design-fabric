#!/usr/bin/env python3
"""FAB.VISUAL Ω11 — static centerline-to-AABB geometry research oracle.

The exact minimum Euclidean distance between a finite straight segment and
an axis-aligned box is computed by piecewise quadratic minimization.
All coordinates share one explicitly declared linear unit.
This is not a mesh/tube, renderer, dynamic-body, physical or scientific proof.
"""
from __future__ import annotations

import math
from typing import Sequence

ALLOWED_UNITS = frozenset(('m', 'mm'))


def _vec(v: Sequence[float], name: str) -> tuple[float, float, float]:
    if not isinstance(v, (tuple, list)) or len(v) != 3:
        raise ValueError(f'{name}: require 3 coordinates')
    if any(type(x) not in (float, int) or not math.isfinite(x) for x in v):
        raise ValueError(f'{name}: finite real coordinates required')
    return tuple(float(x) for x in v)


def _scalar(x: float, name: str, *, positive: bool = False) -> float:
    if type(x) not in (float, int) or not math.isfinite(x):
        raise ValueError(f'{name}: finite real number required')
    if x < 0 or (positive and x <= 0):
        raise ValueError(f'{name}: invalid nonpositive value')
    return float(x)


def segment_aabb_min_distance(p0, p1, lower, upper) -> float:
    """Minimize squared distance across all slab-crossing subintervals."""
    p = _vec(p0, 'p0'); q = _vec(p1, 'p1')
    lo = _vec(lower, 'lower'); hi = _vec(upper, 'upper')
    if any(a > b for a, b in zip(lo, hi)):
        raise ValueError('invalid AABB: lower exceeds upper')
    delta = tuple(b - a for a, b in zip(p, q))
    breakpoints = [0.0, 1.0]
    for i, d in enumerate(delta):
        if d != 0:
            for face in (lo[i], hi[i]):
                t = (face - p[i]) / d
                if 0 < t < 1:
                    breakpoints.append(t)
    ts = sorted(set(breakpoints))

    def sq_at(t: float) -> float:
        return sum(max(lo[i] - (p[i] + delta[i] * t), 0.0,
                       (p[i] + delta[i] * t) - hi[i]) ** 2
                   for i in range(3))

    best = min(sq_at(t) for t in ts)
    for a, b in zip(ts, ts[1:]):
        mid = (a + b) / 2
        numer = denom = 0.0
        for i, d in enumerate(delta):
            m = p[i] + mid * d
            if m < lo[i]:
                c = lo[i]
            elif m > hi[i]:
                c = hi[i]
            else:
                continue
            numer += d * (p[i] - c)
            denom += d * d
        if denom:
            stationary = max(a, min(b, -numer / denom))
            best = min(best, sq_at(stationary))
    return math.sqrt(best)


def classify_clearance(p0, p1, lower, upper, *, radius: float,
                       uncertainty: float = 0.0, epsilon: float = 1e-9,
                       unit: str) -> dict:
    """Synthetic static tube-centerline clearance, fail-closed at boundaries."""
    if unit not in ALLOWED_UNITS:
        raise ValueError('unit must be explicitly declared m or mm')
    r = _scalar(radius, 'radius')
    u = _scalar(uncertainty, 'uncertainty')
    e = _scalar(epsilon, 'epsilon', positive=True)
    d = segment_aabb_min_distance(p0, p1, lower, upper)
    margin = d - r
    state = ('CLEAR' if margin > u + e else
             'INTERSECTS' if margin < -u - e else 'INCONCLUSIVE')
    return dict(schema='fab.visual.omega11.clearance.v1', state=state,
                distance=d, radius=r, signed_margin=margin, uncertainty=u,
                epsilon=e, unit=unit, scope='STRAIGHT_SEGMENT_STATIC_AABB_ONLY',
                release='HOLD')


def classify_port(endpoint, center, *, tolerance: float,
                  uncertainty: float = 0.0, epsilon: float = 1e-9,
                  unit: str) -> dict:
    """Center proximity only; NOT connector orientation/mating verification."""
    if unit not in ALLOWED_UNITS:
        raise ValueError('unit must be explicitly declared m or mm')
    p = _vec(endpoint, 'endpoint'); c = _vec(center, 'port center')
    t = _scalar(tolerance, 'tolerance')
    u = _scalar(uncertainty, 'uncertainty')
    e = _scalar(epsilon, 'epsilon', positive=True)
    dist = math.dist(p, c)
    state = ('WITHIN' if dist < t - u - e else
             'OUTSIDE' if dist > t + u + e else 'INCONCLUSIVE')
    return dict(schema='fab.visual.omega11.port.v1', state=state,
                center_distance=dist, tolerance=t, uncertainty=u,
                epsilon=e, unit=unit, release='HOLD')


def classify_sampled_motion(samples, lower, upper, *, radius: float,
                            endpoint_speed_bound: float | None,
                            uncertainty: float = 0.0,
                            epsilon: float = 1e-9, unit: str) -> dict:
    """Static-body motion requires an EXTERNALLY VALIDATED endpoint-speed bound.

    For an independently valid bound L on each endpoint motion, segment
    Hausdorff displacement is at most L*dt. Conservatively compare minimum
    endpoint-sample signed margins against L*dt/2. Samples alone cannot
    establish L. A modeled intersection at a sampled time is detectable.
    """
    if not isinstance(samples, (tuple, list)) or len(samples) < 2:
        raise ValueError('at least two samples required')
    speed = (None if endpoint_speed_bound is None else
             _scalar(endpoint_speed_bound, 'endpoint speed bound'))
    prior = None
    checks = []
    for time, a, b in samples:
        if type(time) not in (int, float) or not math.isfinite(time):
            raise ValueError('finite sample time required')
        if prior is not None and time <= prior:
            raise ValueError('strictly increasing sample times required')
        prior = time
        checks.append(classify_clearance(a, b, lower, upper, radius=radius,
                                         uncertainty=uncertainty,
                                         epsilon=epsilon, unit=unit))
    if any(x['state'] == 'INTERSECTS' for x in checks):
        state = 'INTERSECTS'
    elif speed is None:
        state = 'INCONCLUSIVE'
    else:
        state = 'CLEAR'
        for i, (before, after) in enumerate(zip(samples, samples[1:])):
            dt = after[0] - before[0]
            if min(checks[i]['signed_margin'], checks[i+1]['signed_margin']) \
                    <= uncertainty + epsilon + speed * dt / 2:
                state = 'INCONCLUSIVE'
                break
    return dict(schema='fab.visual.omega11.motion.v1', state=state,
                sample_count=len(samples), endpoint_speed_bound=speed,
                speed_bound_independently_verified=False,
                static_body_only=True, source='SYNTHETIC_OR_USER_DECLARED',
                release='HOLD')

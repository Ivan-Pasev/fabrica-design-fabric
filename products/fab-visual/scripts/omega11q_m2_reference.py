#!/usr/bin/env python3
"""Ω11Q-M2 independent Python decimal/Fraction reference oracle.
No JavaScript rational routines are imported. Source inputs are synthetic.
"""
import hashlib
import json
import sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

FACTORS = {"W": Fraction(1), "kW": Fraction(1000), "MW": Fraction(1000000),
           "s": Fraction(1), "ms": Fraction(1, 1000), "h": Fraction(3600)}

def exact(text, unit):
    if not isinstance(text, str):
        raise ValueError("decimal strings only")
    if unit not in FACTORS:
        raise ValueError("unrecognized unit")
    return Fraction(Decimal(text)) * FACTORS[unit]

def label(v):
    return {"numerator": str(v.numerator), "denominator": str(v.denominator)}

def image(lo, hi, nominal):
    return {"lo": label(lo), "hi": label(hi), "nominal": label(nominal)}

def calculate(vector):
    lo = hi = nominal = Fraction(0)
    for term in vector["terms"]:
        m = exact(term["magnitude"], term["unit"])
        u = exact(term["uncertainty"], term["unit"])
        if m < 0 or u < 0:
            raise ValueError("negative magnitude/uncertainty")
        if term["direction"] == "IN":
            lo += m - u
            hi += m + u
            nominal += m
        elif term["direction"] == "OUT":
            lo -= m + u
            hi -= m - u
            nominal -= m
        else:
            raise ValueError("invalid direction")
    dt = exact(vector["duration"]["value"], vector["duration"]["unit"])
    if dt <= 0 or lo > hi:
        raise ValueError("invalid duration or interval")
    return {"id": vector["id"], "power": image(lo, hi, nominal),
            "energy": image(lo * dt, hi * dt, nominal * dt)}

def main():
    if len(sys.argv) != 2:
        raise ValueError("usage: python3 omega11q_m2_reference.py <vectors.json>")
    raw = Path(sys.argv[1]).read_bytes()
    data = json.loads(raw)
    if (data["schema"] != "fab.visual.exact-rational-vectors.v1"
            or data["seed"] != "0x5eed1141" or data["count"] != 10000
            or len(data["vectors"]) != 10000):
        raise ValueError("wrong test identity")
    results = [calculate(v) for v in data["vectors"]]
    print(json.dumps({"schema": "fab.visual.python-fraction-oracle.v1",
                      "vectorSha256": hashlib.sha256(raw).hexdigest(),
                      "count": len(results), "results": results},
                     separators=(",", ":")))

if __name__ == "__main__":
    main()

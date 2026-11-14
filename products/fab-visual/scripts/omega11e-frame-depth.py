#!/usr/bin/env python3
"""FAB.VISUAL Ω11E — independent synthetic camera-ray / triangle depth oracle.

All geometric coordinates are in explicitly declared model metres. All matrices
are 4x4 row-major and act on column vectors; NDC convention is OpenGL z in [-1,1].
This module does NOT read a renderer frame, establish source-camera equivalence,
prove a physical 3D model or certify depth ordering in Anatomy itself.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

PIN = "1482e8469b0a9e0d8cc18ea2740a01423d29ae80"
SCHEMA = "fab.visual.omega11e.frame-depth.v1"
GRADES = frozenset(("SOURCE_STATIC", "RUNTIME_READBACK",
                    "DERIVED_WITH_ASSUMPTIONS", "NOT_AVAILABLE"))


def scalar(x, name):
    if type(x) not in (float, int) or not math.isfinite(x):
        raise ValueError(f"{name}: finite nonboolean number required")
    return float(x)


def vec3(x, name):
    if not isinstance(x, (tuple, list)) or len(x) != 3:
        raise ValueError(f"{name}: three coordinates required")
    return tuple(scalar(v, name) for v in x)


def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def scale(a,f): return tuple(x*f for x in a)
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],
                       a[2]*b[0]-a[0]*b[2],
                       a[0]*b[1]-a[1]*b[0])
def norm(a): return math.sqrt(dot(a,a))


def matrix4(value, name):
    if not isinstance(value, (list,tuple)) or len(value)!=4:
        raise ValueError(f"{name}: 4x4 matrix required")
    if any(not isinstance(row,(tuple,list)) or len(row)!=4 for row in value):
        raise ValueError(f"{name}: four rows of four required")
    return tuple(tuple(scalar(a,name) for a in row) for row in value)


def matmul4(a,b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(4))
                       for j in range(4)) for i in range(4))


def matvec4(a,v):
    return tuple(sum(a[i][k]*v[k] for k in range(4)) for i in range(4))


def inverse4(m):
    a=[list(row)+[float(i==j) for j in range(4)]
       for i,row in enumerate(matrix4(m,"transform"))]
    for j in range(4):
        k=max(range(j,4),key=lambda i:abs(a[i][j]))
        if abs(a[k][j]) <= 1e-12 * max(1.0,max(abs(x) for row in a for x in row[:4])):
            raise ValueError("noninvertible or ill-conditioned matrix")
        a[j],a[k]=a[k],a[j]
        pivot=a[j][j]
        a[j]=[x/pivot for x in a[j]]
        for i in range(4):
            if i!=j:
                p=a[i][j]
                a[i]=[a[i][q]-p*a[j][q] for q in range(8)]
    result=tuple(tuple(row[4:]) for row in a)
    for i in range(4):
        for j in range(4):
            x=sum(m[i][k]*result[k][j] for k in range(4))
            if not math.isfinite(x) or abs(x-float(i==j))>1e-7:
                raise ValueError("matrix inverse residual exceeds tolerance")
    return result


def perspective(fovy_radians, aspect, near, far):
    fov=scalar(fovy_radians,"fovy")
    a=scalar(aspect,"aspect"); n=scalar(near,"near"); f=scalar(far,"far")
    if not (0<fov<math.pi and a>0 and 0<n<f):
        raise ValueError("invalid OpenGL near/far/fov/aspect")
    q=1/math.tan(fov/2)
    return ((q/a,0,0,0),(0,q,0,0),
            (0,0,(f+n)/(n-f),2*f*n/(n-f)),(0,0,-1,0))


def unproject(inv_view_projection,x,y,z):
    h=matvec4(inv_view_projection,(x,y,z,1.0))
    if abs(h[3])<1e-12:
        raise ValueError("homogeneous unprojection at infinity")
    return tuple(scalar(v/h[3],"unproject") for v in h[:3])


def camera_ray(view,projection,pixel,viewport,*,unit):
    if unit!="m":
        raise ValueError("camera and model unit must be explicitly m")
    v=matrix4(view,"view");p=matrix4(projection,"projection")
    if not isinstance(viewport,(tuple,list)) or len(viewport)!=2:
        raise ValueError("viewport width, height required")
    w,h=viewport
    if type(w)!=int or type(h)!=int or w<=0 or h<=0:
        raise ValueError("positive integer viewport required")
    if not isinstance(pixel,(tuple,list)) or len(pixel)!=2:
        raise ValueError("pixel x,y required")
    x,y=(scalar(z,"pixel") for z in pixel)
    if not (0<=x<w and 0<=y<h):
        raise ValueError("pixel outside the viewport")
    inverse=inverse4(matmul4(p,v))
    ndcx=2*(x+.5)/w-1
    ndcy=1-2*(y+.5)/h
    before=unproject(inverse,ndcx,ndcy,-1.0)
    after=unproject(inverse,ndcx,ndcy,1.0)
    delta=sub(after,before)
    length=norm(delta)
    if length<=1e-12 or not math.isfinite(length):
        raise ValueError("degenerate near-to-far camera ray")
    return {"origin":before, "direction":scale(delta,1/length),
            "max_t":length,"near_world":before,"far_world":after,
            "unit":"m","pixel":(x,y),"viewport":(w,h),
            "clip_z_convention":"OPENGL_NEGATIVE_ONE_TO_ONE",
            "source":"SYNTHETIC_MATRIX_INPUT"}


def ray_triangle(ray, triangle, *, epsilon=1e-9):
    eps=scalar(epsilon,"epsilon")
    if eps<=0:
        raise ValueError("epsilon must be positive")
    vertices=triangle.get("vertices")
    if not isinstance(vertices,(tuple,list)) or len(vertices)!=3:
        raise ValueError("triangle requires exactly three vertices")
    a,b,c=(vec3(v,"vertex") for v in vertices)
    e1=sub(b,a);e2=sub(c,a)
    n=cross(e1,e2)
    if norm(n)<eps:
        raise ValueError("degenerate triangle")
    orig=vec3(ray["origin"],"ray origin")
    direction=vec3(ray["direction"],"ray direction")
    distance=scalar(ray["max_t"],"ray max_t")
    if not (abs(norm(direction)-1)<1e-8 and distance>0):
        raise ValueError("normalized finite ray and far bound required")
    pvec=cross(direction,e2)
    det=dot(e1,pvec)
    if abs(det) <= eps:
        return None
    inv=1/det
    tvec=sub(orig,a)
    u=dot(tvec,pvec)*inv
    if u<-eps or u>1+eps:
        return None
    qvec=cross(tvec,e1)
    v=dot(direction,qvec)*inv
    if v<-eps or u+v>1+eps:
        return None
    t=dot(e2,qvec)*inv
    if t<-eps or t>distance+eps:
        return None
    w=1-u-v
    if min(u,v,w,t,distance-t)<-eps:
        return None
    boundary=min(u,v,w,t,distance-t)<=eps
    return {"triangle_id":triangle["triangle_id"],
            "part_id":triangle["part_id"],
            "t_m":t,
            "barycentric":(w,u,v),
            "front_face":dot(n,direction)<0,
            "boundary":boundary}


def ordered_depth(ray, triangles, *, epsilon=1e-9, uncertainty=0.0):
    eps=scalar(epsilon,"epsilon")
    u=scalar(uncertainty,"uncertainty")
    if not (eps>0 and u>=0):
        raise ValueError("invalid uncertainty/epsilon")
    if ray.get("unit")!="m":
        raise ValueError("ray/triangle common unit m required")
    if not isinstance(triangles,(tuple,list)):
        raise ValueError("triangle collection required")
    seen=set()
    hits=[]
    for tri in triangles:
        if not isinstance(tri,dict) or type(tri.get("triangle_id"))!=str or not tri["triangle_id"]:
            raise ValueError("typed nonempty triangle_id required")
        if type(tri.get("part_id"))!=str or not tri["part_id"]:
            raise ValueError("typed nonempty part_id required")
        if tri["triangle_id"] in seen:
            raise ValueError("duplicate triangle identity")
        seen.add(tri["triangle_id"])
        hit=ray_triangle(ray,tri,epsilon=eps)
        if hit is not None:
            hits.append(hit)
    hits.sort(key=lambda h:(h["t_m"],h["triangle_id"]))
    ambiguous=any(h["boundary"] for h in hits)
    for prior,current in zip(hits,hits[1:]):
        if current["t_m"]-prior["t_m"]<=eps+u:
            ambiguous=True
    status=("INCONCLUSIVE_BOUNDARY_OR_TIE" if ambiguous else
            "FINITE_RAY_HIT" if hits else "FINITE_RAY_EMPTY")
    return {"schema":SCHEMA,"state":status,
            "ordered_hits":hits,"epsilon_m":eps,"uncertainty_m":u,
            "model_scope":"INDEPENDENT_SYNTHETIC_TRIANGLES_ONLY",
            "real_anatomy_depth_order":"NOT_RUN",
            "physical_clearance":"NOT_RUN","release":"HOLD"}


def grade(field):
    if not isinstance(field,dict) or field.get("grade") not in GRADES:
        raise ValueError("invalid evidence grade")
    return field["grade"]


def frame_contract(witness):
    """Validate declared evidence form, never accept an untrusted claim as proof."""
    required=("source_commit","source_html_sha256","model_sha256","scene_id",
              "frame_event_id","camera_pose","camera_projection",
              "visible_part_ids","viewport","renderer_version")
    if not isinstance(witness,dict):
        raise ValueError("typed frame witness required")
    for key in required:
        grade(witness.get(key))
    if witness["source_commit"].get("value")!=PIN:
        raise ValueError("source commit differs from immutable pin")
    for key in ("source_html_sha256","model_sha256"):
        x=witness[key].get("value")
        if type(x)!=str or len(x)!=64 or any(v not in "0123456789abcdef" for v in x):
            raise ValueError(f"{key}: SHA256 required")
    scene=witness["scene_id"].get("value")
    if type(scene)!=str or scene not in ("raptor-light","turning-light"):
        raise ValueError("unrecognized pinned scene identity")
    token=witness["frame_event_id"].get("value")
    camera=witness["camera_pose"].get("value")
    projection=witness["camera_projection"].get("value")
    if projection is not None:
        inverse4(matrix4(projection["matrix"],"camera projection"))
    if camera is not None:
        inverse4(matrix4(camera["view_matrix"],"camera view"))
    claimed_grades=(witness[key]["grade"] for key in
                    ("frame_event_id","camera_pose","camera_projection"))
    complete=all(g=="RUNTIME_READBACK" for g in claimed_grades)
    linked=(type(token)==str and len(token)>0 and
            isinstance(camera,dict) and camera.get("frame_event_id")==token and
            isinstance(projection,dict) and projection.get("frame_event_id")==token)
    structurally_complete=bool(complete and linked)
    # Even structurally complete user JSON is untrusted. Actual render hook + signed
    # or independently verified source-to-frame capture is not supplied by this API.
    return {"schema":"fab.visual.omega11e.frame-contract.v1",
            "scene":scene,
            "contract_status":("DECLARED_FRAME_FIELDS_CONSISTENT"
                               if structurally_complete else "INCOMPLETE_PROVENANCE"),
            "authoritative_frame_verified":"NOT_ADMITTED",
            "rendered_camera_geometry_verified":"NOT_ADMITTED",
            "independent_runtime_attestation":"NOT_AVAILABLE",
            "release":"HOLD"}


def example_receipt():
    view=((1.,0,0,0),(0,1.,0,0),(0,0,1.,0),(0,0,0,1.))
    projection=perspective(math.pi/2,1,1,10)
    ray=camera_ray(view,projection,(0,0),(1,1),unit="m")
    front={"triangle_id":"front-1","part_id":"front","vertices":[(-2,-2,-2),(2,-2,-2),(0,2,-2)]}
    back={"triangle_id":"back-1","part_id":"back","vertices":[(-2,-2,-4),(2,-2,-4),(0,2,-4)]}
    res=ordered_depth(ray,[back,front])
    return {"schema":SCHEMA,"upstream_pin":PIN,"test_scope":"SYNTHETIC_STANDALONE_ONLY",
            "center_ray":ray,"synthetic_depth_case":res,
            "real_renderer_frame":"NOT_ADMITTED","real_anatomy_camera":"NOT_ADMITTED",
            "real_anatomy_geometry":"NOT_RUN","real_anatomy_occlusion":"NOT_RUN",
            "platform_reproducibility":"NOT_RUN",
            "byte_parity":"FAIL","historical_pixel_repeatability":"FAIL",
            "release":"HOLD"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    report=example_receipt()
    assert report["synthetic_depth_case"]["state"]=="FINITE_RAY_HIT"
    assert [h["part_id"] for h in report["synthetic_depth_case"]["ordered_hits"]]==["front","back"]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({"synthetic_depth_case":"PASS",
                      "renderer_frame":"NOT_ADMITTED",
                      "real_geometry":"NOT_RUN","release":"HOLD"}))

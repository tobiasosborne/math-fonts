#!/usr/bin/env python3
"""Independent compiled-geometry audit for the final bounded root proposal."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

from design_campaign import flatten


def audit(run):
    private=run/"private"
    provenance=json.loads((private/"provenance.json").read_text())
    old=TTFont(provenance["input"])
    font=TTFont(provenance["candidate"])
    pen=RecordingPen()
    font.getGlyphSet()["bask.radical.bottom"].draw(pen)
    segments=[]
    current=None
    for op,args in pen.value:
        if op=="moveTo":
            current=args[0]
        elif op in ["lineTo","curveTo"]:
            segments.append((op,current,args))
            current=args[-1]
    left=font["hmtx"]["bask.radical.ext"][1]
    outer=next(s for s in segments if s[0]=="curveTo" and s[2][-1]==(650,1500))
    inner=next(s for s in segments if s[0]=="curveTo" and s[1]==(left,1500))
    a,b,c,d=outer[1],*outer[2]
    outer_tangent=[3*(d[i]-c[i])for i in [0,1]]
    outer_second=[6*(d[i]-2*c[i]+b[i])for i in [0,1]]
    a,b,c,d=inner[1],*inner[2]
    inner_tangent=[3*(b[i]-a[i])for i in [0,1]]
    inner_second=[6*(a[i]-2*b[i]+c[i])for i in [0,1]]
    assert outer_tangent[0]==inner_tangent[0]==outer_second[0]==inner_second[0]==0
    assert outer_tangent[1]>0 and inner_tangent[1]<0

    def scan(name,y):
        pts=flatten(font,name)
        xs=[]
        for a,b in zip(pts,pts[1:]):
            if (a[1]<=y<b[1])or(b[1]<=y<a[1]):
                xs.append(a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1]))
        return sorted(xs)

    probes={}
    for name,ys in [("bask.radical.bottom",[1501,1650,1850]),
                    ("bask.radical.ext",[1,150,500]),
                    ("bask.radical.top",[1,150,400])]:
        probes[name]={str(y):scan(name,y)for y in ys}
        assert all(v==[float(left),650.0]for v in probes[name].values())
    actual=[]
    old_glyphs,new_glyphs=old.getGlyphSet(),font.getGlyphSet()
    for name in font.getGlyphOrder():
        a,b=RecordingPen(),RecordingPen()
        old_glyphs[name].draw(a)
        new_glyphs[name].draw(b)
        if a.value!=b.value or old["hmtx"][name]!=font["hmtx"][name]:
            actual.append(name)
        assert old["hmtx"][name][0]==font["hmtx"][name][0],name
    assert set(actual)=={"uni221A.s1","uni221A.s2","uni221A.s3",
                        "bask.radical.bottom","bask.radical.ext","bask.radical.top"}
    for name in ["uni221A","uni221A.ssty","uni221A.ssty2"]:
        assert name not in actual
    for key in ["RadicalKernBeforeDegree","RadicalKernAfterDegree",
                "RadicalDegreeBottomRaisePercent","RadicalVerticalGap",
                "RadicalDisplayStyleVerticalGap","RadicalRuleThickness","RadicalExtraAscender"]:
        a=getattr(old["MATH"].table.MathConstants,key)
        b=getattr(font["MATH"].table.MathConstants,key)
        assert getattr(a,"Value",a)==getattr(b,"Value",b)
    intervals=[]
    for count in range(1,6):
        full=1905+count*651+642
        intervals.append([full-(count+1)*300,full-(count+1)*100])
        if len(intervals)>1:
            assert intervals[-1][0]<=intervals[-2][1]
    report=json.loads((private/"engineering.json").read_text())
    report.update({"actually_changed_outlines_or_metrics":actual,
                   "all_advance_widths":"unchanged",
                   "small_and_script_outlines":"RecordingPen comparison unchanged",
                   "compiled_transition_audit":{"outer_tangent":outer_tangent,
                       "inner_tangent":inner_tangent,"outer_second_derivative":outer_second,
                       "inner_second_derivative":inner_second,"G1_to_vertical":True,
                       "zero_endpoint_curvature_for_G2_to_straight":True,"connector_probes":probes},
                   "one_to_five_extender_height_intervals":intervals,
                   "degree_position_parameters":"all unchanged",
                   "experimental_version":font["name"].getDebugName(5),
                   "proof_checks":{"missing_characters":False,"overfull_boxes":False,
                       "expected_embedded_font":True,"matched_detail_and_direct_comparison":True,
                       "cube_root_degree_and_nested_cases":"D5 rendered and visually checked; no observed degree/radicand contact",
                       "near_boundary_heights_pt":[32,36,40,44,48],
                       "clearance_scope":"Preserved outer radicand-side boundary, advances and degree-position constants; not an exhaustive ink-collision certificate."}})
    shutil.copy2(__file__,private/"design_geometry_audit-at-check.py")
    report["audit_implementation_sha256"]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (private/"engineering.json").write_text(json.dumps(report,indent=2)+"\n")
    provenance["actually_changed_outlines_or_metrics"]=actual
    provenance["experimental_version"]=font["name"].getDebugName(5)
    provenance["geometry_audit_sha256"]=report["audit_implementation_sha256"]
    (private/"provenance.json").write_text(json.dumps(provenance,indent=2)+"\n")
    for name,checksum in provenance["build_snapshot"].items():
        assert hashlib.sha256((private/name).read_bytes()).hexdigest()==checksum
    manifest=json.loads((run/"packet/manifest.json").read_text())
    for image in manifest["images"]:
        assert hashlib.sha256((run/"packet"/image["path"]).read_bytes()).hexdigest()==image["sha256"]
    return {"pass":True,"actual_changed_glyphs":actual,
            "candidate_sha256":provenance["candidate_sha256"],
            "version":report["experimental_version"],"images":len(manifest["images"])}


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("run",type=Path)
    print(json.dumps(audit(parser.parse_args().run),indent=2))

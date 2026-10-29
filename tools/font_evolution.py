#!/usr/bin/env python3
"""Build a local visual history from frozen evidence; never redraw the fonts."""
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGNS = [("Radicals", "campaign-2026-10-29"),
             ("Lowercase Greek", "greek-campaign-2026-10-29")]


def read(path):
    return json.loads(path.read_text())


def relative(path):
    p = Path(path)
    return str(p.relative_to(ROOT)) if p.is_absolute() else str(p)


def collect():
    stages = []
    for family, campaign in CAMPAIGNS:
        for number in range(1, 4):
            run = ROOT / "runs" / campaign / f"round-{number}"
            decision = read(run / "decision.json")
            result = read(run / "council-result.json")
            provenance = read(run / "private/provenance.json")
            manifest = read(run / "packet/manifest.json")
            key = result["key"]
            candidate = next(k for k, v in key.items() if v in ("candidate", "trial"))
            incumbent = next(k for k in "AB" if k != candidate)
            accepted = decision["decision"] == "accept_candidate"
            images = []
            for item in manifest["images"]:
                if "control" in item["id"].lower():
                    continue
                path = run / "packet" / item["path"]
                assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], path
                images.append({"id": item["id"], "path": str(path),
                               "mode": item.get("mode", item["id"]),
                               "label": item.get("description", item.get("mode", item["id"])),
                               "sha256": item["sha256"]})
            ballots = {m: read(run / "ballots" / f"{m}.json")
                       for m in ("opus", "sol", "muse")
                       if (run / "ballots" / f"{m}.json").exists()}
            feedback = [{"judge": m, "problem": b["problem"], "change": b["change"],
                         "verify": b["verify"]}
                        for m, ballot in ballots.items()
                        for b in ballot["publication_blockers"][:1]]
            stages.append({"id": f"{campaign}-{number}", "family": family,
                           "round": number, "accepted": accepted,
                           "candidate": candidate, "incumbent": incumbent,
                           "key": key, "reason": decision["reason"],
                           "votes": [result["candidate_preferences"],
                                     result["incumbent_preferences"],
                                     sum(p == "tie" for p in result["preferences"].values())],
                           "preferences": result["preferences"],
                           "complete": result["round_complete"],
                           "candidate_hash": provenance.get("candidate_sha256", ""),
                           "input_hash": provenance["input_sha256"],
                           "candidate_font": relative(provenance["candidate"]),
                           "input_font": relative(provenance["input"]),
                           "candidate_proof": relative(run / "private" / candidate / "proof.pdf"),
                           "images": images, "feedback": feedback,
                           "report": relative(run / "council-report.md"),
                           "recipe": relative(ROOT / "design" / (f"greek-round-{number}.json"
                                      if family == "Lowercase Greek" else f"round-{number}.json")),
                           "manifest": relative(run / "packet/manifest.json")})
    return stages


TEMPLATE = r'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Font evolution</title><style>
html,body{margin:0;padding:0;background:transparent;color:var(--foreground);font-family:var(--font-sans,system-ui)}
*{box-sizing:border-box}h1{font-size:24px;margin:0 0 8px}p{line-height:1.5;margin:8px 0 14px}
.muted{color:var(--muted-foreground,var(--foreground));opacity:.8;font-size:13px}
.chart{height:218px;margin:18px 0}.row{display:grid;grid-template-columns:118px 1fr 82px;gap:10px;align-items:center;height:31px;font-size:12px}
.bar{height:15px;display:flex;background:var(--secondary);border-radius:3px;overflow:hidden}.seg{display:block}
.c{background:var(--chart-1)}.i{background:var(--chart-2)}.t{background:var(--chart-3)}
.legend{display:flex;gap:18px;font-size:12px;margin:10px 0}.dot{display:inline-block;width:9px;height:9px;margin-right:5px}
.controls{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}select,button{font:inherit;color:var(--foreground);background:var(--card);border:1px solid var(--border);padding:8px;border-radius:var(--radius,6px);max-width:100%;min-width:0}
button{cursor:pointer}button.active{border-color:var(--chart-1)}
.status{font-size:14px;font-weight:600;margin:12px 0 6px}.proof{background:white;border-radius:4px;margin-top:12px;overflow:auto}
.proof img{display:block;width:100%;height:auto}.proof.zoom img{width:1500px;max-width:none}.pair{display:grid;grid-template-columns:1fr 1fr}.pair img{min-width:0}.proof.zoom .pair{width:3000px}.caption{font-size:12px;margin:8px 0;overflow-wrap:anywhere}
.note{padding:14px 16px;background:var(--card);border-radius:var(--radius,8px);margin-top:14px}
details{margin:14px 0}summary{cursor:pointer}a{color:var(--chart-1)}.feedback{font-size:13px;line-height:1.5;margin:12px 0}.hash{font-family:var(--font-mono,monospace);font-size:11px;overflow-wrap:anywhere}
@media(max-width:450px){.row{grid-template-columns:92px 1fr 68px;gap:5px;font-size:11px}.legend{gap:10px}}
</style><body>
<h1>Font evolution</h1>
<p>Six proposals, two bounded campaigns. Follow the actual specimens and the decisions that shaped the retained font.</p>
<p class="muted">The starting Greek forms were inherited; each proposal is a revision, not a newly drawn alphabet. Rejected branches remain visible. Model votes measure preference in a particular comparison, not distance to perfection. Proof images are embedded in the downloadable history; linked fonts and records remain in this repository.</p>
<div class="legend"><span><b class="dot c"></b>Proposal</span><span><b class="dot i"></b>Incumbent</span><span><b class="dot t"></b>Tie</span></div>
<div id="chart" class="chart" role="img" aria-label="Three judges' preferences for each proposal"></div>
<div class="controls"><select id="stage" aria-label="Campaign and round"></select><select id="view" aria-label="Proof view"></select><button id="zoom">Inspect at larger scale</button></div>
<div id="status" class="status"></div><div id="key" class="muted"></div>
<p id="reason"></p><div id="proof" class="proof"></div><div id="caption" class="caption"></div>
<div class="note"><b>How to read these proofs</b><p class="muted">A/B identities are revealed here after judging. Both sides retain the original matched proof scale and rendering. Screen fit is a reduction; use larger-scale inspection and the linked full proof records for detail. Distance views are unblurred simulations. Grids and space masks are diagnostics, not quality scores.</p></div>
<details><summary>Constructive critique and provenance</summary><div id="feedback"></div><p id="links"></p><div id="hash" class="hash"></div></details>
__ENTROPY__
<p class="muted">Absolute rubric 0.3: a 3 requires release-quality craft with only minor refinements. A featured new design demands exceptional authorship and resolution. These model panels do not establish perfection, print performance, or publication acceptance.</p>
__ASSETS__<script>const DATA=__DATA__;
const $=s=>document.getElementById(s);const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
DATA.forEach((s,n)=>{let o=new Option(`${s.family} · round ${s.round} · ${s.accepted?'accepted':'retained incumbent'}`,n);$('stage').add(o);
let row=document.createElement('div');row.className='row';row.innerHTML=`<span>${s.family==='Radicals'?'Radical':'Greek'} ${s.round}</span><div class="bar">${s.votes.map((v,i)=>`<span class="seg ${['c','i','t'][i]}" style="width:${v/3*100}%" title="${['Proposal','Incumbent','Tie'][i]}: ${v}"></span>`).join('')}</div><span>${s.accepted?'Accepted':'Retained'}</span>`;$('chart').append(row)});
function show(){const s=DATA[$('stage').value];const image=s.images[$('view').value||0];$('status').textContent=`${s.family} · round ${s.round} — ${s.accepted?'proposal accepted':'incumbent retained'}`;
$('key').textContent=`A = ${s.key.A}; B = ${s.key.B}. Opus / Sol / Muse: ${['opus','sol','muse'].map(m=>s.preferences[m]||'unavailable').join(' / ')}.`;
$('reason').textContent=s.reason;const paired=(image.id==='A-D'||image.id==='B-D')&&!s.images.some(p=>p.id==='AB-D');const images=paired?s.images.filter(p=>p.id==='A-D'||p.id==='B-D'):[image];$('proof').innerHTML=(paired?'<div class="pair">':'')+images.map(p=>`<img alt="${esc(p.label)}" src="${p.asset?$(p.asset).src:p.src}">`).join('')+(paired?'</div>':'');$('caption').textContent=paired?'Original A/B detail sheets shown together at matching scale.':image.label;
$('feedback').innerHTML=s.feedback.map(b=>`<div class="feedback"><b>${esc(b.judge)}: ${esc(b.problem)}</b><br>${esc(b.change)}<br>Verify: ${esc(b.verify)}</div>`).join('');
$('links').innerHTML=`<a href="${s.report}">Complete council critique</a> · <a href="${s.recipe}">Design recipe</a> · <a href="${s.manifest}">Original proof manifest</a><br><a href="${s.input_font}">Input font</a> · <a href="${s.candidate_font}">Proposal font</a> · <a href="${s.candidate_proof}">Proposal proof PDF</a>`;$('hash').textContent='Input SHA-256: '+s.input_hash+' / Candidate SHA-256: '+s.candidate_hash;}
function stage(){const s=DATA[$('stage').value];$('view').replaceChildren();s.images.forEach((p,n)=>$('view').add(new Option(p.id+' · '+p.mode,n)));let direct=s.images.findIndex(p=>p.id==='AB-D'||p.id==='AB-forms');if(direct<0)direct=s.images.findIndex(p=>p.id==='A-D');$('view').value=direct<0?0:direct;show()}
$('stage').onchange=stage;$('view').onchange=show;$('zoom').onclick=()=>{const z=$('proof').classList.toggle('zoom');$('zoom').textContent=z?'Fit to screen':'Inspect at larger scale'};
$('stage').value=DATA.length-1;stage();</script></body></html>'''


def main():
    stages = collect()
    (ROOT / "font-evolution-data.json").write_text(json.dumps(stages, indent=2) + "\n")
    for embedded, filename in [(False, "font-evolution-preview.html"), (True, "font-evolution.html")]:
        data = json.loads(json.dumps(stages))
        assets = []
        for stage in data:
            for image in stage["images"]:
                path = Path(image.pop("path"))
                if embedded:
                    image["src"] = "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()
                else:
                    image["asset"] = f"asset-{len(assets)}"
                    assets.append(f'<img id="{image["asset"]}" src="{path}">')
        encoded = json.dumps(data).replace("<", "\\u003c")
        asset_markup = '<div hidden>' + ''.join(assets) + '</div>' if assets else ''
        entropy = ROOT / 'runs/entropy-2026-10-29/redesigned-storm-inspired.png'
        branch = ''
        if entropy.exists():
            src = ('data:image/png;base64,' + base64.b64encode(entropy.read_bytes()).decode()
                   if embedded else str(entropy))
            branch = ('<details><summary>Unscored image branch · Štorm-inspired exploration</summary>'
                      '<p class="muted">User-requested constructive entropy: a Codex image-generation concept from the retained0.152 reference. '
                      'This raster is inspiration, not a compiled font or an additional hillclimb round. It is not authored by František Štorm.</p>'
                      f'<div class="proof"><img src="{src}" alt="AI generated Greek math design exploration"></div>'
                      '<p><a href="runs/entropy-2026-10-29/redesigned-storm-inspired.png">Original PNG</a> · '
                      '<a href="runs/entropy-2026-10-29/current-design-600dpi.png">Exact current-font reference</a> · '
                      '<a href="runs/entropy-2026-10-29/prompt.txt">Generation prompt</a></p></details>')
        (ROOT / filename).write_text(TEMPLATE.replace("__DATA__", encoded).replace("__ASSETS__", asset_markup).replace("__ENTROPY__", branch))
    print("Built font-evolution.html, preview and provenance data from six frozen rounds.")


if __name__ == "__main__":
    main()

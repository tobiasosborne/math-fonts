#!/usr/bin/env python3
"""Build a planning inventory from pinned primary-source TeX/Unicode definitions.

This only writes design/ams-glyph-inventory.json. It never creates images, edits
experimental outputs, or claims that a requested glyph has been designed.
Run with --sources-dir containing the files listed in SOURCES; --download may
populate that cache. Sources are recorded by SHA-256 in the resulting manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "fontdef.dtx": "https://raw.githubusercontent.com/latex3/latex2e/main/base/fontdef.dtx",
    "amsfonts.dtx": "https://mirrors.ctan.org/fonts/amsfonts/source/amsfonts.dtx",
    "amssymb.dtx": "https://mirrors.ctan.org/fonts/amsfonts/source/amssymb.dtx",
    "amsmath-release.dtx": "https://mirrors.ctan.org/macros/latex/required/amsmath/amsmath.dtx",
    "amsopn-release.dtx": "https://mirrors.ctan.org/macros/latex/required/amsmath/amsopn.dtx",
    "unicode-math-table.tex": "https://tug.ctan.org/macros/unicodetex/latex/unicode-math/unicode-math-table.tex",
    "um-code-epilogue.dtx": "https://tug.ctan.org/macros/unicodetex/latex/unicode-math/um-code-epilogue.dtx",
    "UnicodeData.txt": "https://www.unicode.org/Public/17.0.0/ucd/UnicodeData.txt",
    "StandardizedVariants.txt": "https://www.unicode.org/Public/17.0.0/ucd/StandardizedVariants.txt",
}
MASTER = "baskerville-unified-master-v1"


def code(source):
    """Exclude documentation and docstrip guards; retain executable lines."""
    return "\n".join(re.split(r"(?<!\\)%", line, 1)[0]
                     for line in source.splitlines()
                     if not line.lstrip().startswith("%"))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sources-dir", type=Path, required=True)
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--output", type=Path, default=ROOT / "design/ams-glyph-inventory.json")
    args = ap.parse_args()
    args.sources_dir.mkdir(parents=True, exist_ok=True)
    texts, provenance = {}, []
    for filename, url in SOURCES.items():
        path = args.sources_dir / filename
        if args.download and not path.exists():
            path.write_bytes(urllib.request.urlopen(url, timeout=45).read())
        data = path.read_bytes()
        texts[filename] = data.decode("utf-8-sig")
        provenance.append({"id": filename, "url": url,
                           "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    ucd = {int(parts[0], 16): {"name": parts[1], "decomposition": parts[5]}
           for line in texts["UnicodeData.txt"].splitlines()
           if (parts := line.split(";")) and len(parts) > 5}
    glyphs, by_command, bindings = {}, {}, {}

    def glyph(cps, category="symbol", gid=None, scope="optional", **extra):
        gid = gid or "u" + "_".join(f"{cp:04X}" for cp in cps)
        if gid not in glyphs:
            glyphs[gid] = {"id": gid, "codepoints": [f"U+{cp:04X}" for cp in cps],
                           "characters": "".join(map(chr, cps)),
                           "unicode_names": [ucd.get(cp, {}).get("name", "") for cp in cps],
                           "category": category, "scope": scope,
                           "encoding_kind": "scalar" if len(cps) == 1 else "sequence" if cps else "unencoded",
                           "design_master_id": MASTER, "master_cell": None,
                           "design_status": "uncovered", "evidence": []}
        row = glyphs[gid]
        if scope == "v1":
            row["scope"] = "v1"
        row.update(extra)
        return gid

    table_re = r'\\UnicodeMathSymbol\{"([0-9A-F]+)\}\{\\(\w+)\s*\}\{\\(\w+)\}'
    for cphex, command, mathclass in re.findall(table_re, texts["unicode-math-table.tex"]):
        cp = int(cphex, 16)
        cat = {"mathop": "large_operator", "mathbin": "binary_operator",
               "mathrel": "relation", "mathopen": "delimiter", "mathclose": "delimiter",
               "mathaccent": "accent", "mathaccentwide": "accent", "mathaccentoverlay": "accent",
               "mathover": "horizontal_extensible", "mathunder": "horizontal_extensible",
               "mathpunct": "punctuation", "mathalpha": "alphabet"}.get(mathclass, "ordinary_symbol")
        if "ARROW" in ucd.get(cp, {}).get("name", ""):
            cat = "arrow"
        gid = glyph([cp], cat, unicode_math_command="\\" + command, unicode_math_class=mathclass)
        by_command[command] = gid

    # Compatibility names are aliases only when the replacement is one symbol.
    aliases = {a: b for a, b in re.findall(
        r'\\protected\\def\\(\w+)\s*\{\\(\w+)\}', code(texts["um-code-epilogue.dtx"]))}
    aliases.update({
        "mith": "Planckconst",
        "mfrakI": "Im", "mfrakR": "Re",
        "le": "leq", "ge": "geq", "to": "rightarrow", "gets": "leftarrow",
        "land": "wedge", "lor": "vee", "lnot": "neg", "owns": "ni", "|": "Vert",
        "colon": "mathcolon", "ldotp": "period", "cdotp": "cdotp", "mathring": "ocirc",
        "intop": "int", "ointop": "oint", "smallint": "int", "sqrtsign": "sqrt",
        "triangle": "bigtriangleup", "varbigtriangleup": "bigtriangleup",
        "varbigtriangledown": "bigtriangledown", "bigcirc": "mdlgwhtcircle",
        "circ": "vysmwhtcircle", "bullet": "smblkcircle", "diamond": "smwhtdiamond",
        "square": "mdlgwhtsquare", "lozenge": "mdlgwhtlozenge", "blacksquare": "smblksquare",
        "blacklozenge": "smblklozenge", "centerdot": "cdotp", "circledS": "circledS",
        "circlearrowleft": "acwopencirclearrow", "circlearrowright": "cwopencirclearrow",
        "doteqdot": "Doteq", "backepsilon": "upbackepsilon", "digamma": "updigamma",
        "dashrightarrow": "rightdasharrow", "dashleftarrow": "leftdasharrow",
        "eth": "matheth", "lhd": "vartriangleleft", "rhd": "vartriangleright",
        "unlhd": "trianglelefteq", "unrhd": "trianglerighteq",
    })
    for prefix in ["mbf", "Bbb", "msans", "mtt"]:
        for digit, word in enumerate("zero one two three four five six seven eight nine".split()):
            aliases[prefix + str(digit)] = prefix + word
    # Known scalar spellings absent from the package's chosen canonical names.
    scalar = {"period": 0x2E, "circledS": 0x24C8, "mathparagraph": 0xB6,
              "mathsection": 0xA7, "mathdollar": 0x24, "mathsterling": 0xA3,
              "yen": 0xA5, "checkmark": 0x2713, "circledR": 0xAE, "maltese": 0x2720,
              "ne": 0x2260, "neq": 0x2260, "vdots": 0x22EE, "ddots": 0x22F1,
              "cdots": 0x22EF, "mathellipsis": 0x2026, "ldots": 0x2026,
              "ntriangleleft": 0x22EA, "ntriangleright": 0x22EB,
              "npreceq": 0x22E0, "nsucceq": 0x22E1,
              "dddot": 0x20DB, "ddddot": 0x20DC}
    for command, cp in scalar.items():
        by_command[command] = glyph([cp])
    # Preserve AMS shapes that Unicode/modern command aliases would collapse.
    visual_variants = {"emptyset": "varnothing", "hbar": "hslash", "shortmid": "mid",
                       "shortparallel": "parallel", "smallsetminus": "setminus",
                       "thicksim": "sim", "thickapprox": "approx", "varpropto": "propto",
                       "smallsmile": "smile", "smallfrown": "frown",
                       "nshortmid": "nmid", "nshortparallel": "nparallel"}
    for command, base in visual_variants.items():
        base_gid = by_command[base]
        by_command[command] = glyph([], "legacy_shape_variant", "legacy." + command,
                                    scope="v1", semantic_base_id=base_gid,
                                    reason="Distinct legacy AMS/core shape; no separate Unicode scalar. Explicit package binding required.")
        glyphs[base_gid]["scope"] = "v1"
    seqs = {"lvertneqq": (0x2268, 0xFE00), "gvertneqq": (0x2269, 0xFE00),
            "varsubsetneq": (0x228A, 0xFE00), "varsupsetneq": (0x228B, 0xFE00),
            "varsubsetneqq": (0x2ACB, 0xFE00), "varsupsetneqq": (0x2ACC, 0xFE00),
            "nleqslant": (0x2A7D, 0x338), "ngeqslant": (0x2A7E, 0x338),
            "nleqq": (0x2266, 0x338), "ngeqq": (0x2267, 0x338),
            "nsubseteqq": (0x2AC5, 0x338), "nsupseteqq": (0x2AC6, 0x338)}
    for command, cps in seqs.items():
        by_command[command] = glyph(cps, "relation", scope="v1",
                                    implementation="cmap14-or-package-binding" if cps[1] == 0xFE00 else "composed-or-precomposed-unencoded")
    construction_commands = ["braceld", "bracerd", "bracelu", "braceru", "bracevert",
                             "arrowvert", "Arrowvert", "mapstochar", "lhook", "rhook", "dabar@"]
    for command in construction_commands:
        by_command[command] = glyph([], "legacy_construction_piece", "legacy." + command,
                                    scope="v1", package_binding="\\" + command)
    by_command["not"] = by_command["notaccent"]

    greek = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta", "Iota", "Kappa", "Lambda",
             "Mu", "Nu", "Xi", "Omicron", "Pi", "Rho", "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega"]
    greek += [x.lower() for x in greek]
    greek += ["varTheta", "varsigma", "vartheta", "varkappa", "varrho", "varpi", "varepsilon", "varphi"]
    for command in greek:
        aliases[command] = ("mup" if command[:1].isupper() else "mit") + command

    def resolve(command):
        seen = set()
        while command not in by_command and command in aliases and command not in seen:
            seen.add(command)
            command = aliases[command]
        return by_command.get(command)

    def bind(command, package, mathclass=None, declaration=None, slot=None, gid=None, literal=False):
        gid = gid or resolve(command)
        if gid is None:
            raise ValueError(f"Unmapped command {package}: {command}")
        glyphs[gid]["scope"] = "v1"
        spelling = command if literal else "\\" + command
        key = (package, spelling)
        row = {"command": spelling, "input_kind": "literal_character" if literal else "control_sequence",
               "package": package, "target_id": gid, "kind": declaration or "compatibility_or_composite"}
        if mathclass:
            row["legacy_math_class"] = mathclass
        if slot:
            row["legacy_font_and_slot"] = slot
        bindings[key] = row

    declaration_counts = {}
    decl_re = r'\\(?:ams@)?DeclareMath(Symbol|Accent|Delimiter|Radical)\{([^}]+)\}\s*\{([^}]+)\}\s*\{([^}]+)\}\s*\{([^}]+)\}'
    for filename, package in [("fontdef.dtx", "latex-core"), ("amsfonts.dtx", "amsfonts"), ("amssymb.dtx", "amssymb")]:
        source = code(texts[filename])
        declarations = re.findall(decl_re, source)
        declarations = [d for d in declarations if "#" not in d[1]]
        declaration_counts[package] = len(declarations)
        for typ, command, mathclass, font, slot in declarations:
            literal = not command.startswith("\\")
            command = command.removeprefix("\\")
            if len(command) == 1 and command.isascii() and command.isalnum():
                gid = resolve("mit" + command) if command.isalpha() else glyph([ord(command)], "numeral")
            elif len(command) == 1 and command in "!*+,-.:;=?()[]<>/|":
                cp = {"-": 0x2212, "*": 0x2217}.get(command, ord(command))
                gid = glyph([cp], "punctuation" if command in "!,.?;:" else "binary_operator")
            else:
                gid = resolve(command)
            legacy_location = {"font": font, "slot": slot}
            if typ == "Radical":
                # Radical signature has no math-class argument.
                legacy_location = {"small_font": mathclass, "small_slot": font,
                                   "large_font": slot}
            bind(command, package, None if typ == "Radical" else mathclass,
                 typ, legacy_location, gid, literal)
        # Exact public symbol aliases; initial relax/undefined assignments excluded.
        for alias, target in re.findall(r'\\(?:global\\)?let\\([A-Za-z]+)\s*\\([A-Za-z]+)', source):
            if resolve(target) and not resolve(alias):
                aliases[alias] = target
            if resolve(alias) and target not in {"relax", "undefined", "square"}:
                bind(alias, package, declaration="source_alias")

    # Core composites: each is a semantic symbol even when old TeX assembled it.
    composites = "cong notin rightleftharpoons doteq mapsto hookrightarrow hookleftarrow bowtie models Longrightarrow longrightarrow longleftarrow Longleftarrow longmapsto longleftrightarrow Longleftrightarrow iff relbar Relbar cdots vdots ddots overrightarrow overleftarrow overbrace underbrace mathellipsis mathsterling".split()
    aliases.update({"iff": "Longleftrightarrow", "relbar": "minus", "Relbar": "equal",
                    "overrightarrow": "overrightarrow", "overleftarrow": "overleftarrow"})
    for command in composites:
        bind(command, "latex-core", declaration="composite_or_robust_symbol")
    for command in "yen checkmark circledR maltese dashrightarrow dashleftarrow Join".split():
        if command == "Join":
            by_command[command] = glyph([], "legacy_shape_variant", "legacy.Join", scope="v1",
                                        reason="Legacy AMS overlaid rtimes/ltimes; retain explicit package construction.")
        bind(command, "amsfonts")
    for command in "int iint iiint iiiint idotsint dddot ddddot overleftrightarrow underleftarrow underrightarrow underleftrightarrow lvert rvert lVert rVert".split():
        aliases.update({"lvert": "vert", "rvert": "vert", "lVert": "Vert", "rVert": "Vert"})
        if command == "idotsint":
            by_command[command] = glyph([], "composite_recipe", "recipe.idotsint", scope="v1",
                                        recipe=["\\int", "\\cdots", "\\int"], outline_required=False)
        bind(command, "amsmath", declaration="composite_or_public_symbol")
    bind("neq", "latex-core")
    bind("ldots", "latex-core")

    # Finite package alphabets: encoded styles, not typographic-style name guesses.
    alphabet_styles = {
        "upright": ("mup", "symup", "latin+greek+digits"),
        "italic": ("mit", "symit", "latin+greek"),
        "bold_upright": ("mbf", "symbfup", "latin+greek+digits"),
        "bold_italic": ("mbfit", "symbfit", "latin+greek"),
        "double_struck": ("Bbb", "symbb", "latin+digits"),
        "fraktur": ("mfrak", "symfrak", "latin"),
        "bold_fraktur": ("mbffrak", "symbffrak", "latin"),
        "script": ("mscr", "symscr", "latin"),
        "sans_upright": ("msans", "symsfup", "latin+digits"),
        "monospace": ("mtt", "symtt", "latin+digits"),
    }
    alphabet_sets = []
    latin = [chr(x) for x in list(range(65, 91)) + list(range(97, 123))]
    digits = list("0123456789")
    for style, (prefix, public, domains) in alphabet_styles.items():
        members = []
        for letter in latin:
            if prefix == "mup":
                gid = glyph([ord(letter)], "alphabet", scope="v1")
            else:
                gid = resolve(prefix + letter)
            if gid is None:
                raise ValueError(f"Missing alphabet {prefix}{letter}")
            glyphs[gid].update(scope="v1", category="alphabet", alphabet_style=style)
            members.append({"input": letter, "target_id": gid})
        if "greek" in domains:
            for letter in greek + ["partial", "nabla"]:
                gid = resolve(prefix + letter)
                if not gid:
                    # Upright partial/nabla are the regular symbol scalars.
                    gid = resolve(letter) if prefix == "mup" else None
                if gid is None:
                    raise ValueError(f"Missing Greek {prefix}{letter}")
                glyphs[gid].update(scope="v1", category="alphabet", alphabet_style=style)
                members.append({"input": "\\" + letter, "target_id": gid})
        if "digits" in domains:
            for digit in digits:
                gid = glyph([ord(digit)], "numeral", scope="v1") if prefix == "mup" else resolve(prefix + digit)
                if gid is None:
                    raise ValueError(f"Missing numeral {prefix}{digit}")
                glyphs[gid].update(scope="v1", category="numeral", alphabet_style=style)
                members.append({"input": digit, "target_id": gid})
        alphabet_sets.append({"style": style, "selector": "\\" + public,
                              "members": members, "scope": "v1"})
    for cp in range(48, 58):
        glyph([cp], "numeral", scope="v1", alphabet_style="upright")
    # Accented variables need dotless i/j; italic versions are encoded separately.
    for cp in [0x131, 0x237, 0x1D6A4, 0x1D6A5]:
        base = glyph([cp], "alphabet", scope="v1")
        glyph([], "bold_dotless_variant", base + ".bold", scope="v1", base_id=base)
    # Small/bold digamma, upright capital digamma: explicit finite additions.
    for command in ["upDigamma", "updigamma", "mbfDigamma", "mbfdigamma"]:
        if resolve(command):
            glyphs[resolve(command)]["scope"] = "v1"

    # Engineering targets are separate from semantic Unicode coverage.
    # Four legacy named sizes, large-operator display variants, three stretch
    # widths and explicit assembly pieces make the initial work finite.
    engineering = []
    vertical = "lparen rparen lbrack rbrack lbrace rbrace lceil rceil lfloor rfloor langle rangle vert Vert backslash mathslash uparrow downarrow updownarrow Uparrow Downarrow Updownarrow lmoustache rmoustache lgroup rgroup sqrt".split()
    horizontal = "widehat widetilde overbrace underbrace overleftarrow overrightarrow overleftrightarrow underleftarrow underrightarrow underleftrightarrow leftarrow rightarrow".split()
    for command in vertical + horizontal:
        base = resolve(command)
        if base is None:
            raise ValueError(f"Missing extensible {command}")
        glyphs[base]["scope"] = "v1"
        axis = "vertical" if command in vertical else "horizontal"
        sizes = ["size1", "size2", "size3", "size4"] if axis == "vertical" else ["wide1", "wide2", "wide3"]
        ids = [glyph([], "size_variant", f"{base}.{size}", scope="v1", base_id=base, axis=axis)
               for size in sizes]
        parts = (["top", "extender", "bottom"] + (["middle"] if command in ["lbrace", "rbrace"] else [])) if axis == "vertical" else ["left", "extender", "right"]
        # Non-extending diagonal/angle/moustache constructions use only discrete sizes.
        if command in ["backslash", "mathslash", "langle", "rangle", "lmoustache", "rmoustache"]:
            parts = []
        partids = [glyph([], "assembly_part", f"{base}.part.{part}", scope="v1", base_id=base, axis=axis, role=part)
                   for part in parts]
        engineering.append({"base_id": base, "command": "\\" + command, "axis": axis,
                            "size_variant_ids": ids, "assembly_part_ids": partids,
                            "note": "Initial engineering budget; joining/overlap and exact dimensions must be proved. Shared outlines may reduce physical glyph count."})
    largeops = sorted({r["target_id"] for r in bindings.values()
                       if glyphs[r["target_id"]].get("unicode_math_class") == "mathop"})
    for base in largeops:
        glyph([], "display_variant", base + ".display", scope="v1", base_id=base)
    # Full bold-symbol support is budgeted explicitly, not confused with alphabets.
    bold_bases = [r for r in list(glyphs.values()) if r["scope"] == "v1" and
                  r["category"] not in {"numeral", "composite_recipe", "size_variant", "display_variant", "assembly_part", "bold_dotless_variant"}
                  and (r["category"] != "alphabet" or not r.get("alphabet_style") and r["id"] not in {"u0131", "u0237", "u1D6A4", "u1D6A5"})]
    for base in bold_bases:
        glyph([], "bold_symbol_variant", base["id"] + ".bold", scope="v1", base_id=base["id"],
              reason="Bold math companion; separately drawn/proved. No automatic emboldening accepted as completion.")

    # Operator strings are spelling/spacing recipes, never new ligature glyphs.
    operators = []
    op_source = code(texts["amsopn-release.dtx"])
    for name, limits, spelling in re.findall(r'\\protected\\def\\(\w+)\{\\qopname\\relax\s+([om])\{([^}]+)\}', op_source):
        operators.append({"command": "\\" + name, "upright_text": spelling,
                          "takes_display_limits": limits == "m", "glyph_recipe": "upright Latin, punctuation and spacing"})
    for name in "varinjlim varprojlim varliminf varlimsup".split():
        operators.append({"command": "\\" + name, "glyph_recipe": "upright lim plus arrow/rule construction"})

    # Immutable current32 evidence. Character labels describe Unicode identities,
    # not a promise that the raster visibly distinguishes the paired forms.
    requests = json.loads((ROOT / "runs/glyph-consistency-2026-10-29/requests.json").read_text())
    ambiguous = {"epsilon": "epsilon pair near-duplicate", "variant-epsilon": "epsilon pair near-duplicate",
                 "kappa": "kappa pair near-duplicate", "variant-kappa": "kappa pair near-duplicate",
                 "phi": "phi pair possibly near-duplicate", "variant-phi": "phi pair possibly near-duplicate"}
    current32 = []
    for req in requests:
        cp = int(req["codepoint"][2:], 16)
        # Map by the Unicode source character into the styled italic identity.
        candidates = [row["id"] for row in glyphs.values() if row.get("alphabet_style") == "italic" and
                      row["encoding_kind"] == "scalar" and
                      ucd.get(int(row["codepoints"][0][2:], 16), {}).get("decomposition") == f"<font> {cp:04X}"]
        target = candidates[0] if candidates else None
        if target:
            glyphs[target]["evidence"].append("current32:" + req["name"])
            glyphs[target]["design_status"] = "prior_outline_study_identity_review" if req["name"] in ambiguous else "prior_outline_study"
        current32.append({"name": req["name"], "source_codepoint": req["codepoint"],
                          "italic_target_id": target, "semantic_status": ambiguous.get(req["name"], "label mapped; design not yet accepted as engineered glyph"),
                          "weight_classification": "unresolved; regular-italic prompt does not establish observed weight",
                          "coverage_credit": False,
                          "svg": f"runs/glyph-consistency-2026-10-29/vector-outlines/{req['name']}.svg",
                          "source_master": "runs/glyph-consistency-2026-10-29/master.png",
                          "v1_master_cell": None})

    # Validate actual finite data, not just the fact that the builder ran.
    assert len(current32) == 32 and all(r["italic_target_id"] for r in current32)
    assert all(r["target_id"] in glyphs for r in bindings.values())
    assert all(r["design_master_id"] == MASTER for r in glyphs.values())
    for command, cps in seqs.items():
        if cps[1] == 0xFE00:
            assert f"{cps[0]:04X} FE00;" in texts["StandardizedVariants.txt"]
    reference_table_scalar_count = len({int(cp, 16) for cp, _, _ in re.findall(table_re, texts["unicode-math-table.tex"])})
    # The full Unicode table is a mapping source, never an implicit production list.
    glyphs = {key: row for key, row in glyphs.items() if row["scope"] == "v1"}
    v1 = list(glyphs.values())
    counts = {
        "all_glyph_records": len(glyphs), "v1_glyph_records": len(v1),
        "v1_distinct_encoded_scalars": len({r["codepoints"][0] for r in v1 if r["encoding_kind"] == "scalar"}),
        "v1_sequence_targets": sum(r["encoding_kind"] == "sequence" for r in v1),
        "v1_unencoded_records": sum(r["encoding_kind"] == "unencoded" for r in v1),
        "v1_by_category": dict(sorted(Counter(r["category"] for r in v1).items())),
        "unicode_math_reference_table_scalars": reference_table_scalar_count,
        "optional_glyph_records": 0,
        "command_bindings": len(bindings), "distinct_command_spellings": len({r["command"] for r in bindings.values()}),
        "source_alias_bindings": sum(r["kind"] == "source_alias" for r in bindings.values()),
        "bindings_by_package": dict(Counter(r["package"] for r in bindings.values())),
        "extracted_direct_declarations_by_package": declaration_counts,
        "alphabet_selector_member_requests": sum(len(a["members"]) for a in alphabet_sets),
        "operator_string_recipes": len(operators), "prior_outline_studies": len(current32),
        "unified_master_cells_filled": 0,
    }
    local = []
    for filename in ["fontmath.ltx", "amsfonts.sty", "amssymb.sty", "amsmath.sty", "unicode-math-table.tex"]:
        found = subprocess.run(["kpsewhich", filename], text=True, capture_output=True, check=False).stdout.strip()
        if found:
            data = Path(found).read_bytes()
            local.append({"file": filename, "path": found, "sha256": hashlib.sha256(data).hexdigest()})
    out = {
        "schema_version": 1, "status": "planning_inventory_not_font_coverage", "snapshot_date": "2026-10-29",
        "scope": "Core LaTeX math + amsmath + amsfonts/amssymb + finite modern math alphabets and construction budget. Optional unicode-math remainder is explicit.",
        "design_master": {"id": MASTER, "path": None, "status": "planned_not_generated",
                          "baskerville_reference_manifest": "design/storm-reference.json",
                          "rule": "One unified design image is the design root for the entire package. Category sheets and crops are derived views. No independent category design roots.",
                          "seed_evidence": "runs/glyph-consistency-2026-10-29/master.png",
                          "seed_policy": "Continue accepted image-derived theme; immutable current32 studies inform the unified root. Cell assignments remain uncovered until the unified master exists and identities are reviewed."},
        "sources": provenance, "local_installation_audit": local, "counts": counts,
        "command_bindings": sorted(bindings.values(), key=lambda r: (r["package"], r["command"])),
        "alphabet_sets": alphabet_sets, "operator_recipes": operators,
        "engineering_constructions": engineering, "current32_evidence": current32,
        "layout_capabilities_not_new_glyphs": {
            "amsmath_environments": "equation align alignat flalign gather multline split aligned alignedat gathered cases matrix pmatrix bmatrix Bmatrix vmatrix Vmatrix smallmatrix subequations".split(),
            "fraction_binomial_commands": ["\\" + c for c in "frac dfrac tfrac cfrac genfrac binom dbinom tbinom".split()],
            "placement_commands": ["\\" + c for c in "overset underset sideset stackrel limits nolimits displaylimits substack smash phantom hphantom vphantom".split()],
            "extensible_labeled_arrows": ["\\xleftarrow", "\\xrightarrow"],
            "dots_recipes": ["\\" + c for c in "dots dotsc dotsb dotsm dotsi dotso ldots cdots vdots ddots".split()],
            "text_and_bold": ["\\text", "\\operatorname", "\\boldsymbol", "\\pmb"],
            "note": "Representative compatibility proof obligations, not an exhaustive macro inventory. pmb must not substitute for designed bold completion.",
        },
        "optional_extensions_not_in_v1": [
            "Bold script/calligraphic; separate calligraphic and script alternates",
            "Sans italic, sans bold and sans bold italic alphabets",
            "Italic/bold italic numeral alternates; oldstyle/proportional/tabular numeral features",
            "Double-struck italic and nonstandard Greek blackboard/script/fraktur",
            "Remaining Unicode mathematical symbols outside the named core/AMS target",
            "Additional optical masters, text ligatures and extended multilingual text coverage",
        ],
        "glyphs": sorted(glyphs.values(), key=lambda r: r["id"]),
        "limitations": [
            "No generated or compiled font coverage is asserted; this is a finite design/work inventory.",
            "Direct package declarations and selected public composites are inventoried, not every macro in amsmath or every TeX command accepting math.",
            "unicode-math canonical command names and legacy TeX names can differ in glyph identity, class and construction; compatibility needs explicit tests.",
            "Size and assembly counts are an initial engineering budget. Bold companion construction/optical variants may require additional physical glyphs.",
            "Regular math is the first implementation milestone; complete designed bold MATH support remains required for this full v1 inventory.",
            "One record is one semantic/variant request; glyph sharing, recipes and cmap aliases mean this is not a final physical OTF glyph count.",
            "Italic and bold italic numerals, oldstyle/proportional numerals, bold script, sans italic/bold, additional script/calligraphic alternates are optional extras, not silently required by AMS.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()

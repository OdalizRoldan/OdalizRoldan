"""Build the profile: every SVG in assets/ (dark and light) and README.md.

Run from the repo root:  python scripts/build.py
Text is set in JetBrains Mono (embedded), so widths are exact: 0.6 em per character.
"""
import base64
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
USER = "OdalizRoldan"
RAW = f"https://github.com/{USER}"

THEMES = {
    "dark": dict(
        panel="#0b0f14", card="#161b22", border="#30363d", edge="#2f363e", dash="#4b5563",
        text="#e6edf3", soft="#c9d1d9", muted="#9198a1",
        research="#6ee7b7", research_text="#d1fae5", concept="#c4b5fd",
        product="#fbbf24", product_text="#fde68a", blue="#9db4ff", orange="#f0883e",
        me="#e6edf3", me_text="#0d1117", thesis_border="#285e4b", product_border="#5c4614",
    ),
    "light": dict(
        panel="#f6f8fa", card="#ffffff", border="#d0d7de", edge="#c8d1da", dash="#8c959f",
        text="#1f2328", soft="#31373d", muted="#59636e",
        research="#047857", research_text="#065f46", concept="#6d28d9",
        product="#b45309", product_text="#92400e", blue="#1d4ed8", orange="#bc4c00",
        me="#1f2328", me_text="#ffffff", thesis_border="#7dd3b0", product_border="#e3bf7d",
    ),
}

FONTS = {w: base64.b64encode((ROOT / "fonts" / f"jbm-{w}.woff2").read_bytes()).decode() for w in (400, 700, 800)}


# ---------- primitives ----------

def tw(s, size):
    return len(s) * 0.6 * size


def wrap(s, width, size):
    per = max(1, int(width // (0.6 * size)))
    lines, cur = [], ""
    for word in s.split():
        cand = f"{cur} {word}" if cur else word
        if len(cand) <= per:
            cur = cand
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text(x, y, s, size, fill, weight=400, anchor="start", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" xml:space="preserve"{extra}>{escape(s)}</text>')


def segs(x, y, parts, size, weight=400):
    """One line made of (string, color) parts."""
    spans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in parts)
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" xml:space="preserve">{spans}</text>'


def pills(x, y, labels, t, size=11, max_w=None, color=None):
    """Rounded tags; wraps onto a new row when max_w is reached. Returns (svg, bottom_y)."""
    out, cx, cy, h = [], x, y, size + 13
    for lab in labels:
        w = tw(lab, size) + 18
        if max_w and cx + w > x + max_w:
            cx, cy = x, cy + h + 6
        out.append(f'<rect x="{cx:.1f}" y="{cy}" width="{w:.1f}" height="{h}" rx="{h/2}" fill="none" stroke="{t["border"]}"/>')
        out.append(text(cx + 9, cy + h / 2 + size * 0.36, lab, size, color or t["soft"]))
        cx += w + 6
    return "".join(out), cy + h


def svg(w, h, body, label, weights=(400, 700)):
    faces = "".join(
        f"@font-face{{font-family:'JBM';font-weight:{wt};src:url(data:font/woff2;base64,{FONTS[wt]}) format('woff2')}}"
        for wt in weights)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label, {chr(34): "&quot;"})}">'
            f'<title>{escape(label)}</title>'
            f"<style>{faces}text{{font-family:'JBM',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}</style>"
            f"{body}</svg>")


LOCK = '<g transform="translate({x},{y})" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></g>'

W = 840


# ---------- sections ----------

def hero(t):
    b = [f'<rect x="0.5" y="0.5" width="{W-1}" height="299" rx="16" fill="{t["panel"]}" stroke="{t["border"]}"/>']
    b.append(f'<line x1="580" y1="1" x2="580" y2="299" stroke="{t["border"]}"/>')
    prompt = [("odaliz@kg:~$ ", t["muted"]), ("MATCH", t["concept"]), (" (me)-[", t["soft"]), (":BUILDS", t["research"]),
              ("]->(x) ", t["soft"]), ("RETURN", t["concept"]), (" x", t["soft"])]
    b.append(segs(36, 52, prompt, 13))
    cx = 36 + tw("odaliz@kg:~$ MATCH (me)-[:BUILDS]->(x) RETURN x", 13) + 4
    b.append(f'<rect x="{cx:.1f}" y="41" width="8" height="14" fill="{t["research"]}">'
             '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/></rect>')
    b.append(text(34, 112, "Odaliz", 46, t["text"], 800))
    b.append(text(34, 162, "Rojas Roldán", 46, t["text"], 800))
    b.append(segs(36, 204, [("I ground LLM agents in ", t["soft"]), ("knowledge graphs,", t["research"])], 16))
    b.append(text(36, 228, "so they stop inventing what isn't there.", 16, t["soft"]))
    p, _ = pills(36, 252, ["AI Engineer · ICI-UPB", "Leader · AWS UG AI Bolivia", "Cochabamba, BO"], t, 11)
    b.append(p)
    # decorative graph
    ox, oy = 580, 10
    E = [(130, 140, 55, 70), (130, 140, 215, 60), (130, 140, 220, 200), (130, 140, 50, 215), (55, 70, 215, 60),
         (215, 60, 220, 200), (50, 215, 130, 255), (220, 200, 130, 255), (55, 70, 20, 140), (20, 140, 50, 215)]
    b.append(f'<g transform="translate({ox},{oy})" stroke="{t["edge"]}" stroke-width="1.3">' +
             "".join(f'<line x1="{a}" y1="{c}" x2="{d}" y2="{e}"/>' for a, c, d, e in E) + "</g>")
    g = [f'<circle cx="130" cy="140" r="22" fill="none" stroke="{t["research"]}"><animate attributeName="r" values="20;40;20" dur="3s" repeatCount="indefinite"/>'
         '<animate attributeName="opacity" values="0.9;0;0.9" dur="3s" repeatCount="indefinite"/></circle>',
         f'<circle cx="130" cy="140" r="17" fill="{t["me"]}"/>',
         f'<circle cx="55" cy="70" r="9" fill="{t["research"]}"/>', f'<circle cx="215" cy="60" r="7" fill="{t["concept"]}"/>',
         f'<circle cx="220" cy="200" r="9" fill="{t["product"]}"/>', f'<circle cx="50" cy="215" r="7" fill="{t["research"]}"/>',
         f'<circle cx="130" cy="255" r="6" fill="{t["concept"]}"/>', f'<circle cx="20" cy="140" r="5" fill="{t["product"]}"/>',
         text(70, 50, ":Research", 10, t["research"]), text(150, 230, ":Product", 10, t["product"]),
         text(144, 278, ":Concept", 10, t["concept"])]
    b.append(f'<g transform="translate({ox},{oy})">' + "".join(g) + "</g>")
    return svg(W, 300, "".join(b), "Odaliz Rojas Roldán. I ground LLM agents in knowledge graphs, so they stop inventing what isn't there.",
               (400, 800))


def header(t, parts, sub=""):
    b = [segs(0, 34, [(s, t[c]) for s, c in parts], 21, 700)]
    if sub:
        x = tw("".join(s for s, _ in parts), 21) + 16
        b.append(text(x, 34, sub, 13, t["muted"]))
    b.append(f'<line x1="0" y1="52.5" x2="{W}" y2="52.5" stroke="{t["border"]}"/>')
    return svg(W, 60, "".join(b), "".join(s for s, _ in parts) + (f" — {sub}" if sub else ""))


def code_panel(t, lines, label, size=13.5, lh=27):
    h = 22 * 2 + len(lines) * lh - 6
    b = [f'<rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="10" fill="{t["panel"]}" stroke="{t["border"]}"/>']
    for i, parts in enumerate(lines):
        b.append(segs(24, 22 + 17 + i * lh, [(s, t[c]) for s, c in parts], size))
    return svg(W, h, "".join(b), label)


def about(t):
    rows = [("focus", "knowledge graphs × LLM agents × distributed systems"),
            ("research", "ICI-UPB, Institute of Computational Intelligence"),
            ("thesis", "multi-agent RCA with topological memory · in development"),
            ("community", "I lead the AWS User Group AI Bolivia"),
            ("ships", "software for real businesses, from clinics to construction")]
    lines = [[("MATCH", "concept"), (" (o:", "text"), ("Engineer", "research"), (" {handle: ", "text"),
              ('"OdalizRoldan"', "product"), ("})", "text")]]
    for i, (k, v) in enumerate(rows):
        lead = "RETURN" if i == 0 else "     ,"
        lines.append([(lead, "concept" if i == 0 else "text"), (f" o.{k:<11}", "text"), (f"// {v}", "muted")])
    label = "About: " + "; ".join(v for _, v in rows)
    return code_panel(t, lines, label)


def graph(t):
    Wg, Hg = 880, 600
    b = [f'<rect x="0.5" y="0.5" width="{Wg-1}" height="{Hg-1}" rx="16" fill="{t["panel"]}" stroke="{t["border"]}"/>']
    dy = 22
    O = (440, 285)
    hubs = {"KG": (290, 205, "Knowledge Graphs"), "AG": (440, 165, "LLM Agents"), "DS": (590, 205, "Distributed Systems"),
            "ML": (290, 395, "Machine Learning"), "RB": (590, 395, "Real-world builds")}
    research = [(440, 55, 17, "MAS-KG · thesis", ["KG", "AG", "DS"]), (110, 230, 12, "Katuy Graph", ["KG"]),
                (150, 130, 11, "NL2SPARQL", ["KG", "AG"]), (760, 120, 12, "Online Boutique", ["DS"]),
                (130, 460, 10, "RoboAI", ["ML"]), (290, 490, 10, "CartPole DQN", ["ML"]),
                (400, 470, 9, "Haskell classifier", ["ML"]), (170, 330, 9, "nanochat study", ["ML"])]
    products = [(770, 310, "Rivt"), (800, 400, "Katuy"), (760, 485, "Clinic system"), (620, 500, "Dipafex"),
                (510, 480, "Online store"), (680, 300, "AI agency"), (840, 470, "Clase360")]
    E = []
    for k, (x, y, _) in hubs.items():
        E.append((O[0], O[1], x, y))
    for x, y, _, _, to in research:
        for k in to:
            E.append((x, y, hubs[k][0], hubs[k][1]))
    for x, y, _ in products:
        E.append((x, y, hubs["RB"][0], hubs["RB"][1]))
    g = [f'<g stroke="{t["edge"]}" stroke-width="1.4">' + "".join(f'<line x1="{a}" y1="{c}" x2="{d}" y2="{e}"/>' for a, c, d, e in E) + "</g>"]
    g.append(f'<g stroke="{t["dash"]}" stroke-width="1.2" stroke-dasharray="4 5" fill="none"><path d="M440 55 Q 640 40 760 120"/>'
             '</g>')
    for lx, ly, lab in [(440, 238, ":RESEARCHES"), (509, 345, ":BUILDS"), (366, 345, ":LEARNS"), (640, 52, ":RUNS_ON")]:
        w = tw(lab, 10) + 12
        g.append(f'<rect x="{lx-w/2:.1f}" y="{ly-12}" width="{w:.1f}" height="16" rx="3" fill="{t["panel"]}"/>')
        g.append(text(lx, ly, lab, 10, t["muted"], anchor="middle"))
    g.append(f'<circle cx="{O[0]}" cy="{O[1]}" r="30" fill="none" stroke="{t["me"]}" stroke-opacity="0.4">'
             '<animate attributeName="r" values="30;48;30" dur="3.2s" repeatCount="indefinite"/>'
             '<animate attributeName="stroke-opacity" values="0.45;0;0.45" dur="3.2s" repeatCount="indefinite"/></circle>')
    g.append(f'<circle cx="{O[0]}" cy="{O[1]}" r="30" fill="{t["me"]}"/>')
    g.append(text(O[0], O[1] + 4, "Odaliz", 12, t["me_text"], 700, "middle"))
    for x, y, lab in hubs.values():
        g.append(f'<circle cx="{x}" cy="{y}" r="20" fill="{t["panel"]}" stroke="{t["concept"]}" stroke-width="2"/>')
        g.append(text(x, y + 38, lab, 11.5, t["concept"], 700, "middle"))
    for x, y, r, lab, _ in research:
        g.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{t["research"]}"/>')
        if lab.startswith("MAS"):
            g.append(text(x, y - 26, lab, 12, t["research_text"], 700, "middle"))
        else:
            g.append(text(x, y + r + 16, lab, 11, t["research_text"], 400, "middle"))
    for x, y, lab in products:
        g.append(f'<rect x="{x-10}" y="{y-10}" width="20" height="20" rx="5" fill="{t["product"]}"/>')
        g.append(text(x, y + 28, lab, 11, t["product_text"], 400, "middle"))
    b.append(f'<g transform="translate(0,{dy})">' + "".join(g) + "</g>")
    # legend
    ly = Hg - 26
    leg = [f'<circle cx="34" cy="{ly-4}" r="6" fill="{t["me"]}"/>', text(46, ly, "me", 11, t["muted"]),
           f'<circle cx="94" cy="{ly-4}" r="5" fill="none" stroke="{t["concept"]}" stroke-width="2"/>', text(106, ly, ":Concept", 11, t["muted"]),
           f'<circle cx="198" cy="{ly-4}" r="6" fill="{t["research"]}"/>', text(210, ly, ":Research / :Experiment", 11, t["muted"]),
           f'<rect x="392" y="{ly-10}" width="12" height="12" rx="3" fill="{t["product"]}"/>', text(410, ly, ":Product (private)", 11, t["muted"]),
           f'<line x1="562" y1="{ly-4}" x2="590" y2="{ly-4}" stroke="{t["dash"]}" stroke-width="1.2" stroke-dasharray="4 5"/>',
           text(598, ly, "cross-links", 11, t["muted"])]
    b.extend(leg)
    return svg(Wg, Hg, "".join(b),
               "Knowledge graph of my work: me at the center, linked to Knowledge Graphs, LLM Agents, Distributed Systems, "
               "Machine Learning and Real-world builds, and each of those to its projects.")


def thesis(t):
    pad, colw, gap = 24, 248, 24
    cols = [("PROBLEM", "orange", "LLMs that diagnose microservices invent dependencies that don't exist: structural hallucination."),
            ("APPROACH", "research", "A typed knowledge graph of the cluster in Memgraph, built from protos, manifests and DB schemas. "
                                     "Root cause by deterministic graph traversal; the LLM reasons over the result."),
            ("EVALUATION", "concept", "A multi-agent system against a vector-RAG baseline, under strict fairness, on Google's Online Boutique.")]
    wrapped = [wrap(body, colw, 13) for _, _, body in cols]
    body_top = 140
    tags_y = body_top + max(len(w) for w in wrapped) * 20 + 10
    h = tags_y + 24 + pad
    b = [f'<rect x="1" y="1" width="{W-2}" height="{h-2}" rx="14" fill="{t["card"]}" stroke="{t["thesis_border"]}" stroke-width="1.5"/>']
    b.append(text(pad, 40, '(:Thesis {status: "in development"})', 12, t["research"]))
    b.append(text(W - pad, 40, "ICI-UPB · repo opens when it's ready", 12, t["muted"], anchor="end"))
    b.append(text(pad, 78, "MAS-KG · root-cause analysis", 22, t["text"], 700))
    b.append(text(pad, 104, "with topological memory", 22, t["text"], 700))
    for i, ((head, c, _), lines) in enumerate(zip(cols, wrapped)):
        x = pad + i * (colw + gap)
        b.append(text(x, 128, head, 11, t[c], 700))
        for j, ln in enumerate(lines):
            b.append(text(x, body_top + 6 + j * 20, ln, 13, t["soft"]))
    p, _ = pills(pad, tags_y, ["Python", "Memgraph", "Cypher", "OpenTelemetry", "Kubernetes", "AWS Bedrock"], t)
    b.append(p)
    return svg(W, h, "".join(b), "Thesis, in development: MAS-KG, root-cause analysis with topological memory. " + " ".join(c[2] for c in cols))


def small_cards(t, cards, w, size=12.5):
    """Equal-height cards. cards: dicts with label, title, body, tags, lock. Returns list of svg strings."""
    pad = 20
    inner = w - 2 * pad
    lay = []
    for c in cards:
        lines = wrap(c["body"], inner, size)
        body_end = 92 + len(lines) * 19
        _, tag_bottom = pills(pad, body_end + 6, c["tags"], t, 10.5, inner)
        lay.append((c, lines, body_end, tag_bottom))
    h = max(tb for *_, tb in lay) + pad
    out = []
    for c, lines, body_end, _ in lay:
        b = [f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="12" fill="{t["card"]}" stroke="{t["border"]}"/>']
        b.append(text(pad, 34, c["label"], 11, t["research"]))
        tsize = 16 if tw(c["title"], 16) <= inner else 14
        b.append(text(pad, 64, c["title"], tsize, t["text"], 700))
        if c.get("lock"):
            b.append(LOCK.format(x=w - pad - 22, y=46, c=t["muted"]))
        for j, ln in enumerate(lines):
            b.append(text(pad, 92 + j * 19, ln, size, t["soft"]))
        p, _ = pills(pad, body_end + 6, c["tags"], t, 10.5, inner)
        b.append(p)
        out.append(svg(w, h, "".join(b), f'{c["title"]}: {c["body"]}'))
    return out


RESEARCH_CARDS = [
    dict(slug="katuy-graph", label="(:Research {cold_start: true})", title="Katuy Graph", lock=True,
         body='Small shops have no sales history, so "bought together" finds nothing. This graph links products by shared '
              "supplies, substitutes and category, then proposes offers that respect margin, with a justification you can check.",
         tags=["Python", "Knowledge graph", "Agents"]),
    dict(slug="nl2sparql", label="(:Experiment)", title="NL2SPARQL",
         body="Agents that translate natural-language questions into SPARQL over knowledge graphs. Groundwork for the thesis.",
         tags=["SPARQL", "FastAPI", "LLM agents"]),
    dict(slug="testbed", label="(:Testbed {public: true})", title="microservices-demo-thesis",
         href=f"{RAW}/microservices-demo-thesis",
         body="Google's Online Boutique (11 gRPC services) instrumented with OpenTelemetry: the cluster the thesis agent diagnoses.",
         tags=["Go", "gRPC", "Istio", "OTel"]),
]

LAB_CARDS = [
    dict(slug="roboai", label="(:Experiment {public: true})", title="RoboAI_VO", href=f"{RAW}/RoboAI_VO",
         body="Differential-drive robot navigation, with config-driven training and evaluation.", tags=["Python", "PyTorch"]),
    dict(slug="cartpole", label="(:Experiment)", title="cartpole-dqn",
         body="Deep Q-learning from scratch, with a physics visualizer to see what the agent learned.", tags=["PyTorch", "Gymnasium"]),
    dict(slug="haskell", label="(:Experiment {public: true})", title="project_clasifier_haskell",
         href=f"{RAW}/project_clasifier_haskell",
         body="Spam and toxicity classifier for comments, written in a purely functional style.", tags=["Haskell"]),
    dict(slug="nanochat", label="(:Study)", title="nanochat study",
         body="A ChatGPT-style model end to end, from Karpathy's nanochat: tokenizer, pretraining, fine-tuning.", tags=["PyTorch", "uv"]),
]

PRODUCTS = [("Rivt", "Management SaaS for construction companies · co-founder"),
            ("Katuy", "Commerce platform for small businesses: web, API and mobile · co-founder"),
            ("Clinic system", "Patients, treatment plans and costing for a dental clinic"),
            ("Dipafex", "Product catalog for a ceramics manufacturer in Potosí"),
            ("Online store", "Mobile-first shop for a local food business, checkout over WhatsApp"),
            ("AI marketing agency", "Content pipelines orchestrated by AI agents")]


def products(t):
    cols, gap = 3, 12
    tw_ = (W - gap * (cols - 1)) / cols
    inner = tw_ - 64
    wrapped = [wrap(d, inner, 12.5) for _, d in PRODUCTS]
    th = 50 + max(len(w) for w in wrapped) * 18 + 10
    rows = (len(PRODUCTS) + cols - 1) // cols
    h = rows * th + (rows - 1) * gap + 40
    b = []
    for i, ((name, _), lines) in enumerate(zip(PRODUCTS, wrapped)):
        x = (i % cols) * (tw_ + gap)
        y = (i // cols) * (th + gap)
        b.append(f'<rect x="{x+0.5:.1f}" y="{y+0.5}" width="{tw_-1:.1f}" height="{th-1}" rx="10" fill="none" '
                 f'stroke="{t["product_border"]}" stroke-dasharray="5 4"/>')
        b.append(LOCK.format(x=f"{x+16:.1f}", y=y + 14, c=t["product"]))
        b.append(text(x + 48, y + 32, name, 14, t["product_text"], 700))
        for j, ln in enumerate(lines):
            b.append(text(x + 48, y + 54 + j * 18, ln, 12.5, t["soft"]))
    b.append(text(0, h - 10, "Private repositories. Happy to walk through any of them.", 12.5, t["muted"]))
    return svg(W, h, "".join(b), "Private products: " + "; ".join(f"{n}, {d}" for n, d in PRODUCTS))


LANGS = [("Python", "rrrrrrp", "research & agents · MAS-KG, Katuy Graph, search service, RoboAI, DQN, clinic API"),
         ("TypeScript", "pppppppp", "products · Rivt, Katuy, clinic, store, finance app, cacao traceability, portfolio"),
         ("Cypher · SPARQL", "rr", "querying graphs · MAS-KG, NL2SPARQL"),
         ("SQL", "ppppr", "Postgres and Supabase with row-level security; schema extraction for the KG"),
         ("JavaScript", "ww", "scraping robots at work (Puppeteer, Cheerio)"),
         ("Go", "r", "instrumenting the Online Boutique testbed"),
         ("Haskell", "r", "functional text classifier"),
         ("C · C++", "ww", "university systems coursework")]


def languages(t):
    pad, namew, dotw = 24, 150, 130
    descx = pad + namew + dotw
    rows, y = [], 20
    for name, dots, desc in LANGS:
        lines = wrap(desc, W - descx - pad, 12.5)
        rh = max(40, 22 + len(lines) * 18)
        rows.append((name, dots, lines, y, rh))
        y += rh
    h = y + 52
    b = [f'<rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="12" fill="{t["panel"]}" stroke="{t["border"]}"/>']
    col = {"r": t["research"], "p": t["product"], "w": t["blue"]}
    for i, (name, dots, lines, ry, rh) in enumerate(rows):
        base = ry + 25
        b.append(text(pad, base, name, 13.5, t["text"], 700))
        for k, d in enumerate(dots):
            b.append(f'<circle cx="{pad + namew + 6 + k * 15}" cy="{base - 4.5}" r="5" fill="{col[d]}"/>')
        for j, ln in enumerate(lines):
            b.append(text(descx, base + j * 18, ln, 12.5, t["muted"]))
        if i < len(rows) - 1:
            b.append(f'<line x1="{pad}" y1="{ry+rh:.1f}" x2="{W-pad}" y2="{ry+rh:.1f}" stroke="{t["border"]}" stroke-opacity="0.6"/>')
    ly = h - 22
    for k, (c, lab) in enumerate([("r", "research"), ("p", "product"), ("w", "work / coursework")]):
        x = pad + k * 140
        b.append(f'<circle cx="{x+5}" cy="{ly-4}" r="5" fill="{col[c]}"/>')
        b.append(text(x + 16, ly, lab, 11, t["muted"]))
    b.append(text(W - pad, ly, "one dot = one project", 11, t["muted"], anchor="end"))
    return svg(W, h, "".join(b), "Languages, by project: " + "; ".join(f"{n}: {d}" for n, _, d in LANGS))



def button(t, label, icon):
    w = int(tw(label, 13) + 64)
    icons = {
        "mail": '<rect x="0" y="2" width="18" height="14" rx="2"/><path d="M0 4l9 6 9-6"/>',
        "in": '<rect x="0" y="0" width="18" height="18" rx="3"/><path d="M5 8v6M5 4.5v.5M9 14V8m0 3a3 3 0 0 1 6 0v3"/>',
    }
    b = [f'<rect x="0.5" y="0.5" width="{w-1}" height="43" rx="22" fill="{t["card"]}" stroke="{t["border"]}"/>',
         f'<g transform="translate(20,13)" fill="none" stroke="{t["research"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{icons[icon]}</g>',
         text(50, 27, label, 13, t["text"], 700)]
    return svg(w, 44, "".join(b), label)




# ---------- build ----------

HEADERS = {
    "about": ([("(:", "muted"), ("About", "concept"), (")", "muted")], ""),
    "graph": ([("(me)-[", "text"), (":WORKED_ON", "research"), ("]->(*)", "text")], "my work, as a graph"),
    "research": ([("(:", "muted"), ("Research", "research"), (")", "muted")], "the problems I'm studying"),
    "lab": ([("(:", "muted"), ("Lab", "research"), (")", "muted")], "built to understand something properly"),
    "product": ([("(:", "muted"), ("Product", "product"), (")", "muted")], "built to solve real problems"),
    "languages": ([("(:", "muted"), ("Language", "concept"), (")-[:USED_IN]->(:", "text"), ("Project", "research"), (")", "muted")], ""),
    "contact": ([("CREATE", "concept"), (" (you)-[", "text"), (":TALKS_TO", "research"), ("]->(me)", "text")], ""),
}


def build_assets():
    ASSETS.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        files = {"hero": hero(t), "about": about(t), "graph": graph(t), "thesis": thesis(t),
                 "products": products(t), "languages": languages(t),
                 "btn-email": button(t, "odaliz.rojas.roldan4417@gmail.com", "mail"),
                 "btn-linkedin": button(t, "LinkedIn", "in")}
        for key, (parts, sub) in HEADERS.items():
            files[f"h-{key}"] = header(t, parts, sub)
        for c, s in zip(RESEARCH_CARDS, small_cards(t, RESEARCH_CARDS, 272)):
            files[f"card-{c['slug']}"] = s
        for c, s in zip(LAB_CARDS, small_cards(t, LAB_CARDS, 414)):
            files[f"lab-{c['slug']}"] = s
        for stem, content in files.items():
            (ASSETS / f"{stem}-{name}.svg").write_text(content, encoding="utf-8")


def pic(stem, alt, width="100%", href=None):
    tag = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/{stem}-dark.svg">'
           f'<img src="./assets/{stem}-light.svg" alt="{escape(alt, {chr(34): "&quot;"})}" width="{width}"></picture>')
    return f'<a href="{href}">{tag}</a>' if href else tag


def build_readme():
    P = []
    P.append(pic("hero", "Odaliz Rojas Roldán. I ground LLM agents in knowledge graphs, so they stop inventing what isn't there."))
    P.append(pic("h-about", "(:About)"))
    P.append(pic("about", "Knowledge graphs × LLM agents × distributed systems. AI Engineer at ICI-UPB; thesis on multi-agent root-cause analysis "
                          "with topological memory (in development); I lead the AWS User Group AI Bolivia; I ship software for real businesses."))
    P.append(pic("h-graph", "(me)-[:WORKED_ON]->(*) — my work, as a graph"))
    P.append(pic("graph", "Knowledge graph of my work: concepts in the middle, research projects and private products around them."))
    P.append(pic("h-research", "(:Research) — the problems I'm studying"))
    P.append(pic("thesis", "Thesis, in development: MAS-KG, root-cause analysis with topological memory over a typed knowledge graph in Memgraph."))
    P.append("\n".join(pic(f"card-{c['slug']}", f"{c['title']}: {c['body']}", "32.4%", c.get("href")) for c in RESEARCH_CARDS))
    P.append(pic("h-lab", "(:Lab) — built to understand something properly"))
    P.append("\n".join(pic(f"lab-{c['slug']}", f"{c['title']}: {c['body']}", "49.2%", c.get("href")) for c in LAB_CARDS))
    P.append(pic("h-product", "(:Product) — built to solve real problems"))
    P.append(pic("products", "Private products: " + "; ".join(n for n, _ in PRODUCTS)))
    P.append(pic("h-languages", "(:Language)-[:USED_IN]->(:Project)"))
    P.append(pic("languages", "Languages: Python, TypeScript, Cypher and SPARQL, SQL, JavaScript, Go, Haskell, C and C++."))
    P.append(pic("h-contact", "CREATE (you)-[:TALKS_TO]->(me)"))
    P.append("\n".join([pic("btn-email", "Email: odaliz.rojas.roldan4417@gmail.com", None, "mailto:odaliz.rojas.roldan4417@gmail.com"),
                        pic("btn-linkedin", "LinkedIn", None, "https://www.linkedin.com/in/odaliz-rojas/")]))
    body = "\n\n".join(f'<p>\n{p}\n</p>' for p in P)
    body = body.replace(' width="None"', "")
    (ROOT / "README.md").write_text(f"<!-- Generated by scripts/build.py. Edit the script, not this file. -->\n\n{body}\n", encoding="utf-8")


if __name__ == "__main__":
    build_assets()
    build_readme()
    print("ok:", len(list(ASSETS.glob("*.svg"))), "svgs")

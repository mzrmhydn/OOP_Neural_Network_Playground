"""Generate UML class diagram SVG for OOP Neural Network Playground."""

# ─── palette ─────────────────────────────────────────────────────────────────

IF_FILL    = "#EBF2FA"; IF_STROKE    = "#2E79B5"   # interface
AB_FILL    = "#F5F5F5"; AB_STROKE    = "#555555"   # abstract
CO_FILL    = "#FFFFFF"; CO_STROKE    = "#333333"   # concrete
EX_FILL    = "#EEEEEE"; EX_STROKE    = "#999999"   # external (JDK)
ARROW      = "#555555"
SEC_BG     = "#F8F9FD"; SEC_STROKE   = "#CCCCDD"
T_PRI      = "#1A1A2E"; T_SEC        = "#5A5A7A"   # text colours
FONT       = "Arial, Helvetica, sans-serif"

NW, NH, NH2 = 188, 52, 40   # node sizes  (with-stereotype, without)
AS, AH      = 8, 14         # arrowhead half-width / height

# ─── SVG primitives ──────────────────────────────────────────────────────────

def esc(s):
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def node(x, y, label, kind, w=NW):
    """Return (background_elems, foreground_elems, height) for a class box."""
    if   kind == 'interface': fill, stroke, dash = IF_FILL, IF_STROKE, "5,3"
    elif kind == 'abstract':  fill, stroke, dash = AB_FILL, AB_STROKE, None
    elif kind == 'external':  fill, stroke, dash = EX_FILL, EX_STROKE, "4,4"
    else:                     fill, stroke, dash = CO_FILL, CO_STROKE, None

    italic   = kind in ('abstract',)
    stereo   = {"interface":"«interface»","abstract":"«abstract»"}.get(kind)
    h        = NH if stereo else NH2
    cx       = x + w // 2
    da       = f' stroke-dasharray="{dash}"' if dash else ''
    fg       = []

    bg = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3"'
          f' fill="{fill}" stroke="{stroke}" stroke-width="1.5"{da}/>']

    if stereo:
        ty    = "italic" if italic else "normal"
        sc    = IF_STROKE if kind == 'interface' else T_SEC
        bg.append(f'<line x1="{x}" y1="{y+22}" x2="{x+w}" y2="{y+22}"'
                  f' stroke="{stroke}" stroke-width="1" opacity="0.4"/>')
        fg.append(f'<text x="{cx}" y="{y+14}" text-anchor="middle"'
                  f' font-size="9" font-style="italic" fill="{sc}"'
                  f' font-family="{FONT}">{stereo}</text>')
        fg.append(f'<text x="{cx}" y="{y+37}" text-anchor="middle"'
                  f' font-size="11" font-weight="600" font-style="{ty}"'
                  f' fill="{T_PRI}" font-family="{FONT}">{esc(label)}</text>')
    else:
        fg.append(f'<text x="{cx}" y="{y+h//2+4}" text-anchor="middle"'
                  f' font-size="11" font-weight="600" fill="{T_PRI}"'
                  f' font-family="{FONT}">{esc(label)}</text>')

    return bg, fg, h

def arrow_tip(px, py, direction):
    """Hollow triangle arrowhead pointing in direction (down|right)."""
    if direction == 'down':
        pts = f"{px},{py} {px-AS},{py+AH} {px+AS},{py+AH}"
    else:  # right
        pts = f"{px},{py} {px+AH},{py-AS} {px+AH},{py+AS}"
    return (f'<polygon points="{pts}" fill="white"'
            f' stroke="{ARROW}" stroke-width="1.5"/>')

def line(x1, y1, x2, y2, dashed=False):
    da = ' stroke-dasharray="5,3"' if dashed else ''
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"'
            f' stroke="{ARROW}" stroke-width="1.5"{da}/>')

def section_box(x, y, w, h, title):
    return [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6"'
        f' fill="{SEC_BG}" stroke="{SEC_STROKE}" stroke-width="1"/>',
        f'<text x="{x+w//2}" y="{y+18}" text-anchor="middle"'
        f' font-size="12" font-weight="700" fill="{T_SEC}"'
        f' font-family="{FONT}">{esc(title)}</text>',
    ]

# ─── Collector ───────────────────────────────────────────────────────────────

bg_els, ln_els, fg_els = [], [], []   # bg=section boxes, ln=arrows, fg=node boxes

def b(*e):
    for x in e: (bg_els.extend(x) if isinstance(x, list) else bg_els.append(x))
def l(*e):
    for x in e: (ln_els.extend(x) if isinstance(x, list) else ln_els.append(x))
def f(*e):
    for x in e: (fg_els.extend(x) if isinstance(x, list) else fg_els.append(x))

def N(x, y, label, kind, w=NW):
    """Register a node and return (cx, cy_top, cy_bot)."""
    bg_e, fg_e, h = node(x, y, label, kind, w)
    f(bg_e, fg_e)
    return x + w//2, y, y + h

def V_arrow(px, py_bot, cx, cy_top, dashed=False):
    """Vertical (or angled) arrow from parent-bottom to child-top."""
    l(arrow_tip(px, py_bot, 'down'),
      line(px, py_bot + AH, cx, cy_top, dashed))

def H_arrow(px_right, py, cx_left, cy, dashed=False):
    """Horizontal arrow from parent-right to child-left."""
    l(arrow_tip(px_right, py, 'right'),
      line(px_right + AH, py, cx_left, cy, dashed))

def V_bus(px, py_bot, children, bus_y, dashed=False):
    """Bus connector: parent → horizontal bus → multiple children."""
    l(arrow_tip(px, py_bot, 'down'),
      line(px, py_bot + AH, px, bus_y, dashed))
    cxs = [cx for cx, ct in children]
    l(line(min(cxs), bus_y, max(cxs), bus_y))
    for cx, child_top in children:
        l(line(cx, bus_y, cx, child_top))

# ─── Layout constants ─────────────────────────────────────────────────────────

ROW1_Y  = 95      # top of first row of sections
ROW2_Y  = 545     # top of second row
S_PAD   = 24      # section inner padding (top and sides)

# ─── SECTION 1 · Activation Functions  (x=20, y=95, w=340, h=435) ───────────

S1X, S1Y, S1W, S1H = 20, ROW1_Y, 340, 440
b(section_box(S1X, S1Y, S1W, S1H, "Activation Functions"))

# DifferentiableFunction  (centered inside section)
df1_w = 210
df1_x = S1X + (S1W - df1_w) // 2
df1_cx, df1_top, df1_bot = N(df1_x, S1Y + S_PAD + 8, "DifferentiableFunction", 'interface', df1_w)

# ActivationFunction
af_w = 210
af_x = S1X + (S1W - af_w) // 2
af_cx, af_top, af_bot = N(af_x, df1_bot + 50, "ActivationFunction", 'abstract', af_w)

V_arrow(df1_cx, df1_bot, af_cx, af_top, dashed=True)  # implements (dashed)

# 4 concrete children in 2×2
ch_y1 = af_bot + 56   # row 1 y
ch_y2 = ch_y1 + NH2 + 10  # row 2 y
cw    = 148

tanh_cx, _, _  = N(S1X + 10,       ch_y1, "TanhActivation",    'concrete', cw)
relu_cx, _, _  = N(S1X + 10+cw+12, ch_y1, "ReluActivation",    'concrete', cw)
sig_cx,  _, _  = N(S1X + 10,       ch_y2, "SigmoidActivation",  'concrete', cw+4)
lin_cx,  _, _  = N(S1X + 10+cw+12, ch_y2, "LinearActivation",   'concrete', cw+4)

bus1_y = af_bot + 28
V_bus(af_cx, af_bot,
      [(tanh_cx, ch_y1), (relu_cx, ch_y1),
       (sig_cx,  ch_y2), (lin_cx,  ch_y2)],
      bus1_y)

# ─── SECTION 2 · Regularization & Error  (x=375, y=95, w=360, h=435) ────────

S2X, S2Y, S2W, S2H = 375, ROW1_Y, 370, 440
b(section_box(S2X, S2Y, S2W, S2H, "Regularization & Error Functions"))

# Left sub-tree: DiffFn → RegFn → {No, L1, L2}
df2_w = 210
df2_x = S2X + 10
df2_cx, df2_top, df2_bot = N(df2_x, S2Y + S_PAD + 8, "DifferentiableFunction", 'interface', df2_w)

rf_w  = 210
rf_x  = S2X + 10
rf_cx, rf_top, rf_bot = N(rf_x, df2_bot + 50, "RegularizationFunction", 'abstract', rf_w)

V_arrow(df2_cx, df2_bot, rf_cx, rf_top, dashed=True)

rch_y = rf_bot + 50
rcw   = 112
no_cx,  _, _ = N(S2X + 8,          rch_y, "NoRegularization", 'concrete', rcw)
l1_cx,  _, _ = N(S2X + 8+rcw+8,    rch_y, "L1Regularization", 'concrete', rcw)
l2_cx,  _, _ = N(S2X + 8+2*(rcw+8),rch_y, "L2Regularization", 'concrete', rcw)

rbus_y = rf_bot + 26
V_bus(rf_cx, rf_bot, [(no_cx, rch_y), (l1_cx, rch_y), (l2_cx, rch_y)], rbus_y)

# Right sub-tree: ErrorFunction → SquaredError  (right side of section)
ef_w = 152
ef_x = S2X + S2W - ef_w - 12
ef_cx, ef_top, ef_bot = N(ef_x, S2Y + S_PAD + 8, "ErrorFunction", 'interface', ef_w)

sq_w = 152
sq_x = S2X + S2W - sq_w - 12
sq_cx, sq_top, sq_bot = N(sq_x, ef_bot + 50, "SquaredError", 'concrete', sq_w)

V_arrow(ef_cx, ef_bot, sq_cx, sq_top, dashed=True)

# Vertical divider between the two sub-trees
div_x = S2X + df2_w + 20
l(f'<line x1="{div_x}" y1="{S2Y+10}" x2="{div_x}" y2="{S2Y+S2H-10}"'
  f' stroke="{SEC_STROKE}" stroke-width="1" stroke-dasharray="4,4"/>')

# ─── SECTION 3 · Exception Hierarchy  (x=760, y=95, w=340, h=435) ────────────

S3X, S3Y, S3W, S3H = 760, ROW1_Y, 370, 440
b(section_box(S3X, S3Y, S3W, S3H, "Exception Hierarchy"))

rte_w = 210
rte_x = S3X + (S3W - rte_w) // 2
rte_cx, rte_top, rte_bot = N(rte_x, S3Y + S_PAD + 8, "RuntimeException", 'external', rte_w)

pg_w  = 210
pg_x  = S3X + (S3W - pg_w) // 2
pg_cx, pg_top, pg_bot = N(pg_x, rte_bot + 50, "PlaygroundException", 'abstract', pg_w)

V_arrow(rte_cx, rte_bot, pg_cx, pg_top)

# Three direct children of PlaygroundException
exch_y = pg_bot + 54
excw   = 108
cfg_cx, _, _  = N(S3X + 8,            exch_y, "ConfigurationException", 'concrete', excw)
trn_cx, _, _  = N(S3X + 8+excw+8,     exch_y, "TrainingException",      'concrete', excw)
nf_cx,  _, nf_bot = N(S3X + 8+2*(excw+8), exch_y, "NotFoundException",   'concrete', excw)

exbus_y = pg_bot + 28
V_bus(pg_cx, pg_bot,
      [(cfg_cx, exch_y), (trn_cx, exch_y), (nf_cx, exch_y)],
      exbus_y)

# Grandchild: SessionNotFoundException extends NotFoundException
snf_y = exch_y + NH2 + 38
snf_cx, snf_top, _ = N(nf_cx - excw//2, snf_y, "SessionNotFoundException", 'concrete', excw+18)
V_arrow(nf_cx, exch_y + NH2, snf_cx, snf_top)

# ─── SECTION 4 · Dataset Generators  (x=1145, y=95, w=400, h=435) ───────────
#   Horizontal layout: DataGenerator on left, 6 datasets on right

S4X, S4Y, S4W, S4H = 1145, ROW1_Y, 400, 440
b(section_box(S4X, S4Y, S4W, S4H, "Dataset Generators"))

dg_w  = 172
dg_x  = S4X + 14
dg_cx, _, dg_bot = N(dg_x, S4Y + S4H//2 - NH//2, "DataGenerator", 'abstract', dg_w)

dg_right = dg_x + dg_w   # right edge of DataGenerator box
dg_mid_y = S4Y + S4H//2  # vertical center of DataGenerator

# 6 children: 2 columns × 3 rows on the right side of section
ds_w   = 158
ds_col = S4X + dg_w + 50    # left edge of children
ds_gap = 12                  # vertical gap between children

ds_names = [
    "CircleDataset", "XorDataset",
    "GaussianDataset", "SpiralDataset",
    "PlaneRegressionDataset", "GaussianRegressionDataset",
]

row_heights = []
# 6 datasets in single column (stacked)
total_h = 6 * NH2 + 5 * ds_gap
ds_start_y = S4Y + (S4H - total_h) // 2

ds_cxs_tops = []
for i, name in enumerate(ds_names):
    dy = ds_start_y + i * (NH2 + ds_gap)
    ds_cx, _, _ = N(ds_col, dy, name, 'concrete', ds_w)
    ds_cxs_tops.append((ds_cx, dy))

# Horizontal bus from DataGenerator's right to children left edges
ds_left = ds_col
children_mids = [top + NH2 // 2 for (_, top) in ds_cxs_tops]

# Single H-line fan: draw one arrow tip on DataGenerator right, then a vertical
# trunk, then horizontal arms to each child
parent_right = dg_x + dg_w
parent_mid   = dg_mid_y

# Draw arrowhead at DataGenerator's right side
l(arrow_tip(parent_right, parent_mid, 'right'))
# Vertical trunk at x=trunk_x
trunk_x = parent_right + 26
l(line(parent_right + AH, parent_mid, trunk_x, parent_mid))
l(line(trunk_x, children_mids[0], trunk_x, children_mids[-1]))
for (ds_cx, ds_top) in ds_cxs_tops:
    child_mid = ds_top + NH2 // 2
    l(line(trunk_x, child_mid, ds_col, child_mid))

# ─── SECTION 5 · API Layer  (x=20, y=545, w=500, h=360) ─────────────────────

S5X, S5Y, S5W, S5H = 20, ROW2_Y, 500, 350
b(section_box(S5X, S5Y, S5W, S5H, "API Layer"))

# Trainable interface
tr_w  = 168
tr_x  = S5X + 30
tr_cx, _, tr_bot = N(tr_x, S5Y + S_PAD + 8, "Trainable", 'interface', tr_w)

# Session (implements Trainable)
ss_w  = 168
ss_x  = S5X + 30
ss_cx, ss_top, ss_bot = N(ss_x, tr_bot + 55, "Session", 'concrete', ss_w)
V_arrow(tr_cx, tr_bot, ss_cx, ss_top, dashed=True)

# SessionManager
sm_w  = 168
sm_x  = S5X + 30
sm_cx, sm_top, sm_bot = N(sm_x, ss_bot + 30, "SessionManager", 'concrete', sm_w)

# Dependency line: SessionManager uses Session
l(line(sm_cx, sm_top, ss_cx, ss_bot))
l(f'<polygon points="{sm_cx},{sm_top} {sm_cx-6},{sm_top-10} {sm_cx+6},{sm_top-10}"'
  f' fill="{ARROW}" stroke="{ARROW}" stroke-width="1"/>')

# ApiServer + RequestHandlers on the right
api_w = 165
api_x = S5X + S5W - api_w - 20
api_cx, api_top, api_bot = N(api_x, S5Y + S_PAD + 8, "ApiServer", 'concrete', api_w)

rh_w = 175
rh_x = S5X + S5W - rh_w - 15
rh_cx, rh_top, rh_bot = N(rh_x, api_bot + 40, "RequestHandlers", 'concrete', rh_w)

l(line(api_cx, api_bot, rh_cx, rh_top))
l(f'<polygon points="{api_cx},{api_bot} {api_cx-6},{api_bot+10} {api_cx+6},{api_bot+10}"'
  f' fill="{ARROW}" stroke="{ARROW}" stroke-width="1"/>')

# Composition notes (small text alongside Session box)
note_y = ss_top + 4
for i, txt in enumerate([
    "has-a DataGenerator",
    "has-a ActivationFunction",
    "has-a RegularizationFunction",
    "has-a List<List<Node>>",
]):
    tx = ss_x + ss_w + 12
    ty = note_y + i * 16
    f(f'<text x="{tx}" y="{ty+11}" font-size="9" fill="{T_SEC}"'
      f' font-family="{FONT}">{esc(txt)}</text>')

# ─── SECTION 6 · NN Core  (x=535, y=545, w=380, h=360) ──────────────────────

S6X, S6Y, S6W, S6H = 535, ROW2_Y, 370, 350
b(section_box(S6X, S6Y, S6W, S6H, "Neural Network Core"))

node_cx, _, node_bot = N(S6X + 20, S6Y + S_PAD + 8, "Node", 'concrete', 145)
link_cx, link_top, link_bot = N(S6X + 195, S6Y + S_PAD + 8, "Link", 'concrete', 140)
nn_cx,   nn_top,   nn_bot   = N(S6X + (S6W-165)//2, S6Y + S_PAD + NH2 + 60, "NeuralNetwork", 'concrete', 165)

# Node ←→ Link (association)
l(line(S6X + 20 + 145, S6Y + S_PAD + 8 + NH2//2,
       S6X + 195,       S6Y + S_PAD + 8 + NH2//2))

# NeuralNetwork uses Node and Link
l(line(nn_cx - 30, nn_top, node_cx, S6Y + S_PAD + 8 + NH2))
l(line(nn_cx + 30, nn_top, link_cx, S6Y + S_PAD + 8 + NH2))

ef2_w = 145
ef2_cx, ef2_top, ef2_bot = N(S6X + 20, nn_bot + 38, "ErrorFunction", 'interface', ef2_w)
sq2_cx, sq2_top, _       = N(S6X + 195, nn_bot + 38, "SquaredError",  'concrete',  145)
V_arrow(ef2_cx, ef2_bot, sq2_cx, sq2_top, dashed=True)

# Dependency: NeuralNetwork uses ErrorFunction (simple dashed line)
l(line(nn_cx, nn_bot, ef2_cx, ef2_top, dashed=True))

# ─── SECTION 7 · Composition Table  (x=920, y=545, w=625, h=360) ─────────────

S7X, S7Y, S7W, S7H = 920, ROW2_Y, 625, 350
b(section_box(S7X, S7Y, S7W, S7H, "Composition & Key OOP Concepts"))

rows = [
    ("Encapsulation",   "Node, Link, Session, Example2D — all fields private"),
    ("Inheritance",     "ActivationFunction(4) · RegularizationFunction(3) · DataGenerator(6) · PlaygroundException(4)"),
    ("Polymorphism",    "activation.output(x) → Tanh/ReLU/Sigmoid/Linear at runtime"),
    ("Abstraction",     "DifferentiableFunction · ErrorFunction · Trainable (interfaces)"),
    ("Composition",     "Session has-a {DataGenerator, ActivationFunction, RegFn, List<List<Node>>}"),
    ("Overloading",     "Session.trainOneEpoch(lr,rr,batch)  and  Session.trainOneEpoch()"),
    ("final",           "Example2D (immutable) · TanhActivation (leaf) · getHttpStatus() (final method)"),
    ("Static Factory",  "Activations.byKey()  · Regularizations.byKey()  · DatasetRegistry.byKey()"),
    ("Exc. Hierarchy",  "PlaygroundException → {ConfigurationEx(400) · TrainingEx(500) · NotFoundException(404)}"),
]

rx, ry = S7X + 16, S7Y + S_PAD + 10
col2_x = rx + 175

for i, (concept, detail) in enumerate(rows):
    cy = ry + i * 32
    if i % 2 == 1:
        f(f'<rect x="{S7X+8}" y="{cy-4}" width="{S7W-16}" height="26"'
          f' rx="2" fill="#F0F1F8" stroke="none"/>')
    f(f'<text x="{rx}" y="{cy+13}" font-size="11" font-weight="700"'
      f' fill="{T_PRI}" font-family="{FONT}">{esc(concept)}</text>')
    f(f'<text x="{col2_x}" y="{cy+13}" font-size="9.5"'
      f' fill="{T_SEC}" font-family="{FONT}">{esc(detail)}</text>')

# ─── Title, Legend ───────────────────────────────────────────────────────────

SVG_W, SVG_H = 1560, 920

title_els = [
    f'<text x="{SVG_W//2}" y="38" text-anchor="middle" font-size="20"'
    f' font-weight="700" fill="{T_PRI}" font-family="{FONT}">'
    f'OOP Neural Network Playground — UML Class Diagram</text>',
    f'<text x="{SVG_W//2}" y="60" text-anchor="middle" font-size="11"'
    f' fill="{T_SEC}" font-family="{FONT}">'
    f'Java Backend · 39 source files · 3 interfaces · 5 abstract classes · 5 exception types</text>',
]

leg_items = [
    (IF_FILL, IF_STROKE, "5,3",  "Interface"),
    (AB_FILL, AB_STROKE, None,   "Abstract class"),
    (CO_FILL, CO_STROKE, None,   "Concrete class"),
    (EX_FILL, EX_STROKE, "4,4",  "External (JDK)"),
]
legend_els = []
lx = SVG_W // 2 - 350
ly = 70
for fill, stroke, dash, label in leg_items:
    da = f' stroke-dasharray="{dash}"' if dash else ''
    legend_els.append(f'<rect x="{lx}" y="{ly}" width="26" height="16" rx="2"'
                      f' fill="{fill}" stroke="{stroke}" stroke-width="1.5"{da}/>')
    legend_els.append(f'<text x="{lx+32}" y="{ly+12}" font-size="10"'
                      f' fill="{T_SEC}" font-family="{FONT}">{label}</text>')
    lx += 115

# extends arrow legend
legend_els.append(f'<line x1="{lx}" y1="{ly+8}" x2="{lx+26}" y2="{ly+8}"'
                  f' stroke="{ARROW}" stroke-width="1.5"/>')
legend_els.append(f'<polygon points="{lx+26},{ly+8} {lx+20},{ly+4} {lx+20},{ly+12}"'
                  f' fill="white" stroke="{ARROW}" stroke-width="1.5"/>')
legend_els.append(f'<text x="{lx+32}" y="{ly+12}" font-size="10"'
                  f' fill="{T_SEC}" font-family="{FONT}">extends</text>')
lx += 100

# implements arrow legend
legend_els.append(f'<line x1="{lx}" y1="{ly+8}" x2="{lx+26}" y2="{ly+8}"'
                  f' stroke="{ARROW}" stroke-width="1.5" stroke-dasharray="5,3"/>')
legend_els.append(f'<polygon points="{lx+26},{ly+8} {lx+20},{ly+4} {lx+20},{ly+12}"'
                  f' fill="white" stroke="{ARROW}" stroke-width="1.5"/>')
legend_els.append(f'<text x="{lx+32}" y="{ly+12}" font-size="10"'
                  f' fill="{T_SEC}" font-family="{FONT}">implements</text>')

# ─── Assemble ────────────────────────────────────────────────────────────────

all_parts = (
    [f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}"'
     f' viewBox="0 0 {SVG_W} {SVG_H}">',
     f'<rect width="{SVG_W}" height="{SVG_H}" fill="#FAFAFA"/>']
    + title_els
    + legend_els
    + bg_els   # section backgrounds
    + ln_els   # arrows (under nodes)
    + fg_els   # node boxes + text (on top)
    + ['</svg>']
)

svg_content = "\n".join(all_parts)

with open("uml_diagram.svg", "w", encoding="utf-8") as fh:
    fh.write(svg_content)

print("uml_diagram.svg written.")

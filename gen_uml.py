#!/usr/bin/env python3
"""
UML Class Diagram — OOP Neural Network Playground
Arrows follow the course document notation:
  Inheritance   ——▷   solid line, hollow triangle at superclass
  Realization   --▷   dashed line, hollow triangle at interface
  Composition   ◆——>  filled diamond at owner, open arrow at part
  Aggregation   ◇——>  hollow diamond at whole, open arrow at part
  Association   ——>   solid line, open arrowhead
  Dependency    -->   dashed line, open arrowhead
Class boxes have three compartments: Name | Attributes | Methods
Visibility: + public  - private  # protected
"""

# ─── palette ─────────────────────────────────────────────────────────────────
IF_F,IF_S  = "#EBF2FA","#2E79B5"   # interface
AB_F,AB_S  = "#F4F4F4","#444444"   # abstract
CO_F,CO_S  = "#FFFFFF","#333333"   # concrete
EX_F,EX_S  = "#EBEBEB","#999999"   # external (JDK)
ARR        = "#333333"
SBG,SST    = "#F7F8FD","#C5C8DF"
TPR,TSC    = "#111111","#556"
TIF        = "#2E79B5"
FONT       = "Arial, Helvetica, sans-serif"
MONO       = "Courier New, Courier, monospace"

# arrow / compartment geometry
TH, TS  = 14, 8    # hollow-triangle height / half-base
AH, AS  = 10, 6    # open-arrowhead depth / half-base
DH, DW  = 14, 8    # diamond half-height / half-width
LINE_H  = 15       # px per text line inside a compartment
PAD     = 8        # top-padding inside a compartment

SVG_W, SVG_H = 2200, 1640

# z-order buckets: bg=section rects, ln=arrows, fg=class boxes+text
BG, LN, FG = [], [], []
BOXES = {}   # name -> (x, y, w, h)

def q(s): return (s.replace("&","&amp;").replace("<","&lt;")
                   .replace(">","&gt;").replace('"',"&quot;"))

# ─── compartment height ───────────────────────────────────────────────────────

def nh(kind):      return 42 if kind in ('interface','abstract') else 28
def ch(n):         return max(18, n*LINE_H + PAD)
def box_h(k,a,m):  return nh(k)+ch(len(a))+ch(len(m))

# ─── draw a class box ─────────────────────────────────────────────────────────

def N(name, x, y, w, kind, attrs, methods):
    h = box_h(kind, attrs, methods)
    BOXES[name] = (x, y, w, h)

    if   kind=='interface': fill,st,da = IF_F,IF_S,"5,3"
    elif kind=='abstract':  fill,st,da = AB_F,AB_S,None
    elif kind=='external':  fill,st,da = EX_F,EX_S,"4,4"
    else:                   fill,st,da = CO_F,CO_S,None

    da_s  = f' stroke-dasharray="{da}"' if da else ''
    nh_   = nh(kind)
    ah_   = ch(len(attrs))
    cx    = x + w//2

    BG.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2"'
              f' fill="{fill}" stroke="{st}" stroke-width="1.5"{da_s}/>')
    BG.append(f'<line x1="{x}" y1="{y+nh_}" x2="{x+w}" y2="{y+nh_}"'
              f' stroke="{st}" stroke-width="1"/>')
    BG.append(f'<line x1="{x}" y1="{y+nh_+ah_}" x2="{x+w}" y2="{y+nh_+ah_}"'
              f' stroke="{st}" stroke-width="1"/>')

    stereo = {'interface':'«interface»','abstract':'«abstract»'}.get(kind)
    fg = []
    if stereo:
        sc = TIF if kind=='interface' else TSC
        fg.append(f'<text x="{cx}" y="{y+14}" text-anchor="middle" font-size="9"'
                  f' font-style="italic" fill="{sc}" font-family="{FONT}">{stereo}</text>')
        istyle = 'italic' if kind=='abstract' else 'normal'
        fg.append(f'<text x="{cx}" y="{y+30}" text-anchor="middle" font-size="11"'
                  f' font-weight="700" font-style="{istyle}" fill="{TPR}"'
                  f' font-family="{FONT}">{q(name)}</text>')
    else:
        fg.append(f'<text x="{cx}" y="{y+nh_//2+4}" text-anchor="middle" font-size="11"'
                  f' font-weight="700" fill="{TPR}" font-family="{FONT}">{q(name)}</text>')

    ty = y + nh_ + PAD + 7
    for a in attrs:
        fg.append(f'<text x="{x+6}" y="{ty}" font-size="9.5" fill="{TPR}"'
                  f' font-family="{MONO}">{q(a)}</text>')
        ty += LINE_H

    ty = y + nh_ + ah_ + PAD + 7
    for m in methods:
        fg.append(f'<text x="{x+6}" y="{ty}" font-size="9.5" fill="{TPR}"'
                  f' font-family="{MONO}">{q(m)}</text>')
        ty += LINE_H

    FG.extend(fg)

# ─── box accessors ────────────────────────────────────────────────────────────

def cx_(n):  b=BOXES[n]; return b[0]+b[2]//2
def top_(n): return BOXES[n][1]
def bot_(n): b=BOXES[n]; return b[1]+b[3]
def lft_(n): return BOXES[n][0]
def rgt_(n): b=BOXES[n]; return b[0]+b[2]
def midy(n): b=BOXES[n]; return b[1]+b[3]//2

# ─── SVG line/polygon helpers ─────────────────────────────────────────────────

def L(x1,y1,x2,y2,dash=False):
    da = ' stroke-dasharray="5,3"' if dash else ''
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"'
            f' stroke="{ARR}" stroke-width="1.5"{da}/>')

def ML(pts, dash=False):
    da = ' stroke-dasharray="5,3"' if dash else ''
    ps = " ".join(f"{p[0]},{p[1]}" for p in pts)
    return (f'<polyline points="{ps}" fill="none" stroke="{ARR}"'
            f' stroke-width="1.5"{da}/>')

def poly(pts, fill, sw=1.5):
    ps = " ".join(f"{p[0]},{p[1]}" for p in pts)
    return f'<polygon points="{ps}" fill="{fill}" stroke="{ARR}" stroke-width="{sw}"/>'

def mlabel(x,y,t,anch="middle"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anch}" font-size="10"'
            f' fill="{TSC}" font-family="{FONT}">{q(t)}</text>')

# ─── arrowhead primitives ─────────────────────────────────────────────────────

def hollow_tri_v(px, py):
    """Hollow triangle: tip at (px,py), base BELOW — used at parent's bottom
    for vertical (top=parent, bottom=child) inheritance/realization."""
    pts = [(px,py),(px-TS,py+TH),(px+TS,py+TH)]
    return poly(pts,'white')

def hollow_tri_h(px, py):
    """Hollow triangle: tip at (px,py), base to RIGHT — used at parent's right
    for horizontal (left=parent) inheritance."""
    pts = [(px,py),(px+TH,py-TS),(px+TH,py+TS)]
    return poly(pts,'white')

def open_arr_up(px, py):
    return (f'<polyline points="{px-AS},{py+AH} {px},{py} {px+AS},{py+AH}"'
            f' fill="none" stroke="{ARR}" stroke-width="1.5"/>')

def open_arr_left(px, py):
    return (f'<polyline points="{px+AH},{py-AS} {px},{py} {px+AH},{py+AS}"'
            f' fill="none" stroke="{ARR}" stroke-width="1.5"/>')

def open_arr_down(px, py):
    return (f'<polyline points="{px-AS},{py-AH} {px},{py} {px+AS},{py-AH}"'
            f' fill="none" stroke="{ARR}" stroke-width="1.5"/>')

def open_arr_right(px, py):
    return (f'<polyline points="{px-AH},{py-AS} {px},{py} {px-AH},{py+AS}"'
            f' fill="none" stroke="{ARR}" stroke-width="1.5"/>')

def filled_dia_down(px, py):
    """Filled diamond: outermost point at bottom (px,py), extends upward."""
    pts = [(px,py),(px-DW,py-DH),(px,py-2*DH),(px+DW,py-DH)]
    return poly(pts, ARR, sw=1)

def filled_dia_right(px, py):
    """Filled diamond: outermost tip at right (px,py), extends leftward."""
    pts = [(px,py),(px-DH,py-DW),(px-2*DH,py),(px-DH,py+DW)]
    return poly(pts, ARR, sw=1)

def hollow_dia_down(px, py):
    pts = [(px,py),(px-DW,py-DH),(px,py-2*DH),(px+DW,py-DH)]
    return poly(pts,'white')

def hollow_dia_right(px, py):
    pts = [(px,py),(px-DH,py-DW),(px-2*DH,py),(px-DH,py+DW)]
    return poly(pts,'white')

# ─── high-level relationship builders ────────────────────────────────────────

def _vpath(x1,y1,x2,y2,dash=False):
    """Right-angle routing: vertical then horizontal."""
    if abs(x1-x2)<2:
        return L(x1,y1,x2,y2,dash)
    my = (y1+y2)//2
    return ML([(x1,y1),(x1,my),(x2,my),(x2,y2)],dash)

def _hpath(x1,y1,x2,y2,dash=False):
    if abs(y1-y2)<2:
        return L(x1,y1,x2,y2,dash)
    mx = (x1+x2)//2
    return ML([(x1,y1),(mx,y1),(mx,y2),(x2,y2)],dash)

def inherit_v(child, parent):
    """——▷  solid line, hollow triangle at parent bottom."""
    px,py = cx_(parent),bot_(parent)
    cx,cy = cx_(child),top_(child)
    LN.append(hollow_tri_v(px,py))
    LN.append(_vpath(px,py+TH,cx,cy))

def realize_v(child, iface):
    """--▷  dashed line, hollow triangle at interface bottom."""
    px,py = cx_(iface),bot_(iface)
    cx,cy = cx_(child),top_(child)
    LN.append(hollow_tri_v(px,py))
    LN.append(_vpath(px,py+TH,cx,cy,dash=True))

def inherit_bus_v(parent, children, dash=False):
    """Fan from parent-bottom to multiple children via horizontal bus.
    One hollow triangle at parent; bus line fans to each child top."""
    px,py = cx_(parent),bot_(parent)
    tops  = [(cx_(c),top_(c)) for c in children]
    minx  = min(t[0] for t in tops)
    maxx  = max(t[0] for t in tops)
    by    = py+30
    LN.append(hollow_tri_v(px,py))
    LN.append(L(px,py+TH,px,by,dash))
    LN.append(L(minx,by,maxx,by))           # horizontal bus
    for (cx,cy) in tops:
        LN.append(L(cx,by,cx,cy))           # drops to each child

def compose_h(owner, part, mult_o="1", mult_p="0..*"):
    """◆——>  horizontal: filled diamond on owner's right, open arrow at part left."""
    ox,oy = rgt_(owner), midy(owner)
    px,py = lft_(part),  midy(part)
    LN.append(filled_dia_right(ox,oy))
    LN.append(_hpath(ox-2*DH,oy,px-AH,py))
    LN.append(open_arr_left(px,py))
    LN.append(mlabel(ox-2*DH-2,oy-6,mult_o,"end"))
    LN.append(mlabel(px+4,py-6,mult_p,"start"))

def aggr_h(whole, part, mult_w="1", mult_p="0..*"):
    """◇——>  horizontal: hollow diamond on whole's right, open arrow at part left."""
    ox,oy = rgt_(whole), midy(whole)
    px,py = lft_(part),  midy(part)
    LN.append(hollow_dia_right(ox,oy))
    LN.append(_hpath(ox-2*DH,oy,px-AH,py))
    LN.append(open_arr_left(px,py))
    LN.append(mlabel(ox-2*DH-2,oy-6,mult_w,"end"))
    LN.append(mlabel(px+4,py-6,mult_p,"start"))

def compose_v(owner, part, mult_o="1", mult_p="0..*"):
    """◆——>  vertical: filled diamond on owner's bottom, open arrow at part top."""
    ox,oy = cx_(owner),bot_(owner)
    px,py = cx_(part), top_(part)
    LN.append(filled_dia_down(ox,oy))
    LN.append(_vpath(ox,oy-2*DH,px,py+AH))
    LN.append(open_arr_up(px,py))
    LN.append(mlabel(ox+10,oy-2*DH-4,mult_o,"start"))
    LN.append(mlabel(px+10,py+12,mult_p,"start"))

def aggr_v(whole, part, mult_w="1", mult_p="0..*"):
    """◇——>  vertical: hollow diamond on whole's bottom, open arrow at part top."""
    ox,oy = cx_(whole),bot_(whole)
    px,py = cx_(part), top_(part)
    LN.append(hollow_dia_down(ox,oy))
    LN.append(_vpath(ox,oy-2*DH,px,py+AH))
    LN.append(open_arr_up(px,py))
    LN.append(mlabel(ox+10,oy-2*DH-4,mult_w,"start"))
    LN.append(mlabel(px+10,py+12,mult_p,"start"))

def assoc_h(src, tgt, label=None, ms=None, mt=None, dash=False):
    """——>  horizontal: open arrowhead at target left."""
    sx,sy = rgt_(src), midy(src)
    tx,ty = lft_(tgt), midy(tgt)
    LN.append(_hpath(sx,sy,tx-AH,ty,dash))
    LN.append(open_arr_left(tx,ty))
    if label: LN.append(mlabel((sx+tx)//2,(sy+ty)//2-8,label))
    if ms: LN.append(mlabel(sx+4,sy-5,ms,"start"))
    if mt: LN.append(mlabel(tx-4,ty-5,mt,"end"))

def assoc_v(src, tgt, label=None, ms=None, mt=None, dash=False):
    """——> or --> vertical: open arrowhead at target top."""
    sx,sy = cx_(src), bot_(src)
    tx,ty = cx_(tgt), top_(tgt)
    LN.append(_vpath(sx,sy,tx,ty-AH,dash))
    LN.append(open_arr_up(tx,ty))
    if label: LN.append(mlabel(sx+8,(sy+ty)//2,label,"start"))
    if ms: LN.append(mlabel(sx+5,sy+10,ms,"start"))
    if mt: LN.append(mlabel(tx+5,ty-6,mt,"start"))

def sect(x,y,w,h,title):
    BG.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6"'
              f' fill="{SBG}" stroke="{SST}" stroke-width="1"/>')
    BG.append(f'<text x="{x+w//2}" y="{y+18}" text-anchor="middle" font-size="12"'
              f' font-weight="700" fill="{TSC}" font-family="{FONT}">{q(title)}</text>')

# ═══════════════════════════════════════════════════════════════════════════════
#  LAYOUT — Row 1  (y = 90 .. 700)
# ═══════════════════════════════════════════════════════════════════════════════

# ── SECTION 1 · Function Hierarchies  (x=20, w=1215, h=610) ──────────────────

sect(20, 90, 1215, 610, "Function Hierarchies")

# Interfaces (top row)
N("DifferentiableFunction", 500, 120, 220, 'interface', [], [
    '+ output(x : double) : double',
    '+ derivative(x : double) : double',
])
N("ErrorFunction", 1035, 120, 195, 'interface', [], [
    '+ error(out, tgt : double) : double',
    '+ derivative(out, tgt : double) : double',
])

# Abstract classes (middle row)
N("ActivationFunction", 188, 305, 220, 'abstract', [
    '- name : String',
], [
    '+ getName() : String',
    '+ output(x : double) : double',
    '+ derivative(x : double) : double',
])

N("RegularizationFunction", 780, 305, 240, 'abstract', [
    '- name : String',
], [
    '+ getName() : String',
    '+ output(w : double) : double',
    '+ derivative(w : double) : double',
    '+ crossesZero(o,n : double) : bool',
])

N("SquaredError", 1035, 305, 195, 'concrete', [
    '+ INSTANCE : SquaredError',
], [
    '+ error(out, tgt : double) : double',
    '+ derivative(out, tgt : double) : double',
])

# Realization arrows (--▷)
realize_v("ActivationFunction",     "DifferentiableFunction")
realize_v("RegularizationFunction", "DifferentiableFunction")
realize_v("SquaredError",           "ErrorFunction")

# Activation concretes (2 × 2 grid, bottom of section)
N("TanhActivation",     28,  490, 188, 'concrete', [], [
    '+ output(x : double) : double',
    '+ derivative(x : double) : double',
])
N("ReluActivation",    230,  490, 188, 'concrete', [], [
    '+ output(x : double) : double',
    '+ derivative(x : double) : double',
])
N("SigmoidActivation",  28,  585, 192, 'concrete', [], [
    '+ output(x : double) : double',
    '+ derivative(x : double) : double',
])
N("LinearActivation",  234,  585, 188, 'concrete', [], [
    '+ output(x : double) : double',
    '+ derivative(x : double) : double',
])

# Inheritance (——▷): ActivationFunction → 4 concretes (individual fan arrows)
# One shared triangle at ActFn bottom, 4 diverging lines
af_px, af_py = cx_("ActivationFunction"), bot_("ActivationFunction")
LN.append(hollow_tri_v(af_px, af_py))
for ch_name in ["TanhActivation","ReluActivation","SigmoidActivation","LinearActivation"]:
    LN.append(L(af_px, af_py+TH, cx_(ch_name), top_(ch_name)))

# Regularization concretes (single row)
N("NoRegularization",  748, 510, 162, 'concrete', [], [
    '+ output(w : double) : double',
    '+ derivative(w : double) : double',
])
N("L1Regularization",  921, 510, 175, 'concrete', [], [
    '+ output(w : double) : double',
    '+ derivative(w : double) : double',
    '+ crossesZero(o,n:double):bool',
])
N("L2Regularization", 1107, 510, 162, 'concrete', [], [
    '+ output(w : double) : double',
    '+ derivative(w : double) : double',
])

# Inheritance bus: RegularizationFunction → 3 concretes
inherit_bus_v("RegularizationFunction",
              ["NoRegularization","L1Regularization","L2Regularization"])

# ── SECTION 2 · Exception Hierarchy  (x=1252, w=490, h=610) ─────────────────

sect(1252, 90, 490, 610, "Exception Hierarchy")

N("RuntimeException",      1345, 120, 192, 'external', [], [])

N("PlaygroundException",   1340, 248, 205, 'abstract', [
    '- httpStatus : int',
], [
    '+ getHttpStatus() : int',
])

inherit_v("PlaygroundException", "RuntimeException")

N("ConfigurationException", 1258, 410, 155, 'concrete', [], [
    '# ConfigurationException',
    '  (msg : String) — HTTP 400',
])
N("TrainingException",      1424, 410, 150, 'concrete', [], [
    '# TrainingException',
    '  (msg : String) — HTTP 500',
])
N("NotFoundException",      1588, 410, 148, 'concrete', [], [
    '# NotFoundException',
    '  (msg : String) — HTTP 404',
])

inherit_bus_v("PlaygroundException",
              ["ConfigurationException","TrainingException","NotFoundException"])

N("SessionNotFoundException", 1575, 526, 168, 'concrete', [], [
    '# SessionNotFoundException',
    '  (id : String) — HTTP 404',
])

inherit_v("SessionNotFoundException", "NotFoundException")

# ── SECTION 3 · Dataset Generators  (x=1760, w=418, h=610) ──────────────────

sect(1760, 90, 418, 610, "Dataset Generators")

N("DataGenerator", 1768, 120, 208, 'abstract', [], [
    '+ generate(n : int,',
    '  noise : double,',
    '  rng : Random) : List',
    '+ getKey() : String',
    '+ isRegression() : boolean',
])

N("CircleDataset",              1768, 345, 188, 'concrete', [], [
    '+ generate(...) : List',
])
N("XorDataset",                 1768, 398, 170, 'concrete', [], [
    '+ generate(...) : List',
])
N("GaussianDataset",            1768, 451, 195, 'concrete', [], [
    '+ generate(...) : List',
])
N("SpiralDataset",              1768, 504, 178, 'concrete', [], [
    '+ generate(...) : List',
])
N("PlaneRegressionDataset",     1768, 557, 200, 'concrete', [], [
    '+ generate(...) : List',
])
N("GaussianRegressionDataset",  1768, 610, 210, 'concrete', [], [
    '+ generate(...) : List',
])

inherit_bus_v("DataGenerator", [
    "CircleDataset","XorDataset","GaussianDataset",
    "SpiralDataset","PlaneRegressionDataset","GaussianRegressionDataset",
])

# ═══════════════════════════════════════════════════════════════════════════════
#  LAYOUT — Row 2  (y = 740 .. 1170)
# ═══════════════════════════════════════════════════════════════════════════════

# ── SECTION 4 · Neural Network Core  (x=20, w=870, h=430) ───────────────────

sect(20, 740, 870, 430, "Neural Network Core")

N("Node", 32, 772, 248, 'concrete', [
    '- id : String',
    '- bias : double',
    '- output : double',
    '- outputDer : double',
], [
    '+ updateOutput() : double',
    '+ seedOutputDer(v : double) : void',
    '+ computeAndAccumulateInputDer() : void',
    '+ recomputeOutputDer() : void',
    '+ applyBiasUpdate(lr : double) : void',
])

N("Link", 302, 772, 252, 'concrete', [
    '- weight : double',
    '- errorDer : double',
    '- accErrorDer : double',
], [
    '+ computeAndAccumulateErrorDer() : void',
    '+ applyWeightUpdate(lr, rr : double) : void',
    '+ getWeight() : double',
    '+ getSource() : Node',
    '+ getDest() : Node',
])

N("NeuralNetwork", 578, 772, 298, 'concrete', [], [
    '+ buildNetwork(shape, activation,',
    '  reg, ids, initZero,',
    '  rng) : List<List<Node>>',
    '+ forwardProp(net, input[]) : double',
    '+ backProp(net, label,',
    '  err : ErrorFunction) : void',
    '+ updateWeights(net,lr,rr) : void',
])

# Node ◆——> Link  (composition: Node owns its Links)
compose_h("Node", "Link", "1", "0..*")

# NeuralNetwork ——> Node  (association: NeuralNetwork orchestrates Nodes)
assoc_h("Link", "NeuralNetwork", label=None, ms="0..*", mt="1..*")

# ── SECTION 5 · API Layer  (x=910, w=1268, h=430) ────────────────────────────

sect(910, 740, 1268, 430, "API Layer")

N("Trainable", 920, 772, 185, 'interface', [], [
    '+ trainOneEpoch(lr, rr : double,',
    '  batchSize : int) : void',
    '+ getIteration() : int',
    '+ getTrainLoss() : double',
    '+ getTestLoss() : double',
])

N("Session", 920, 990, 258, 'concrete', [
    '- id : String',
    '- iter : int',
    '- lossTrain : double',
    '- dataset : DataGenerator',
    '- activation : ActivationFunction',
    '- regularization : RegularizationFunction',
], [
    '+ trainOneEpoch(lr, rr, b) : void',
    '+ trainOneEpoch() : void',
    '+ rebuildNetwork() : void',
    '+ regenerateData() : void',
])

# Realization: Session --▷ Trainable
realize_v("Session", "Trainable")

N("SessionManager", 1215, 772, 238, 'concrete', [
    '- sessions : Map<String, Session>',
], [
    '+ create() : Session',
    '+ get(id : String) : Session',
    '+ require(id : String) : Session',
    '+ remove(id : String) : void',
])

# SessionManager ◇——> Session (aggregation: holds many sessions, 1 to 0..*)
aggr_v("SessionManager", "Session", "1", "0..*")

N("ApiServer", 1490, 772, 218, 'concrete', [
    '- port : int',
    '- manager : SessionManager',
], [
    '+ start() : void',
    '+ dispatch(ex : HttpExchange) : void',
])

N("RequestHandlers", 1745, 772, 258, 'concrete', [
    '- manager : SessionManager',
], [
    '+ handleCreate(ex) : void',
    '+ handleConfig(ex) : void',
    '+ handleStep(ex) : void',
    '+ handleBoundary(ex) : void',
])

# ApiServer ——> RequestHandlers (association)
assoc_h("ApiServer", "RequestHandlers", label=None, ms="1", mt="1")

# ApiServer ——> SessionManager (association: uses manager)
# Draw as vertical since they're at same y level but both already have it as attr

# ─── Cross-section: Session ◆——> Node (Session owns the network nodes) ────────
# Session right → toward Section 4; route: Session right → mid horizontal → Node top
sess_rx = rgt_("Session")
sess_my = midy("Session")
node_tx = cx_("Node")
node_ty = top_("Node")
# Filled diamond at Session right side
LN.append(filled_dia_right(sess_rx, sess_my))
LN.append(ML([(sess_rx-2*DH, sess_my),
              (sess_rx-2*DH-20, sess_my),
              (sess_rx-2*DH-20, node_ty-20),
              (node_tx+60, node_ty-20),
              (node_tx+60, node_ty-AH)]))
LN.append(open_arr_up(node_tx+60, node_ty))
LN.append(mlabel(sess_rx-2*DH-24, sess_my-6, "1", "end"))
LN.append(mlabel(node_tx+65, node_ty+10, "0..*", "start"))

# ─── Legend note labels on cross arrows ──────────────────────────────────────
LN.append(f'<text x="{(sess_rx-2*DH-20 + node_tx+60)//2}" y="{node_ty-28}"'
          f' text-anchor="middle" font-size="9" fill="{TSC}"'
          f' font-family="{FONT}">◆ Session owns network nodes</text>')

# ═══════════════════════════════════════════════════════════════════════════════
#  TITLE, LEGEND
# ═══════════════════════════════════════════════════════════════════════════════

title_els = [
    f'<text x="{SVG_W//2}" y="38" text-anchor="middle" font-size="20"'
    f' font-weight="700" fill="#1A1A2E" font-family="{FONT}">'
    f'OOP Neural Network Playground — UML Class Diagram</text>',
    f'<text x="{SVG_W//2}" y="57" text-anchor="middle" font-size="11"'
    f' fill="{TSC}" font-family="{FONT}">'
    f'Java Backend · Arrows: ——▷ Inheritance  --▷ Realization  '
    f'◆——> Composition  ◇——> Aggregation  ——> Association</text>',
]

leg_x = SVG_W//2 - 520
leg_y = 70
leg_items = [
    (IF_F, IF_S, "5,3",  "«interface»"),
    (AB_F, AB_S, None,   "«abstract»"),
    (CO_F, CO_S, None,   "Concrete class"),
    (EX_F, EX_S, "4,4",  "External (JDK)"),
]
leg_els = []
lx = leg_x
for fill, stroke, da, label in leg_items:
    da_s = f' stroke-dasharray="{da}"' if da else ''
    leg_els.append(f'<rect x="{lx}" y="{leg_y}" width="28" height="17" rx="2"'
                   f' fill="{fill}" stroke="{stroke}" stroke-width="1.5"{da_s}/>')
    leg_els.append(f'<text x="{lx+34}" y="{leg_y+12}" font-size="10" fill="{TSC}"'
                   f' font-family="{FONT}">{label}</text>')
    lx += 138

# ─── Assemble ─────────────────────────────────────────────────────────────────

out = (
    [f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}"'
     f' viewBox="0 0 {SVG_W} {SVG_H}">',
     f'<rect width="{SVG_W}" height="{SVG_H}" fill="#F9FAFE"/>']
    + title_els + leg_els
    + BG + LN + FG
    + ['</svg>']
)

with open("uml_diagram.svg", "w", encoding="utf-8") as fh:
    fh.write("\n".join(out))

print("uml_diagram.svg written successfully.")

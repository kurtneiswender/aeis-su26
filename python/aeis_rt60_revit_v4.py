# -*- coding: utf-8 -*-
# VERSION: v4 — fix UnicodeEncodeError (ASCII-safe strings in ray SVG)
"""
AEIS RT60 Acoustic Analyzer — Revit / Dynamo
ARC 5443 · Acoustics, Electrical & Illumination Systems
Lawrence Technological University

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOW TO USE IN DYNAMO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Open Dynamo (Manage tab → Dynamo Player or Dynamo)
2. Create a Python Script node (right-click canvas → Script → IronPython
   or CPython 3.x depending on your Dynamo version)
3. Paste this entire file into the Python node editor
4. Wire three inputs to the Python node:
      IN[0] → a single Room element
              (All Elements of Category → Rooms → Index 0, or Select Model Element)
      IN[1] → String node: program type
              "speech" | "mixed" | "music_opera" | "music_symph" | "cinema"
      IN[2] → (optional) File Path node: full path for HTML report
              e.g.  C:/Users/you/Desktop/rt60_report.html
              Leave unconnected or set to None to skip.
5. Run — connect a Watch node to OUT to see results.

MATERIAL MAPPING
━━━━━━━━━━━━━━━━
Revit wall/floor/ceiling type names are matched against MATERIAL_MAP below
(case-insensitive substring). Edit MATERIAL_MAP to match your project's
type naming conventions. The first matching rule wins.
If no rule matches, the category default is used (edit DEFAULT_* below).

COMPARISON WITH RHINO SCRIPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Rhino version uses layer names: AEIS_<MATERIAL>
Revit version reads from the model: room volumes + element type names
The material table, Sabine/Eyring math, and HTML report are identical.
"""

import clr
import math
import os

# ─── Revit API ────────────────────────────────────────────────────────────────
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import (
    FilteredElementCollector, BoundingBoxIntersectsFilter, Outline,
    SpatialElementBoundaryOptions, SpatialElementBoundaryLocation,
    BuiltInParameter, BuiltInCategory, ElementId, Element
)

# Document access — works in both Dynamo and pyRevit
try:
    clr.AddReference('RevitServices')
    from RevitServices.Persistence import DocumentManager
    doc = DocumentManager.Instance.CurrentDBDocument
    _DYNAMO = True
except Exception:
    try:
        doc = __revit__.ActiveUIDocument.Document
        _DYNAMO = False
    except Exception:
        doc = None

# ──────────────────────────────────────────────────────────────────────────────
# MATERIAL LOOKUP TABLE
# Octave-band absorption coefficients: [125, 250, 500, 1000, 2000, 4000] Hz
# Sources: MEEB 13th ed. Table 27.1 / Knudsen & Harris / manufacturer averages
# ──────────────────────────────────────────────────────────────────────────────
MATERIAL_TABLE = {
    # ── Floors ──────────────────────────────────────────────────────────────
    "CARPET_THICK":        [0.08, 0.24, 0.57, 0.69, 0.71, 0.73],
    "CARPET_THIN":         [0.02, 0.06, 0.14, 0.37, 0.60, 0.65],
    "WOOD_FLOOR":          [0.15, 0.11, 0.10, 0.07, 0.06, 0.07],
    "CONCRETE_FLOOR":      [0.01, 0.01, 0.02, 0.02, 0.02, 0.02],

    # ── Ceilings ────────────────────────────────────────────────────────────
    "GYPSUM_BOARD":        [0.29, 0.10, 0.05, 0.04, 0.07, 0.09],
    "ACOUSTIC_TILE":       [0.25, 0.45, 0.78, 0.92, 0.89, 0.87],
    "PLASTER_HARD":        [0.03, 0.03, 0.02, 0.03, 0.04, 0.05],
    "PLASTER_ACOUSTIC":    [0.08, 0.15, 0.40, 0.45, 0.40, 0.38],
    "WOOD_PANEL":          [0.10, 0.11, 0.10, 0.08, 0.08, 0.11],
    "CEILING_CLOUD":       [0.10, 0.20, 0.55, 0.70, 0.65, 0.60],

    # ── Walls ───────────────────────────────────────────────────────────────
    "CONCRETE_BARE":       [0.01, 0.01, 0.02, 0.02, 0.03, 0.03],
    "CONCRETE_BLOCK":      [0.36, 0.44, 0.31, 0.29, 0.39, 0.25],
    "BRICK":               [0.03, 0.03, 0.03, 0.04, 0.05, 0.07],
    "GLASS":               [0.35, 0.25, 0.18, 0.12, 0.07, 0.04],
    "FABRIC_CURTAIN":      [0.07, 0.31, 0.49, 0.75, 0.70, 0.60],
    "GRC_CONVEX":          [0.04, 0.04, 0.05, 0.06, 0.07, 0.08],
    "WOOD_DIFFUSER":       [0.07, 0.12, 0.10, 0.09, 0.08, 0.10],

    # ── Seating ─────────────────────────────────────────────────────────────
    "SEATS_UPHOLSTERED":   [0.44, 0.56, 0.67, 0.74, 0.83, 0.87],
    "SEATS_OCCUPIED":      [0.39, 0.57, 0.80, 0.94, 0.92, 0.87],
    "SEATS_WOOD":          [0.02, 0.03, 0.03, 0.06, 0.06, 0.05],

    # ── Special ─────────────────────────────────────────────────────────────
    "ACOUSTIC_PANEL":      [0.20, 0.55, 0.90, 0.95, 0.95, 0.90],
    "BASS_TRAP":           [0.40, 0.80, 0.90, 0.85, 0.80, 0.75],
    "OPEN_WINDOW":         [1.00, 1.00, 1.00, 1.00, 1.00, 1.00],
}

FREQ_BANDS = [125, 250, 500, 1000, 2000, 4000]

RT60_TARGETS = {
    "speech":       [0.6,  1.0],
    "mixed":        [1.4,  1.8],
    "music_opera":  [1.6,  2.0],
    "music_symph":  [1.8,  2.2],
    "cinema":       [0.3,  0.5],
}

# ──────────────────────────────────────────────────────────────────────────────
# MATERIAL MAP  (Revit type name substring → MATERIAL_TABLE key)
# Rules are checked top to bottom; first match wins.
# Edit these to match your project's wall/floor/ceiling type naming.
# ──────────────────────────────────────────────────────────────────────────────
MATERIAL_MAP = [
    # ─ Flooring ──────────────────────────────────────────────────────────────
    ("carpet",           "CARPET_THICK"),
    ("hardwood",         "WOOD_FLOOR"),
    ("wood floor",       "WOOD_FLOOR"),
    ("tile",             "CONCRETE_FLOOR"),
    ("terrazzo",         "CONCRETE_FLOOR"),
    ("concrete floor",   "CONCRETE_FLOOR"),

    # ─ Ceilings ──────────────────────────────────────────────────────────────
    ("acoustic tile",    "ACOUSTIC_TILE"),
    ("acoustic ceil",    "ACOUSTIC_TILE"),
    ("lay-in",           "ACOUSTIC_TILE"),
    ("layin",            "ACOUSTIC_TILE"),
    ("cloud",            "CEILING_CLOUD"),
    ("gypsum ceil",      "GYPSUM_BOARD"),
    ("drywall ceil",     "GYPSUM_BOARD"),
    ("plaster",          "PLASTER_HARD"),

    # ─ Walls ─────────────────────────────────────────────────────────────────
    ("gypsum",           "GYPSUM_BOARD"),
    ("drywall",          "GYPSUM_BOARD"),
    ("gwb",              "GYPSUM_BOARD"),
    ("cmu",              "CONCRETE_BLOCK"),
    ("masonry",          "CONCRETE_BLOCK"),
    ("block",            "CONCRETE_BLOCK"),
    ("brick",            "BRICK"),
    ("concrete",         "CONCRETE_BARE"),
    ("curtain wall",     "GLASS"),
    ("glazing",          "GLASS"),
    ("glass",            "GLASS"),
    ("fabric",           "FABRIC_CURTAIN"),
    ("wood panel",       "WOOD_PANEL"),
    ("plywood",          "WOOD_PANEL"),
]

# Defaults when no rule matches
DEFAULT_WALL_MATERIAL    = "GYPSUM_BOARD"
DEFAULT_FLOOR_MATERIAL   = "CONCRETE_FLOOR"
DEFAULT_CEILING_MATERIAL = "ACOUSTIC_TILE"


# ──────────────────────────────────────────────────────────────────────────────
# UNIT HELPERS
# Revit internal units are decimal feet. Revit 2022+ has UnitTypeId;
# earlier versions use DisplayUnitType. Both paths are handled.
# ──────────────────────────────────────────────────────────────────────────────

def _eid_key(eid):
    """Hashable key for an ElementId — handles Revit 2024+ API change.
    IntegerValue was removed in 2024; Value (Int64) replaced it."""
    try:
        return eid.Value          # Revit 2024+
    except AttributeError:
        return eid.IntegerValue   # Revit 2023 and earlier


def _ft3_to_m3(ft3):
    return ft3 * 0.0283168

def _ft2_to_m2(ft2):
    return ft2 * 0.092903

def _ft_to_m(ft):
    return ft * 0.3048


def to_m3(internal_val):
    try:
        from Autodesk.Revit.DB import UnitTypeId, UnitUtils
        return UnitUtils.ConvertFromInternalUnits(internal_val, UnitTypeId.CubicMeters)
    except Exception:
        return _ft3_to_m3(internal_val)


def to_m2(internal_val):
    try:
        from Autodesk.Revit.DB import UnitTypeId, UnitUtils
        return UnitUtils.ConvertFromInternalUnits(internal_val, UnitTypeId.SquareMeters)
    except Exception:
        return _ft2_to_m2(internal_val)


def to_m(internal_val):
    try:
        from Autodesk.Revit.DB import UnitTypeId, UnitUtils
        return UnitUtils.ConvertFromInternalUnits(internal_val, UnitTypeId.Meters)
    except Exception:
        return _ft_to_m(internal_val)


# ──────────────────────────────────────────────────────────────────────────────
# MATERIAL MATCHING
# ──────────────────────────────────────────────────────────────────────────────

def match_material(type_name):
    """Return MATERIAL_TABLE key for a Revit type name, or None."""
    lower = (type_name or "").lower().strip()
    for substr, key in MATERIAL_MAP:
        if substr.lower() in lower:
            return key
    return None


def get_type_name(element):
    """Return the type name of a Revit element."""
    try:
        etype = doc.GetElement(element.GetTypeId())
        if etype is not None:
            return Element.Name.GetValue(etype)
    except Exception:
        pass
    return ""


def assign_material(category_name, type_name):
    """MATERIAL_TABLE key from category + type name."""
    mat = match_material(type_name)
    if mat:
        return mat
    if category_name == "Floors":
        return DEFAULT_FLOOR_MATERIAL
    if category_name == "Ceilings":
        return DEFAULT_CEILING_MATERIAL
    return DEFAULT_WALL_MATERIAL


# ──────────────────────────────────────────────────────────────────────────────
# ROOM SURFACE EXTRACTION
# Returns: list of (category_name, type_name, material_key, area_m2)
# ──────────────────────────────────────────────────────────────────────────────

def get_room_surfaces(room):
    surfaces = []

    # ── Room height (for wall area calculation) ───────────────────────────────
    height_internal = None
    try:
        h = room.get_Parameter(BuiltInParameter.ROOM_HEIGHT)
        if h and h.HasValue:
            height_internal = h.AsDouble()
    except Exception:
        pass

    if not height_internal or height_internal < 0.001:
        try:
            a = room.Area
            v = room.Volume
            height_internal = v / a if a > 0.001 else 10.0
        except Exception:
            height_internal = 10.0  # ~3 m fallback

    # ── Wall areas from boundary segments ─────────────────────────────────────
    opts = SpatialElementBoundaryOptions()
    try:
        opts.SpatialElementBoundaryLocation = SpatialElementBoundaryLocation.Finish
    except Exception:
        pass

    try:
        boundary_loops = room.GetBoundarySegments(opts)
    except Exception:
        boundary_loops = None

    wall_accum = {}  # _eid_key(eid) → (type_name, area_m2)

    if boundary_loops:
        for bloop in boundary_loops:
            for seg in bloop:
                eid = seg.ElementId
                if eid == ElementId.InvalidElementId:
                    continue
                elem = doc.GetElement(eid)
                if elem is None:
                    continue
                cat = elem.Category
                if cat is None:
                    continue
                cat_name = cat.Name

                if cat_name in ("Walls", "Curtain Panels", "Curtain Wall Mullions"):
                    seg_len  = seg.GetCurve().Length
                    area_m2  = to_m2(seg_len * height_internal)
                    tname    = get_type_name(elem)
                    eid_int  = _eid_key(eid)
                    if eid_int in wall_accum:
                        wall_accum[eid_int] = (tname, wall_accum[eid_int][1] + area_m2)
                    else:
                        wall_accum[eid_int] = (tname, area_m2)

    for eid_int, (tname, area_m2) in wall_accum.items():
        if area_m2 < 0.001:
            continue
        mat = assign_material("Walls", tname)
        surfaces.append(("Walls", tname or "(no type name)", mat, area_m2))

    # ── Floor area ────────────────────────────────────────────────────────────
    floor_area_m2 = to_m2(room.Area)
    floor_type    = ""
    try:
        bb = room.get_BoundingBox(None)
        if bb:
            outline = Outline(bb.Min, bb.Max)
            floors  = (FilteredElementCollector(doc)
                       .OfCategory(BuiltInCategory.OST_Floors)
                       .WherePasses(BoundingBoxIntersectsFilter(outline))
                       .ToElements())
            if len(floors) > 0:
                floor_type = get_type_name(floors[0])
    except Exception:
        pass
    floor_mat = assign_material("Floors", floor_type)
    surfaces.append(("Floors", floor_type or "(default)", floor_mat, floor_area_m2))

    # ── Ceiling area ~~~ flat ceiling assumption ≈ floor area ─────────────────
    ceiling_type = ""
    try:
        bb = room.get_BoundingBox(None)
        if bb:
            outline  = Outline(bb.Min, bb.Max)
            ceilings = (FilteredElementCollector(doc)
                        .OfCategory(BuiltInCategory.OST_Ceilings)
                        .WherePasses(BoundingBoxIntersectsFilter(outline))
                        .ToElements())
            if len(ceilings) > 0:
                ceiling_type = get_type_name(ceilings[0])
    except Exception:
        pass
    ceiling_mat = assign_material("Ceilings", ceiling_type)
    surfaces.append(("Ceilings", ceiling_type or "(default)", ceiling_mat, floor_area_m2))

    return surfaces


# ──────────────────────────────────────────────────────────────────────────────
# RT60 CALCULATIONS  (identical math to the Rhino version)
# ──────────────────────────────────────────────────────────────────────────────

def sabine_rt60(volume_m3, total_absorption_m2):
    if total_absorption_m2 < 0.001:
        return float("inf")
    return 0.161 * volume_m3 / total_absorption_m2


def eyring_rt60(volume_m3, total_surface_m2, mean_absorption):
    if mean_absorption >= 1.0:
        return 0.0
    term = -total_surface_m2 * math.log(1.0 - mean_absorption)
    if term < 0.001:
        return float("inf")
    return 0.161 * volume_m3 / term


def compute_rt60(volume_m3, surface_data):
    """
    surface_data: list of (cat, typename, material_key, area_m2)
    Returns (rt60_sabine[6], rt60_eyring[6], total_surface_area_m2)
    """
    total_surface = sum(s[3] for s in surface_data)
    rt60_sabine   = []
    rt60_eyring   = []

    for band_idx in range(6):
        total_abs = sum(MATERIAL_TABLE[s[2]][band_idx] * s[3] for s in surface_data)
        mean_alpha = total_abs / total_surface if total_surface > 0 else 0.0
        rt60_sabine.append(sabine_rt60(volume_m3, total_abs))
        rt60_eyring.append(eyring_rt60(volume_m3, total_surface, mean_alpha))

    return rt60_sabine, rt60_eyring, total_surface


# ──────────────────────────────────────────────────────────────────────────────
# TEXT REPORT
# ──────────────────────────────────────────────────────────────────────────────

def format_report(room_name, volume_m3, surface_data, rt60_sabine, rt60_eyring,
                  total_surface, program_type):
    target  = RT60_TARGETS.get(program_type, RT60_TARGETS["mixed"])
    t_min, t_max = target
    lines   = []

    lines.append("")
    lines.append("=" * 62)
    lines.append("  AEIS RT60 ANALYSIS  .  ARC 5443")
    lines.append("  Room: {}".format(room_name))
    lines.append("  Volume: {:.0f} m3  ({:.0f} ft3)".format(volume_m3, volume_m3 * 35.3147))
    lines.append("  Program target: {}  [{:.1f}-{:.1f} s]".format(
        program_type.upper(), t_min, t_max))
    lines.append("=" * 62)
    lines.append("  {:>6}   {:>10}   {:>10}   {}".format(
        "Freq", "Sabine RT60", "Eyring RT60", "Status (Eyring)"))
    lines.append("  " + "-" * 58)

    for i, freq in enumerate(FREQ_BANDS):
        s_val = rt60_sabine[i]
        e_val = rt60_eyring[i]
        if t_min <= e_val <= t_max:
            status = "OK"
        elif e_val < t_min:
            status = "TOO DRY  <- reduce absorption or add volume"
        else:
            status = "TOO LIVE <- add absorptive material"
        lines.append("  {:>5} Hz  {:>8.2f} s    {:>8.2f} s    {}".format(
            freq, s_val, e_val, status))

    lines.append("=" * 62)
    mid_idx = FREQ_BANDS.index(500)
    lines.append("  Mid-freq Eyring (500 Hz): {:.2f} s  [primary result]".format(
        rt60_eyring[mid_idx]))
    lines.append("  Mid-freq Sabine (500 Hz): {:.2f} s  [hand-calc worksheet]".format(
        rt60_sabine[mid_idx]))
    lines.append("=" * 62)
    lines.append("")
    lines.append("  SURFACE MATERIAL SUMMARY")
    lines.append("  " + "-" * 60)
    lines.append("  {:10s} {:28s} {:>8s} {:>6s}".format(
        "Category", "Type / Material", "Area m2", "NRC"))
    lines.append("  " + "-" * 60)
    for cat, tname, mat, area in surface_data:
        coeffs = MATERIAL_TABLE[mat]
        nrc    = (coeffs[2] + coeffs[3] + coeffs[4] + coeffs[5]) / 4.0
        lines.append("  {:10s} {:28s} {:>8.1f} {:>6.2f}".format(
            cat[:10],
            "{} ({})".format(tname[:14], mat.replace("_", " "))[:28],
            area, nrc))
    lines.append("  " + "-" * 60)
    lines.append("")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# 2D RAY TRACE  (overhead plan diagram for HTML report)
# ──────────────────────────────────────────────────────────────────────────────

def _get_boundary_2d(room):
    """Return list of ((x1,y1),(x2,y2)) segments from room boundary (internal ft)."""
    opts = SpatialElementBoundaryOptions()
    try:
        opts.SpatialElementBoundaryLocation = SpatialElementBoundaryLocation.Finish
    except Exception:
        pass
    segs = []
    try:
        loops = room.GetBoundarySegments(opts)
        if loops:
            for loop in loops:
                for seg in loop:
                    c = seg.GetCurve()
                    p0 = c.GetEndPoint(0)
                    p1 = c.GetEndPoint(1)
                    segs.append(((p0.X, p0.Y), (p1.X, p1.Y)))
    except Exception:
        pass
    return segs


def _ray_seg_hit(ox, oy, dx, dy, x1, y1, x2, y2):
    """2D ray-segment intersection. Returns (t, hit_x, hit_y) or None."""
    ex, ey = x2 - x1, y2 - y1
    denom = dx * ey - dy * ex
    if abs(denom) < 1e-10:
        return None
    tx, ty = x1 - ox, y1 - oy
    t = (tx * ey - ty * ex) / denom
    u = (tx * dy - ty * dx) / denom
    if t > 1e-4 and 0.0 <= u <= 1.0:
        return t, ox + t * dx, oy + t * dy
    return None


def _cast_rays_2d(source, segs, mean_alpha_500, n_rays=72, max_bounces=8, cutoff=0.05):
    """Cast rays from source point, bounce off boundary segments."""
    sx, sy = source
    paths = []
    for i in range(n_rays):
        angle = 2.0 * math.pi * i / n_rays
        dx, dy = math.cos(angle), math.sin(angle)
        cx, cy = sx, sy
        energy = 1.0
        pts = [(cx, cy)]
        energies = [1.0]
        for _ in range(max_bounces):
            best = None
            for si, ((x1, y1), (x2, y2)) in enumerate(segs):
                hit = _ray_seg_hit(cx, cy, dx, dy, x1, y1, x2, y2)
                if hit and (best is None or hit[0] < best[0]):
                    best = hit + (si,)
            if best is None:
                break
            _, hx, hy, si = best
            energy *= (1.0 - mean_alpha_500)
            pts.append((hx, hy))
            energies.append(energy)
            if energy < cutoff:
                break
            # Wall normal (perpendicular to segment, facing inward)
            (x1, y1), (x2, y2) = segs[si]
            ex, ey = x2 - x1, y2 - y1
            ln = math.sqrt(ex * ex + ey * ey)
            if ln < 1e-10:
                break
            nx, ny = -ey / ln, ex / ln
            if nx * (-dx) + ny * (-dy) < 0:
                nx, ny = -nx, -ny
            dot = dx * nx + dy * ny
            dx, dy = dx - 2 * dot * nx, dy - 2 * dot * ny
            cx, cy = hx, hy
        if len(pts) > 1:
            paths.append((pts, energies))
    return paths


def _rays_to_svg(paths, segs, source, w=640, h=400):
    """Render 2D ray paths and room boundary as an SVG string."""
    all_x = [p[0] for s in segs for p in s]
    all_y = [p[1] for s in segs for p in s]
    if not all_x:
        return ""
    pad = 28
    rw = max(all_x) - min(all_x) or 1.0
    rh = max(all_y) - min(all_y) or 1.0
    scale = min((w - 2 * pad) / rw, (h - 2 * pad) / rh)
    ox0, oy0 = min(all_x), min(all_y)

    def sv(x, y):   # world → SVG (flip Y)
        return pad + (x - ox0) * scale, h - pad - (y - oy0) * scale

    def ecol(e):
        e = max(0.0, min(1.0, e))
        if e > 0.66:
            return "rgb(200,{},40)".format(int(40 + (1 - e) * 3 * 180))
        elif e > 0.33:
            return "rgb({},140,80)".format(int(40 + (e - 0.33) * 3 * 160))
        else:
            return "rgb(40,80,{})".format(int(100 + (0.33 - e) * 3 * 155))

    out = []
    out.append('<svg viewBox="0 0 {} {}" xmlns="http://www.w3.org/2000/svg" '
               'style="width:100%;max-width:{}px;display:block;margin:0 auto;'
               'background:#0e0d0b;border-radius:4px;">'.format(w, h, w))

    # Room boundary
    for (x1, y1), (x2, y2) in segs:
        sx1, sy1 = sv(x1, y1)
        sx2, sy2 = sv(x2, y2)
        out.append('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}" '
                   'stroke="rgba(212,162,76,0.75)" stroke-width="2"/>'.format(
                   sx1, sy1, sx2, sy2))

    # Ray paths
    for pts, energies in paths:
        for i in range(len(pts) - 1):
            x1, y1 = sv(*pts[i])
            x2, y2 = sv(*pts[i + 1])
            e_mid = (energies[i] + energies[i + 1]) * 0.5
            out.append('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}" '
                       'stroke="{}" stroke-width="0.75" opacity="{:.2f}"/>'.format(
                       x1, y1, x2, y2, ecol(e_mid), max(0.12, e_mid * 0.65)))

    # Source dot
    ssx, ssy = sv(*source)
    out.append('<circle cx="{:.1f}" cy="{:.1f}" r="5" fill="#c8472f"/>'.format(ssx, ssy))
    out.append('<circle cx="{:.1f}" cy="{:.1f}" r="9" fill="none" '
               'stroke="#c8472f" stroke-width="1" opacity="0.5"/>'.format(ssx, ssy))

    # Labels
    out.append('<text x="10" y="18" font-family="monospace" font-size="9" '
               'fill="rgba(237,228,211,0.45)" letter-spacing="1.5">'
               'RAY TRACE &middot; 2D PLAN &middot; {} RAYS</text>'.format(len(paths)))
    out.append('<text x="10" y="32" font-family="monospace" font-size="8" '
               'fill="rgba(237,228,211,0.3)">RED = HIGH ENERGY  -&gt;  BLUE = ABSORBED</text>')
    out.append('</svg>')
    return "\n".join(out)


# ──────────────────────────────────────────────────────────────────────────────
# HTML REPORT  (same design system as the Rhino version)
# ──────────────────────────────────────────────────────────────────────────────

def save_html_report(room_name, volume_m3, surface_data, rt60_sabine, rt60_eyring,
                     total_surface, program_type, report_path, ray_svg=""):
    target   = RT60_TARGETS.get(program_type, RT60_TARGETS["mixed"])
    t_min, t_max = target
    mid_idx  = FREQ_BANDS.index(500)
    mid_eyring = rt60_eyring[mid_idx]
    mid_sabine = rt60_sabine[mid_idx]

    def scolor(v):
        if t_min <= v <= t_max: return "#3a8a5a"
        if v < t_min:           return "#c87030"
        return "#c8472f"

    def slabel(v):
        if t_min <= v <= t_max: return "IN RANGE"
        if v < t_min:           return "TOO DRY"
        return "TOO LIVE"

    band_rows = ""
    for i, freq in enumerate(FREQ_BANDS):
        s = rt60_sabine[i]; e = rt60_eyring[i]
        col = scolor(e); lbl = slabel(e)
        row_bg = " style=\"background:#eef6f1\"" if t_min <= e <= t_max else ""
        band_rows += (
            "<tr{}><td>{} Hz</td><td>{:.2f} s</td>"
            "<td><strong>{:.2f} s</strong></td>"
            "<td style=\"color:{};font-weight:600\">{}</td></tr>\n"
        ).format(row_bg, freq, s, e, col, lbl)

    mat_rows     = ""
    total_abs_500 = 0.0
    for cat, tname, mat, area in surface_data:
        coeffs = MATERIAL_TABLE[mat]
        nrc    = (coeffs[2] + coeffs[3] + coeffs[4] + coeffs[5]) / 4.0
        a500   = coeffs[2]
        abs500 = area * a500
        total_abs_500 += abs500
        mat_rows += (
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{:.0f}</td>"
            "<td>{:.2f}</td><td>{:.2f}</td><td>{:.0f}</td></tr>\n"
        ).format(
            cat,
            tname,
            mat.replace("_", " ").title(),
            area, a500, nrc, abs500
        )
    mat_rows += (
        "<tr style=\"font-weight:700;background:#e8e0d0\">"
        "<td colspan=\"3\">TOTAL</td><td>{:.0f} m²</td>"
        "<td>-</td><td>-</td><td>{:.0f} sabins</td></tr>\n"
    ).format(total_surface, total_abs_500)

    bar_pct   = min(100, (mid_eyring / 3.0) * 100)
    tgt_left  = (t_min / 3.0) * 100
    tgt_width = ((t_max - t_min) / 3.0) * 100
    mc        = scolor(mid_eyring)
    sl        = slabel(mid_eyring)

    alpha_mean = total_abs_500 / total_surface if total_surface > 0 else 0

    if ray_svg:
        ray_section = (
            "<h2>Ray Trace &mdash; 2D Plan</h2>\n"
            "<p class=\"note\">Overhead plan view. "
            "Source at room centroid (red dot). "
            "Color encodes energy: red = full &rarr; blue = absorbed. "
            "Mean &alpha; at 500 Hz used for all surfaces.</p>\n"
            + ray_svg
        )
    else:
        ray_section = ""

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>RT60 Report - AEIS ARC 5443</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;600&display=swap');
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Newsreader', Georgia, serif; background: #ede4d3; color: #0e0d0b; max-width: 960px; margin: 48px auto; padding: 0 24px 64px; }}
  header {{ border-bottom: 3px solid #0e0d0b; padding-bottom: 16px; margin-bottom: 32px; }}
  header h1 {{ font-size: 2rem; font-weight: 600; letter-spacing: -.02em; }}
  header p {{ color: #555; font-size: 0.9rem; margin-top: 4px; }}
  h2 {{ font-size: 1rem; font-weight: 600; text-transform: uppercase; letter-spacing: .08em; margin: 32px 0 12px; border-bottom: 1px solid #c4b89a; padding-bottom: 6px; }}
  .summary-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 24px; }}
  .card {{ background: #fff; border: 1px solid #c4b89a; border-radius: 6px; padding: 18px 20px; }}
  .card-val {{ font-family: 'JetBrains Mono', monospace; font-size: 2.2rem; font-weight: 600; line-height: 1; }}
  .card-label {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: .07em; color: #777; margin-top: 4px; }}
  .badge {{ display: inline-block; padding: 3px 12px; border-radius: 20px; color: #fff; font-size: 0.8rem; font-weight: 700; letter-spacing: .04em; }}
  .bar-wrap {{ background: #d6ccb8; border-radius: 8px; height: 18px; position: relative; overflow: hidden; margin-bottom: 6px; }}
  .bar-target {{ position: absolute; top: 0; height: 100%; opacity: .45; background: #3a8a5a; }}
  .bar-needle {{ position: absolute; top: 2px; width: 4px; height: 14px; border-radius: 2px; transform: translateX(-2px); }}
  .bar-labels {{ display: flex; justify-content: space-between; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #777; margin-bottom: 20px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
  th {{ background: #0e0d0b; color: #ede4d3; padding: 8px 12px; text-align: left; font-weight: 600; font-size: 0.78rem; text-transform: uppercase; letter-spacing: .05em; }}
  td {{ padding: 7px 12px; border-bottom: 1px solid #d6ccb8; }}
  tr:last-child td {{ border-bottom: none; }}
  .note {{ font-size: .78rem; color: #888; margin-top: 8px; }}
  footer {{ margin-top: 40px; padding-top: 16px; border-top: 1px solid #c4b89a; font-size: 0.75rem; color: #888; font-style: italic; }}
  code {{ font-family: 'JetBrains Mono', monospace; font-size: 0.82em; background: #e0d9cc; padding: 1px 5px; border-radius: 3px; }}
</style>
</head>
<body>
<header>
  <h1>RT60 Acoustic Analysis</h1>
  <p>ARC 5443 AEIS &nbsp;&middot;&nbsp; Lawrence Technological University
     &nbsp;&middot;&nbsp; Room: <strong>{room}</strong>
     &nbsp;&middot;&nbsp; Program: <strong>{prog}</strong>
     &nbsp;&middot;&nbsp; Target: {tmin:.1f}&ndash;{tmax:.1f} s</p>
</header>

<h2>500 Hz Summary</h2>
<div class="summary-grid">
  <div class="card">
    <div class="card-val" style="color:{mc}">{eyring:.2f} s</div>
    <div class="card-label">Eyring RT60 &mdash; primary result</div>
  </div>
  <div class="card">
    <div class="card-val" style="color:#555">{sabine:.2f} s</div>
    <div class="card-label">Sabine RT60 &mdash; hand-calc reference</div>
  </div>
  <div class="card">
    <div class="card-val"><span class="badge" style="background:{mc}">{sl}</span></div>
    <div class="card-label">vs. {prog} target</div>
  </div>
</div>

<div class="bar-wrap">
  <div class="bar-target" style="left:{tl:.1f}%;width:{tw:.1f}%"></div>
  <div class="bar-needle" style="left:{bp:.1f}%;background:{mc}"></div>
</div>
<div class="bar-labels"><span>0 s</span><span>1.0 s</span><span>2.0 s</span><span>3.0 s</span></div>

<h2>Octave Band Results</h2>
<table>
  <tr><th>Frequency</th><th>Sabine RT60</th><th>Eyring RT60</th><th>Status</th></tr>
  {band_rows}
</table>
<p class="note">Status based on Eyring RT60 vs. program target [{tmin:.1f}&ndash;{tmax:.1f} s].</p>

<h2>Material Schedule</h2>
<table>
  <tr><th>Category</th><th>Revit Type</th><th>Material Key</th><th>Area (m&sup2;)</th><th>&alpha; 500 Hz</th><th>NRC</th><th>Absorption (sabins)</th></tr>
  {mat_rows}
</table>
<p class="note">NRC = avg of &alpha; at 250, 500, 1000, 2000 Hz. Absorption sabins = area &times; &alpha; at 500 Hz.
  <br>Wall areas = boundary segment length &times; room height. Ceiling area = floor area (flat ceiling assumed).</p>

__RAY_SECTION__

<h2>Room Parameters</h2>
<table>
  <tr><th>Parameter</th><th>Value</th></tr>
  <tr><td>Room name</td><td>{room}</td></tr>
  <tr><td>Volume</td><td><code>{vol:.0f} m&sup3;</code> &nbsp;({volft:.0f} ft&sup3;)</td></tr>
  <tr><td>Total surface area</td><td><code>{sa:.0f} m&sup2;</code></td></tr>
  <tr><td>Total absorption at 500 Hz</td><td><code>{abs500:.0f} sabins</code></td></tr>
  <tr><td>Mean absorption coefficient (500 Hz)</td><td><code>{alpha_mean:.3f}</code></td></tr>
  <tr><td>Program type</td><td>{prog}</td></tr>
  <tr><td>RT60 target</td><td>{tmin:.1f}&ndash;{tmax:.1f} s</td></tr>
</table>

<footer>
  Generated by AEIS RT60 Script (Revit/Dynamo) &mdash; ARC 5443 AEIS &mdash; Lawrence Technological University<br>
  Sabine: RT60 = 0.161 &times; V / A &nbsp;&nbsp; Eyring: RT60 = 0.161 &times; V / (&minus;S &times; ln(1 &minus; &alpha;&#772;))<br>
  Compare Eyring result with your hand calculation at 500 Hz. Discrepancy &gt; &plusmn;0.2 s should be explained in your submission.
  <br><br>Note: wall areas derived from room boundary segments &times; room height.
  Ceiling area equals floor area (flat ceiling). Window/door areas are not subtracted.
  For more accurate results, manually override areas in the surface_data list.
</footer>
</body>
</html>""".format(
        room=room_name,
        prog=program_type.upper().replace("_", " "),
        tmin=t_min, tmax=t_max,
        mc=mc, eyring=mid_eyring, sabine=mid_sabine, sl=sl,
        tl=tgt_left, tw=tgt_width, bp=bar_pct,
        band_rows=band_rows, mat_rows=mat_rows,
        vol=volume_m3, volft=volume_m3 * 35.3147,
        sa=total_surface, abs500=total_abs_500, alpha_mean=alpha_mean,
    )
    html = html.replace("__RAY_SECTION__", ray_section)

    try:
        with open(report_path, "w") as f:
            f.write(html)
        return True
    except Exception as e:
        return "Report save failed: {}".format(e)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN  — called by Dynamo via IN[] / OUT
# ──────────────────────────────────────────────────────────────────────────────

def run(room_element, program_type="mixed", report_path=None):
    if room_element is None:
        return "ERROR: No room element connected to IN[0]."

    # Unwrap Dynamo wrapper if present
    try:
        from Revit.Elements import Element as DynElement
        if hasattr(room_element, "InternalElement"):
            room_element = room_element.InternalElement
    except Exception:
        pass

    room_name = "Unknown Room"
    try:
        room_name = room_element.get_Parameter(
            BuiltInParameter.ROOM_NAME).AsString() or room_name
        room_number = room_element.get_Parameter(
            BuiltInParameter.ROOM_NUMBER).AsString() or ""
        if room_number:
            room_name = "{} {}".format(room_number, room_name)
    except Exception:
        pass

    volume_m3 = to_m3(room_element.Volume)
    if volume_m3 < 0.1:
        return "ERROR: Room '{}' has no computable volume. Check that the room is bounded.".format(
            room_name)

    surface_data = get_room_surfaces(room_element)
    if not surface_data:
        return "ERROR: No boundary surfaces found for room '{}'.".format(room_name)

    program_type = (program_type or "mixed").strip().lower()
    if program_type not in RT60_TARGETS:
        program_type = "mixed"

    rt60_sabine, rt60_eyring, total_surface = compute_rt60(volume_m3, surface_data)
    text_report = format_report(room_name, volume_m3, surface_data,
                                rt60_sabine, rt60_eyring, total_surface, program_type)

    # ── 2D ray trace for HTML report ─────────────────────────────────────────
    ray_svg = ""
    try:
        boundary_2d = _get_boundary_2d(room_element)
        if boundary_2d:
            # Room centroid as source
            all_x = [p[0] for seg in boundary_2d for p in seg]
            all_y = [p[1] for seg in boundary_2d for p in seg]
            source_2d = (
                (max(all_x) + min(all_x)) / 2.0,
                (max(all_y) + min(all_y)) / 2.0
            )
            mid_idx_500 = FREQ_BANDS.index(500)
            total_abs_500_rt = sum(MATERIAL_TABLE[s[2]][mid_idx_500] * s[3]
                                   for s in surface_data)
            mean_alpha_500 = total_abs_500_rt / total_surface if total_surface > 0 else 0.15
            paths_2d = _cast_rays_2d(source_2d, boundary_2d, mean_alpha_500)
            ray_svg = _rays_to_svg(paths_2d, boundary_2d, source_2d)
    except Exception:
        pass

    html_status = ""
    if report_path and str(report_path).strip().lower() not in ("none", ""):
        rp = str(report_path).strip()
        if not rp.lower().endswith(".html"):
            rp = rp + ".html"
        result = save_html_report(room_name, volume_m3, surface_data,
                                  rt60_sabine, rt60_eyring, total_surface,
                                  program_type, rp, ray_svg=ray_svg)
        if result is True:
            html_status = "\nHTML report saved: {}".format(rp)
            try:
                import subprocess, sys
                if sys.platform == "win32":
                    os.startfile(rp)
                else:
                    subprocess.Popen(["open", rp])
            except Exception:
                pass
        else:
            html_status = "\n" + str(result)

    return text_report + html_status


# ─── Dynamo entry point ───────────────────────────────────────────────────────
try:
    _room    = IN[0] if len(IN) > 0 else None
    _prog    = IN[1] if len(IN) > 1 else "mixed"
    _rpath   = IN[2] if len(IN) > 2 else None
    OUT = run(_room, _prog, _rpath)
except NameError:
    # Running outside Dynamo (e.g. pyRevit) — call run() directly
    pass

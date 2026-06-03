# -*- coding: utf-8 -*-
"""
AEIS RT60 Acoustic Analyzer for Rhino
ARC 5443 — Acoustics, Electrical & Illumination Systems
Lawrence Technological University

Usage:
  1. Layer all room surfaces with AEIS_<MATERIAL> names (see MATERIAL_TABLE below)
  2. Place a Point object on layer AEIS_SOURCE
  3. Run: _RunPythonScript and select this file
  4. The script computes RT60 per octave band and draws a ray trace

Requires: Rhino 7 or 8 (RhinoCommon + rhinoscriptsyntax)
"""

import rhinoscriptsyntax as rs
import Rhino
import Rhino.Geometry as rg
import scriptcontext as sc
import System
import math
import random
import os

# ──────────────────────────────────────────────────────────────────────────────
# MATERIAL LOOKUP TABLE
# Octave-band absorption coefficients: [125, 250, 500, 1000, 2000, 4000] Hz
# Sources: MEEB 13th ed. Table 27.1 / Knudsen & Harris / manufacturer averages
# ──────────────────────────────────────────────────────────────────────────────
MATERIAL_TABLE = {
    # ── Floors ──────────────────────────────────────────────────────────────
    "CARPET_THICK":        [0.08, 0.24, 0.57, 0.69, 0.71, 0.73],  # heavy carpet on concrete
    "CARPET_THIN":         [0.02, 0.06, 0.14, 0.37, 0.60, 0.65],  # thin carpet / felt
    "WOOD_FLOOR":          [0.15, 0.11, 0.10, 0.07, 0.06, 0.07],  # hardwood on joist
    "CONCRETE_FLOOR":      [0.01, 0.01, 0.02, 0.02, 0.02, 0.02],  # sealed concrete

    # ── Ceilings ────────────────────────────────────────────────────────────
    "GYPSUM_BOARD":        [0.29, 0.10, 0.05, 0.04, 0.07, 0.09],  # 1/2" GWB on studs
    "ACOUSTIC_TILE":       [0.25, 0.45, 0.78, 0.92, 0.89, 0.87],  # 3/4" lay-in tile
    "PLASTER_HARD":        [0.03, 0.03, 0.02, 0.03, 0.04, 0.05],  # hard plaster on lath
    "PLASTER_ACOUSTIC":    [0.08, 0.15, 0.40, 0.45, 0.40, 0.38],  # sprayed acoustic plaster
    "WOOD_PANEL":          [0.10, 0.11, 0.10, 0.08, 0.08, 0.11],  # 3/4" wood panel air gap
    "CEILING_CLOUD":       [0.10, 0.20, 0.55, 0.70, 0.65, 0.60],  # suspended reflector/absorber

    # ── Walls ───────────────────────────────────────────────────────────────
    "CONCRETE_BARE":       [0.01, 0.01, 0.02, 0.02, 0.03, 0.03],  # poured / painted concrete
    "CONCRETE_BLOCK":      [0.36, 0.44, 0.31, 0.29, 0.39, 0.25],  # unpainted CMU
    "BRICK":               [0.03, 0.03, 0.03, 0.04, 0.05, 0.07],  # unglazed brick
    "GLASS":               [0.35, 0.25, 0.18, 0.12, 0.07, 0.04],  # 1/4" plate glass
    "FABRIC_CURTAIN":      [0.07, 0.31, 0.49, 0.75, 0.70, 0.60],  # heavy draped fabric
    "GRC_CONVEX":          [0.04, 0.04, 0.05, 0.06, 0.07, 0.08],  # GRC reflector panel
    "WOOD_DIFFUSER":       [0.07, 0.12, 0.10, 0.09, 0.08, 0.10],  # QRD / wood diffuser

    # ── Seating & Audience ───────────────────────────────────────────────────
    "SEATS_UPHOLSTERED":   [0.44, 0.56, 0.67, 0.74, 0.83, 0.87],  # fully upholstered seats
    "SEATS_OCCUPIED":      [0.39, 0.57, 0.80, 0.94, 0.92, 0.87],  # occupied upholstered seats
    "SEATS_WOOD":          [0.02, 0.03, 0.03, 0.06, 0.06, 0.05],  # unupholstered wood seats

    # ── Special ─────────────────────────────────────────────────────────────
    "ACOUSTIC_PANEL":      [0.20, 0.55, 0.90, 0.95, 0.95, 0.90],  # 2" fabric-wrapped panel
    "BASS_TRAP":           [0.40, 0.80, 0.90, 0.85, 0.80, 0.75],  # corner bass absorber
    "OPEN_WINDOW":         [1.00, 1.00, 1.00, 1.00, 1.00, 1.00],  # calibration / opening
}

FREQ_BANDS = [125, 250, 500, 1000, 2000, 4000]

# ──────────────────────────────────────────────────────────────────────────────
# UNIT CONVERSION
# Sabine/Eyring constants assume SI (m3 / m2). Convert native Rhino units to
# meters so the script works in both metric and imperial files.
# ──────────────────────────────────────────────────────────────────────────────
def get_meters_per_unit():
    """Return the scale factor to convert the current Rhino unit to meters."""
    import Rhino
    us = Rhino.RhinoDoc.ActiveDoc.ModelUnitSystem
    UnitSystem = Rhino.UnitSystem
    table = {
        UnitSystem.Millimeters: 0.001,
        UnitSystem.Centimeters: 0.01,
        UnitSystem.Meters:      1.0,
        UnitSystem.Kilometers:  1000.0,
        UnitSystem.Inches:      0.0254,
        UnitSystem.Feet:        0.3048,
        UnitSystem.Yards:       0.9144,
        UnitSystem.Miles:       1609.344,
    }
    return table.get(us, 1.0)

# RT60 target ranges by program type (seconds)
RT60_TARGETS = {
    "speech":       [0.6,  1.0],
    "mixed":        [1.4,  1.8],
    "music_opera":  [1.6,  2.0],
    "music_symph":  [1.8,  2.2],
    "cinema":       [0.3,  0.5],
}

# ──────────────────────────────────────────────────────────────────────────────
# RAY TRACE SETTINGS
# ──────────────────────────────────────────────────────────────────────────────
RAY_COUNT      = 200
MAX_BOUNCES    = 8
ENERGY_CUTOFF  = 0.05
DRAW_RAYS      = True


def energy_color(e):
    e = max(0.0, min(1.0, e))
    if e > 0.75:
        r, g, b = 220, int(40 + (1-e)*4*120), 40
    elif e > 0.50:
        r, g, b = 220, int(120 + (0.75-e)*4*100), 40
    elif e > 0.25:
        r, g, b = int(40 + (0.5-e)*4*180), 140, 140
    else:
        r, g, b = 40, 80, int(140 + (0.25-e)*4*115)
    return System.Drawing.Color.FromArgb(r, g, b)


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def parse_material_from_layer(layer_name):
    upper = layer_name.upper().strip()
    if not upper.startswith("AEIS_"):
        return None
    key = upper[5:]
    if key == "SOURCE":
        return None
    if key in MATERIAL_TABLE:
        return key
    for k in MATERIAL_TABLE:
        if k in key or key in k:
            return k
    return None


def get_room_volume(all_surfaces, tolerance=0.001):
    """
    Try to join all surfaces into a closed solid and return (volume, method).
    method is 'solid' (true volume) or 'bbox' (bounding box approximation).
    Returns (None, 'failed') if geometry is unusable.
    """
    breps = []
    for obj_id in all_surfaces:
        geo = rs.coercebrep(obj_id)
        if geo is None:
            srf = rs.coercesurface(obj_id)
            if srf:
                geo = srf.ToBrep()
        if geo:
            breps.append(geo)

    if not breps:
        return None, "failed"

    # Attempt solid join
    joined = rg.Brep.JoinBreps(breps, tolerance)
    if joined and len(joined) == 1 and joined[0].IsSolid:
        vmp = rg.VolumeMassProperties.Compute(joined[0])
        if vmp and vmp.Volume > 0:
            return vmp.Volume, "solid"

    # Fall back to bounding box
    bbox = rg.BoundingBox.Empty
    for b in breps:
        bbox.Union(b.GetBoundingBox(True))
    if bbox.IsValid:
        dims = bbox.Max - bbox.Min
        return dims.X * dims.Y * dims.Z, "bbox"

    return None, "failed"


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


# ──────────────────────────────────────────────────────────────────────────────
# RAY TRACING
# ──────────────────────────────────────────────────────────────────────────────

def random_hemisphere_direction(normal):
    while True:
        dx = random.uniform(-1, 1)
        dy = random.uniform(-1, 1)
        dz = random.uniform(-1, 1)
        v = rg.Vector3d(dx, dy, dz)
        if v.Length < 0.001:
            continue
        v.Unitize()
        if v * normal >= 0:
            return v
        return rg.Vector3d(-dx, -dy, -dz)


def reflect_direction(direction, normal):
    dot = direction * normal
    return rg.Vector3d(
        direction.X - 2 * dot * normal.X,
        direction.Y - 2 * dot * normal.Y,
        direction.Z - 2 * dot * normal.Z
    )


def _brep_normal_at(brep, hit_pt, incoming_dir):
    face = brep.Faces[0]
    rc, u, v = face.ClosestPoint(hit_pt)
    if rc:
        n = face.NormalAt(u, v)
        n.Unitize()
        if n * incoming_dir > 0:
            n = rg.Vector3d(-n.X, -n.Y, -n.Z)
        return n
    return rg.Vector3d(0, 0, 1)


def cast_rays(source_pt, surface_objects, surface_alphas_1k, num_rays, max_bounces, cutoff):
    breps = []
    alphas = []
    for obj_id, alpha in zip(surface_objects, surface_alphas_1k):
        geo = rs.coercebrep(obj_id)
        if geo is None:
            srf = rs.coercesurface(obj_id)
            if srf:
                geo = srf.ToBrep()
        if geo:
            breps.append(geo)
            alphas.append(alpha)

    if not breps:
        return []

    paths = []
    src = rg.Point3d(source_pt)

    for _ in range(num_rays):
        direction = rg.Vector3d(
            random.uniform(-1, 1),
            random.uniform(-1, 1),
            random.uniform(-1, 1)
        )
        direction.Unitize()

        pts      = [src]
        energies = [1.0]
        energy   = 1.0
        current_pt  = src
        current_dir = direction

        for _bounce in range(max_bounces):
            ray = rg.Ray3d(current_pt, current_dir)

            best_dist   = float("inf")
            best_hit    = None
            best_normal = None
            best_alpha  = 0.1

            for brep, alpha in zip(breps, alphas):
                hits = rg.Intersect.Intersection.RayShoot(ray, [brep], 1)
                if not hits or len(hits) == 0:
                    continue
                hit_pt = hits[0]
                dist = current_pt.DistanceTo(hit_pt)
                if dist < 0.001:
                    continue
                if dist < best_dist:
                    best_dist   = dist
                    best_hit    = hit_pt
                    best_normal = _brep_normal_at(brep, hit_pt, current_dir)
                    best_alpha  = alpha

            if best_hit is None:
                break

            energy *= (1.0 - best_alpha)
            pts.append(best_hit)
            energies.append(energy)

            if energy < cutoff:
                break

            current_dir = reflect_direction(current_dir, best_normal)
            current_dir.Unitize()
            current_pt = best_hit

        if len(pts) > 1:
            paths.append((pts, energies))

    return paths


def draw_ray_paths(paths):
    added = []
    for pts, energies in paths:
        for i in range(len(pts) - 1):
            a = pts[i]
            b = pts[i + 1]
            line = rs.AddLine(a, b)
            if line:
                e_mid = (energies[i] + energies[i + 1]) * 0.5
                col = energy_color(e_mid)
                rs.ObjectColor(line, (col.R, col.G, col.B))
                added.append(line)
    return added


# ──────────────────────────────────────────────────────────────────────────────
# OUTPUT FORMATTING
# ──────────────────────────────────────────────────────────────────────────────

def print_rt60_table(rt60_sabine, rt60_eyring, volume, program_type="mixed"):
    target = RT60_TARGETS.get(program_type, RT60_TARGETS["mixed"])
    t_min, t_max = target

    print("\n" + "=" * 62)
    print("  AEIS RT60 ANALYSIS  .  ARC 5443")
    print("  Room volume: {:.0f} m3  ({:.0f} ft3)".format(volume, volume * 35.3147))
    print("  Program target: {}  [{:.1f}-{:.1f} s]".format(program_type.upper(), t_min, t_max))
    print("=" * 62)
    print("  {:>6}   {:>10}   {:>10}   {:>6}".format(
        "Freq", "Sabine RT60", "Eyring RT60", "Status (Eyring)"))
    print("  " + "-" * 58)

    for i, freq in enumerate(FREQ_BANDS):
        s_val = rt60_sabine[i]
        e_val = rt60_eyring[i]
        # Status based on Eyring (more accurate for rooms with alpha > 0.2)
        if t_min <= e_val <= t_max:
            status = "  OK"
        elif e_val < t_min:
            status = "  TOO DRY  <- reduce absorption or add volume"
        else:
            status = "  TOO LIVE <- add absorptive material"

        print("  {:>5} Hz  {:>8.2f} s    {:>8.2f} s    {}".format(
            freq, s_val, e_val, status))

    print("=" * 62)
    mid_idx = FREQ_BANDS.index(500)
    print("  Mid-freq Eyring (500 Hz): {:.2f} s  [primary result]".format(rt60_eyring[mid_idx]))
    print("  Mid-freq Sabine (500 Hz): {:.2f} s  [hand-calc worksheet]".format(rt60_sabine[mid_idx]))
    print("=" * 62 + "\n")


def print_material_summary(layer_data):
    print("\n  SURFACE MATERIAL SUMMARY")
    print("  " + "-" * 56)
    print("  {:30s} {:>10s}  {:>8s}".format("Layer / Material", "Area (m2)", "NRC ~"))
    print("  " + "-" * 56)
    for layer, mat, area, coeffs in layer_data:
        nrc_approx = (coeffs[2] + coeffs[3] + coeffs[4] + coeffs[5]) / 4.0
        print("  {:30s} {:>10.1f}  {:>8.2f}".format(
            "{} ({})".format(layer[5:], mat)[:30], area, nrc_approx))
    print("  " + "-" * 56 + "\n")


# ──────────────────────────────────────────────────────────────────────────────
# REPORT GENERATION
# ──────────────────────────────────────────────────────────────────────────────

def capture_viewport_to_file(save_path):
    """Capture active Rhino viewport to a PNG file."""
    try:
        view = sc.doc.Views.ActiveView
        if view:
            bmp = view.CaptureToBitmap(System.Drawing.Size(1920, 1080))
            if bmp:
                bmp.Save(save_path, System.Drawing.Imaging.ImageFormat.Png)
                return True
    except Exception as e:
        print("  Viewport capture: {}".format(e))
    return False


def save_html_report(layer_data, rt60_sabine, rt60_eyring, volume,
                     total_surface_area, program_type, report_path, img_filename=None):
    """Generate a self-contained HTML report and save to report_path."""
    target = RT60_TARGETS.get(program_type, RT60_TARGETS["mixed"])
    t_min, t_max = target
    mid_idx = FREQ_BANDS.index(500)
    mid_eyring = rt60_eyring[mid_idx]
    mid_sabine = rt60_sabine[mid_idx]

    def scolor(val):
        if t_min <= val <= t_max: return "#3a8a5a"
        if val < t_min: return "#c87030"
        return "#c8472f"

    def slabel(val):
        if t_min <= val <= t_max: return "IN RANGE"
        if val < t_min: return "TOO DRY"
        return "TOO LIVE"

    # Octave band rows
    band_rows = ""
    for i, freq in enumerate(FREQ_BANDS):
        s = rt60_sabine[i]
        e = rt60_eyring[i]
        col = scolor(e)
        lbl = slabel(e)
        in_range = t_min <= e <= t_max
        row_bg = " style=\"background:#eef6f1\"" if in_range else ""
        band_rows += (
            "<tr{}><td>{} Hz</td><td>{:.2f} s</td>"
            "<td><strong>{:.2f} s</strong></td>"
            "<td style=\"color:{};font-weight:600\">{}</td></tr>\n"
        ).format(row_bg, freq, s, e, col, lbl)

    # Material schedule rows
    mat_rows = ""
    total_abs_500 = 0.0
    for layer, mat, area, coeffs in layer_data:
        nrc = (coeffs[2] + coeffs[3] + coeffs[4] + coeffs[5]) / 4.0
        a500 = coeffs[2]
        abs_500 = area * a500
        total_abs_500 += abs_500
        mat_rows += (
            "<tr><td>{}</td><td>{}</td><td>{:.0f}</td>"
            "<td>{:.2f}</td><td>{:.2f}</td><td>{:.0f}</td></tr>\n"
        ).format(
            layer[5:],
            mat.replace("_", " ").title(),
            area, a500, nrc, abs_500
        )
    mat_rows += (
        "<tr style=\"font-weight:700;background:#e8e0d0\">"
        "<td colspan=\"2\">TOTAL</td><td>{:.0f} m²</td>"
        "<td>-</td><td>-</td><td>{:.0f} sabins</td></tr>\n"
    ).format(total_surface_area, total_abs_500)

    # RT60 position bar (0-3 s scale)
    bar_pct    = min(100, (mid_eyring / 3.0) * 100)
    tgt_left   = (t_min / 3.0) * 100
    tgt_width  = ((t_max - t_min) / 3.0) * 100
    main_color = scolor(mid_eyring)
    status_lbl = slabel(mid_eyring)

    img_tag = ""
    if img_filename:
        img_tag = "<img src=\"{}\" alt=\"Rhino viewport\" style=\"width:100%;border-radius:6px;margin:0 0 32px\">".format(img_filename)

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>RT60 Report - AEIS ARC 5443</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;600&display=swap');
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Newsreader', Georgia, serif; background: #ede4d3; color: #0e0d0b; max-width: 900px; margin: 48px auto; padding: 0 24px 64px; }}
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
  footer {{ margin-top: 40px; padding-top: 16px; border-top: 1px solid #c4b89a; font-size: 0.75rem; color: #888; font-style: italic; }}
  code {{ font-family: 'JetBrains Mono', monospace; font-size: 0.82em; background: #e0d9cc; padding: 1px 5px; border-radius: 3px; }}
</style>
</head>
<body>
<header>
  <h1>RT60 Acoustic Analysis</h1>
  <p>ARC 5443 AEIS &nbsp;&middot;&nbsp; Lawrence Technological University &nbsp;&middot;&nbsp; Program: <strong>{prog}</strong> &nbsp;&middot;&nbsp; Target: {tmin:.1f}&ndash;{tmax:.1f} s</p>
</header>

{img_tag}

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
    <div class="card-val"><span class="badge" style="background:{mc}">{status}</span></div>
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
<p style="font-size:.78rem;color:#888;margin-top:8px">Status based on Eyring RT60 vs. program target [{tmin:.1f}&ndash;{tmax:.1f} s].</p>

<h2>Material Schedule</h2>
<table>
  <tr><th>Surface</th><th>Material</th><th>Area (m&sup2;)</th><th>&alpha; 500 Hz</th><th>NRC</th><th>Absorption (sabins)</th></tr>
  {mat_rows}
</table>
<p style="font-size:.78rem;color:#888;margin-top:8px">NRC = average of &alpha; at 250, 500, 1000, 2000 Hz. Absorption sabins = area &times; &alpha; at 500 Hz.</p>

<h2>Room Parameters</h2>
<table>
  <tr><th>Parameter</th><th>Value</th></tr>
  <tr><td>Volume</td><td><code>{vol:.0f} m&sup3;</code> &nbsp;({volft:.0f} ft&sup3;)</td></tr>
  <tr><td>Total surface area</td><td><code>{sa:.0f} m&sup2;</code></td></tr>
  <tr><td>Total absorption at 500 Hz</td><td><code>{abs500:.0f} sabins</code></td></tr>
  <tr><td>Mean absorption coefficient (500 Hz)</td><td><code>{alpha_mean:.3f}</code></td></tr>
  <tr><td>Program type</td><td>{prog}</td></tr>
  <tr><td>RT60 target</td><td>{tmin:.1f}&ndash;{tmax:.1f} s</td></tr>
</table>

<footer>
  Generated by the AEIS RT60 Script &mdash; ARC 5443 AEIS &mdash; Lawrence Technological University<br>
  Sabine: RT60 = 0.161 &times; V / A &nbsp;&nbsp; Eyring: RT60 = 0.161 &times; V / (&minus;S &times; ln(1 &minus; &alpha;&#772;))<br>
  Compare Eyring result with your hand calculation at 500 Hz. Discrepancy &gt; &plusmn;0.2 s should be explained in your submission.
</footer>
</body>
</html>""".format(
        prog=program_type.upper().replace("_", " "),
        tmin=t_min, tmax=t_max,
        img_tag=img_tag,
        mc=main_color,
        eyring=mid_eyring,
        sabine=mid_sabine,
        status=status_lbl,
        tl=tgt_left, tw=tgt_width,
        bp=bar_pct,
        band_rows=band_rows,
        mat_rows=mat_rows,
        vol=volume, volft=volume * 35.3147,
        sa=total_surface_area,
        abs500=total_abs_500,
        alpha_mean=total_abs_500 / total_surface_area if total_surface_area > 0 else 0,
    )

    try:
        with open(report_path, "w") as f:
            f.write(html)
        return True
    except Exception as e:
        print("  Report save failed: {}".format(e))
        return False


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    rs.EnableRedraw(False)

    print("\n-- AEIS RT60 Analyzer starting --")

    # ── 1. Collect AEIS layers and their objects ──────────────────────────────
    all_layers = rs.LayerNames()
    aeis_layers = [l for l in all_layers if l.upper().startswith("AEIS_")
                   and "SOURCE" not in l.upper()]

    if not aeis_layers:
        rs.MessageBox(
            "No AEIS_ layers found.\n\nCreate layers named AEIS_<MATERIAL> "
            "(e.g. AEIS_CONCRETE_BARE) and assign room surfaces to them.",
            title="AEIS RT60: No Layers Found"
        )
        return

    layer_data      = []
    all_surface_ids = []
    all_alphas_1k   = []

    for layer in aeis_layers:
        mat_key = parse_material_from_layer(layer)
        if mat_key is None:
            print("  WARNING: layer '{}' not in material table -- skipping.".format(layer))
            continue

        obj_ids = rs.ObjectsByLayer(layer)
        if not obj_ids:
            continue

        coeffs = MATERIAL_TABLE[mat_key]
        total_area = 0.0
        valid_ids  = []

        for oid in obj_ids:
            geo = rs.coercegeometry(oid)
            if geo is None:
                continue
            if isinstance(geo, rg.Surface):
                geo = geo.ToBrep()
            if isinstance(geo, rg.Brep):
                amp = rg.AreaMassProperties.Compute(geo)
                if amp:
                    total_area += amp.Area
            valid_ids.append(oid)
            all_alphas_1k.append(coeffs[3])

        if total_area > 0:
            layer_data.append((layer, mat_key, total_area, coeffs))
            all_surface_ids.extend(valid_ids)
            print("  Found: {:28s} {:.1f} (native units)".format(layer, total_area))

    if not layer_data:
        rs.MessageBox("No valid surfaces found on AEIS_ layers.", title="AEIS RT60")
        return

    # ── 2. Room volume ────────────────────────────────────────────────────────
    m_per_unit = get_meters_per_unit()
    volume_native, vol_method = get_room_volume(all_surface_ids)

    if volume_native is None or volume_native < 0.001:
        # Complete failure — ask for manual entry
        rs.MessageBox(
            "VOLUME DETECTION FAILED\n\n"
            "The script could not read any geometry from the AEIS_ layers.\n"
            "Check that surfaces are assigned and visible, then re-run.",
            0 | 16,
            "AEIS RT60 — Volume Error"
        )
        return

    # Convert to meters for Sabine/Eyring (constant 0.161 is SI)
    volume_m3 = volume_native * (m_per_unit ** 3)
    volume_ft3 = volume_m3 * 35.3147

    # Build confirmation message — make the method and value impossible to miss
    if vol_method == "solid":
        method_line = (
            "METHOD:  Closed solid  (ACCURATE)\n"
            "All surfaces joined into a sealed room — this is the true volume."
        )
    else:
        method_line = (
            "METHOD:  Bounding box  (APPROXIMATE)\n"
            "Surfaces did not join into a closed solid.\n"
            "The bounding box may OVERESTIMATE volume for non-rectangular rooms\n"
            "(sloped ceilings, raked floors, fly space above the stage, etc.).\n\n"
            "To get a true volume: close any open edges in Rhino,\n"
            "make sure all room surfaces are on AEIS_ layers, and re-run."
        )

    confirm = rs.MessageBox(
        "ROOM VOLUME DETECTED\n\n"
        "{:.0f}  m\xb3      ({:.0f}  ft\xb3)\n\n"
        "{}\n\n"
        "Press YES to accept this volume and continue.\n"
        "Press NO to enter the volume manually.".format(
            volume_m3, volume_ft3, method_line
        ),
        4 | 32,
        "AEIS RT60 — Confirm Room Volume"
    )

    if confirm != 6:  # 6 = Yes
        vol_str = rs.GetString(
            "Enter room volume in m\xb3 (e.g. 8500 for a 500-seat hall):",
            "{:.0f}".format(volume_m3)
        )
        try:
            volume_m3 = float(vol_str)
            volume_ft3 = volume_m3 * 35.3147
        except Exception:
            rs.MessageBox("Invalid entry — using detected volume.", 0 | 48, "AEIS RT60")

    # Apply unit conversion to areas
    layer_data = [(lyr, mat, area * (m_per_unit ** 2), coeffs)
                  for lyr, mat, area, coeffs in layer_data]
    total_surface_area = sum(d[2] for d in layer_data)
    volume = volume_m3

    print("  Room volume: {:.0f} m3  ({:.0f} ft3)  [{}]".format(
        volume, volume_ft3, vol_method))

    # ── 3. Program type ───────────────────────────────────────────────────────
    prog_options = list(RT60_TARGETS.keys())
    prog_idx = rs.ListBox(
        prog_options,
        message="Select the room program type for RT60 target:",
        title="AEIS RT60 -- Program Type",
        default="mixed"
    )
    program_type = prog_idx if prog_idx else "mixed"

    # ── 4. Compute RT60 per octave band ───────────────────────────────────────
    rt60_sabine = []
    rt60_eyring = []

    for band_idx in range(6):
        total_absorption = sum(d[2] * d[3][band_idx] for d in layer_data)
        mean_alpha = total_absorption / total_surface_area if total_surface_area > 0 else 0

        rt60_sabine.append(sabine_rt60(volume, total_absorption))
        rt60_eyring.append(eyring_rt60(volume, total_surface_area, mean_alpha))

    # ── 5. Print results ──────────────────────────────────────────────────────
    print_material_summary(layer_data)
    print_rt60_table(rt60_sabine, rt60_eyring, volume, program_type)

    # ── 6. Ray trace visualization ────────────────────────────────────────────
    if DRAW_RAYS:
        source_objs = []
        for layer in all_layers:
            if "AEIS_SOURCE" in layer.upper():
                source_objs = rs.ObjectsByLayer(layer) or []
                break

        source_pt = None
        if source_objs:
            pt = rs.PointCoordinates(source_objs[0])
            if pt:
                source_pt = pt
                print("  Source point found on AEIS_SOURCE layer.")

        if source_pt is None:
            source_pt = rs.GetPoint("Click to place the sound source point")

        if source_pt is not None:
            print("  Casting {} rays from source...".format(RAY_COUNT))
            rs.EnableRedraw(False)

            if rs.IsLayer("AEIS_RAYS"):
                old = rs.ObjectsByLayer("AEIS_RAYS")
                if old:
                    rs.DeleteObjects(old)
            else:
                rs.AddLayer("AEIS_RAYS", color=(80, 80, 80))

            paths = cast_rays(
                source_pt,
                all_surface_ids,
                all_alphas_1k,
                RAY_COUNT,
                MAX_BOUNCES,
                ENERGY_CUTOFF
            )

            ray_objects = draw_ray_paths(paths)
            if ray_objects:
                rs.ObjectLayer(ray_objects, "AEIS_RAYS")

            print("  Drew {} ray segments on layer AEIS_RAYS.".format(len(ray_objects)))
            print("  Colors: RED = high energy  ->  BLUE = near absorbed")
            rs.EnableRedraw(True)
            sc.doc.Views.Redraw()
        else:
            print("  No source point -- ray trace skipped.")
    else:
        rs.EnableRedraw(True)

    # ── 7. Summary dialog (Eyring as primary) ─────────────────────────────────
    target    = RT60_TARGETS.get(program_type, [1.4, 1.8])
    mid_idx   = FREQ_BANDS.index(500)
    mid_eyring = rt60_eyring[mid_idx]
    mid_sabine = rt60_sabine[mid_idx]
    status_str = "IN RANGE" if target[0] <= mid_eyring <= target[1] else "OUT OF RANGE"

    rs.MessageBox(
        "RT60 at 500 Hz (Eyring):  {:.2f} s\n"
        "Program target [{:.1f}-{:.1f} s]:  {}\n\n"
        "Sabine RT60 at 500 Hz:  {:.2f} s  (hand-calc reference)\n"
        "Room volume:  {:.0f} m\xb3  ({:.0f} ft\xb3)  [{}]\n"
        "Total surface area:  {:.0f} m\xb2\n\n"
        "See Rhino command line for full octave-band table.\n"
        "Ray trace drawn on layer AEIS_RAYS.".format(
            mid_eyring,
            target[0], target[1], status_str,
            mid_sabine,
            volume, volume_ft3, vol_method,
            total_surface_area
        ),
        title="AEIS RT60 Results -- 500 Hz"
    )

    # ── 8. Save HTML report (optional) ────────────────────────────────────────
    save_choice = rs.MessageBox(
        "Save HTML report with viewport screenshot?",
        4 | 32,
        "AEIS RT60 -- Save Report"
    )

    if save_choice == 6:  # Yes
        report_path = rs.SaveFileName(
            "Save RT60 Report",
            "HTML Files (*.html)|*.html||",
            "",
            "rt60_report",
            "html"
        )
        if report_path:
            img_filename = None
            img_path = report_path.replace(".html", "_viewport.png")
            if capture_viewport_to_file(img_path):
                img_filename = os.path.basename(img_path)
                print("  Viewport saved: {}".format(img_path))
            else:
                print("  Viewport capture skipped.")

            if save_html_report(layer_data, rt60_sabine, rt60_eyring, volume,
                                total_surface_area, program_type,
                                report_path, img_filename):
                print("  Report saved: {}".format(report_path))
                # Open in default browser
                import subprocess
                try:
                    if os.name == "nt":
                        os.startfile(report_path)
                    else:
                        subprocess.Popen(["open", report_path])
                except Exception:
                    pass
                rs.MessageBox(
                    "Report saved:\n{}".format(report_path),
                    title="AEIS RT60 -- Report Saved"
                )

    print("-- AEIS RT60 Analyzer complete --\n")


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()

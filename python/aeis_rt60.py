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

# RT60 target ranges by program type (seconds)
# Format: [min, max]
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
RAY_COUNT      = 200   # number of rays to cast
MAX_BOUNCES    = 8     # max reflections per ray
ENERGY_CUTOFF  = 0.05  # stop tracing when energy falls below 5%
DRAW_RAYS      = True  # set False to skip visualization (faster)

# Energy → color mapping (red = full → blue = near dead)
def energy_color(e):
    e = max(0.0, min(1.0, e))
    if e > 0.75:
        r, g, b = 220, int(40 + (1-e)*4*120), 40        # red
    elif e > 0.50:
        r, g, b = 220, int(120 + (0.75-e)*4*100), 40    # orange
    elif e > 0.25:
        r, g, b = int(40 + (0.5-e)*4*180), 140, 140     # teal
    else:
        r, g, b = 40, 80, int(140 + (0.25-e)*4*115)     # blue
    return System.Drawing.Color.FromArgb(r, g, b)


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def parse_material_from_layer(layer_name):
    """
    Layer names follow convention: AEIS_<MATERIAL_KEY>
    e.g. AEIS_CONCRETE_BARE → CONCRETE_BARE
    Returns the key string or None if not found in table.
    """
    upper = layer_name.upper().strip()
    if not upper.startswith("AEIS_"):
        return None
    key = upper[5:]  # strip AEIS_ prefix
    if key == "SOURCE":
        return None
    if key in MATERIAL_TABLE:
        return key
    # fuzzy: check if any table key is a substring
    for k in MATERIAL_TABLE:
        if k in key or key in k:
            return k
    return None


def get_room_volume(all_surfaces):
    """
    Approximate room volume from bounding box of all geometry.
    For a convex room (box) this is exact; for complex rooms it overestimates.
    Falls back to bounding box if JoinBreps fails.
    """
    bbox = rg.BoundingBox.Empty
    for obj_id in all_surfaces:
        geo = rs.coercegeometry(obj_id)
        if geo:
            bbox.Union(geo.GetBoundingBox(True))
    if not bbox.IsValid:
        return None
    dims = bbox.Max - bbox.Min
    return dims.X * dims.Y * dims.Z


def sabine_rt60(volume_m3, total_absorption_m2):
    """Classic Sabine equation. Returns RT60 in seconds."""
    if total_absorption_m2 < 0.001:
        return float("inf")
    return 0.161 * volume_m3 / total_absorption_m2


def eyring_rt60(volume_m3, total_surface_m2, mean_absorption):
    """
    Eyring-Norris equation — more accurate when mean absorption > 0.2.
    RT60 = 0.161 * V / (-S * ln(1 - mean_alpha))
    """
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
    """Random direction in the hemisphere oriented toward +normal."""
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
    """Reflect a direction vector off a surface with the given normal."""
    dot = direction * normal
    return rg.Vector3d(
        direction.X - 2 * dot * normal.X,
        direction.Y - 2 * dot * normal.Y,
        direction.Z - 2 * dot * normal.Z
    )


def _brep_normal_at(brep, hit_pt, incoming_dir):
    """
    Return the surface normal of a brep at hit_pt, flipped so it faces the
    incoming ray direction (i.e. normal · incoming < 0 after flip).
    Falls back to +Z if ClosestPoint fails.
    """
    face = brep.Faces[0]
    rc, u, v = face.ClosestPoint(hit_pt)
    if rc:
        n = face.NormalAt(u, v)
        n.Unitize()
        # Flip if pointing same direction as incoming ray
        if n * incoming_dir > 0:
            n = rg.Vector3d(-n.X, -n.Y, -n.Z)
        return n
    return rg.Vector3d(0, 0, 1)


def cast_rays(source_pt, surface_objects, surface_alphas_1k, num_rays, max_bounces, cutoff):
    """
    Cast rays from source_pt, bounce off surfaces, record paths.
    surface_alphas_1k: absorption at 1 kHz (mid-frequency proxy for energy decay).
    Returns list of (path_points, energy_at_each_point).
    """
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
                # RayShoot returns Point3d[] of hit points in order along ray
                hits = rg.Intersect.Intersection.RayShoot(ray, [brep], 1)
                if not hits or len(hits) == 0:
                    continue
                hit_pt = hits[0]
                dist = current_pt.DistanceTo(hit_pt)
                if dist < 0.001:        # skip self-intersection
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
    """Draw ray paths as colored lines in the current Rhino viewport."""
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
    print("  AEIS RT60 ANALYSIS  ·  ARC 5443")
    print("  Room volume: {:.0f} m³  ({:.0f} ft³)".format(volume, volume * 35.3147))
    print("  Program target: {}  [{:.1f}–{:.1f} s]".format(program_type.upper(), t_min, t_max))
    print("=" * 62)
    print("  {:>6}   {:>10}   {:>10}   {:>6}".format(
        "Freq", "Sabine RT60", "Eyring RT60", "Status"))
    print("  " + "-" * 58)

    for i, freq in enumerate(FREQ_BANDS):
        s_val = rt60_sabine[i]
        e_val = rt60_eyring[i]
        if t_min <= s_val <= t_max:
            status = "  OK"
        elif s_val < t_min:
            status = "  TOO DRY  ← reduce absorption or add volume"
        else:
            status = "  TOO LIVE ← add absorptive material"

        print("  {:>5} Hz  {:>8.2f} s    {:>8.2f} s    {}".format(
            freq, s_val, e_val, status))

    print("=" * 62)
    mid_idx = FREQ_BANDS.index(500)
    print("  Mid-freq RT60 (500 Hz, Sabine): {:.2f} s".format(rt60_sabine[mid_idx]))
    print("  Use 500 Hz Sabine as your hand-calc worksheet value.")
    print("=" * 62 + "\n")


def print_material_summary(layer_data):
    print("\n  SURFACE MATERIAL SUMMARY")
    print("  " + "-" * 56)
    print("  {:30s} {:>10s}  {:>8s}".format("Layer / Material", "Area (m²)", "NRC ~"))
    print("  " + "-" * 56)
    for layer, mat, area, coeffs in layer_data:
        nrc_approx = (coeffs[2] + coeffs[3] + coeffs[4] + coeffs[5]) / 4.0
        print("  {:30s} {:>10.1f}  {:>8.2f}".format(
            "{} ({})".format(layer[5:], mat)[:30], area, nrc_approx))
    print("  " + "-" * 56 + "\n")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    rs.EnableRedraw(False)

    print("\n── AEIS RT60 Analyzer starting ──")

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

    layer_data     = []   # (layer_name, mat_key, area_m2, coeffs)
    all_surface_ids = []
    all_alphas_1k   = []

    for layer in aeis_layers:
        mat_key = parse_material_from_layer(layer)
        if mat_key is None:
            print("  WARNING: layer '{}' not in material table — skipping.".format(layer))
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
            # Compute true surface area via AreaMassProperties
            if isinstance(geo, rg.Surface):
                geo = geo.ToBrep()
            if isinstance(geo, rg.Brep):
                amp = rg.AreaMassProperties.Compute(geo)
                if amp:
                    total_area += amp.Area
            valid_ids.append(oid)
            all_alphas_1k.append(coeffs[3])  # 1 kHz index

        if total_area > 0:
            layer_data.append((layer, mat_key, total_area, coeffs))
            all_surface_ids.extend(valid_ids)
            print("  Found: {:28s} {:.1f} m²".format(layer, total_area))

    if not layer_data:
        rs.MessageBox("No valid surfaces found on AEIS_ layers.", title="AEIS RT60")
        return

    # ── 2. Room volume ────────────────────────────────────────────────────────
    volume = get_room_volume(all_surface_ids)
    if volume is None or volume < 1.0:
        vol_str = rs.GetString(
            "Could not auto-detect volume. Enter room volume in cubic meters",
            "12000"
        )
        try:
            volume = float(vol_str)
        except Exception:
            volume = 12000.0
    print("  Room volume: {:.0f} m³".format(volume))

    # ── 3. Program type ───────────────────────────────────────────────────────
    prog_options = list(RT60_TARGETS.keys())
    prog_idx = rs.ListBox(
        prog_options,
        message="Select the room program type for RT60 target:",
        title="AEIS RT60 — Program Type",
        default="mixed"
    )
    program_type = prog_idx if prog_idx else "mixed"

    # ── 4. Compute RT60 per octave band ───────────────────────────────────────
    rt60_sabine = []
    rt60_eyring = []

    total_surface_area = sum(d[2] for d in layer_data)

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
        # Find source point
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

            # Remove previous ray objects (on layer AEIS_RAYS if it exists)
            if rs.IsLayer("AEIS_RAYS"):
                old = rs.ObjectsByLayer("AEIS_RAYS")
                if old:
                    rs.DeleteObjects(old)
            else:
                rs.AddLayer("AEIS_RAYS", color=(80, 80, 80))

            # Use mid-freq absorption for ray energy decay
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
            print("  Colors: RED = high energy  →  BLUE = near absorbed")
            rs.EnableRedraw(True)
            sc.doc.Views.Redraw()
        else:
            print("  No source point — ray trace skipped.")
    else:
        rs.EnableRedraw(True)

    # ── 7. Summary dialog ─────────────────────────────────────────────────────
    target = RT60_TARGETS.get(program_type, [1.4, 1.8])
    mid_rt60 = rt60_sabine[2]  # 500 Hz
    status_str = "IN RANGE" if target[0] <= mid_rt60 <= target[1] else "OUT OF RANGE"

    rs.MessageBox(
        "RT60 at 500 Hz (Sabine):  {:.2f} s\n"
        "Program target [{:.1f}–{:.1f} s]:  {}\n\n"
        "Eyring RT60 at 500 Hz:  {:.2f} s\n"
        "Room volume:  {:.0f} m³  ({:.0f} ft³)\n"
        "Total surface area:  {:.0f} m²\n\n"
        "See Rhino command line for full octave-band table.\n"
        "Ray trace drawn on layer AEIS_RAYS.".format(
            mid_rt60,
            target[0], target[1], status_str,
            rt60_eyring[2],
            volume, volume * 35.3147,
            total_surface_area
        ),
        title="AEIS RT60 Results — 500 Hz"
    )

    print("── AEIS RT60 Analyzer complete ──\n")


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()

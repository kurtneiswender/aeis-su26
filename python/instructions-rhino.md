# RT60 Acoustic Analysis — Rhino Instructions
ARC 5443 AEIS · Lawrence Technological University

---

## Before You Begin

- You need Rhino 7 or 8 with the Python scripting engine enabled
- Download `aeis_rt60_rhino.py` from the course site
- Have your room model open with all surfaces visible

---

## Step 1 — Set Up Your Layers

Create one layer per material type using this naming convention:

```
AEIS_<MATERIAL>
```

Examples: `AEIS_GYPSUM_BOARD`, `AEIS_CARPET_THICK`, `AEIS_CONCRETE_BARE`, `AEIS_SEATS_OCCUPIED`

The full list of valid material names is in the script's `MATERIAL_TABLE` section and on the Week 2 course page.

**Rules:**
- Layer names must start with `AEIS_` (uppercase)
- Every room surface must be on one of these layers
- Do not leave room surfaces on the default layer

---

## Step 2 — Assign Surfaces to Layers

Move each wall, floor, ceiling, and seating surface to the appropriate `AEIS_` layer based on its finish material.

- A surface can only be on one layer, so choose the dominant finish
- Openings (doors, windows) are typically ignored unless they are significant glazed areas (`AEIS_GLASS`)
- Seating areas should use `AEIS_SEATS_OCCUPIED` or `AEIS_SEATS_UPHOLSTERED`

---

## Step 3 — Place a Source Point (Optional)

Create a Point object and place it on a layer named `AEIS_SOURCE`. This is the sound source location for the ray trace visualization.

If you skip this step, the script will ask you to click a location when it runs.

---

## Step 4 — Run the Script

1. In Rhino, go to **Tools → Python Script → Run**
2. Navigate to and select `aeis_rt60_rhino.py`
3. The script will begin collecting geometry from your AEIS_ layers

---

## Step 5 — Confirm the Room Volume

A dialog will appear showing the detected volume and the method used:

- **Closed solid (ACCURATE)** — your surfaces formed a sealed room; accept this value
- **Bounding box (APPROXIMATE)** — surfaces have gaps; the volume may be overestimated

If the volume looks wrong, click **No** and enter your room volume manually in cubic meters.

> To convert: cubic feet ÷ 35.315 = cubic meters

---

## Step 6 — Select Program Type

Choose the program type that matches your room's intended use:

| Option | Target RT60 |
|---|---|
| speech | 0.6 – 1.0 s |
| mixed | 1.4 – 1.8 s |
| music_opera | 1.6 – 2.0 s |
| music_symph | 1.8 – 2.2 s |
| cinema | 0.3 – 0.5 s |

---

## Step 7 — Review Results

The script outputs results in two places:

**Rhino command line** — full octave band table (125 Hz through 4000 Hz) with Sabine and Eyring RT60 values and status for each band

**Results dialog** — summary showing RT60 at 500 Hz, room volume, and total surface area

**Use the Eyring RT60 at 500 Hz as your primary result.** The Sabine value is provided for comparison with your hand calculation worksheet.

---

## Step 8 — Save the HTML Report

When prompted, click **Yes** to save an HTML report. Choose a save location on your desktop or project folder.

The report includes:
- 500 Hz summary with status badge
- Full octave band table
- Material schedule with areas and absorption coefficients
- A screenshot of your Rhino viewport

Submit the HTML file with your assignment.

---

## Troubleshooting

**Volume is much larger than expected**
Your surfaces likely have gaps and the script is using the bounding box method. Override the volume manually in Step 5 using your known room volume.

**"No AEIS_ layers found"**
Check that your layer names start with `AEIS_` in uppercase and that objects are assigned to those layers.

**A layer is skipped with a warning**
The material name after `AEIS_` does not match the table. Check spelling against the material list on the course page.

**RT60 is far from your hand calc**
First verify the volume is correct (Step 5). If the volume matches but RT60 differs, check that your surface areas and material assignments are consistent with your hand calc worksheet.

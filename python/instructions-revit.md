# RT60 Acoustic Analysis — Revit / Dynamo Instructions
ARC 5443 AEIS · Lawrence Technological University

---

## Before You Begin

- You need Revit 2021 or later with Dynamo installed
- Download `aeis_rt60_revit_dynamo.dyn` and `aeis_rt60_revit.py` from the course site
- Your Revit model must have at least one **Room** defined and bounded

---

## Step 1 — Verify Your Room is Properly Defined

In Revit, rooms must be bounded and have a computable volume before the script can run.

1. Open a floor plan view
2. Place a Room if you have not already (Architecture tab → Room)
3. Check that walls, floors, and a ceiling close the room on all sides
4. In the Properties panel, confirm that **Volume** shows a value (not blank)

If Volume is blank, the room is not fully enclosed. Close any gaps in the boundary before continuing.

---

## Step 2 — Open Dynamo

Go to **Manage tab → Dynamo** (or Dynamo Player).

**Option A — Use the pre-built graph (recommended):**
Open `aeis_rt60_revit_dynamo.dyn` directly in Dynamo. The Python node is already wired — skip to Step 4 to connect your inputs.

**Option B — Build it manually:**
Create a new empty graph and continue to Step 3.

---

## Step 3 — Create a Python Script Node (Option B only)

Right-click on the canvas and choose **Script → Python Script**.

In the node editor that opens, **select all existing code and delete it**, then paste the entire contents of `aeis_rt60_revit.py` into the editor.

**Important — set the Python engine:**
- Right-click the Python node → Engine → select **CPython 3** if available
- If only IronPython 2 is shown, use that — the script supports both, but CPython 3 is preferred

---

## Step 4 — Wire the Inputs

The Python node has three inputs (IN[0], IN[1], IN[2]).

| Input | What to connect | Example |
|---|---|---|
| IN[0] | A single Room element | All Elements of Category (Rooms) → List.GetItemAtIndex → index 0 |
| IN[1] | A String node with the program type | `"mixed"` |
| IN[2] | A File Path string for the HTML report (optional) | `"C:/Users/you/Desktop/rt60_report.html"` |

**Valid program type strings:**

| String | Target RT60 |
|---|---|
| `"speech"` | 0.6 – 1.0 s |
| `"mixed"` | 1.4 – 1.8 s |
| `"music_opera"` | 1.6 – 2.0 s |
| `"music_symph"` | 1.8 – 2.2 s |
| `"cinema"` | 0.3 – 0.5 s |

Leave IN[2] unconnected if you do not want an HTML file saved.

---

## Step 5 — How the Script Reads Materials

The script reads material assignments from your Revit **element type names** — you do not assign layers like in Rhino. It matches type names against a built-in lookup table using keyword rules.

Examples of what it recognizes automatically:

| If your type name contains… | Script assigns… |
|---|---|
| "gypsum", "drywall", "GWB" | Gypsum board |
| "carpet" | Thick carpet |
| "acoustic tile", "lay-in", "layin" | Acoustic ceiling tile |
| "CMU", "masonry", "block" | Concrete block |
| "curtain wall", "glazing", "glass" | Glass |
| "concrete" | Bare concrete |

If no keyword matches, the script uses a default: gypsum board for walls, concrete for floors, acoustic tile for ceilings.

To override a default, rename your Revit type to include one of the keywords above, or edit the `MATERIAL_MAP` section in the script directly.

---

## Step 6 — Run the Graph

Click **Run** in Dynamo.

Connect a **Watch node** to the Python node's output (OUT) to see the results in the Dynamo canvas.

---

## Step 7 — Review Results

The Watch node output is a text report containing:

- Full octave band table (125 Hz through 4000 Hz)
- Sabine and Eyring RT60 for each band, with status
- Surface material summary with areas and absorption

**Use the Eyring RT60 at 500 Hz as your primary result.** The Sabine value is for comparison with your hand calculation worksheet.

---

## Step 8 — HTML Report (Optional)

If you connected a file path to IN[2], the script saves an HTML report to that location and attempts to open it in your default browser automatically.

The report includes:
- 500 Hz summary with status badge
- Full octave band table
- Material schedule with Revit type names, material keys, areas, and absorption
- Room parameters (volume, surface area, mean absorption coefficient)

Submit the HTML file with your assignment.

---

## Troubleshooting

**Error at line 47 in the Python node**
The script cannot import a Revit API class in your version of Revit or Python engine. Switch the Python node engine to **CPython 3** (right-click the node → Engine). If that option is not available, your Dynamo version may be too old — check the Week 2 compatibility table on the course page.

**"Room has no computable volume"**
The room is not fully enclosed in Revit. Go back to Step 1 and verify the room boundary is closed and the Volume parameter has a value.

**"No boundary surfaces found"**
The room exists but has no wall or floor elements in its boundary. This can happen if the room is bounded by room separation lines rather than actual walls. Replace separation lines with wall elements where possible, or the surface data will be estimated from defaults only.

**Materials all show as defaults**
Your Revit type names do not contain any of the recognized keywords. Rename your wall/floor/ceiling types to include a keyword (e.g. rename "Basic Wall - 6" to "Basic Wall - GWB 6") or edit `MATERIAL_MAP` at the top of the script.

**RT60 is far from your hand calc**
Check that the room volume shown in the report matches your expected volume. If the volume is correct but RT60 differs, compare the material schedule in the report against your hand calc worksheet — the most likely cause is a material mismatch on a large surface.

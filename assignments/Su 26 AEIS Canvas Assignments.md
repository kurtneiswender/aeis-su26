# ARC 5443 — Canvas Assignment Shells
## Summer 2026 · Kurt Neiswender, AIA

Copy each block below directly into Canvas's assignment text editor.
Each block is one Canvas assignment. The line after the title gives you the
Canvas settings to configure (points, submission type, availability dates).

---

## UNIVERSAL WEEKLY RUBRIC — 10 Points
### Apply to all six weekly deliverables (Weeks 1, 2, 4, 6, 7, 9)

**How to add this to Canvas:**
Assignments → open the weekly assignment → Rubric → Add Rubric → create new.
Enter the two criteria below. Set "Use this rubric for assignment grading" on.
The rubric stays attached to each weekly assignment — build it once on Week 1,
then find it by name ("Weekly Deliverable") when adding it to subsequent weeks.

---

### Criterion 1 — Deliverable Package · 6 points

| Rating | Pts | Description |
|---|---|---|
| Complete & Engaged | 6 | All required components submitted. Technical output (model, screenshots, calculations, or analysis) demonstrates genuine effort and responds to the week's specific task. Work is legible and organized. |
| Complete, Thin | 4–5 | All components present but one or more show minimal effort — screenshots unlabeled, calculations incomplete, or analysis copied from the tutorial without application to the student's own room. |
| Incomplete | 2–3 | One required component missing, or the submitted work does not address the week's specific task (e.g., Week 2 script output absent, Week 4 daylighting analysis missing). |
| Minimal | 1 | Multiple components missing or work is placeholder quality (blank layers, no annotations, generic model with no student decisions visible). |
| Not submitted | 0 | Nothing submitted by the 48-hour grace period deadline. |

---

### Criterion 2 — Decision Log · 4 points

| Rating | Pts | Description |
|---|---|---|
| Connected & Specific | 4 | Required entries written and directly connected to this week's analysis. At least one entry references a specific number, calculation result, or published criterion from the week's work (e.g., "revised rear wall material after RT60 came in at 2.4 s, above my 1.6–1.8 s target"). Trade-off field completed. |
| Present, Descriptive | 2–3 | Entries written but reasoning is descriptive rather than analytical — documents *what* was done without explaining *why* or connecting to a calculation or criterion. Trade-off field thin or blank. |
| Absent or Disconnected | 1 | Entries missing, or entries present but show no connection to this week's technical work. |
| Not submitted | 0 | No Decision Log entries for the week, or Google Doc link not accessible. |

---

**Grading note:** A student who scores 6 + 4 = 10 has submitted everything and made their reasoning visible. A student who submits everything but writes no Decision Log can score at most 6/10. The log is not optional — it is half the grade on every weekly.

---
---

---
---

## UNGRADED — Decision Log Link

**Canvas settings:** Points: 0 · Submission: Text Entry · Available: Week 1

---

Share the link to your Google Doc Decision Log here. Make sure sharing is set to **"Anyone with the link can view"** — the instructor needs ongoing view access throughout the term.

**How to submit:**
1. Open your Decision Log Google Doc.
2. Click Share → Change to "Anyone with the link" → Viewer.
3. Copy the link and paste it into the text entry box below.

You only need to submit this once. If you make a new copy or move the doc, re-submit the updated link.

The instructor will check your live doc before each Act Review. The Canvas text submissions at Act close are timestamped snapshots for grading — the Google Doc is the primary working record.

---
---

## Week 1 Deliverable — Hall Volume & Program Declaration

**Canvas settings:** Points: 10 · Submission: File Upload + Text Entry · Due: Tue 05·26 · 11:59 PM

---

Your hall exists — on paper, in Rhino, and in your head. This deliverable captures your first committed geometry and starts your acoustic reasoning record.

**Submit three items:**

**1 — Rhino Model File (.3dm)**
Your hall volume with AEIS_ layers assigned to all room surfaces and an AEIS_SOURCE point placed at stage center (approximately 5 ft above floor level). Minimum four surface types: floor, walls, ceiling, and seating. The Week 2 RT60 script will run directly on this file.

**2 — Two Rhino Screenshots**
One plan view and one section view. The Rhino layer panel must be visible in at least one screenshot so material assignments are legible. Annotate (in Rhino or in a PDF overlay): seat count, stage dimensions, and ceiling height.

**3 — Program Declaration (150–200 words, paste into the text entry box)**
Write a short declaration covering:
- Your geometry type (shoebox, fan, vineyard, or horseshoe) and one acoustic reason you chose it
- Program: speech-primary, music-primary, or mixed
- NC target for the main hall and a different NC target for the prefunction lobby
- One acoustic trade-off you have already accepted (a consequence of your geometry or material choices)
- Your RT60 target range (e.g., "1.4–1.8 s for mixed program") — we will calculate whether your volume supports this in Week 2

**4 — Decision Log Entry 1**
Written in your Google Doc before submission. Entry 1 should document your geometry choice and the reasoning behind it. Gut response to the precedents counts here — but say *why*, not just *what*.

---

**Late work:** 48-hour grace period at no penalty. Beyond 48 hours: –20% per week. Work more than two weeks late will not be accepted without prior instructor approval.

---
---

## Week 2 Deliverable — RT60 Calculation & Script Output

**Canvas settings:** Points: 10 · Submission: File Upload + Text Entry · Due: Tue 06·03 · 11:59 PM

---

This week you run the numbers. By the end of this deliverable, your hall has a calculated RT60 and you know whether you need more absorption, less, or whether you landed in range on the first try.

**Submit four items:**

**1 — Updated Rhino Model (.3dm)**
Surfaces refined based on RT60 results. Layer assignments should be final or near-final for Act I close.

**2 — RT60 Hand Calculation Worksheet (PDF or scanned pages)**
Sabine and Eyring equations at 500 Hz, 1 kHz, and 2 kHz. Show all work:
- Room volume (V) and total surface area (S)
- A table listing each surface, its area (ft²), and its absorption coefficient at each octave band
- Total absorption (A) and mean absorption coefficient (ᾱ) per band
- RT60 from both Sabine and Eyring
- Your target RT60 at the top of the page, with the source citation (MEEB table number or published range)
- A note on which method is more conservative for your room and why

**3 — RT60 Script HTML Report**
The HTML file generated by aeis_rt60.py, plus at least one viewport screenshot showing the ray paths (layer AEIS_RAYS visible, energy-colored lines). If the script errored, include a screenshot of the error and a note on what you tried.

**4 — Comparison Note (paste into text entry, 3–5 sentences)**
Does your hand-calculation Eyring result agree with the script's Eyring output within ±0.2 s? If yes, note it. If no, identify the most likely source of the discrepancy (volume difference, material assignment mismatch, audience area not modeled, etc.). A clear explanation of a discrepancy satisfies the rubric as fully as a match.

**Decision Log Entry 2** must address a material or geometry change made in response to your RT60 result. If you hit target on the first run, note that and describe why your first choice worked.

---
---

## Act I Review — The Hall, Heard

**Canvas settings:** Points: 20 · Submission: File Upload + Text Entry · Due: Tue 06·10 · 11:59 PM

---

Act I closes with a two-part submission: a PDF package and a pasted Decision Log text entry. Both parts are required. A missing Decision Log text entry will score zero on Criterion 5 regardless of the quality of the PDF.

The full assignment brief, rubric, and submission instructions are in the **Act I Assignment document** posted in this module. Read it before you submit.

**Part 1 — PDF Package (file upload)**
Export everything into a single PDF. All items must be present:
- Acoustic plan and section (minimum 1/8" = 1' scale)
- RT60 worksheet (Sabine + Eyring, minimum 500 Hz, 1 kHz, 2 kHz)
- RT60 script HTML report + viewport screenshot showing ray paths
- Material schedule (minimum five distinct assemblies with NRC values cited)
- STC wall assembly for your critical partition
- Act I review slides from the Week 3 in-class pin-up (6–8 slides)

**Part 2 — Decision Log Text Paste (text entry)**
In the text entry box below the file upload, paste the full text of your Decision Log entries from Weeks 1–3. Do not summarize or edit — paste as written. Separate entries with a blank line.

**Rubric (20 points total — see Act I Assignment document for full criteria):**
- Criterion 1: Acoustic Geometry — 4 pts
- Criterion 2: Quantitative Analysis (RT60) — 4 pts
- Criterion 3: Material Strategy (NRC) — 4 pts
- Criterion 4: Noise Isolation (STC) — 4 pts
- Criterion 5: Decision Log Quality — 4 pts

NAAB alignment: SC.4B (primary) · SC.4E (secondary)

---
---

## Week 4 Deliverable — Daylighting Strategy

**Canvas settings:** Points: 10 · Submission: File Upload + Text Entry · Due: Tue 06·17 · 11:59 PM

---

[CONTENT TBD — Act II / Daylighting. Update this block when Week 4 materials are finalized.]

Act II begins. This week you commit to a daylighting strategy for the hall: aperture type, orientation, and shading approach. Deliverable details will be posted in the Week 4 module before class.

**Placeholder checklist (update before posting):**
- [ ] Daylighting analysis output
- [ ] Aperture strategy diagram
- [ ] Decision Log entries for Week 4

---
---

## Act II Review — The Hall, Lit by Day

**Canvas settings:** Points: 20 · Submission: File Upload + Text Entry · Due: Tue 06·24 · 11:59 PM

---

[CONTENT TBD — Act II / Daylighting. Update this block when the Act II assignment and rubric are finalized.]

Act II closes with a daylighting package. Full brief, rubric, and submission instructions will be posted in the Act II Assignment document in this module.

**Placeholder checklist (update before posting):**
- [ ] Act II Assignment HTML built and posted
- [ ] Act II Rubric posted
- [ ] Submission instructions added here

---
---

## Week 6 Deliverable — Lighting & Electrical: Luminaire Selection

**Canvas settings:** Points: 10 · Submission: File Upload + Text Entry · Due: Tue 07·01 · 11:59 PM

---

[CONTENT TBD — Act III / Lighting + Electrical. Update when Week 6 materials are finalized.]

Act III begins. This week you select and justify luminaires for the main house and stage. Deliverable details will be posted in the Week 6 module before class.

**Placeholder checklist (update before posting):**
- [ ] Luminaire specification requirements
- [ ] IES file and photometric data
- [ ] Decision Log entries for Week 6

---
---

## Week 7 Deliverable — Electrical Distribution & Load Calculation

**Canvas settings:** Points: 10 · Submission: File Upload + Text Entry · Due: Tue 07·08 · 11:59 PM

---

[CONTENT TBD — Act III / Electrical. Update when Week 7 materials are finalized.]

This week you build the load summary and begin panel schedule layout. Deliverable details will be posted in the Week 7 module before class.

**Placeholder checklist (update before posting):**
- [ ] Load calculation table requirements
- [ ] Panel schedule format
- [ ] Decision Log entries for Week 7

---
---

## Act III Review — The Hall, Powered & Illuminated

**Canvas settings:** Points: 20 · Submission: File Upload + Text Entry · Due: Tue 07·15 · 11:59 PM

---

[CONTENT TBD — Act III / Lighting + Electrical. Update when the Act III assignment and rubric are finalized.]

Act III closes with a lighting and electrical package. Full brief, rubric, and submission instructions will be posted in the Act III Assignment document in this module.

**Placeholder checklist (update before posting):**
- [ ] Act III Assignment HTML built and posted
- [ ] Act III Rubric posted
- [ ] Submission instructions added here

---
---

## Week 9 Deliverable — Integration Study

**Canvas settings:** Points: 10 · Submission: File Upload + Text Entry · Due: Tue 07·22 · 11:59 PM

---

[CONTENT TBD — Integration week. Update when Week 9 materials are finalized.]

This week you examine where your three systems interact — where acoustic decisions constrained daylighting, where lighting layout affected electrical distribution, where geometry served (or conflicted with) multiple systems simultaneously.

**Placeholder checklist (update before posting):**
- [ ] Integration diagram or annotated plan
- [ ] Cross-system conflict/resolution table
- [ ] Decision Log entries 18–20

---
---

## Encore — The Full Hall

**Canvas settings:** Points: 60 · Submission: File Upload + Text Entry · Due: Tue 07·28 · 11:59 PM

---

[CONTENT TBD — Encore / Final. Update when Week 10 materials and final rubric are finalized.]

The Encore brings all three acts together into a single submission package. Full brief and rubric will be posted in the Week 10 module.

**Placeholder checklist (update before posting):**
- [ ] Encore assignment document built
- [ ] Final rubric posted (60 pts total)
- [ ] Submission instructions added here

---

## Build Status

| Assignment | Status | Points | Due |
|---|---|---|---|
| Decision Log Link | ✅ Ready to post | 0 (ungraded) | Week 1 tonight |
| Week 1 Deliverable | ✅ Ready to post | 10 | Tue 05·26 |
| Week 2 Deliverable | ✅ Ready to post | 10 | Tue 06·03 |
| Act I Review | ✅ Ready to post — assignment + rubric attached | 20 | Tue 06·10 |
| Week 4 Deliverable | 🔲 TBD | 10 | Tue 06·17 |
| Act II Review | 🔲 TBD | 20 | Tue 06·24 |
| Week 6 Deliverable | 🔲 TBD | 10 | Tue 07·01 |
| Week 7 Deliverable | 🔲 TBD | 10 | Tue 07·08 |
| Act III Review | 🔲 TBD | 20 | Tue 07·15 |
| Week 9 Deliverable | 🔲 TBD | 10 | Tue 07·22 |
| Encore | 🔲 TBD | 60 | Tue 07·28 |
| **Total (graded)** | | **180 pts** | |

**Note on course total:** Memory has 6 weekly × 10 + 3 Act Reviews × 20 + Encore 60 = 180 pts graded, plus 20 pts participation = 200 pts. Verify against the posted syllabus before publishing. The Act I Rubric (20 pts = 10%) implies a 200-pt course scale — adjust point values in Canvas if your gradebook uses a different scale.

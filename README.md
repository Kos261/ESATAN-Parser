<p align="center">
  <img src="assets/CBKLOGO.png" alt="CBK PAN Logo" width="360"/>
</p>

# ESATAN-Parser

**ESATAN-Parser** is a tool developed to **simplify and accelerate thermal modelling workflows** for the [ESATAN-TMS](https://www.esatan-tms.com/) software.

Instead of manually building models inside ESATAN’s graphical environment, this parser allows you to **combine spacecraft geometry (BDF)** with **material and optical properties (Excel sheets)** into a ready-to-use **ERG input file**.  
This saves time and reduces errors, letting engineers move directly to thermal case definition and analysis.

---

## ✨ Features

- **Geometry conversion**  
  Reads NASTRAN BDF models and converts nodes, elements and primitives into ESATAN-compatible `SHELLS` blocks.

- **Excel integration**  
  Imports required thermal/optical material data from standardized Excel sheets (`HIERARCHY`, `MASS`, `BULK`, `OPTICAL`, `PRIMITIVES`, `CUTS`).

- **Automatic ERG generation**  
  Produces a complete `.erg` file with geometry, bulks, optics, groups, hierarchy and assembly sections.

- **Validation**  
  Detects missing or invalid sheets/columns in Excel and provides clear error handling.

- **Consistency rules**  
  Handles defaults for `unity1/unity2`, checks ID ranges in hierarchy, fills in missing values with fallback parameters.

- **Workflow integration**  
  GUI launcher (`PARSER-GUI`) can automatically place converted `.erg` files into the correct ESATAN case folder structure.

---

## 🚀 Workflow

1. **Input files**
   - BDF geometry (`.bdf`)
   - Excel sheet with material/optical data (`.xls`/`.xlsx`)

2. **Conversion**
   - The parser matches geometry IDs with hierarchy and primitive definitions.
   - Missing or partial fields are auto-completed (defaults to `fid` if necessary).

3. **Output**
   - A ready-to-use `.erg` file for ESATAN.

---

## 🛠️ Structure

- `src/` – main parser code (geometry handling, ERG writer, error checking)  
- `tests/` – validation and unit tests  
- `assets/` – project logo and auxiliary files  
- `output/` – generated ERG files  

---

## 📖 Usage

<!-- ### CLI (not implemented)
```bash
uv run -m src.PARSER --input model.bdf --excel materials.xlsx --output output.erg
``` -->

<!-- ### GUI -->

For easier use and automatic file transfer into ESATAN case folders, run the PARSER-GUI. Run command
```bash
uv run -m  Parser_runner
python -m Parser_runner
python Parser_runner.py
```

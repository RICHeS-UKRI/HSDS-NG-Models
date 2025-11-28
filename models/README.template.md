# Models

This folder contains all model definitions used in this project.  
Models are expressed as simple TSV triple structures and are designed for use with the
**National Gallery Dynamic Modeller**.

These models support CIDOC CRM v7.1.3-aligned documentation of:

- Paintings and their components
- Heritage samples and analytical context
- Conservation, technical imaging, and material relationships
- Higher-level NG-wide relationships

Each model is maintained in its own subfolder and may contain multiple versioned TSV files.
Version history and detail is documented in the individual model README pages.

---

## Folder Structure

models/
ng_models_vX.Y.tsv
<model_name>/
<model_name>_vA.B.tsv
README.md

---

## Available Model Folders

<!-- BEGIN AUTO: MODEL-FOLDERS -->
<!-- END AUTO: MODEL-FOLDERS -->

---

## Creating or Updating a Model

1. Add a new folder inside `models/`.
2. Add a TSV file using the pattern `<model>_v0.1.tsv`.
3. Commit and push; the GitHub Action will:
   - Create or update that model’s README  
   - Update the top-level README  
   - Integrate the model into the master list

---

If you would like help constructing new models or integrating them with CIDOC CRM, please open an
issue or contact the maintainers.

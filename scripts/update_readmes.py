#!/usr/bin/env python3
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = REPO_ROOT / "models"
NG_MERMAID_FILE = MODELS_DIR / "ng_models_mermaid.mmd"

VERSION_RE = re.compile(r"_v(\d+(?:\.\d+)*)\.tsv$")


def parse_version(filename: str) -> Optional[Tuple[int, ...]]:
    """
    Extract version tuple from a filename like 'sample_model_v1.2.tsv' -> (1, 2)
    """
    m = VERSION_RE.search(filename)
    if not m:
        return None
    parts = m.group(1).split(".")
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return None


def find_ng_models_latest(tsvs: List[Path]) -> Optional[Path]:
    """
    Given a list of Paths to ng_models_v*.tsv files, return the latest by version.
    """
    versions = []
    for p in tsvs:
        v = parse_version(p.name)
        if v is not None:
            versions.append((v, p))
    if not versions:
        return None
    versions.sort(reverse=True, key=lambda vp: vp[0])
    return versions[0][1]


def discover_models() -> Dict[str, List[Path]]:
    """
    Discover model folders under models/ and collect versioned TSVs.
    Returns dict: {model_folder_name: [list of .tsv Paths]}
    """
    models: Dict[str, List[Path]] = {}
    if not MODELS_DIR.exists():
        return models

    for child in MODELS_DIR.iterdir():
        if child.is_dir():
            tsvs = sorted(child.glob("*_v*.tsv"))
            if tsvs:
                models[child.name] = tsvs
    return models


def model_title_from_folder(folder_name: str) -> str:
    """
    Turn 'samples' into 'Samples Model' etc. Simple heuristic – adjust if needed.
    """
    base = folder_name.replace("_", " ").strip()
    if not base:
        return "Model"
    return base[:1].upper() + base[1:] + " Model"


def build_dynamic_modeller_url(raw_base: str, rel_path: Path) -> str:
    """
    Build the dynamic modeller URL from the raw GitHub URL to the TSV file.
    rel_path is relative to REPO_ROOT.
    """
    raw_url = f"{raw_base}/{rel_path.as_posix()}"
    return (
        "https://research.nationalgallery.org.uk/lab/modelling/?url="
        + raw_url
    )


def read_mermaid_block() -> str:
    """
    Read the mermaid code for the overall ng_models file if present.
    """
    if NG_MERMAID_FILE.exists():
        text = NG_MERMAID_FILE.read_text(encoding="utf-8").strip()
        if text:
            return f"```mermaid\n{text}\n```\n"
    return "_Mermaid diagram not available yet._\n"


def replace_auto_block(content: str, block_name: str, replacement: str) -> str:
    """
    Replace the content between markers:
      <!-- BEGIN AUTO: block_name -->
      <!-- END AUTO: block_name -->
    with the given replacement text.
    If markers are missing, content is returned unchanged.
    """
    pattern = re.compile(
        rf"(<!-- BEGIN AUTO: {re.escape(block_name)} -->)(.*?)(<!-- END AUTO: {re.escape(block_name)} -->)",
        flags=re.DOTALL,
    )

    def repl(match: re.Match) -> str:
        start, _, end = match.groups()
        # Ensure replacement has surrounding newlines
        rep = "\n" + replacement.strip() + "\n"
        return f"{start}{rep}{end}"

    new_content, count = pattern.subn(repl, content)
    if count == 0:
        # No markers found; return original content
        return content
    return new_content


def generate_model_list_block(models: Dict[str, List[Path]], raw_base: str) -> str:
    """
    Generate a simple table listing each model with links to:
    - model folder
    - latest TSV (raw)
    - dynamic modeller visualisation
    """
    if not models:
        return "_No model folders have been detected yet._"

    lines: List[str] = []
    lines.append("| Model | Folder | Latest TSV | Visualisation |")
    lines.append("|-------|--------|-----------|---------------|")

    for folder_name in sorted(models.keys()):
        tsvs = models[folder_name]

        # Find latest version in this folder
        version_info = []
        for p in tsvs:
            v = parse_version(p.name)
            if v is not None:
                version_info.append((v, p))
        if not version_info:
            continue

        version_info.sort(reverse=True, key=lambda vp: vp[0])
        latest_ver_tuple, latest_path = version_info[0]
        latest_ver_str = ".".join(str(x) for x in latest_ver_tuple)

        rel_latest = latest_path.relative_to(REPO_ROOT)
        raw_url = f"{raw_base}/{rel_latest.as_posix()}"
        modeller_url = build_dynamic_modeller_url(raw_base, rel_latest)

        model_title = model_title_from_folder(folder_name)
        folder_link = f"[`models/{folder_name}`](models/{folder_name})"
        tsv_link = f"[v{latest_ver_str}]({raw_url})"
        vis_link = f"[Open]({modeller_url})"

        lines.append(f"| {model_title} | {folder_link} | {tsv_link} | {vis_link} |")

    return "\n".join(lines)


def generate_ng_models_table(ng_tsvs: List[Path], raw_base: str) -> str:
    """
    Generate a table listing all ng_models_v*.tsv versions with raw + modeller links.
    """
    if not ng_tsvs:
        return "_No `ng_models_v*.tsv` files found in the `models/` folder._"

    # Collect and sort by version descending
    version_info = []
    for p in ng_tsvs:
        v = parse_version(p.name)
        if v is not None:
            version_info.append((v, p))
    if not version_info:
        return "_No valid `ng_models_v*.tsv` version filenames found._"

    version_info.sort(reverse=True, key=lambda vp: vp[0])

    lines: List[str] = []
    lines.append("### NG-wide model versions\n")
    lines.append("| Version | Raw TSV | Visualisation |")
    lines.append("|---------|---------|---------------|")

    for ver_tuple, path in version_info:
        ver_str = ".".join(str(x) for x in ver_tuple)
        rel_path = path.relative_to(REPO_ROOT)
        raw_url = f"{raw_base}/{rel_path.as_posix()}"
        modeller_url = build_dynamic_modeller_url(raw_base, rel_path)
        lines.append(
            f"| {ver_str} | [TSV]({raw_url}) | [Open in Modeller]({modeller_url}) |"
        )

    return "\n".join(lines)


def generate_model_details_block(
    model_name: str,
    tsv_files: List[Path],
    raw_base: str,
) -> str:
    """
    Generate the <details> block with the version table for a single model.
    Used for per-model READMEs.
    """
    # Sort versions descending
    version_info = []
    for p in tsv_files:
        v = parse_version(p.name)
        if v is not None:
            version_info.append((v, p))
    version_info.sort(reverse=True, key=lambda vp: vp[0])

    if not version_info:
        return ""

    latest_version, latest_path = version_info[0]
    latest_version_str = ".".join(str(x) for x in latest_version)
    latest_url = build_dynamic_modeller_url(
        raw_base, latest_path.relative_to(REPO_ROOT)
    )

    lines: List[str] = []
    lines.append("<details>")
    lines.append(
        f"<summary>{model_name}: "
        f'<a href="{latest_url}">{latest_version_str}</a>'
        f"</summary>\n"
    )
    lines.append(f"## {model_name} Details\n")
    lines.append("| | Date | Author | Model | Comment |")
    lines.append("| :-----------: | :-----------: | :-----------: | :-----------: | ----------- |")

    for idx, (ver_tuple, path) in enumerate(version_info):
        version_str = ".".join(str(x) for x in ver_tuple)
        url = build_dynamic_modeller_url(
            raw_base, path.relative_to(REPO_ROOT)
        )
        status = ":heavy_check_mark:" if idx == 0 else ""
        lines.append(
            f"| {status} |  |  | "
            f"[{version_str}]({url}) |  |"
        )

    # Spacer row for layout (optional)
    lines.append(
        "| | <img width=325 /> |<img width=175 /> | <img width=60 /> | <img width=500 /> |"
    )
    lines.append("</details>\n")

    return "\n".join(lines)


def write_top_readme(
    models: Dict[str, List[Path]],
    raw_base: str,
    ng_latest: Optional[Path],
    ng_tsvs: List[Path],
):
    """
    Generate the top-level README.md from README.template.md
    by replacing the NG-MODEL-VISUAL and MODEL-LIST blocks.
    """
    template_path = REPO_ROOT / "README.template.md"
    if not template_path.exists():
        raise SystemExit("Missing README.template.md at repository root.")

    template = template_path.read_text(encoding="utf-8")

    # NG-wide visual block
    if ng_latest:
        mermaid_block = read_mermaid_block()
    else:
        mermaid_block = "_Mermaid diagram not available yet._"

    new_content = replace_auto_block(
        template,
        "NG-MODEL-VISUAL",
        mermaid_block,
    )

    # Model list table (no per-version detail here)
    model_list_block = generate_model_list_block(models, raw_base)
    new_content = replace_auto_block(
        new_content,
        "MODEL-LIST",
        model_list_block,
    )

    REPO_ROOT.joinpath("README.md").write_text(new_content, encoding="utf-8")


def write_models_readme(models: Dict[str, List[Path]], raw_base: str, ng_tsvs: List[Path]):
    """
    Generate models/README.md from models/README.template.md by
    replacing the MODEL-FOLDERS block with:
      - a table of ng_models_v*.tsv versions
      - a simple list of model folders
    """
    template_path = MODELS_DIR / "README.template.md"
    if not template_path.exists():
        # Fallback: just write a simple auto-generated README
        lines = []
        lines.append("# Models\n")
        lines.append("This folder contains the NG-wide model definitions and individual model folders.\n")
        if ng_tsvs:
            lines.append("\n## NG-wide model versions\n")
            lines.append(generate_ng_models_table(ng_tsvs, raw_base))
        if models:
            lines.append("\n## Model folders\n")
            for folder_name in sorted(models.keys()):
                lines.append(f"- `{folder_name}/`")
        MODELS_DIR.joinpath("README.md").write_text("\n".join(lines), encoding="utf-8")
        return

    template = template_path.read_text(encoding="utf-8")

    # Build block for the marker
    pieces: List[str] = []
    # NG-wide model table
    pieces.append(generate_ng_models_table(ng_tsvs, raw_base))
    pieces.append("")  # blank line
    # Model folders list
    pieces.append("### Model folders\n")
    if models:
        for folder_name in sorted(models.keys()):
            pieces.append(f"- [`{folder_name}/`](./{folder_name})")
    else:
        pieces.append("_No per-model folders detected yet._")

    block_text = "\n".join(pieces)

    new_content = replace_auto_block(
        template,
        "MODEL-FOLDERS",
        block_text,
    )

    MODELS_DIR.joinpath("README.md").write_text(new_content, encoding="utf-8")


def write_per_model_readmes(models: Dict[str, List[Path]], raw_base: str):
    """
    Generate a README.md inside each model folder (still fully generated for now).
    """
    for folder_name, tsvs in models.items():
        folder_path = MODELS_DIR / folder_name
        model_title = model_title_from_folder(folder_name)
        block = generate_model_details_block(model_title, tsvs, raw_base)

        lines: List[str] = []
        lines.append(f"# {model_title}\n")
        lines.append(
            "This folder contains versioned TSV definitions of the model, "
            "intended for use with the National Gallery Dynamic Modeller.\n"
        )
        if block:
            lines.append("## Versions\n")
            lines.append(block)

        folder_path.joinpath("README.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    raw_base = os.environ.get("RAW_BASE")
    if not raw_base:
        raise SystemExit("RAW_BASE environment variable must be set to the raw GitHub base URL.")

    # Find ng_models tsvs at models/ level
    ng_tsvs = list(MODELS_DIR.glob("ng_models_v*.tsv"))
    ng_latest = find_ng_models_latest(ng_tsvs)

    models = discover_models()

    write_top_readme(models, raw_base, ng_latest, ng_tsvs)
    write_models_readme(models, raw_base, ng_tsvs)
    write_per_model_readmes(models, raw_base)


if __name__ == "__main__":
    main()

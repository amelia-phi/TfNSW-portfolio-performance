"""Generate repository.txt and maintain its link in README.md."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_FILE = PROJECT_ROOT / "README.md"
TREE_FILE = PROJECT_ROOT / "repository.txt"

START_MARKER = "<!-- REPOSITORY_TREE_START -->"
END_MARKER = "<!-- REPOSITORY_TREE_END -->"


@dataclass(frozen=True)
class TreeNode:
    """One curated repository path and its responsibility."""

    relative_path: str
    description: str
    children: tuple["TreeNode", ...] = ()


TREE_SPEC = (
    TreeNode(
        "data",
        "Source and generated datasets organised by pipeline stage",
        (
            TreeNode("data/raw", "Immutable copies of public source files"),
            TreeNode("data/interim", "Extracted and partially cleaned datasets"),
            TreeNode("data/processed", "Validated analysis-ready datasets"),
        ),
    ),
    TreeNode(
        "documentation",
        "Data dictionaries, methodology and validation rules",
    ),
    TreeNode("notebooks", "Exploratory analysis and development notebooks"),
    TreeNode(
        "outputs",
        "Generated analytical and data-quality outputs",
        (
            TreeNode("outputs/charts", "Generated portfolio visualisations"),
            TreeNode("outputs/tables", "Generated analytical summary tables"),
            TreeNode("outputs/validation", "Data-quality and exception logs"),
        ),
    ),
    TreeNode("reports", "Methodology and performance briefing deliverables"),
    TreeNode(
        "scripts",
        "Repository maintenance and documentation utilities",
        (
            TreeNode(
                "scripts/update_repository_tree.py",
                "Regenerates repository.txt and its README link",
            ),
        ),
    ),
    TreeNode(
        "src",
        "Production extraction, transformation and validation code",
        (
            TreeNode(
                "src/extract",
                "Source-specific Excel and PDF extraction pipelines",
                (
                    TreeNode(
                        "src/extract/infrastructure_pipeline",
                        "Infrastructure NSW workbook extraction package",
                    ),
                    TreeNode(
                        "src/extract/tfnsw_project_pipeline",
                        "TfNSW PDF text, shape and colour extraction package",
                    ),
                    TreeNode(
                        "src/extract/extract_infrastructure_pipeline.py",
                        "Infrastructure workbook extraction entry point",
                    ),
                    TreeNode(
                        "src/extract/extract_tfnsw_project_pipeline.py",
                        "TfNSW project-pipeline extraction entry point",
                    ),
                ),
            ),
            TreeNode(
                "src/transform",
                "Business rules and analysis-ready dataset construction",
                (
                    TreeNode(
                        "src/transform/project_register",
                        "Project-register transformation package",
                    ),
                    TreeNode(
                        "src/transform/tfnsw_timeline",
                        "Project timeline transformation package",
                    ),
                    TreeNode(
                        "src/transform/transform_project_register.py",
                        "Project-register transformation entry point",
                    ),
                    TreeNode(
                        "src/transform/transform_tfnsw_project_timeline.py",
                        "Project-timeline transformation entry point",
                    ),
                ),
            ),
            TreeNode("src/build_dataset", "Cross-source dataset integration"),
            TreeNode("src/validate", "Cross-dataset assurance checks"),
        ),
    ),
    TreeNode(
        "tableau",
        "Tableau extracts and workbook assets",
        (
            TreeNode("tableau/extracts", "Tableau-ready data extracts"),
            TreeNode("tableau/workbook", "Tableau workbook files"),
        ),
    ),
    TreeNode("tests", "Automated unit and integration tests"),
    TreeNode(".gitignore", "Files and directories excluded from version control"),
    TreeNode("LICENSE", "Repository usage and distribution licence"),
    TreeNode("requirements.txt", "Python runtime dependencies"),
    TreeNode("repository.txt", "Generated annotated repository structure"),
    TreeNode("README.md", "Project overview, architecture and usage guide"),
)


def _existing_nodes(nodes: tuple[TreeNode, ...]) -> tuple[TreeNode, ...]:
    """Return only curated nodes that currently exist in the repository."""

    return tuple(
        node
        for node in nodes
        if node.relative_path == "repository.txt"
        or (PROJECT_ROOT / node.relative_path).exists()
    )


def _format_line(tree_text: str, description: str) -> str:
    """Align a concise responsibility comment beside one tree path."""

    padding = " " * max(2, 54 - len(tree_text))
    return f"{tree_text}{padding}# {description}"


def _render_nodes(
    nodes: tuple[TreeNode, ...],
    prefix: str = "",
) -> list[str]:
    """Render curated nodes using standard directory-tree connectors."""

    lines = []
    visible_nodes = _existing_nodes(nodes)

    for index, node in enumerate(visible_nodes):
        is_last = index == len(visible_nodes) - 1
        connector = "└──" if is_last else "├──"
        path = PROJECT_ROOT / node.relative_path
        label = path.name + ("/" if path.is_dir() else "")
        tree_text = f"{prefix}{connector} {label}"
        lines.append(_format_line(tree_text, node.description))

        if node.children:
            child_prefix = prefix + ("    " if is_last else "│   ")
            lines.extend(_render_nodes(node.children, child_prefix))

    return lines


def generate_tree() -> str:
    """Generate the complete curated repository tree."""

    return "\n".join([".", *_render_nodes(TREE_SPEC)])


def write_tree_file() -> None:
    """Write the current annotated repository structure to repository.txt."""

    TREE_FILE.write_text(generate_tree() + "\n", encoding="utf-8")
    print("Updated:", TREE_FILE)


def build_readme_block() -> str:
    """Build the marker-delimited README link managed by this script."""

    return (
        f"{START_MARKER}\n"
        "[View the annotated repository structure](repository.txt).\n"
        f"{END_MARKER}"
    )


def update_readme() -> None:
    """Insert or replace only the generated repository-file link."""

    readme_text = README_FILE.read_text(encoding="utf-8")
    has_start = START_MARKER in readme_text
    has_end = END_MARKER in readme_text

    if has_start != has_end:
        raise ValueError(
            "README.md contains only one repository-tree marker. "
            "Restore both markers before running the update."
        )

    generated_block = build_readme_block()

    if has_start:
        start_index = readme_text.index(START_MARKER)
        end_index = readme_text.index(END_MARKER) + len(END_MARKER)
        updated_text = (
            readme_text[:start_index]
            + generated_block
            + readme_text[end_index:]
        )
    else:
        introduction = (
            "\n\n## Repository Structure\n\n"
            "The annotated structure is generated by "
            "`python scripts/update_repository_tree.py`.\n\n"
        )
        updated_text = readme_text.rstrip() + introduction + generated_block + "\n"

    README_FILE.write_text(updated_text, encoding="utf-8")
    print("Updated:", README_FILE)


def main() -> None:
    """Update repository.txt and its README link."""

    write_tree_file()
    update_readme()


if __name__ == "__main__":
    main()

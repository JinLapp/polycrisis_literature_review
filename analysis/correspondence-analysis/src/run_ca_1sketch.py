'''1. Load graph JSON
2. Extract Institution nodes
3. Extract Concept nodes
4. Find Institution → Concept edges
5. Build Institution × Concept matrix
6. Run correspondence analysis
7. Export coordinates
8. Create first 2D plot'''

import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "polycrisis_seed_graph.json"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_graph(path: Path) -> tuple[list[dict], list[dict]]:
    with path.open("r", encoding="utf-8") as f:
        graph = json.load(f)

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    return nodes, edges


def get_node_label(node: dict) -> str:
    return node.get("label") or node.get("name") or node.get("id")


def build_institution_concept_matrix(nodes: list[dict], edges: list[dict]) -> pd.DataFrame:
    node_by_id = {node["id"]: node for node in nodes}

    institutions = {
        node["id"]: get_node_label(node)
        for node in nodes
        if node.get("type") == "Institution"
    }

    concepts = {
        node["id"]: get_node_label(node)
        for node in nodes
        if node.get("type") == "Concept"
    }

    matrix = pd.DataFrame(
        0.0,
        index=sorted(institutions.values()),
        columns=sorted(concepts.values()),
    )

    institution_label_by_id = institutions
    concept_label_by_id = concepts

    relevant_edge_types = {
        "works_on",
        "uses_concept",
        "promotes",
        "develops",
        "linked_to",
        "active_in",
        "related_to",
    }

    for edge in edges:
        source_id = edge.get("source")
        target_id = edge.get("target")
        edge_type = edge.get("type")

        if edge_type not in relevant_edge_types:
            continue

        source_node = node_by_id.get(source_id)
        target_node = node_by_id.get(target_id)

        if not source_node or not target_node:
            continue

        source_type = source_node.get("type")
        target_type = target_node.get("type")

        weight = float(edge.get("weight", 1.0))

        # Institution -> Concept
        if source_type == "Institution" and target_type == "Concept":
            inst = institution_label_by_id[source_id]
            concept = concept_label_by_id[target_id]
            matrix.loc[inst, concept] += weight

        # Concept -> Institution, just in case direction is reversed
        elif source_type == "Concept" and target_type == "Institution":
            inst = institution_label_by_id[target_id]
            concept = concept_label_by_id[source_id]
            matrix.loc[inst, concept] += weight

    # Drop empty rows/columns
    matrix = matrix.loc[matrix.sum(axis=1) > 0, matrix.sum(axis=0) > 0]

    return matrix


def correspondence_analysis(matrix: pd.DataFrame, n_components: int = 2):
    """
    Manual correspondence analysis using singular value decomposition.

    Input:
        rows = institutions
        columns = concepts

    Output:
        row coordinates, column coordinates, explained inertia
    """
    X = matrix.to_numpy(dtype=float)
    grand_total = X.sum()

    if grand_total == 0:
        raise ValueError("The matrix is empty. No institution-concept links found.")

    P = X / grand_total

    row_masses = P.sum(axis=1)
    col_masses = P.sum(axis=0)

    expected = np.outer(row_masses, col_masses)

    standardized_residuals = (P - expected) / np.sqrt(expected)

    U, singular_values, Vt = np.linalg.svd(standardized_residuals, full_matrices=False)

    eigenvalues = singular_values**2
    explained_inertia = eigenvalues / eigenvalues.sum()

    Dr_inv_sqrt = np.diag(1 / np.sqrt(row_masses))
    Dc_inv_sqrt = np.diag(1 / np.sqrt(col_masses))

    row_coords = Dr_inv_sqrt @ U[:, :n_components] @ np.diag(singular_values[:n_components])
    col_coords = Dc_inv_sqrt @ Vt.T[:, :n_components] @ np.diag(singular_values[:n_components])

    row_df = pd.DataFrame(
        row_coords,
        index=matrix.index,
        columns=[f"Dim{i+1}" for i in range(n_components)],
    )

    col_df = pd.DataFrame(
        col_coords,
        index=matrix.columns,
        columns=[f"Dim{i+1}" for i in range(n_components)],
    )

    inertia_df = pd.DataFrame({
        "dimension": [f"Dim{i+1}" for i in range(len(explained_inertia))],
        "eigenvalue": eigenvalues,
        "explained_inertia": explained_inertia,
        "explained_inertia_percent": explained_inertia * 100,
    })

    return row_df, col_df, inertia_df


def plot_ca(row_coords: pd.DataFrame, col_coords: pd.DataFrame, inertia: pd.DataFrame):
    plt.figure(figsize=(14, 10))

    plt.scatter(row_coords["Dim1"], row_coords["Dim2"], marker="o", label="Institutions")
    plt.scatter(col_coords["Dim1"], col_coords["Dim2"], marker="x", label="Concepts")

    for label, row in row_coords.iterrows():
        plt.text(row["Dim1"], row["Dim2"], label, fontsize=8)

    for label, row in col_coords.iterrows():
        plt.text(row["Dim1"], row["Dim2"], label, fontsize=8)

    dim1 = inertia.loc[0, "explained_inertia_percent"]
    dim2 = inertia.loc[1, "explained_inertia_percent"]

    plt.axhline(0, linewidth=0.8)
    plt.axvline(0, linewidth=0.8)

    plt.xlabel(f"Dimension 1 ({dim1:.1f}% inertia)")
    plt.ylabel(f"Dimension 2 ({dim2:.1f}% inertia)")
    plt.title(
        "Prototype correspondence analysis map\n"
        "Institution × Concept seed matrix — illustrative, not yet validated bibliometric result"
    )
    plt.legend()
    plt.tight_layout()

    output_path = OUTPUT_DIR / "ca_institution_concept_map.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    return output_path


def main():
    print("Loading graph...")
    nodes, edges = load_graph(DATA_PATH)

    print("Building Institution × Concept matrix...")
    matrix = build_institution_concept_matrix(nodes, edges)

    print(f"Matrix shape: {matrix.shape[0]} institutions × {matrix.shape[1]} concepts")

    matrix.to_csv(OUTPUT_DIR / "ca_institution_concept_matrix.csv")

    print("Running correspondence analysis...")
    row_coords, col_coords, inertia = correspondence_analysis(matrix)

    row_coords.to_csv(OUTPUT_DIR / "ca_row_coordinates_institutions.csv")
    col_coords.to_csv(OUTPUT_DIR / "ca_column_coordinates_concepts.csv")
    inertia.to_csv(OUTPUT_DIR / "ca_explained_inertia.csv", index=False)

    print("Creating plot...")
    plot_path = plot_ca(row_coords, col_coords, inertia)

    print("Done.")
    print(f"Matrix saved to: {OUTPUT_DIR / 'ca_institution_concept_matrix.csv'}")
    print(f"Institution coordinates saved to: {OUTPUT_DIR / 'ca_row_coordinates_institutions.csv'}")
    print(f"Concept coordinates saved to: {OUTPUT_DIR / 'ca_column_coordinates_concepts.csv'}")
    print(f"Inertia saved to: {OUTPUT_DIR / 'ca_explained_inertia.csv'}")
    print(f"Plot saved to: {plot_path}")


if __name__ == "__main__":
    main()
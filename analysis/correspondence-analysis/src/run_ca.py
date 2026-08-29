import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "polycrisis_seed_graph.json"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


EXPERIMENTS = [
    {
        "name": "institution_concept",
        "row_type": "Institution",
        "column_type": "Concept",
        "edge_types": ["works_on", "uses_concept", "promotes", "develops", "linked_to"],
    },
    {
        "name": "researchfield_concept",
        "row_type": "ResearchField",
        "column_type": "Concept",
        "edge_types": ["uses_concept", "part_of", "related_to", "works_on"],
    },
    {
        "name": "publication_concept",
        "row_type": "KeyPublication",
        "column_type": "Concept",
        "edge_types": ["uses_concept", "works_on", "related_to"],
    },
    {
        "name": "institution_method",
        "row_type": "Institution",
        "column_type": "Method",
        "edge_types": ["uses_method", "works_on", "active_in"],
    },
    {
        "name": "researchfield_method",
        "row_type": "ResearchField",
        "column_type": "Method",
        "edge_types": ["uses_method", "studied_with"],
    },
    {
        "name": "publication_method",
        "row_type": "KeyPublication",
        "column_type": "Method",
        "edge_types": ["uses_method", "studied_with"],
    },
]


def load_graph(path: Path) -> tuple[list[dict], list[dict]]:
    with path.open("r", encoding="utf-8") as f:
        graph = json.load(f)

    return graph.get("nodes", []), graph.get("edges", [])


def get_node_label(node: dict) -> str:
    return node.get("label") or node.get("name") or node.get("id")


def build_incidence_matrix(
    nodes: list[dict],
    edges: list[dict],
    row_type: str,
    column_type: str,
    edge_types: list[str],
) -> pd.DataFrame:
    node_by_id = {node["id"]: node for node in nodes}

    row_nodes = {
        node["id"]: get_node_label(node)
        for node in nodes
        if node.get("type") == row_type
    }

    column_nodes = {
        node["id"]: get_node_label(node)
        for node in nodes
        if node.get("type") == column_type
    }

    matrix = pd.DataFrame(
        0.0,
        index=sorted(row_nodes.values()),
        columns=sorted(column_nodes.values()),
    )

    allowed_edge_types = set(edge_types)

    for edge in edges:
        source_id = edge.get("source")
        target_id = edge.get("target")
        edge_type = edge.get("type")

        if edge_type not in allowed_edge_types:
            continue

        source_node = node_by_id.get(source_id)
        target_node = node_by_id.get(target_id)

        if not source_node or not target_node:
            continue

        source_type = source_node.get("type")
        target_type = target_node.get("type")

        weight = float(edge.get("weight", 1.0))

        # row_type -> column_type
        if source_type == row_type and target_type == column_type:
            row_label = row_nodes[source_id]
            col_label = column_nodes[target_id]
            matrix.loc[row_label, col_label] += weight

        # column_type -> row_type
        elif source_type == column_type and target_type == row_type:
            row_label = row_nodes[target_id]
            col_label = column_nodes[source_id]
            matrix.loc[row_label, col_label] += weight

    matrix = matrix.loc[matrix.sum(axis=1) > 0, matrix.sum(axis=0) > 0]

    return matrix


def correspondence_analysis(matrix: pd.DataFrame, n_components: int = 2):
    X = matrix.to_numpy(dtype=float)
    grand_total = X.sum()

    if grand_total == 0:
        raise ValueError("The matrix is empty.")

    P = X / grand_total

    row_masses = P.sum(axis=1)
    col_masses = P.sum(axis=0)

    expected = np.outer(row_masses, col_masses)

    # Avoid divide-by-zero issues
    expected[expected == 0] = np.nan

    standardized_residuals = (P - expected) / np.sqrt(expected)
    standardized_residuals = np.nan_to_num(standardized_residuals)

    U, singular_values, Vt = np.linalg.svd(
        standardized_residuals,
        full_matrices=False,
    )

    eigenvalues = singular_values**2
    explained_inertia = eigenvalues / eigenvalues.sum()

    available_components = min(n_components, len(singular_values))

    row_coords = (
        np.diag(1 / np.sqrt(row_masses))
        @ U[:, :available_components]
        @ np.diag(singular_values[:available_components])
    )

    col_coords = (
        np.diag(1 / np.sqrt(col_masses))
        @ Vt.T[:, :available_components]
        @ np.diag(singular_values[:available_components])
    )

    row_df = pd.DataFrame(
        row_coords,
        index=matrix.index,
        columns=[f"Dim{i + 1}" for i in range(available_components)],
    )

    col_df = pd.DataFrame(
        col_coords,
        index=matrix.columns,
        columns=[f"Dim{i + 1}" for i in range(available_components)],
    )

    inertia_df = pd.DataFrame(
        {
            "dimension": [f"Dim{i + 1}" for i in range(len(explained_inertia))],
            "eigenvalue": eigenvalues,
            "explained_inertia": explained_inertia,
            "explained_inertia_percent": explained_inertia * 100,
        }
    )

    return row_df, col_df, inertia_df


def export_diagnostics(matrix: pd.DataFrame, experiment_name: str):
    diagnostics = {
        "experiment": experiment_name,
        "rows": matrix.shape[0],
        "columns": matrix.shape[1],
        "non_zero_cells": int((matrix > 0).sum().sum()),
        "total_weight": float(matrix.sum().sum()),
        "density": float((matrix > 0).sum().sum() / matrix.size),
    }

    diagnostics_df = pd.DataFrame([diagnostics])
    diagnostics_df.to_csv(
        OUTPUT_DIR / f"{experiment_name}_diagnostics.csv",
        index=False,
    )

    matrix.sum(axis=1).sort_values(ascending=False).to_csv(
        OUTPUT_DIR / f"{experiment_name}_row_totals.csv",
        header=["total_weight"],
    )

    matrix.sum(axis=0).sort_values(ascending=False).to_csv(
        OUTPUT_DIR / f"{experiment_name}_column_totals.csv",
        header=["total_weight"],
    )

    return diagnostics


def plot_ca(
    row_coords: pd.DataFrame,
    col_coords: pd.DataFrame,
    inertia: pd.DataFrame,
    experiment_name: str,
    row_type: str,
    column_type: str,
    max_labels_each: int = 25,
):
    if "Dim1" not in row_coords.columns or "Dim2" not in row_coords.columns:
        print(f"Skipping plot for {experiment_name}: fewer than two dimensions.")
        return None

    plt.figure(figsize=(14, 10))

    plt.scatter(row_coords["Dim1"], row_coords["Dim2"], marker="o", label=row_type)
    plt.scatter(col_coords["Dim1"], col_coords["Dim2"], marker="x", label=column_type)

    # Label only the most distant points from origin to reduce visual clutter
    row_label_candidates = (
        row_coords.assign(distance=row_coords["Dim1"] ** 2 + row_coords["Dim2"] ** 2)
        .sort_values("distance", ascending=False)
        .head(max_labels_each)
    )

    col_label_candidates = (
        col_coords.assign(distance=col_coords["Dim1"] ** 2 + col_coords["Dim2"] ** 2)
        .sort_values("distance", ascending=False)
        .head(max_labels_each)
    )

    for label, row in row_label_candidates.iterrows():
        plt.text(row["Dim1"], row["Dim2"], label, fontsize=8)

    for label, row in col_label_candidates.iterrows():
        plt.text(row["Dim1"], row["Dim2"], label, fontsize=8)

    dim1 = inertia.loc[0, "explained_inertia_percent"]
    dim2 = inertia.loc[1, "explained_inertia_percent"]

    plt.axhline(0, linewidth=0.8)
    plt.axvline(0, linewidth=0.8)

    plt.xlabel(f"Dimension 1 ({dim1:.1f}% inertia)")
    plt.ylabel(f"Dimension 2 ({dim2:.1f}% inertia)")

    plt.title(
        f"Prototype correspondence analysis: {row_type} × {column_type}\n"
        "Illustrative seed-data map — not yet a validated bibliometric result"
    )

    plt.legend()
    plt.tight_layout()

    output_path = OUTPUT_DIR / f"{experiment_name}_ca_map.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    return output_path


def run_experiment(nodes: list[dict], edges: list[dict], experiment: dict):
    name = experiment["name"]
    row_type = experiment["row_type"]
    column_type = experiment["column_type"]
    edge_types = experiment["edge_types"]

    print("\n" + "=" * 80)
    print(f"Experiment: {name}")
    print(f"Matrix: {row_type} × {column_type}")
    print(f"Edge types: {', '.join(edge_types)}")

    matrix = build_incidence_matrix(
        nodes=nodes,
        edges=edges,
        row_type=row_type,
        column_type=column_type,
        edge_types=edge_types,
    )

    if matrix.empty:
        print("No data found. Skipping.")
        return

    matrix_path = OUTPUT_DIR / f"{name}_matrix.csv"
    matrix.to_csv(matrix_path)

    diagnostics = export_diagnostics(matrix, name)

    print(
        f"Matrix shape: {diagnostics['rows']} × {diagnostics['columns']} | "
        f"non-zero cells: {diagnostics['non_zero_cells']} | "
        f"density: {diagnostics['density']:.3f}"
    )

    if matrix.shape[0] < 2 or matrix.shape[1] < 2:
        print("Matrix too small for CA. Skipping.")
        return

    row_coords, col_coords, inertia = correspondence_analysis(matrix)

    row_coords.to_csv(OUTPUT_DIR / f"{name}_row_coordinates.csv")
    col_coords.to_csv(OUTPUT_DIR / f"{name}_column_coordinates.csv")
    inertia.to_csv(OUTPUT_DIR / f"{name}_explained_inertia.csv", index=False)

    plot_path = plot_ca(
        row_coords=row_coords,
        col_coords=col_coords,
        inertia=inertia,
        experiment_name=name,
        row_type=row_type,
        column_type=column_type,
    )

    print(f"Saved matrix: {matrix_path}")
    print(f"Saved plot: {plot_path}")


def main():
    print("Loading graph...")
    nodes, edges = load_graph(DATA_PATH)

    print(f"Nodes: {len(nodes)}")
    print(f"Edges: {len(edges)}")

    for experiment in EXPERIMENTS:
        run_experiment(nodes, edges, experiment)

    print("\nAll experiments finished.")


if __name__ == "__main__":
    main()
# Polycrisis Graph Analysis and Literature Review

> **Status:** Exploratory research prototype / proof of concept\
> **Purpose:** Mapping actors, concepts, institutions, publications,
> methods, and intellectual structures around polycrisis research.

## Overview

This repository documents a first exploratory iteration of a research
project on the emerging **polycrisis research landscape**.

The project asks whether polycrisis is developing into a coherent
research field, or whether it is better understood as an intersection of
established traditions such as systemic risk, resilience, Earth system
science, sustainability transitions, governance research, political
ecology, and related approaches.

The repository deliberately contains both **results and process
documentation**. The current graph and derived analyses are prototypes
based on a manually curated and qualitatively enriched seed dataset.
They should therefore **not be interpreted as validated bibliometric
findings**. Their purpose is to demonstrate and evaluate a possible
research methodology that can later be applied to a larger,
systematically collected empirical dataset.

## Research workflow

``` text
Literature review / exploratory research
                  |
                  v
       Heterogeneous seed graph
                  |
                  v
       Qualitative enrichment
                  |
                  v
        Incidence matrices
                  |
                  v
    Correspondence Analysis (CA)
                  |
                  v
      2D research landscape maps
                  |
                  v
 Qualitative interpretation / validation
```

## PLUS / PLUSPOK perspective

The qualitative enrichment additionally interprets nodes through a
problem--goal--solution--implementation perspective.

> *Zusammenfassend kann man also vereinfacht sagen, um der globalen
> Polykrise zu begegnen bedarf es eines Lösungssystems, das mit Hinblick
> auf ein System konkretisierter Ziele erstellt wurde und das durch ein
> Umsetzungssystem in die Tat umgesetz werden kann. Wir reden im
> weiteren von einem PLUS (Problem/Ziel-Lösung-Umsetzungs System).*

For each relevant node, the enrichment asks about **Problem / Goal**,
**Solution**, and **Implementation**: normative goals and diagnoses of
the world; proposed solution mechanisms and their systemic context; and
actors, institutions, barriers, and enabling conditions for
implementation.

## Repository structure

``` text
.
├── README.md
├── LICENSE
├── data/
│   ├── seed/
│   │   └── polycrisis_seed_graph.json
│   └── enriched/
│       └── polycrisis_seed_graph_enriched_qualitative.json
├── analysis/
│   └── correspondence-analysis/
│       ├── README.md
│       ├── requirements.txt
│       ├── src/
│       │   └── run_ca.py
│       └── output/
│           ├── *_matrix.csv
│           ├── *_row_coordinates.csv
│           ├── *_column_coordinates.csv
│           ├── *_explained_inertia.csv
│           ├── *_diagnostics.csv
│           └── *_ca_map.png
├── documentation/
│   ├── research-design/
│   ├── methodology/
│   │   └── pro-denkvorgang.md
│   └── qualitative-enrichment/
│       └── polycrisis_qualitative_enrichment_summary.md
├── conversation/
│   └── research-development-thread.md
└── references/
    └── README.md
```

### Data

`data/seed/` contains the original exploratory heterogeneous graph.
`data/enriched/` contains the version in which nodes are supplemented
with qualitative descriptions, their relationship to polycrisis,
PLUS/PLUSPOK interpretations, classifications, key phrases, links, and
review flags.

### Correspondence analysis

`analysis/correspondence-analysis/` contains the experimental
dimension-reduction workflow. It constructs incidence matrices such as
`Institution × Concept`, `ResearchField × Concept`,
`Publication × Concept`, and `Institution × Method`, then applies
**Correspondence Analysis (CA)** to represent rows and columns in a
common lower-dimensional space.

The central idea is to move from a visually dense network toward
interpretable two-dimensional maps of the research landscape.

**Important:** The current CA maps are methodological demonstrators.
Their geometry reflects the manually curated seed graph and should not
yet be interpreted as robust empirical structure of the research
community.

**CA analysis / external link:** `<ADD LINK TO CA ANALYSIS HERE>`

### Documentation and conversation

`documentation/` contains the research design, methodological decisions,
assumptions, limitations, and enrichment documentation.

`conversation/` contains an exported research-development conversation
documenting how the project, graph model, qualitative enrichment, and
correspondence-analysis idea evolved. It is included for transparency
and provenance and should be read as working material rather than as a
formal scientific source.

## Data model

At the highest level:

``` json
{
  "metadata": {},
  "schema": {},
  "nodes": [],
  "edges": [],
  "analysis": {}
}
```

Nodes represent heterogeneous entities and edges encode exploratory
relationships. The enriched graph adds a qualitative layer while
retaining the original graph structure, including short presentations,
polycrisis relationships, PLUS/PLUSPOK interpretations, key phrases,
research-landscape roles, importance estimates, references, and
review/provenance information.

## Why Correspondence Analysis?

Selected graph relations can be represented as **bipartite incidence
matrices** instead of immediately being projected into one-mode
co-occurrence networks.

For example:

  Institution / Concept     Concept A   Concept B   Concept C
  ----------------------- ----------- ----------- -----------
  Institution 1                     0           1           1
  Institution 2                     1           0           1
  Institution 3                     1           0           0

Correspondence Analysis can position both institutions and concepts in a
common geometric space. The intended questions are:

-   Which actors have similar conceptual profiles?
-   Which concepts characterize particular regions of the research
    landscape?
-   Which latent dimensions differentiate research traditions?
-   Where do bridge actors or concepts occur?
-   Which apparently related communities remain conceptually separated?

CA is therefore explored as an alternative or complement to conventional
network visualization and community detection.

## How to interpret the current results

The current artifacts are best described as:

**exploratory seed data → methodological prototype → pseudo-result /
proof of concept**

They are **not yet**:

**systematic bibliometric data → validated statistical analysis →
substantive empirical finding**

The prototype tests whether the heterogeneous graph model is expressive
enough, whether qualitative enrichment adds useful semantic structure,
whether graph-derived incidence matrices are suitable for CA, whether CA
produces interpretable research-landscape maps, and which data gaps a
future empirical study must address.

## Limitations

The present dataset is manually curated and partly model-assisted. Node
selection, concept vocabulary, classifications, relationship weights,
qualitative summaries, and source selection therefore contain
interpretive decisions.

In particular:

-   the graph is not exhaustive;
-   absence of an edge is not evidence of absence of a relationship;
-   edge weights are not validated influence measures;
-   concept selection can shape CA geometry;
-   some node types are more densely represented than others;
-   external references differ in evidential strength;
-   qualitative enrichments require human review before use as research
    findings;
-   sparse seed matrices may reveal properties of the coding scheme
    rather than stable structures of the underlying research field.

These limitations are deliberately explicit because evaluating them is
part of the prototype.

## Planned next steps

Potential next stages include systematic data acquisition through
OpenAlex, Crossref, ORCID, institutional sources, project databases, and
reference lists; development of a more inductive concept vocabulary from
titles, abstracts, author keywords, and topic extraction; human
validation of high-importance nodes and relationships; comparison of
multiple incidence matrices; CA contribution and cos² diagnostics;
temporal analysis; comparison with network community detection; stronger
claim- and edge-level provenance; conversion into an Obsidian knowledge
base; and exploration of GraphRAG or other retrieval-based research
interfaces.

## Reproducibility

Keep the correspondence-analysis code and derived matrices under
`analysis/correspondence-analysis/`. A minimal Python environment
currently needs packages such as:

``` text
numpy
pandas
matplotlib
```

Future releases should additionally record software versions,
data-acquisition dates, source identifiers, coding rules,
inclusion/exclusion criteria, manual corrections, and dataset/version
identifiers.

## Suggested citation

This repository currently represents work in progress. Until a formal
citation is defined, please cite the repository URL together with the
specific commit or release used.

## License

A license has not yet been specified in this draft README. Before broad
reuse, consider licenses separately for code and original research
data/documentation. Third-party source material remains subject to its
original terms.

## Acknowledgements and use of AI

Generative AI was used during the exploratory research process for graph
construction, methodological discussion, qualitative enrichment, code
prototyping, and documentation.

AI-generated or AI-assisted content in this repository should be treated
as research material requiring human evaluation, not as independently
verified scholarly evidence. External references should be checked
against their original sources before substantive claims are cited.

------------------------------------------------------------------------

**Repository status:** exploratory / work in progress.

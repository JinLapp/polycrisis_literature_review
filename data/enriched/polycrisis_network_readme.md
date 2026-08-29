# Polycrisis Seed Network

This is a first-stage heterogeneous seed graph for polycrisis-related research. It is derived primarily from the uploaded research program and network-analysis design, with selected representative publication/person anchors added to make the graph empirically extensible.

## Files

- `polycrisis_seed_graph.json`: full machine-readable graph, schema, metrics, communities, gap candidates.
- `polycrisis_nodes.csv`: flat node table for Neo4j/Gephi/spreadsheets.
- `polycrisis_edges.csv`: flat edge table.
- `polycrisis_metrics.csv`: centrality and community metrics.
- `polycrisis_seed_graph.gexf`: graph export for Gephi.

## Counts

{
  "nodes_total": 170,
  "edges_total": 717,
  "nodes_by_type": {
    "Concept": 55,
    "DataInfrastructure": 11,
    "GovernanceFramework": 11,
    "Initiative": 6,
    "Institution": 17,
    "KeyPublication": 15,
    "Method": 16,
    "Person": 23,
    "ResearchField": 16
  },
  "edges_by_type": {
    "active_in": 56,
    "affiliated_with": 7,
    "authored": 34,
    "belongs_to": 35,
    "cites": 8,
    "contributes_to": 16,
    "develops": 2,
    "hosts": 2,
    "informs": 21,
    "linked_to": 26,
    "part_of": 10,
    "participates_in": 4,
    "produced_by": 14,
    "promotes": 27,
    "related_to": 75,
    "studied_with": 29,
    "uses_concept": 165,
    "uses_data": 25,
    "uses_method": 79,
    "works_in": 19,
    "works_on": 63
  }
}

## Top bridge candidates

- Sustainability Science (ResearchField): betweenness=0.1382, weighted_degree=143.0
- Polycrisis (Concept): betweenness=0.1266, weighted_degree=129.0
- Earth System Science (ResearchField): betweenness=0.1011, weighted_degree=126.0
- Governance Research (ResearchField): betweenness=0.0910, weighted_degree=112.0
- Systemic Risk Analysis (ResearchField): betweenness=0.0606, weighted_degree=105.0
- Stockholm Resilience Centre (Institution): betweenness=0.0518, weighted_degree=80.0
- Planetary Boundaries (Concept): betweenness=0.0508, weighted_degree=112.0
- Transformation (Concept): betweenness=0.0500, weighted_degree=70.0
- Scenario Analysis and Foresight Research (ResearchField): betweenness=0.0466, weighted_degree=47.0
- Potsdam Institute for Climate Impact Research (PIK) (Institution): betweenness=0.0441, weighted_degree=56.0

## Caveat

Do not interpret these edges as proof of influence or causality. Low-confidence citation and affiliation edges should be replaced by OpenAlex/Crossref/institutional data in a next empirical round.

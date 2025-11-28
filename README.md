# CIDOC CRM-based models for paintings and samples

This repository collects semantic models (as simple TSV triples) for use with the National Gallery Dynamic Modeller and integration into ResearchSpace.

## Overall NG Models

The current NG-wide model can be explored directly in the Dynamic Modeller:


- [Open in Dynamic Modeller](https://research.nationalgallery.org.uk/lab/modelling/?url=https://raw.githubusercontent.com/RICHeS-UKRI/HSDS-NG-Models/refs/heads/main/models/ng_models_v0.1.tsv)


### Mermaid overview


```mermaid
flowchart LR
classDef object stroke:#2C5D98,fill:#2C5D98,color:white,rx:5px,ry:5px;
classDef event stroke:#5C811F,fill:#5C811F,color:white,rx:5px,ry:5px;


O0("Heritage Sample\nS13_Sample and\nE19_Physical_object")
class O0 object;

O1("Sample Taking\nS2_Sample_Taking")
class O1 event;
O0["Heritage Sample\nS13_Sample and\nE19_Physical_object"] -- "O5i_was_removed_by #40;1 to 1#41;" -->O1["Sample Taking\nS2_Sample_Taking"]

O2("Heritage Object\nE22_Human-Made Object")
class O2 object;
O1["Sample Taking\nS2_Sample_Taking"] -- "O3_sampled_from #40;1 to 1#41;" -->O2["Heritage Object\nE22_Human-Made Object"]

O3("Sample Splitting\nS24_Sample_splitting")
class O3 event;
O0["Heritage Sample\nS13_Sample and\nE19_Physical_object"] -- "O1i_was_diminished_by #40;0 to 1#41;" -->O3["Sample Splitting\nS24_Sample_splitting"]

O4("Heritage Sample\nS13_Sample and\nE19_Physical_object#-1")
class O4 object;
O3["Sample Splitting\nS24_Sample_splitting"] -- "O5_removed #40;1 to n#41;" -->O4["Heritage Sample\nS13_Sample and\nE19_Physical_object"]
;
```

## Models

The following models are defined under the `models/` folder. Each section lists the available versions and links into the Dynamic Modeller.

<details>
<summary>Samples Model: <a href="https://research.nationalgallery.org.uk/lab/modelling/?url=https://raw.githubusercontent.com/RICHeS-UKRI/HSDS-NG-Models/refs/heads/main/models/samples/sample_model_v1.1.tsv">1.1</a></summary>

## Samples Model Details

| | Date | Author | Model | Comment |
| :-----------: | :-----------: | :-----------: | :-----------: | ----------- |
| :heavy_check_mark: |  |  | [1.1](https://research.nationalgallery.org.uk/lab/modelling/?url=https://raw.githubusercontent.com/RICHeS-UKRI/HSDS-NG-Models/refs/heads/main/models/samples/sample_model_v1.1.tsv) |  |
| | <img width=325 /> |<img width=175 /> | <img width=60 /> | <img width=500 /> |
</details>

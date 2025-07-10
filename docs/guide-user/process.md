# HOPE Business Process

``` mermaid
    flowchart TB
    R -- merge --> P[Program Population]
    T -- lock --> PP[Payment Plan]
    
    subgraph Registration Data Import
        A[Kobo] -- import --> R[RDI]
    end

    subgraph Targeting
        P -- target --> T[Target Population]
    end
    
    subgraph Payment Module
        PP -- approve --> PPA
    end

```

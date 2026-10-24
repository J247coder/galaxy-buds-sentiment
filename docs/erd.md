# ERD (Entity Relationship Diagram)

GitHub renders the diagram below automatically (Mermaid).

```mermaid
erDiagram
    PRODUCTS ||--o{ REVIEWS : "has"
    SOURCES  ||--o{ REVIEWS : "provides"
    REVIEWS  ||--|| SENTIMENT_RESULTS : "scored as"
    REVIEWS  ||--o{ REVIEW_ASPECTS : "mentions"
    ASPECTS  ||--o{ REVIEW_ASPECTS : "tagged in"

    PRODUCTS {
        int product_id PK
        string name
        string series
        int release_year
    }
    SOURCES {
        int source_id PK
        string name
    }
    REVIEWS {
        int review_id PK
        int product_id FK
        int source_id FK
        string author
        text text_raw
        text text_clean
        float rating
        int likes
        datetime published_at
    }
    SENTIMENT_RESULTS {
        int review_id PK, FK
        float compound
        string label
    }
    ASPECTS {
        int aspect_id PK
        string name
    }
    REVIEW_ASPECTS {
        int review_id FK
        int aspect_id FK
        float compound
        string label
    }
```

## Relationships in words
- One **product** has many **reviews** (1 : N).
- One **source** (YouTube, web site) provides many **reviews** (1 : N).
- One **review** has exactly one **sentiment result** (1 : 1).
- A **review** can mention many **aspects** and an **aspect** appears in many reviews (M : N), resolved by the `review_aspects` table.

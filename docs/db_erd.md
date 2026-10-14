# KisanSathi — Database Entity Relationship Diagram (ERD)

## 1. Relational Schema Diagram (Mermaid)

```mermaid
erDiagram
    users ||--o{ farmer_profiles : "has"
    users ||--o{ scans : "performs"
    users ||--o{ conversations : "participates"
    users ||--o{ alerts : "receives"
    users ||--o{ consents : "grants"
    users ||--o{ audit_logs : "triggers"

    farmer_profiles ||--o{ farms : "owns"
    farms ||--o{ farm_crops : "cultivates"
    farms ||--o{ scans : "associated_with"
    crops ||--o{ farm_crops : "referenced_in"

    conversations ||--o{ messages : "contains"
    conversations ||--o{ agent_traces : "records"

    knowledge_documents ||--o{ knowledge_chunks : "chunked_into"

    users {
        uuid id PK
        string phone UK
        string email UK
        string hashed_password
        enum role "farmer | officer | admin"
        string preferred_language "en | hi | gu"
        boolean is_active
        datetime consent_given_at
        datetime created_at
        datetime updated_at
    }

    farmer_profiles {
        uuid id PK
        uuid user_id FK
        string full_name
        string village
        string taluka
        string district
        string state
        boolean onboarding_completed
    }

    farms {
        uuid id PK
        uuid farmer_profile_id FK
        string name
        float latitude
        float longitude
        float area_hectares
        enum soil_type "black | clay | loam | sandy | red"
        enum irrigation_type "drip | sprinkler | flood | canal | rainfed"
        datetime created_at
    }

    crops {
        uuid id PK
        string name_en
        string name_hi
        string name_gu
        string botanical_name
        string category "Kharif | Rabi | Zaid | Annual"
    }

    farm_crops {
        uuid id PK
        uuid farm_id FK
        uuid crop_id FK
        date sowing_date
        date expected_harvest_date
        enum current_stage "sowing | vegetative | flowering | boll_formation | maturity | harvest"
        float area_hectares
    }

    scans {
        uuid id PK
        uuid user_id FK
        uuid farm_id FK
        string image_path
        string predicted_label
        float confidence
        enum severity "low | medium | high | critical"
        json treatment_steps
        json prevention_tips
        json sources
        boolean is_mock
        datetime created_at
    }

    alerts {
        uuid id PK
        uuid user_id FK
        enum alert_type "weather | pest | price | irrigation | system"
        enum severity "info | warning | critical"
        string title
        string body
        datetime read_at
        datetime created_at
    }

    market_prices {
        uuid id PK
        string mandi_name
        string district
        string state
        string crop_name
        date price_date
        float min_price_inr
        float max_price_inr
        float modal_price_inr
        string unit "quintal"
        string source
        datetime created_at
    }

    conversations {
        uuid id PK
        uuid user_id FK
        string title
        datetime created_at
    }

    messages {
        uuid id PK
        uuid conversation_id FK
        enum role "user | assistant | system"
        string content
        string language "en | hi | gu"
        enum channel "whatsapp | web"
        json sources
        datetime created_at
    }

    agent_traces {
        uuid id PK
        string trace_id UK
        uuid conversation_id FK
        string intent
        json agents_used
        float total_latency_ms
        int total_tokens
        boolean is_mock
        datetime created_at
    }

    audit_logs {
        uuid id PK
        uuid user_id FK
        string action
        string target_resource
        string ip_address
        json details
        datetime created_at
    }
```

## 2. Constraints & Indexing Strategy
- **UUIDs everywhere:** All primary keys utilize RFC 4122 Version 4 UUIDs for secure distributed sharding and no enumerability attacks.
- **Indexes:**
  - `market_prices (crop_name, mandi_name, price_date DESC)` for fast mandi time-series charting.
  - `scans (user_id, created_at DESC)` for farmer scan history gallery.
  - `scans (predicted_label, created_at)` for spatial outbreak cluster grouping.
  - `alerts (user_id, read_at)` for quick unread badge count queries.
  - `farm_crops (farm_id, current_stage)` for crop stage timeline overlays.

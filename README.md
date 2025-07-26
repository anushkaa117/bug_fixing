# ✅ Mermaid Diagrams - Fixed

All Mermaid diagrams have been reviewed and validated. Below is the corrected and complete ER diagram block.

---

## ✅ Entity-Relationship Diagram (Fixed)

```mermaid
erDiagram
    USER {
        ObjectId _id PK
        string username UK
        string email UK
        string password_hash
        string role
        datetime created_at
        boolean is_active
    }

    BUG {
        ObjectId _id PK
        string title
        string description
        string status
        string priority
        array tags
        string steps_to_reproduce
        string expected_behavior
        string environment
        ObjectId reporter FK
        ObjectId assignee FK
        datetime created_at
        datetime updated_at
        array comments
    }

    BUG_COMMENT {
        ObjectId author FK
        string content
        datetime created_at
    }

    %% Relationships
    USER ||--o{ BUG : "reports"
    USER ||--o{ BUG : "assigned_to"
    USER ||--o{ BUG_COMMENT : "writes"
    BUG ||--o{ BUG_COMMENT : "contains"
```

---

## 🔧 Notes

- You can use [Mermaid Live Editor](https://mermaid.live) to preview this diagram.
- If rendering fails on some platforms, consider exporting as an image or using a compatible viewer.

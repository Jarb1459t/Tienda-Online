# Diseño de Arquitectura de Base de Datos Relacional

**Proyecto:** Plataforma de Tienda Online para la Automatización de Procesos Comerciales y Gestión de Ventas
**Autor:** Alvaro Jose Ruiz Benitez
**Programa:** Análisis y Desarrollo de Software (SENA, 2026)

Este documento contiene la estructura formal, lógica y física de la base de datos relacional. El modelo ha sido normalizado hasta la Tercera Forma Normal (3FN) para evitar redundancias, garantizar la integridad referencial y soportar el flujo transaccional de la tienda online y el sistema POS.

---

## 1. Diagrama de Base de Datos (Modelo Entidad-Relación - MER)

El siguiente diagrama en bloques de Mermaid.js mapea las 8 entidades iniciales del sistema, sus claves primarias (PK), claves foráneas (FK) y sus respectivas relaciones de cardinalidad.

```mermaid
erDiagram
    roles {
        int id PK
        string name "NOT NULL"
        string description
    }
    users {
        int id PK
        int role_id FK
        string name "NOT NULL"
        string email "UK, NOT NULL"
        string password "NOT NULL"
        datetime created_at
    }
    addresses {
        int id PK
        int user_id FK
        string address_line1 "NOT NULL"
        string city "NOT NULL"
        string state "NOT NULL"
        string postal_code
        string phone "NOT NULL"
    }
    categories {
        int id PK
        string name "NOT NULL"
        string description
    }
    products {
        int id PK
        int category_id FK
        string name "NOT NULL"
        string description
        decimal price "NOT NULL"
        int stock "NOT NULL"
        string status "NOT NULL"
    }
    orders {
        int id PK
        int user_id FK
        int address_id FK
        datetime order_date "NOT NULL"
        decimal total "NOT NULL"
        string status "NOT NULL"
    }
    order_items {
        int id PK
        int order_id FK
        int product_id FK
        int quantity "NOT NULL"
        decimal unit_price "NOT NULL"
        decimal subtotal "NOT NULL"
    }
    payments {
        int id PK
        int order_id FK
        datetime payment_date "NOT NULL"
        decimal amount "NOT NULL"
        string payment_method "NOT NULL"
        string status "NOT NULL"
    }

    roles ||--o{ users : "defines"
    users ||--o{ addresses : "has"
    users ||--o{ orders : "places"
    addresses ||--o{ orders : "receives"
    categories ||--o{ products : "classifies"
    orders ||--|{ order_items : "contains"
    products ||--o{ order_items : "is_included"
    orders ||--o{ payments : "has"
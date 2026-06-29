# Arquitectura de Datos y Diseño de la Base de Datos

**Proyecto:** Plataforma de Tienda Online para la Automatización de Procesos Comerciales y Gestión de Ventas
**Autor:** Alvaro Jose Ruiz Benitez
**Programa:** Análisis y Desarrollo de Software (SENA, 2026)

Este documento detalla la estructura lógica y física de la base de datos relacional diseñada para soportar el almacenamiento persistente, la integridad de la información y las transacciones comerciales de la tienda online y el sistema POS.

---

## 1. Modelo Entidad-Relación (MER) en Mermaid.js

El siguiente diagrama representa las entidades del sistema, sus atributos clave y las relaciones cardinales necesarias para garantizar la consistencia en la gestión de usuarios, inventarios y ventas.

```mermaid
erDiagram
    USUARIO {
        int id_usuario PK
        string nombre "NOT NULL"
        string email "UK, NOT NULL"
        string contrasenia "NOT NULL"
        string rol "NOT NULL"
        datetime fecha_registro
    }
    CATEGORIA {
        int id_categoria PK
        string nombre_categoria "NOT NULL"
        string descripcion
    }
    PRODUCTO {
        int id_producto PK
        int id_categoria FK
        string nombre_producto "NOT NULL"
        string descripcion
        decimal precio "NOT NULL"
        int stock "NOT NULL"
        string estado "NOT NULL"
    }
    PEDIDO {
        int id_pedido PK
        int id_usuario FK
        datetime fecha_pedido "NOT NULL"
        decimal total "NOT NULL"
        string estado_pedido "NOT NULL"
        string metodo_pago "NOT NULL"
    }
    DETALLE_PEDIDO {
        int id_detalle PK
        int id_pedido FK
        int id_producto FK
        int cantidad "NOT NULL"
        decimal precio_unitario "NOT NULL"
        decimal subtotal "NOT NULL"
    }

    USUARIO ||--o{ PEDIDO : "realiza"
    CATEGORIA ||--o{ PRODUCTO : "clasifica"
    PEDIDO ||--|{ DETALLE_PEDIDO : "contiene"
    PRODUCTO ||--o{ DETALLE_PEDIDO : "se_incluye"
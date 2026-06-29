# Especificación de Requisitos del Software - Tienda Online
**Proyecto:** Plataforma de Tienda Online para la Automatización de Procesos Comerciales y Gestión de Ventas
**Autor:** Alvaro Jose Ruiz Benitez
**Institución:** SENA - Análisis y Desarrollo de Software (2026)

## 1. Introducción y Alcance
El sistema automatiza los procesos comerciales (ventas, inventarios, clientes y reportes administrativos) de un negocio a través de una interfaz web moderna, segura y accesible desde cualquier dispositivo. Mitiga fallas comunes como errores manuales, pérdidas de información y desactualización de inventarios.

## 2. Matriz de Stakeholders (Poder / Interés)
Mapeo estratégico de los interesados del proyecto gestionado en Notion:

| Interesado | Rol | Nivel de Poder | Nivel de Interés |
| :--- | :--- | :--- | :--- |
| Propietario del negocio | Patrocinador / Cliente final | Alto | Alto |
| Administrador | Gestión operativa del sistema | Medio | Alto |
| Clientes | Usuarios finales compradores | Bajo | Alto |
| Proveedor | Suministro de mercancía | Bajo | Medio |
| Equipo de desarrollo | Construcción técnica del software | Alto | Alto |

## 3. Clasificación de Requisitos (Metodología MoSCoW)
Los requisitos han sido priorizados bajo el framework MoSCoW en un flujo Kanban de cinco estados (*Pendiente, En análisis, Aprobado, En desarrollo, Validado*):

### Requisitos Funcionales (Must Have / Críticos)
* **RF-01:** Módulo de Registro y Autenticación de Usuarios de forma segura.
* **RF-02:** Catálogo e inventario interactivo con filtros por categoría.
* **RF-03:** Carrito de compras funcional que calcule subtotales y totales dinámicamente.
* **RF-04:** Procesamiento, confirmación de pedidos y facturación automática.

### Requisitos No Funcionales y Técnicos (Should / Could Have)
* **RNF-01 (Seguridad):** Control de accesos basado en roles de usuario (`Cliente`, `Administrador`).
* **RNF-02 (Rendimiento):** Disponibilidad y diseño adaptativo (*Responsive Design*) para dispositivos móviles.
* **RNF-03 (Infraestructura):** Soporte técnico para trabajo en red y exportación de reportes administrativos en formatos PDF/Excel.

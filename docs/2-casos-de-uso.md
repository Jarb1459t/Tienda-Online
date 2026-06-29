# Modelado Dinámico: Historias de Usuario y Casos de Uso

A partir del levantamiento de información y el prototipado, se estructuran las interacciones clave del sistema.

## 1. Diagrama de Casos de Uso General (UML)

```mermaid
usecaseDiagram
    direction LR
    actor Cliente as "Cliente / Visitante"
    actor Admin as "Administrador"

    rectangle "Sistema Tienda Online" {
        Cliente --> (HU-02: Registrar Cuenta)
        Cliente --> (HU-01: Iniciar Sesión)
        Cliente --> (HU-03: Consultar Catálogo)
        Cliente --> (HU-04: Gestionar Carrito y Pedido)

        (HU-04: Gestionar Carrito y Pedido) .> (Validar Stock) : include
        (HU-04: Gestionar Carrito y Pedido) .> (Procesar Pago) : include

        Admin --> (HU-01: Iniciar Sesión)
        Admin --> (Gestionar Productos e Inventario)
        Admin --> (Generar Reportes Administrativos)
    }

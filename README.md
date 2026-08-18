# Sistema ERP de Comercio — Mr. Miga

Base de datos relacional que centraliza la operación de **Mr. Miga**, una cadena de comida rápida con locales físicos, ventas por delivery propio y ventas a través de plataformas externas (Rappi, PedidosYa, etc.).

📄 **Documentación del diseño e implementación:** [Ver PDF en Google Drive](https://drive.google.com/file/d/1yYtESyFdqR6ZUwis-ucYmx7_wr-DVf6A/view?usp=sharing)

## 🎯 Propósito

Hoy en día, la información de ventas de Mr. Miga vive dispersa en hojas de cálculo distintas para cada canal (local, delivery, plataformas), lo que genera procesos manuales lentos y propensos a error a la hora de consolidar ventas. Esta base de datos resuelve ese problema centralizando en un solo modelo:

- El registro de **personas, clientes y empleados** (incluyendo repartidores y personal en planilla).
- Los **pedidos**, sin importar si se hicieron de forma presencial, por delivery propio o mediante una plataforma externa.
- Los **pagos y comprobantes** (boleta o factura).
- El **catálogo de productos, promociones, toppings e ingredientes**, con control de stock.
- Un **sistema de puntos de fidelización**, listo para usarse sin necesidad de rediseñar la base de datos.

## 🗃️ Qué contiene la base de datos

El modelo está compuesto por 21 tablas, organizadas en cuatro grupos:

| Grupo | Tablas |
|---|---|
| Personas y personal | Persona, Cliente, Empleado, Repartidor, Local, Planilla |
| Fidelización y pagos | CuentaPuntos, Movimiento_puntos, Pago, Boleta, Factura |
| Pedidos | Pedido, Pedido_presencial, Pedido_delivery, Pedido_plataforma |
| Catálogo | Producto, Promocion, Incluye, Detalle_pedido, Topping, Detalle_topping, Ingrediente, Usa |

Implementada en **PostgreSQL**, administrada con DBeaver / pgAdmin.

## ✅ Qué se hizo y qué se simuló

- **Modelo Entidad-Relación → Modelo Relacional:** diseño completo pasando de reglas semánticas del negocio (por ejemplo, que un pedido no puede ser presencial, delivery y de plataforma a la vez) a tablas, llaves primarias y foráneas.
- **Carga de datos experimentales:** se insertaron registros representativos (locales, productos, personas, pedidos, pagos) para validar que el modelo funciona correctamente de punta a punta.
- **Simulación de datos faltantes:** se simularon valores nulos en campos que en la operación real podrían no llegar completos (referencia de delivery, alias de cliente en plataforma, celular de contacto), para comprobar que el diseño tolera información incompleta sin romper la integridad del sistema.
- **Consultas de negocio:** se implementaron consultas para responder preguntas reales del negocio — producto más vendido, comparación entre canal presencial vs. virtual, edad promedio de clientes en horario de almuerzo, y canal que genera más ingresos — pensadas además como base para un experimento de optimización con distintos volúmenes de datos e índices.
- **Triggers adicionales:** se agregaron triggers para reforzar en la base de datos reglas de negocio que una llave foránea o un CHECK no pueden validar por sí solos (por ejemplo, que un mismo pago no tenga boleta y factura a la vez, o que los puntos de fidelización se acumulen automáticamente con cada pago).

## 📁 Estructura del repositorio

```
├── 01_creacion_tablas.sql                 # Creación de las 21 tablas del modelo
├── 02_insercion_datos_experimentales.sql  # Carga de datos iniciales/experimentales
├── 03_simulacion_datos_faltantes.sql      # Simulación de valores nulos
├── 04_consultas.sql                       # Consultas de negocio
├── 05_triggers.sql                        # Triggers de integridad y automatización
└── README.md
```

## ▶️ Orden de ejecución

1. `01_creacion_tablas.sql`
2. `05_triggers.sql`
3. `02_insercion_datos_experimentales.sql`
4. `03_simulacion_datos_faltantes.sql`
5. `04_consultas.sql`

## 🔗 Más detalles

Para ver el diseño completo (reglas semánticas, modelo E-R, paso al modelo relacional y experimento de optimización de consultas), revisa el [documento del proyecto](https://drive.google.com/file/d/1yYtESyFdqR6ZUwis-ucYmx7_wr-DVf6A/view?usp=sharing).

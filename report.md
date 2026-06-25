# Informe del Proyecto – Il Gusto Giusto

**Autor:** José Rafael Pérez Rivero   

---

## 1. Introducción y dominio elegido

**Il Gusto Giusto** es un sistema de gestión integral para un restaurante italiano. El proyecto aborda el problema de planificar eventos (comandas) que consumen recursos limitados (mesas, chefs, ingredientes) respetando restricciones temporales y reglas culinarias. La aplicación simula la operación diaria de un restaurante y ofrece herramientas administrativas para la carta, el personal, los suministros y la contabilidad.

Se eligió el dominio de la restauración porque permite modelar con claridad las nociones de eventos, recursos compartidos y reglas de negocio, cumpliendo así con los requisitos del planificador inteligente de eventos. Además, el contexto italiano aporta restricciones culturales que enriquecen la lógica del sistema.

---

## 2. Modelado del dominio

### 2.1 Eventos
Cada pedido de una mesa se traduce en un **Evento** (clase `Event` en `src/models/events.py`). Un evento contiene:
- **ID único** (`evt_xxxxxxxx`).
- **ID de la comanda** (`order_id`).
- **Mesa asignada** (`table_id`).
- **Chef asignado** (`assigned_chef_id`).
- **Intervalo de tiempo**: `start_time` y `end_time` calculados a partir del plato con mayor tiempo de preparación.
- **Platos** (`dishes`): diccionario `{dish_id: cantidad}`.
- **Personalizaciones** (`customized_removals`): ingredientes que el cliente decidió quitar.

### 2.2 Recursos

- **Mesas** (`Table`): tienen un número, capacidad máxima y un flag `is_occupied`. Son finitas y solo pueden atender una comanda a la vez.
- **Chefs** (`Employee` con rol `CHEF`): poseen nivel de experiencia (`JUNIOR` o `SENIOR`), una lista de especialidades culinarias (ej. `pasta`, `pizza`) y atributos para controlar disponibilidad (`is_available`, `busy_until`). Solo un chef puede cocinar para una mesa en un mismo intervalo.
- **Ingredientes** (`Ingredient`): tienen una cantidad disponible, unidad, precio unitario y un umbral mínimo (`min_quantity`) que dispara alertas de reabastecimiento.

### 2.3 Restricciones implementadas

El proyecto incluye dos tipos de restricciones modeladas mediante un sistema extensible de clases abstractas (patrón Strategy):

1. **Exclusión mutua** (`MutualExclusionConstraint`) – «Tradición Italiana (Mar & Queso)»:  
   No se permite ordenar platos de las categorías `seafood` y `cheese_heavy` en una misma comanda.  
   *Ejemplo*: un cliente no puede pedir *Spaghetti ai Frutti di Mare* junto con *Gnocchi al Gorgonzola*.

2. **Co‑requisito** (`CoRequirementConstraint`) – «Soporte de Trufa»:  
   Los platos de la categoría `truffle_specialty` requieren que exista aceite de trufa en la despensa (stock > 0).  
   *Ejemplo*: si el inventario de `truffle_oil` se agota, el plato *Tagliatelle al Tartufo* queda automáticamente deshabilitado.

Ambas reglas se evalúan tanto en la planificación inmediata como en la búsqueda de huecos, garantizando que nunca se programe un evento que las viole.

---

## 3. Arquitectura del software

La aplicación sigue una arquitectura modular en capas, respetando los principios SOLID y las buenas prácticas de Python.

### 3.1 Capas y responsabilidades

- **`src/models/`** – Entidades del dominio como dataclasses: `Restaurant`, `Employee`, `Table`, `Dish`, `Ingredient`, `Order`, `Event`. Cada clase tiene una única responsabilidad (Single Responsibility). Se usan `Enum` para roles y experiencia, y `dataclass` para minimizar código repetitivo.

- **`src/core/`** – Lógica de negocio central:
  - `EventScheduler` orquesta la planificación: valida colisiones, restricciones, stock y asigna chef.
  - `constraints.py` define la clase abstracta `Constraint` y sus implementaciones concretas. El `ConstraintValidator` ejecuta todas las restricciones, permitiendo añadir nuevas sin modificar el validador (Open/Closed Principle).

- **`src/services/`** – Casos de uso de alto nivel. `RestaurantService` contiene métodos estáticos para contratar/despedir empleados, comprar ingredientes y gestionar el menú (publicar, actualizar, eliminar platos). La función auxiliar `calculate_role_deficit` determina la necesidad de personal según la cantidad de mesas.

- **`src/persistence/`** – Persistencia en JSON. `JSONHandler` ofrece `save`, `load` y `loads` (para importar desde string). Se define una interfaz `StateRepository` como `Protocol` (Interface Segregation) para permitir futuras implementaciones (base de datos, etc.) sin cambiar el resto del sistema.

- **`src/components/`** – Vistas de Streamlit para cada pestaña: dashboard, menú, staff, suministros, finanzas y configuración. Cada componente recibe el estado necesario y un callback `save_callback` para persistir los cambios.

- **`src/ui/`** – Estilos CSS inyectados con Streamlit. Se importan fuentes italianas (`Playfair Display` para títulos, `Lato` para cuerpo) y se definen reglas para la barra lateral, tarjetas, popovers, etc.

### 3.2 Principios SOLID aplicados

- **S (Single Responsibility):** Cada clase y módulo tiene una única razón de cambio. Por ejemplo, `EventScheduler` solo maneja la planificación, no la persistencia.
- **O (Open/Closed):** El sistema de restricciones está abierto a extensión pero cerrado a modificación; se pueden agregar nuevas reglas creando subclases de `Constraint`.
- **L (Liskov):** Las implementaciones concretas de `Constraint` pueden sustituir a la clase base sin alterar el comportamiento del validador.
- **I (Interface Segregation):** La interfaz `StateRepository` expone solo los métodos necesarios (`save`, `load`), sin forzar dependencias innecesarias.
- **D (Dependency Inversion):** Los componentes de alto nivel (vistas) no dependen de la implementación concreta de persistencia; se pasa una instancia de `JSONHandler` (o cualquier otra que implemente `StateRepository`).

### 3.3 Otras buenas prácticas

- **Nomenclatura en inglés:** Todas las variables, funciones y comentarios están en inglés, mientras que la interfaz de usuario se presenta en español.
- **Type hints:** Todas las funciones públicas incluyen anotaciones de tipo.
- **Documentación:** Cada función y clase relevante tiene docstrings.
- **Código limpio:** Se evita la duplicación, se utilizan list comprehensions y métodos descriptivos.

---

## 4. Funcionamiento del planificador (EventScheduler)

### 4.1 `schedule_order(order, start_time)`

Es la operación central del sistema. Realiza las siguientes validaciones en orden:
1. **Existencia de la mesa y los platos.**
2. **Colisión de mesa:** verifica con `_is_resource_free` que la mesa no esté ocupada en el intervalo `[start_time, end_time]`.
3. **Validación de restricciones:** invoca `ConstraintValidator.validate` con los platos y el inventario de ingredientes.
4. **Disponibilidad de stock:** calcula la cantidad necesaria de cada ingrediente, descontando los ingredientes opcionales que el cliente decidió quitar. Si algún ingrediente falta, rechaza el pedido.
5. **Asignación de chef:** busca un chef con la especialidad requerida (si el plato lo exige) y que esté libre en el intervalo.

Si todo se cumple, descuenta los ingredientes, crea un `Event`, marca la mesa como ocupada, el chef como no disponible, y registra una transacción de ingreso en el historial contable.

### 4.2 `find_next_available_slot(order)`

Busca el siguiente hueco libre dentro de las próximas 24 horas. Utiliza `_dry_run_validation`, que replica las mismas comprobaciones pero sin modificar el estado. Itera en pasos de 5 minutos. Si encuentra un slot válido, lo retorna; en caso contrario, devuelve `None`. El sistema de UI muestra el horario sugerido y permite confirmar la reserva.

### 4.3 `cancel_event(event_id)`

Libera la mesa y el chef, devuelve los ingredientes al inventario y **revierte el ingreso económico** mediante una transacción negativa. Así la contabilidad se mantiene exacta. Este método se invoca manualmente desde el dashboard o automáticamente al despedir a un chef con comandas activas.

### 4.4 Control de colisiones

El método `_is_resource_free(res_id, start, end, res_type)` comprueba solapamiento de intervalos comparando el inicio y fin del evento candidato con los eventos ya planificados para ese recurso. Soporta tanto mesas como chefs cambiando el `res_type`.

---

## 5. Servicios de negocio (RestaurantService)

Los métodos estáticos de `RestaurantService` encapsulan operaciones complejas para mantener la coherencia del estado:

- **`hire_employee`**: Verifica que el balance cubra el sueldo diario, crea un nuevo `Employee`, lo agrega a la nómina, descuenta el sueldo y elimina al candidato de la bolsa.
- **`fire_employee`**: Elimina al empleado de la nómina. Previamente, desde la vista de staff se cancelan todos sus eventos activos para dejar el sistema consistente.
- **`purchase_ingredients`**: Recorre los ingredientes seleccionados, calcula el costo total, verifica saldo, suma las cantidades y registra la transacción.
- **`publish_dish`, `update_dish`, `delete_dish`**: Gestionan el menú, validando que los datos sean correctos (nombre no vacío, al menos un ingrediente).

### 5.1 Déficit de personal

La función `calculate_role_deficit` calcula cuántos empleados de un rol hacen falta, basándose en una proporción entre mesas y personal. Por ejemplo, un camarero por cada dos mesas, un chef por cada tres. Este valor se usa para ordenar la bolsa de empleo y mostrar al usuario qué candidatos son más urgentes.

---

## 6. Interfaz de usuario

La aplicación está organizada en **seis pestañas**, accesibles desde la barra lateral.

### 6.1 Dashboard (Servicio)

- **Tarjetas de mesas:** Muestra cada mesa con su capacidad y estado (ocupada/disponible). Si está libre, un popover permite «Tomar Comanda»: seleccionar platos, cantidades y quitar ingredientes opcionales. Al enviar, se invoca `schedule_order`. Si está ocupada, muestra los detalles del servicio y un botón para «Liberar Mesa».
- **Búsqueda de hueco:** Junto al botón de enviar, hay un botón «Buscar próximo hueco» que llama a `find_next_available_slot`. Si encuentra slot, lo muestra y permite confirmar la reserva.
- **Estado de chefs:** Panel inferior que lista los chefs y su estado actual (cocinando / disponible), incluyendo especialidades.
- **Cronograma:** Tabla con todas las comandas planificadas, mostrando mesa, chef, horario y estado (en preparación, esperando, finalizado).

### 6.2 Gestión del Menú

Dos subpestañas:
- **Ver y Editar Platos:** Selector de plato existente, visualización con badges de categoría, lista de ingredientes (indispensables/opcionales). Permite editar sus parámetros (precio, tiempo, categoría, especialidad, ingredientes) o eliminarlo.
- **Agregar Nuevo Plato:** Formulario completo para crear una receta desde cero, eligiendo ingredientes y marcando cuáles son base.

### 6.3 Contrataciones (Staff)

- **Nómina Activa:** Lista de empleados filtrable por puesto. Cada empleado muestra su rol, experiencia, sueldo y especialidades. Botón «Despedir» que, para chefs, cancela automáticamente todas sus comandas (liberando mesas e ingredientes) antes de eliminarlos.
- **Bolsa de Empleo:** Muestra candidatos ordenados según un algoritmo multicapa: prioriza el rol con mayor déficit, luego la experiencia (senior primero) y finalmente el menor salario. Se muestran con badges de rol, experiencia y un tag «ALTA PRIORIDAD» si corresponden al rol deficitario.
- **Añadir Candidato:** Formulario externo para registrar nuevos postulantes, incluyendo especialidades personalizadas.

### 6.4 Compras y Suministros

- **Alertas de stock:** Mensaje de advertencia con los ingredientes por debajo del mínimo.
- **Inventario:** Visualización con barras de progreso y badges de estado (agotado, crítico, suficiente).
- **Pedido mayorista:** Permite seleccionar cantidades de cada ingrediente, calcula subtotales y total, y procesa la compra verificando el saldo.

### 6.5 Libro de Contabilidad

- **Balance general:** KPIs de capital, número de transacciones y último movimiento.
- **Gráfico de evolución:** `area_chart` del saldo a lo largo del tiempo.
- **Libro diario:** Tabla con todas las transacciones, ordenable y con formato de moneda.
- **Rentabilidad de recetas:** Calcula costo de ingredientes vs precio de venta, muestra margen de ganancia con barras de progreso y clasifica los platos en «Oportunidades de Mejora» (margen <40%) y «Platos Estrella» (margen ≥40%).

### 6.6 Configuración

- **Exportar:** Genera un archivo JSON del estado actual y permite descargarlo.
- **Importar:** Permite subir un archivo JSON y reemplaza completamente el estado del restaurante, con validación de formato.
- **Reiniciar:** Restaura el restaurante a los valores de `default_config.json`.

### 6.7 Estilos visuales

Se inyecta CSS personalizado que:
- Importa las fuentes `Playfair Display` y `Lato` desde Google Fonts.
- Aplica estilos a los botones de la barra lateral, con efecto hover y resaltado del activo.
- Da sombra, bordes redondeados y efecto de elevación a las tarjetas (`st.container(border=True)`).
- Estiliza los popovers y formularios.

El encabezado (`render_italian_header`) muestra los tres colores de la bandera italiana y el título en la fuente `Playfair Display`.

### 6.8 Notificaciones

Para evitar que los mensajes de éxito/error desaparezcan tras un `st.rerun()`, se utiliza un patrón de alertas persistentes en `st.session_state`:
- `menu_alert` y `staff_alert` almacenan un diccionario con `type` y `msg`. Al inicio de cada componente, se verifica si existe una alerta, se muestra y se elimina.
- Esto asegura que el usuario vea la confirmación después de una acción (por ejemplo, «Plato eliminado con éxito»).

---

## 7. Persistencia

### 7.1 `JSONHandler`

- **`save(restaurant, events, filepath)`**: serializa todas las entidades (empleados, mesas, menú, ingredientes, historial, candidatos, eventos) a un diccionario y lo guarda como JSON. Los enums se convierten a strings usando `getattr(obj, 'value', obj)`, garantizando compatibilidad.
- **`load(filepath)`**: carga el archivo y reconstruye los objetos con sus tipos correctos (convierte strings a `EmployeeRole`, `ExperienceLevel`, etc.). Si el archivo no existe, retorna `None`.
- **`loads(json_str)`**: carga desde una cadena JSON, útil para la importación de archivos subidos por el usuario.
- **`_parse_data(data)`**: método interno que centraliza la reconstrucción del modelo a partir de un diccionario, evitando duplicación de código entre `load` y `loads`.

### 7.2 Flujo de inicialización (`init_state` en `main.py`)

Al iniciar la aplicación, se busca `restaurant_state.json`; si no existe, se carga `default_config.json`. Luego se procesan los eventos: los ya finalizados liberan sus recursos, los activos se marcan, y se filtran eventos huérfanos (cuyo chef fue eliminado en una versión anterior). Finalmente, se guarda el estado reconstruido en `st.session_state`.

### 7.3 Exportación/importación desde la UI

La pestaña Configuración permite al usuario descargar el estado actual como JSON y cargar un nuevo estado desde un archivo. Esto facilita respaldos, transferencias y pruebas con diferentes escenarios.

---

## 8. Pruebas unitarias

El archivo `tests/test_scheduler.py` contiene una batería de tests con `pytest` que cubren:

- **Planificación exitosa** y casos de error: mesa inválida, plato inexistente, colisión de mesa/chef, cantidad cero, asignación incorrecta de rol.
- **Cancelación de eventos**: liberación de mesa y chef, devolución exacta de ingredientes (incluso con personalizaciones).
- **Restricciones**: co‑requisito de trufa y exclusión mutua.
- **Stock insuficiente** y no consumo de ingredientes opcionales.
- **Búsqueda de huecos**: después de un evento, respetando restricciones y con el sistema vacío.
- **Persistencia**: guardar y cargar correctamente el estado, incluyendo archivos inexistentes.
- **Cálculo de déficit de personal**.

Todos los tests se ejecutan con `pytest` desde la raíz del proyecto, validando la robustez del motor de planificación.

---

## 9. Conclusión

**Il Gusto Giusto** integra de forma cohesiva los conceptos fundamentales del proyecto: planificación de eventos, recursos compartidos, restricciones personalizadas y persistencia. La arquitectura modular, el uso de patrones SOLID, las buenas prácticas de Python y una interfaz cuidada con temática italiana convierten al sistema en una aplicación profesional y mantenible.

El sistema cumple con todos los requisitos del enunciado y además incorpora funcionalidades avanzadas como la gestión de personal con priorización automática, análisis de rentabilidad, y exportación/importación de estado. Las pruebas unitarias aseguran la corrección del núcleo, y la persistencia en JSON permite retomar la operación en cualquier momento.

---

*Documento generado para el proyecto Il Gusto Giusto – MATCOM, curso 2025-26.*
# 🍕 Il Gusto Giusto – Sistema Inteligente de Gestión de Restaurantes

**Planificador Inteligente de Eventos** aplicado a un restaurante italiano de alto nivel.

## 📖 Dominio y justificación

Il Gusto Giusto es un restaurante gourmet especializado en cocina italiana tradicional.  
Los **eventos** son los **pedidos de los clientes**; los **recursos** son las **mesas**, los **chefs** y los **ingredientes**.  
Cada pedido tiene una duración (tiempo de preparación) y consume recursos finitos que no pueden solaparse.

El sistema no solo gestiona las órdenes, sino que controla todo el flujo del restaurante: menú, contrataciones, compras y finanzas, cumpliendo el modelo de planificador de eventos con restricciones personalizadas.

## 🧠 Restricciones de dominio implementadas

### 1. Co‑requisito (Inclusión)
- **Categoría `truffle_specialty`** → Obliga a tener **Olio al Tartufo** en stock.  
  _Ejemplo:_ No se puede preparar "Tagliatelle al Tartufo" si no hay aceite de trufa en la despensa.

### 2. Exclusión Mutua
- **Categoría `seafood`** no puede combinarse con **`cheese_heavy`** en el mismo pedido.  
  _Regla cultural italiana:_ No se mezclan mariscos con quesos fuertes como el Gorgonzola.

Ambas reglas están modeladas con el patrón **Strategy** (`core/constraints.py`) y se validan automáticamente al crear un pedido.

## 🚀 Funcionalidades (Fases)

| Fase | Pestaña | Descripción |
|------|---------|-------------|
| 1 | **Servicio (Dashboard)** | Ver mesas ocupadas/libres, tomar comandas, quitar ingredientes opcionales, asignar chefs automáticamente respetando especialidades y disponibilidad. |
| 2 | **Gestión del Menú** | Añadir, editar y eliminar platos, definir ingredientes base/opcionales y categorías. |
| 3 | **Contrataciones (Staff)** | Ver empleados activos, despedir. Bolsa de trabajo inteligente: prioriza candidatos del rol que más falta al restaurante (cálculo automático de déficit). |
| 4 | **Compras y Suministros** | Inventario de ingredientes con alertas de stock crítico. Tienda para reabastecer, descontando del balance. Platos bloqueados si falta algún ingrediente. |
| 5 | **Libro de Contabilidad** | Balance en tiempo real, gráfico de evolución temporal, análisis de rentabilidad por plato con consejos automáticos. |

## ⏱️ Motor de planificación

- **Planificar evento (`schedule_order`)**: Valida conflicto de mesas, disponibilidad de chef especializado, stock y restricciones. Si todo es correcto, crea un `Event` con intervalo de tiempo definido.
- **Buscar hueco automático (`find_next_available_slot`)**: Analiza el calendario futuro (cada 5 minutos) hasta encontrar la primera ventana donde mesa y chef estén libres y se cumplan las condiciones.
- **Cancelar evento**: Libera mesa y chef, revirtiendo estados.
- **Persistencia**: Todo el estado se guarda en un archivo JSON al finalizar cada operación.

## 🔧 Estructura del código (SOLID)

src/
    
    ├── core/ → Lógica de planificación (scheduler) y restricciones.

    ├── models/ → Entidades del dominio (dataclasses): Restaurant, Dish, Order, Employee…
    
    ├── persistence/ → Manejo de archivos JSON.
    
    ├── components/ → Vistas de Streamlit (UI).
    
    ├── services/ → Servicios de negocio puros.
    
    └── ui/ → Estilos y temas.



- **Principio de responsabilidad única**: Cada módulo tiene una tarea bien definida.
- **Abierto/Cerrado**: Las restricciones se añaden implementando `Constraint` sin modificar el scheduler.
- **Sustitución de Liskov**: Las subclases de `Constraint` son intercambiables.
- **Segregación de interfaces**: `ConstraintValidator` solo expone `validate()`.
- **Inversión de dependencias**: `EventScheduler` depende de la abstracción `Constraint`, no de implementaciones concretas.

## ▶️ Cómo ejecutar el proyecto desde cero

1. Clona el repositorio e instala dependencias:
   ```bash
   git clone <tu-repo>
   cd Il_Gusto_Giusto
   pip install -r requirements.txt
Asegúrate de que el directorio data/ contenga default_config.json (incluido en el repo).

Ejecuta la aplicación:

```bash 
streamlit run main.py
```
La primera vez se cargará la configuración por defecto. Todas las acciones se guardan automáticamente en data/restaurant_state.json.

## 🧪 Pruebas
Ejecuta todas las pruebas con:

``` bash
pytest tests/
```
Verifica: creación de eventos, colisiones, liberación de recursos, violación de restricciones, co‑requisitos y persistencia.

## 🎨 Personalización visual
La interfaz utiliza la fuente Playfair Display y una paleta granate/oro para recordar la elegancia italiana.
Se aplica mediante CSS inyectado en src/ui/styles.py usando únicamente Streamlit.

## 📦 Tecnologías permitidas
- Python 3.10+
- Streamlit
- Pytest
- pandas


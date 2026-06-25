
<a id="top"></a>

<div align="center">
  <img src="https://img.icons8.com/color/96/pizza.png" alt="Pizza">
  <img src="https://img.icons8.com/color/96/spaghetti.png" alt="Pasta">
  <img src="https://img.icons8.com/color/96/italy.png" alt="Bandera Italia">
  <h1>Il Gusto Giusto</h1>
  <p><em>Sistema de Gestión de Restaurante Italiano</em></p>
</div>

<p align="center">
  <a href="#">
    <img src="https://img.shields.io/badge/made%20with-passione-E760A4.svg" alt="Hecho con pasión">
  </a>
  <a href="https://opensource.org/licenses/MIT" target="_blank">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="Licencia">
  </a>
  <a href="https://www.python.org/downloads/" target="_blank">
    <img src="https://img.shields.io/badge/python-3.12%2B-blue.svg" alt="Python 3.12+">
  </a>
</p>

<div align="center">
  <a href="#-acerca-del-proyecto">Acerca del Proyecto</a>
  <span>&nbsp;✦&nbsp;</span>
  <a href="#-características">Características</a>
  <span>&nbsp;✦&nbsp;</span>
  <a href="#-arquitectura">Arquitectura</a>
  <span>&nbsp;✦&nbsp;</span>
  <a href="#-tecnologías">Tecnologías</a>
  <span>&nbsp;✦&nbsp;</span>
  <a href="#-cómo-empezar">Cómo Empezar</a>
  <span>&nbsp;✦&nbsp;</span>
  <a href="#-instrucciones-de-uso">Instrucciones de Uso</a>
  <span>&nbsp;✦&nbsp;</span>
  <a href="#-restricciones-del-dominio">Restricciones</a>
  <span>&nbsp;✦&nbsp;</span>
  <a href="#-pruebas">Pruebas</a>
  <span>&nbsp;✦&nbsp;</span>
  <a href="#-licencia">Licencia</a>
</div>

<br>

## 📜 Acerca Del Proyecto

**Il Gusto Giusto** es un sistema inteligente de gestión para restaurantes italianos. Modela un restaurante como un conjunto de recursos limitados (mesas, chefs, ingredientes) y las comandas como **eventos** que consumen dichos recursos en intervalos de tiempo. El sistema garantiza que no haya conflictos de horarios (una mesa o un chef nunca se asignan a dos comandas simultáneas) y que se respeten reglas culinarias tradicionales.

El proyecto fue desarrollado aplicando principios SOLID, arquitectura modular, buenas prácticas de Python y una interfaz profesional con Streamlit.

## 💬 Características

- 🕒 **Planificación inteligente**: validación automática de disponibilidad de mesas, chefs, stock de ingredientes y restricciones culinarias.
- 🔍 **Búsqueda de huecos**: encuentra el siguiente intervalo libre para agendar un pedido sin conflictos.
- 🍝 **Menú personalizable**: añadir, editar y eliminar platos, con ingredientes base (indispensables) y opcionales.
- 👥 **Gestión de personal**: contratar y despedir empleados, bolsa de empleo con priorización automática según déficit del restaurante.
- 📦 **Control de inventario**: alertas de stock crítico y compras a proveedores.
- 💰 **Contabilidad completa**: balance, gráfico de evolución, libro diario de transacciones y rentabilidad de recetas.
- ⚙️ **Exportación/importación**: guarda y carga el estado completo del restaurante desde un archivo JSON.
- 🎨 **Interfaz italiana**: tema oscuro elegante con colores terracota, tipografías *Playfair Display* y *Lato*, y animaciones suaves.

<p align="right">(<a href="#top">Volver al inicio 🔝</a>)</p>

## 🏗️ Arquitectura

El código se organiza en capas modulares que siguen los principios **SOLID**:

### Capas del sistema

| Capa | Carpeta | Responsabilidad |
|------|---------|-----------------|
| **Modelos** | `src/models/` | Entidades del dominio (`Restaurant`, `Employee`, `Dish`, `Event`, etc.) como dataclasses. |
| **Core** | `src/core/` | Lógica de planificación (`EventScheduler`) y sistema de restricciones extensible. |
| **Servicios** | `src/services/` | Casos de uso de alto nivel (`RestaurantService`) que orquestan operaciones complejas. |
| **Persistencia** | `src/persistence/` | Guardado y carga en JSON (`JSONHandler`) con interfaz abstracta para futuros cambios. |
| **Componentes** | `src/components/` | Vistas de Streamlit para cada pestaña de la interfaz. |
| **UI** | `src/ui/` | Estilos CSS inyectados y utilidades visuales (fuentes italianas, colores, efectos). |

### Flujo Principal

1. **Inicialización**: carga del estado desde `restaurant_state.json` o `default_config.json`.
2. **Dashboard**: visualización de mesas y chefs en tiempo real, toma de comandas.
3. **Validación**: al enviar un pedido, el `EventScheduler` comprueba colisiones, restricciones, stock y asigna chef.
4. **Persistencia automática**: cada cambio de estado se guarda en disco.
5. **Administración**: pestañas independientes para menú, personal, suministros y contabilidad.
6. **Configuración**: exportar, importar o reiniciar el estado del restaurante.

<p align="right">(<a href="#top">Volver al inicio 🔝</a>)</p>

## 🧰 Tecnologías

- [**Python**](https://www.python.org/): lenguaje principal del proyecto.
- [**Streamlit**](https://streamlit.io/): framework para la interfaz web interactiva.
- [**Pandas**](https://pandas.pydata.org/): manipulación y visualización de datos en tablas y gráficos.
- [**Pytest**](https://docs.pytest.org/): framework de pruebas unitarias.
- **CSS inyectado**: estilizado personalizado del tema oscuro italiano.
- **Dataclasses** y **Enums**: modelado limpio de entidades.
- **Módulo `json`**: persistencia de datos en formato JSON.

<p align="right">(<a href="#top">Volver al inicio 🔝</a>)</p>

## 🚀 Cómo Empezar

### Requisitos

- Python 3.12 
- pip (gestor de paquetes de Python)

### Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/joserafael0160/Il-Gusto-Giusto.git
cd Il-Gusto-Giusto
```

2. Crea un entorno virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  
# En Windows: venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecuta la aplicación:
```bash
streamlit run main.py
```

5. Abre en tu navegador:
```
http://localhost:8501
```

<p align="right">(<a href="#top">Volver al inicio 🔝</a>)</p>

## 📋 Instrucciones de Uso

La aplicación tiene **6 pestañas** accesibles desde la barra lateral:

### 1. 🍽️ Servicio (Dashboard)
- Visualiza el estado de las mesas (🟢 disponible / 🔴 ocupada).
- Toma una comanda: selecciona platos del menú, cantidades y quita ingredientes opcionales.
- Busca el próximo hueco disponible para agendar un pedido.
- Libera mesas y cancela comandas.
- Observa el estado de los chefs (cocinando / disponible) y sus especialidades.

### 2. 📋 Gestión del Menú
- **Ver y Editar**: selecciona un plato, visualiza sus ingredientes (indispensables y opcionales), edita precio, tiempo, categoría o ingredientes.
- **Agregar Nuevo Plato**: crea una receta desde cero, elige ingredientes y márcalos como base si son indispensables.

### 3. 👥 Contrataciones (Staff)
- **Nómina Activa**: lista de empleados filtrable, muestra sueldo, especialidades y permite despedir (cancelando automáticamente las comandas activas del chef).
- **Bolsa de Empleo**: candidatos ordenados por prioridad (déficit del rol → experiencia → salario). Contrata o descarta candidatos.
- **Añadir Candidato**: registra un nuevo postulante con especialidades personalizadas.

### 4. 🛒 Compras y Suministros
- Alerta de ingredientes por debajo del stock mínimo.
- Inventario con barras de progreso y badges de estado (agotado, crítico, suficiente).
- Pedido mayorista: selecciona cantidades, calcula el costo total y procesa la compra (verifica saldo disponible).

### 5. 💰 Libro de Contabilidad
- **Balance**: KPIs de capital, número de transacciones y último movimiento.
- **Gráfico de evolución** del saldo en el tiempo.
- **Libro diario** de transacciones con formato de moneda.
- **Rentabilidad de recetas**: costo vs precio, márgenes de ganancia y clasificación en platos estrella u oportunidades de mejora.

### 6. ⚙️ Configuración
- **Exportar**: descarga el estado actual como archivo JSON.
- **Importar**: carga un archivo JSON y reemplaza el estado del restaurante.
- **Reiniciar**: vuelve a la configuración por defecto.

<p align="right">(<a href="#top">Volver al inicio 🔝</a>)</p>

## 🧠 Restricciones del Dominio

El sistema implementa dos restricciones personalizadas que reflejan la tradición culinaria italiana:

### 🔴 Exclusión Mutua – «Mar y Queso»
No se permite combinar platos de las categorías `seafood` (mariscos) y `cheese_heavy` (quesos fuertes) en una misma comanda.
> *Ejemplo: no se pueden pedir **Spaghetti ai Frutti di Mare** y **Gnocchi al Gorgonzola** juntos.*

### 🟢 Co‑requisito – «Soporte de Trufa»
Los platos de la categoría `truffle_specialty` solo pueden prepararse si existe **aceite de trufa** en el inventario.
> *Ejemplo: si el stock de `truffle_oil` es 0, el plato **Tagliatelle al Tartufo** queda deshabilitado.*

Ambas reglas se validan automáticamente al enviar una comanda y durante la búsqueda de huecos.

<p align="right">(<a href="#top">Volver al inicio 🔝</a>)</p>

## 🧪 Pruebas

El proyecto incluye una batería de **tests unitarios** con `pytest` en la carpeta `tests/`. Para ejecutarlos:

```bash
pytest
```

Cubren los siguientes escenarios:

- Planificación exitosa y rechazo por mesa ocupada, chef no disponible, plato inexistente, etc.
- Verificación de stock insuficiente y no consumo de ingredientes opcionales.
- Cumplimiento y violación de las restricciones de co‑requisito y exclusión mutua.
- Cancelación de eventos con devolución exacta de ingredientes y reversión contable.
- Persistencia: guardar y cargar el estado completo del restaurante.
- Búsqueda del siguiente hueco disponible.
- Cálculo del déficit de personal por rol.

<p align="right">(<a href="#top">Volver al inicio 🔝</a>)</p>

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Sigue estos pasos:

1. Haz un [_fork_](https://github.com/joserafael0160/Il-Gusto-Giusto/fork) del proyecto.
2. Crea una rama para tu feature (`git checkout -b feature/awesome-feature`).
3. Haz commit de tus cambios (`git commit -m 'Add awesome feature'`).
4. Push a la rama (`git push origin feature/awesome-feature`).
5. Abre un [_pull request_](https://github.com/joserafael0160/Il-Gusto-Giusto/pulls).

<p align="right">(<a href="#top">Volver al inicio 🔝</a>)</p>

## 🔑 Licencia

Distribuido bajo licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

<p align="right">(<a href="#top">Volver al inicio 🔝</a>)</p>

## 🙏 Soporte

¿Preguntas o sugerencias? Abre un issue en el repositorio.

No olvides dejar una estrella ⭐️

<p align="right">(<a href="#top">Volver al inicio 🔝</a>)</p>

<br>
<hr>
<p align="center">🍝 ¡Buon appetito e buona gestione! 🍝</p>
<sub><sup>Un proyecto creado por <a href="https://github.com/joserafael0160">@joserafael0160</a></sup></sub>

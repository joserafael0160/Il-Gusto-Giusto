# 🐉 Dragon Restaurant - Sistema de Gestión de Restaurante

## 🎯 Descripción
Sistema de planificación inteligente para restaurantes que gestiona eventos, recursos y optimiza operaciones.

dragon-del-sabor/
│
├── app/                          # Módulo principal de la aplicación
│   ├── __init__.py
│   ├── models/                  # Modelos de datos (clases)
│   │   ├── __init__.py
│   │   ├── restaurant.py       # Restaurante, Mesa, etc.
│   │   ├── employee.py         # Empleado, Candidato
│   │   ├── menu.py             # Plato, Ingrediente
│   │   └── finance.py          # Transacción, Presupuesto
│   │
│   ├── core/                   # Lógica de negocio y simulaciones
│   │   ├── __init__.py
│   │   ├── simulator.py        # Motor de simulación (validaciones, restricciones)
│   │   ├── scheduler.py        # Planificador de eventos (asignación de recursos)
│   │   ├── constraints.py      # Restricciones personalizadas (co-requisito, exclusión)
│   │   └── recommender.py      # Sistema de recomendación de contratación
│   │
│   ├── persistence/            # Persistencia de datos
│   │   ├── __init__.py
│   │   ├── repository.py       # Clase base para repositorios
│   │   ├── restaurant_repo.py  # Guardar/cargar restaurante
│   │   └── file_manager.py     # Manejo de archivos JSON
│   │
│   ├── ui/                     # Interfaz de usuario (Streamlit)
│   │   ├── __init__.py
│   │   ├── pages/              # Páginas de la aplicación
│   │   │   ├── __init__.py
│   │   │   ├── dashboard.py    # Panel principal (Fase 1)
│   │   │   ├── menu.py         # Gestión de menú (Fase 2)
│   │   │   ├── employees.py    # Empleados y contratación (Fase 3)
│   │   │   ├── store.py        # Tienda de ingredientes (Fase 4)
│   │   │   ├── accounting.py   # Contabilidad (Fase 5)
│   │   │   └── settings.py     # Configuración
│   │   │
│   │   ├── components/         # Componentes reutilizables
│   │   │   ├── __init__.py
│   │   │   ├── tables.py       # Componente para mostrar mesas
│   │   │   ├── orders.py       # Componente para pedidos
│   │   │   └── alerts.py       # Alertas de inventario
│   │   │
│   │   └── utils.py            # Utilidades para la UI
│   │
│   ├── services/               # Servicios de aplicación
│   │   ├── __init__.py
│   │   ├── menu_service.py     # Lógica de negocio para menú
│   │   ├── employee_service.py # Lógica para empleados
│   │   └── finance_service.py  # Lógica financiera
│   │
│   └── utils/                  # Utilidades generales
│       ├── __init__.py
│       ├── helpers.py          # Funciones auxiliares
│       └── constants.py        # Constantes del proyecto
│
├── data/                       # Datos persistentes
│   ├── saved/                  # Estados guardados del restaurante
│   │   └── restaurant.json
│   ├── default/                # Configuraciones por defecto
│   │   ├── initial_state.json
│   │   ├── default_menu.json
│   │   └── default_employees.json
│   └── candidates/             # Candidatos para contratar (JSON)
│       └── candidates.json
│
├── assets/                     # Recursos estáticos
│   ├── images/
│   │   ├── dishes/             # Imágenes de platos
│   │   ├── employees/          # Fotos de empleados
│   │   └── icons/              # Íconos de la app
│       └── main.css
│
├── tests/                      # Pruebas
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_simulator.py
│   │   └── test_constraints.py
│   └── integration/
│       └── test_restaurant.py
│
├── config/                     # Configuración de la aplicación
│   ├── __init__.py
│   ├── settings.py            # Configuración general
│   └── constraints_config.py  # Configuración de restricciones (para que sean modificables)
│
├── scripts/                    # Scripts auxiliares
│   ├── generate_candidates.py  # Generar candidatos aleatorios
│   └── init_default_data.py    # Inicializar datos por defecto
│
├── requirements.txt            # Dependencias
├── .gitignore
├── README.md                   # Documentación
├── main.py                     # Punto de entrada de Streamlit
└── run.py                      # Script para ejecutar la aplicación (alternativo)
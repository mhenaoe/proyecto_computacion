# Análisis de Estaciones de Carga para Vehículos Eléctricos
## Descripción General

Este proyecto analiza el comportamiento de uso y desempeño de una red de 31 estaciones de carga eléctrica distribuidas en Colombia durante el período enero a octubre de 2025.
El objetivo es comprender patrones de consumo, identificar oportunidades de optimización y proponer estrategias de expansión y pricing para mejorar la eficiencia operativa y los ingresos.

El análisis se basa en 8,739 transacciones reales, correspondientes a 2,112 usuarios y 109,600 kWh de energía dispensada.

## Objetivos del Proyecto
1. Analizar el crecimiento y comportamiento temporal de las transacciones.
2. Identificar estaciones con mayor y menor rendimiento.
3. Detectar patrones de uso por hora y día.
4. Calcular métricas económicas clave (precio promedio por kWh, ingreso por sesión, etc.).
5. Proponer estrategias para optimizar ingresos y balancear la red de carga.

```
PROYECTO_COMPUTACION/
│
├── dashboards/
│   └── app_dashboard.py          # Dashboard interactivo desarrollado en Dash
│
├── datos/
│   ├── df_oasis_clean.csv        # Dataset limpio principal
│   └── datos_limpios.csv         # Versión procesada de respaldo
│
├── notebooks/
│   ├── 01_analisis_puertos_carga.ipynb    # Limpieza y análisis exploratorio
│   └── 02_visualizaciones.ipynb           # Gráficos y visualizaciones avanzadas
│
├── resultados/
│   └── informe_dashboard_oasis.pdf  # Reporte técnico detallado
│
└── README.md                    # Documentación del proyecto
```

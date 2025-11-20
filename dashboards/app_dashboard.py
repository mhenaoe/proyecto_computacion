import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State
import base64
import io

# Cargar datos iniciales
df = None
rutas_posibles = [
    '../datos/df_oasis_clean.csv',      # Subir a proyecto_computacion/datos/
    'datos/df_oasis_clean.csv',         # Si se ejecuta desde la raíz
    'df_oasis_clean.csv',               # Si está en la misma carpeta
    '../../datos/df_oasis_clean.csv',   # Por si acaso
]

for ruta in rutas_posibles:
    try:
        df = pd.read_csv(ruta)
        df['amount_transaction'] = df['amount_transaction'] / 100
        df['amount_third'] = df['amount_third'] / 100
        df['start_date_time'] = pd.to_datetime(df['start_date_time'], format='mixed')
        df['end_date_time'] = pd.to_datetime(df['end_date_time'], format='mixed')
        df['mes'] = df['start_date_time'].dt.month
        df['mes_nombre'] = df['start_date_time'].dt.strftime('%B')
        df['dia_semana'] = df['start_date_time'].dt.day_name()
        df['hora'] = df['start_date_time'].dt.hour
        df['fecha'] = df['start_date_time'].dt.date
        print(f"✓ Datos cargados exitosamente desde: {ruta}")
        print(f"✓ Total de registros: {len(df):,}")
        break
    except FileNotFoundError:
        continue
    except Exception as e:
        print(f"Error al intentar cargar desde {ruta}: {e}")
        continue

if df is None:
    print("\n" + "="*60)
    print("ADVERTENCIA: No se encontró el archivo df_oasis_clean.csv")
    print("="*60)
    print("\nBusque el archivo en estas ubicaciones:")
    for ruta in rutas_posibles:
        print(f"  - {ruta}")
    print("\nPor favor:")
    print("1. Asegúrate de que el archivo esté en la carpeta 'datos'")
    print("2. O cárgalo manualmente desde el dashboard")
    print("="*60 + "\n")

# Crear la app
app = Dash(__name__)

# Colores
colors = {
    'background': '#f8f9fa',
    'card': '#ffffff',
    'primary': '#2C3E50',
    'secondary': '#3498db',
    'text': '#2c3e50'
}

# Estilos
card_style = {
    'backgroundColor': colors['card'],
    'padding': '20px',
    'margin': '10px',
    'borderRadius': '5px',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
    'textAlign': 'center'
}

container_style = {
    'backgroundColor': colors['background'],
    'padding': '20px',
    'fontFamily': 'Arial, sans-serif'
}

header_style = {
    'textAlign': 'center',
    'color': colors['primary'],
    'marginBottom': '10px'
}

kpi_number_style = {
    'fontSize': '32px',
    'fontWeight': 'bold',
    'color': colors['secondary'],
    'margin': '10px 0'
}

kpi_label_style = {
    'fontSize': '14px',
    'color': '#666',
    'marginBottom': '5px'
}

analysis_style = {
    'backgroundColor': '#f0f8ff',
    'padding': '20px',
    'margin': '20px 0',
    'borderRadius': '5px',
    'borderLeft': '4px solid #3498db',
    'fontSize': '14px',
    'lineHeight': '1.8'
}

# Función para procesar archivo
def procesar_datos(contents, filename):
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        
        df['amount_transaction'] = df['amount_transaction'] / 100
        df['amount_third'] = df['amount_third'] / 100
        df['start_date_time'] = pd.to_datetime(df['start_date_time'], format='mixed')
        df['end_date_time'] = pd.to_datetime(df['end_date_time'], format='mixed')
        df['mes'] = df['start_date_time'].dt.month
        df['mes_nombre'] = df['start_date_time'].dt.strftime('%B')
        df['dia_semana'] = df['start_date_time'].dt.day_name()
        df['hora'] = df['start_date_time'].dt.hour
        df['fecha'] = df['start_date_time'].dt.date
        
        return df, None
    except Exception as e:
        return None, f"Error: {str(e)}"

# Layout
app.layout = html.Div(style=container_style, children=[
    
    # Encabezado
    html.Div([
        html.H1("Estaciones de Carga - Dashboard de Análisis", style=header_style),
        html.H4("Análisis de Estaciones de Carga de Vehículos Eléctricos en Colombia",
               style={'textAlign': 'center', 'color': colors['secondary'], 'marginBottom': '30px'})
    ]),
    
    # Store para datos
    dcc.Store(id='stored-data', data=df.to_json(date_format='iso', orient='split') if df is not None else None),
    
    # Sección de carga de archivo
    html.Details([
        html.Summary("Cargar Nuevo Archivo CSV", 
                    style={'fontSize': '16px', 'fontWeight': 'bold', 'cursor': 'pointer', 
                           'padding': '15px', 'backgroundColor': 'white', 'borderRadius': '5px'}),
        html.Div(style={'backgroundColor': '#e8f4f8', 'padding': '20px', 'borderRadius': '5px', 'marginTop': '10px'}, children=[
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Arrastra y suelta o ',
                    html.A('selecciona un archivo CSV', style={'color': colors['secondary'], 'fontWeight': 'bold'})
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '2px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'backgroundColor': 'white',
                    'cursor': 'pointer'
                },
                multiple=False
            ),
            html.Div(id='upload-status', style={'marginTop': '10px', 'fontWeight': 'bold'})
        ])
    ], style={'marginBottom': '30px'}),
    
    # Filtros
    html.Div(style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '30px'}, children=[
        html.Div(style={'width': '45%'}, children=[
            html.Label("Seleccionar Estación:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='filtro-estacion',
                options=[{'label': 'Todas las estaciones', 'value': 'TODAS'}] + 
                        ([{'label': est, 'value': est} for est in sorted(df['evse_uid'].unique())] if df is not None else []),
                value='TODAS',
                clearable=False,
                style={'marginTop': '5px'}
            )
        ]),
        html.Div(style={'width': '45%'}, children=[
            html.Label("Seleccionar Mes:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='filtro-mes',
                options=[{'label': 'Todos los meses', 'value': 'TODOS'}] + 
                        ([{'label': mes, 'value': num} for num, mes in 
                         sorted(df.groupby('mes')['mes_nombre'].first().items())] if df is not None else []),
                value='TODOS',
                clearable=False,
                style={'marginTop': '5px'}
            )
        ])
    ]),
    
    # KPIs
    html.Div(style={'display': 'flex', 'justifyContent': 'space-around', 'flexWrap': 'wrap'}, children=[
        html.Div(style=card_style, children=[
            html.Div("Total Transacciones", style=kpi_label_style),
            html.Div(id='kpi-transacciones', style=kpi_number_style)
        ]),
        html.Div(style=card_style, children=[
            html.Div("Energía Total (kWh)", style=kpi_label_style),
            html.Div(id='kpi-energia', style=kpi_number_style)
        ]),
        html.Div(style=card_style, children=[
            html.Div("Ingresos Totales", style=kpi_label_style),
            html.Div(id='kpi-ingresos', style=kpi_number_style)
        ])
    ]),
    
    html.Div(style={'display': 'flex', 'justifyContent': 'space-around', 'flexWrap': 'wrap', 'marginTop': '10px'}, children=[
        html.Div(style=card_style, children=[
            html.Div("Usuarios Únicos", style=kpi_label_style),
            html.Div(id='kpi-usuarios', style=kpi_number_style)
        ]),
        html.Div(style=card_style, children=[
            html.Div("Precio Promedio/kWh", style=kpi_label_style),
            html.Div(id='kpi-precio-kwh', style=kpi_number_style)
        ]),
        html.Div(style=card_style, children=[
            html.Div("Duración Promedio", style=kpi_label_style),
            html.Div(id='kpi-duracion', style=kpi_number_style)
        ])
    ]),
    
    # Pestañas
    html.Div(style={'marginTop': '30px'}, children=[
        dcc.Tabs(id='tabs', value='tab-horario', children=[
            dcc.Tab(label='Análisis Horario', value='tab-horario'),
            dcc.Tab(label='Análisis Semanal', value='tab-semanal'),
            dcc.Tab(label='Top Estaciones', value='tab-estaciones'),
            dcc.Tab(label='Distribución Energía', value='tab-energia'),
            dcc.Tab(label='Ingresos Mensuales', value='tab-ingresos'),
            dcc.Tab(label='Duración Sesiones', value='tab-duracion'),
        ]),
    ]),
    
    html.Div(id='tabs-content', style={'marginTop': '20px'})
])

# Callback carga archivo
@app.callback(
    [Output('stored-data', 'data'),
     Output('upload-status', 'children'),
     Output('filtro-estacion', 'options'),
     Output('filtro-mes', 'options')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename'),
     State('stored-data', 'data')]
)
def cargar_archivo(contents, filename, current_data):
    if contents is None:
        if current_data:
            df_current = pd.read_json(io.StringIO(current_data), orient='split')
            estaciones = [{'label': 'Todas las estaciones', 'value': 'TODAS'}] + \
                        [{'label': est, 'value': est} for est in sorted(df_current['evse_uid'].unique())]
            meses = [{'label': 'Todos los meses', 'value': 'TODOS'}] + \
                    [{'label': mes, 'value': num} for num, mes in 
                     sorted(df_current.groupby('mes')['mes_nombre'].first().items())]
            return current_data, "", estaciones, meses
        return current_data, "", [], []
    
    df_new, error = procesar_datos(contents, filename)
    
    if error:
        if current_data:
            df_current = pd.read_json(io.StringIO(current_data), orient='split')
            estaciones = [{'label': 'Todas las estaciones', 'value': 'TODAS'}] + \
                        [{'label': est, 'value': est} for est in sorted(df_current['evse_uid'].unique())]
            meses = [{'label': 'Todos los meses', 'value': 'TODOS'}] + \
                    [{'label': mes, 'value': num} for num, mes in 
                     sorted(df_current.groupby('mes')['mes_nombre'].first().items())]
            return current_data, f"Error: {error}", estaciones, meses
        return None, f"Error: {error}", [], []
    
    estaciones = [{'label': 'Todas las estaciones', 'value': 'TODAS'}] + \
                [{'label': est, 'value': est} for est in sorted(df_new['evse_uid'].unique())]
    meses = [{'label': 'Todos los meses', 'value': 'TODOS'}] + \
            [{'label': mes, 'value': num} for num, mes in 
             sorted(df_new.groupby('mes')['mes_nombre'].first().items())]
    
    return df_new.to_json(date_format='iso', orient='split'), \
           f"Archivo '{filename}' cargado: {len(df_new):,} registros", \
           estaciones, meses

# Callback KPIs
@app.callback(
    [Output('kpi-transacciones', 'children'),
     Output('kpi-energia', 'children'),
     Output('kpi-ingresos', 'children'),
     Output('kpi-usuarios', 'children'),
     Output('kpi-precio-kwh', 'children'),
     Output('kpi-duracion', 'children')],
    [Input('stored-data', 'data'),
     Input('filtro-estacion', 'value'),
     Input('filtro-mes', 'value')]
)
def actualizar_kpis(data, estacion, mes):
    if data is None:
        return "0", "0", "$0", "0", "$0", "0min"
    
    df = pd.read_json(io.StringIO(data), orient='split')
    df['start_date_time'] = pd.to_datetime(df['start_date_time'])
    df['end_date_time'] = pd.to_datetime(df['end_date_time'])
    
    df_filtrado = df.copy()
    if estacion != 'TODAS':
        df_filtrado = df_filtrado[df_filtrado['evse_uid'] == estacion]
    if mes != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['mes'] == mes]
    
    total_transacciones = f"{len(df_filtrado):,}"
    total_energia = f"{df_filtrado['energy_kwh'].sum():,.0f}"
    total_ingresos = f"${df_filtrado['amount_transaction'].sum():,.0f}"
    usuarios_unicos = f"{df_filtrado['user_id'].nunique():,}"
    precio_kwh = f"${(df_filtrado['amount_transaction'].sum() / df_filtrado['energy_kwh'].sum()):,.0f}"
    
    df_filtrado['duracion_minutos'] = (df_filtrado['end_date_time'] - df_filtrado['start_date_time']).dt.total_seconds() / 60
    duracion_promedio = df_filtrado['duracion_minutos'].mean()
    if duracion_promedio >= 60:
        duracion_text = f"{duracion_promedio/60:.1f}h"
    else:
        duracion_text = f"{duracion_promedio:.0f}min"
    
    return total_transacciones, total_energia, total_ingresos, usuarios_unicos, precio_kwh, duracion_text

# Callback contenido pestañas
@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value'),
     Input('stored-data', 'data'),
     Input('filtro-estacion', 'value'),
     Input('filtro-mes', 'value')]
)
def actualizar_contenido(tab, data, estacion, mes):
    if data is None:
        return html.Div([
            html.H3("No hay datos disponibles", style={'textAlign': 'center', 'marginTop': '50px'}),
        ])
    
    df = pd.read_json(io.StringIO(data), orient='split')
    df['start_date_time'] = pd.to_datetime(df['start_date_time'])
    df['end_date_time'] = pd.to_datetime(df['end_date_time'])
    
    df_filtrado = df.copy()
    if estacion != 'TODAS':
        df_filtrado = df_filtrado[df_filtrado['evse_uid'] == estacion]
    if mes != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['mes'] == mes]
    
    # TAB 1: Uso Horario
    if tab == 'tab-horario':
        uso_horario = df_filtrado.groupby('hora').size().reset_index(name='transacciones')
        fig = px.bar(uso_horario, x='hora', y='transacciones',
                     title='Transacciones por Hora del Día',
                     labels={'hora': 'Hora', 'transacciones': 'Número de Transacciones'},
                     color='transacciones',
                     color_continuous_scale='Blues')
        fig.update_layout(showlegend=False)
        
        hora_pico = int(uso_horario.loc[uso_horario['transacciones'].idxmax(), 'hora'])
        trans_pico = int(uso_horario['transacciones'].max())
        hora_baja = int(uso_horario.loc[uso_horario['transacciones'].idxmin(), 'hora'])
        trans_baja = int(uso_horario['transacciones'].min())
        
        return html.Div([
            dcc.Graph(figure=fig),
            html.Div(style=analysis_style, children=[
                html.H4("Análisis del Comportamiento Horario"),
                html.P([
                    html.Strong("Hora pico: "), 
                    f"Las {hora_pico:02d}:00 horas registran el mayor número de transacciones ({trans_pico:,}), "
                    f"lo que representa un {(trans_pico/len(df_filtrado)*100):.1f}% del total de cargas."
                ]),
                html.P([
                    html.Strong("Hora de menor actividad: "),
                    f"Las {hora_baja:02d}:00 horas con {trans_baja:,} transacciones."
                ]),
                html.P([
                    html.Strong("Interpretación: "),
                    f"El pico de uso a las {hora_pico:02d}:00 horas sugiere un patrón de comportamiento relacionado "
                    "con horarios laborales o de movilidad urbana. Esta concentración de demanda en horarios específicos "
                    "requiere garantizar capacidad operativa suficiente para evitar tiempos de espera y saturación del sistema."
                ]),
                html.P([
                    html.Strong("Recomendaciones: "),
                    f"Implementar tarifas dinámicas con descuentos durante las horas de baja demanda ({hora_baja:02d}:00 - "
                    f"{(hora_baja+3)%24:02d}:00) para distribuir mejor la carga. Asegurar disponibilidad de personal técnico "
                    f"durante el horario pico ({hora_pico:02d}:00 horas) para respuesta rápida ante incidencias."
                ])
            ])
        ])
    
    # TAB 2: Uso Semanal
    elif tab == 'tab-semanal':
        orden_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dias_esp = {'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles', 
                    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
        
        uso_diario = df_filtrado.groupby('dia_semana').size().reset_index(name='transacciones')
        uso_diario['dia_semana'] = pd.Categorical(uso_diario['dia_semana'], categories=orden_dias, ordered=True)
        uso_diario = uso_diario.sort_values('dia_semana')
        uso_diario['dia_esp'] = uso_diario['dia_semana'].map(dias_esp)
        
        fig = px.bar(uso_diario, x='dia_esp', y='transacciones',
                     title='Transacciones por Día de la Semana',
                     labels={'dia_esp': 'Día', 'transacciones': 'Número de Transacciones'},
                     color='transacciones',
                     color_continuous_scale='Greens')
        fig.update_layout(showlegend=False)
        
        dia_mayor = uso_diario.loc[uso_diario['transacciones'].idxmax(), 'dia_esp']
        trans_mayor = int(uso_diario['transacciones'].max())
        dia_menor = uso_diario.loc[uso_diario['transacciones'].idxmin(), 'dia_esp']
        trans_menor = int(uso_diario['transacciones'].min())
        
        return html.Div([
            dcc.Graph(figure=fig),
            html.Div(style=analysis_style, children=[
                html.H4("Análisis del Comportamiento Semanal"),
                html.P([
                    html.Strong("Día de mayor demanda: "),
                    f"{dia_mayor} con {trans_mayor:,} transacciones ({(trans_mayor/len(df_filtrado)*100):.1f}% del total semanal)."
                ]),
                html.P([
                    html.Strong("Día de menor demanda: "),
                    f"{dia_menor} con {trans_menor:,} transacciones ({(trans_menor/len(df_filtrado)*100):.1f}% del total)."
                ]),
                html.P([
                    html.Strong("Interpretación: "),
                    f"La diferencia de {trans_mayor - trans_menor:,} transacciones entre el día más activo ({dia_mayor}) "
                    f"y el menos activo ({dia_menor}) representa una variación del {((trans_mayor-trans_menor)/trans_menor*100):.1f}%. "
                    "Este patrón semanal es fundamental para la planificación operativa, asignación de recursos y programación "
                    "de mantenimientos preventivos."
                ]),
                html.P([
                    html.Strong("Recomendaciones: "),
                    f"Programar mantenimientos y actualizaciones de sistema durante el {dia_menor} para minimizar impacto en usuarios. "
                    f"Considerar reforzar el equipo de soporte técnico los días {dia_mayor}. Evaluar campañas promocionales "
                    "en días de baja demanda para equilibrar el uso de la infraestructura a lo largo de la semana."
                ])
            ])
        ])
    
    # TAB 3: Top Estaciones
    elif tab == 'tab-estaciones':
        top_estaciones = df_filtrado.groupby('evse_uid').agg({
            'id': 'count',
            'amount_transaction': 'sum'
        }).reset_index()
        top_estaciones.columns = ['estacion', 'transacciones', 'ingresos']
        top_estaciones = top_estaciones.sort_values('transacciones', ascending=False).head(10)
        
        fig = px.bar(top_estaciones, x='transacciones', y='estacion',
                     orientation='h',
                     title='Top 10 Estaciones por Número de Transacciones',
                     labels={'estacion': 'Estación', 'transacciones': 'Transacciones'},
                     color='ingresos',
                     color_continuous_scale='Oranges')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        
        estacion_top = top_estaciones.iloc[0]['estacion']
        trans_top = int(top_estaciones.iloc[0]['transacciones'])
        ingresos_top = top_estaciones.iloc[0]['ingresos']
        top5_trans = int(top_estaciones.head(5)['transacciones'].sum())
        
        return html.Div([
            dcc.Graph(figure=fig),
            html.Div(style=analysis_style, children=[
                html.H4("Análisis de Estaciones de Mayor Rendimiento"),
                html.P([
                    html.Strong("Estación líder: "),
                    f"{estacion_top} con {trans_top:,} transacciones ({(trans_top/len(df_filtrado)*100):.1f}% del total) "
                    f"y ${ingresos_top:,.0f} en ingresos."
                ]),
                html.P([
                    html.Strong("Concentración top 5: "),
                    f"Las cinco estaciones principales concentran {top5_trans:,} transacciones, "
                    f"representando el {(top5_trans/len(df_filtrado)*100):.1f}% del volumen total."
                ]),
                html.P([
                    html.Strong("Interpretación: "),
                    "La alta concentración de uso en pocas estaciones indica ubicaciones estratégicas exitosas, "
                    "probablemente asociadas a centros comerciales, zonas de alta circulación o rutas principales. "
                    "Sin embargo, esta concentración representa riesgos de saturación y dependencia excesiva de "
                    "pocas instalaciones, lo que podría generar tiempos de espera y afectar la experiencia del usuario."
                ]),
                html.P([
                    html.Strong("Recomendaciones: "),
                    f"Evaluar la ampliación de capacidad en {estacion_top} mediante la instalación de puntos de carga adicionales. "
                    "Analizar factores de éxito de estas ubicaciones (accesibilidad, visibilidad, servicios complementarios) "
                    "para replicar el modelo en nuevas instalaciones. Implementar estrategias de distribución de demanda "
                    "hacia estaciones menos utilizadas mediante incentivos tarifarios o programas de lealtad."
                ])
            ])
        ])
    
    # TAB 4: Distribución Energía
    elif tab == 'tab-energia':
        fig = px.histogram(df_filtrado, x='energy_kwh',
                          title='Distribución de Energía por Transacción',
                          labels={'energy_kwh': 'Energía (kWh)', 'count': 'Frecuencia'},
                          nbins=30,
                          color_discrete_sequence=['#3498db'])
        
        energia_prom = df_filtrado['energy_kwh'].mean()
        energia_med = df_filtrado['energy_kwh'].median()
        energia_max = df_filtrado['energy_kwh'].max()
        energia_min = df_filtrado['energy_kwh'].min()
        
        return html.Div([
            dcc.Graph(figure=fig),
            html.Div(style=analysis_style, children=[
                html.H4("Análisis de Distribución de Energía"),
                html.P([
                    html.Strong("Estadísticas de consumo: "),
                    f"Promedio: {energia_prom:.2f} kWh | Mediana: {energia_med:.2f} kWh | "
                    f"Rango: {energia_min:.2f} - {energia_max:.2f} kWh"
                ]),
                html.P([
                    html.Strong("Interpretación: "),
                    f"La diferencia entre la media ({energia_prom:.1f} kWh) y la mediana ({energia_med:.1f} kWh) "
                    f"de {abs(energia_prom - energia_med):.1f} kWh indica la presencia de cargas atípicas en el dataset. "
                    "La distribución muestra que la mayoría de usuarios realizan cargas parciales en lugar de cargas completas, "
                    "lo cual es típico en estaciones urbanas donde los usuarios complementan su autonomía de forma oportuna."
                ]),
                html.P([
                    html.Strong("Recomendaciones: "),
                    f"Diseñar paquetes tarifarios escalonados: básico (hasta {energia_med:.0f} kWh), "
                    f"estándar ({energia_med:.0f}-{energia_prom:.0f} kWh), premium (>{energia_prom:.0f} kWh). "
                    "Considerar promociones para cargas superiores a la mediana para optimizar la rotación de puntos de carga "
                    "y reducir tiempos de ocupación por sesión."
                ])
            ])
        ])
    
    # TAB 5: Ingresos Mensuales
    elif tab == 'tab-ingresos':
        ingresos_mes = df_filtrado.groupby('mes').agg({
            'amount_transaction': 'sum',
            'mes_nombre': 'first'
        }).reset_index()
        ingresos_mes = ingresos_mes.sort_values('mes')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ingresos_mes['mes_nombre'], 
                                 y=ingresos_mes['amount_transaction'],
                                 mode='lines+markers',
                                 name='Ingresos',
                                 line=dict(color='#27ae60', width=3),
                                 marker=dict(size=10)))
        fig.update_layout(title='Tendencia de Ingresos Mensuales',
                         xaxis_title='Mes',
                         yaxis_title='Ingresos ($)')
        
        if len(ingresos_mes) >= 2:
            crecimiento = ((ingresos_mes.iloc[-1]['amount_transaction'] - 
                          ingresos_mes.iloc[0]['amount_transaction']) / 
                          ingresos_mes.iloc[0]['amount_transaction'] * 100)
            mes_mayor = ingresos_mes.loc[ingresos_mes['amount_transaction'].idxmax(), 'mes_nombre']
            ingreso_mayor = ingresos_mes['amount_transaction'].max()
            mes_inicial = ingresos_mes.iloc[0]['mes_nombre']
            mes_final = ingresos_mes.iloc[-1]['mes_nombre']
        else:
            crecimiento = 0
            mes_mayor = "N/A"
            ingreso_mayor = 0
            mes_inicial = mes_final = "N/A"
        
        return html.Div([
            dcc.Graph(figure=fig),
            html.Div(style=analysis_style, children=[
                html.H4("Análisis de Tendencia de Ingresos"),
                html.P([
                    html.Strong("Crecimiento período: "),
                    f"{crecimiento:+.1f}% desde {mes_inicial} hasta {mes_final}."
                ]),
                html.P([
                    html.Strong("Mejor mes: "),
                    f"{mes_mayor} con ${ingreso_mayor:,.0f} en ingresos."
                ]),
                html.P([
                    html.Strong("Ingreso promedio mensual: "),
                    f"${ingresos_mes['amount_transaction'].mean():,.0f}"
                ]),
                html.P([
                    html.Strong("Interpretación: "),
                    f"La tendencia de ingresos muestra un {'crecimiento sostenido' if crecimiento > 0 else 'decrecimiento'} "
                    f"de {abs(crecimiento):.1f}% en el período analizado. Este comportamiento puede estar influenciado por "
                    "la adopción creciente de vehículos eléctricos, mejoras en infraestructura, campañas de marketing, "
                    f"y factores estacionales. El desempeño destacado de {mes_mayor} merece análisis detallado."
                ]),
                html.P([
                    html.Strong("Recomendaciones: "),
                    f"Proyectar ingresos futuros considerando la tendencia de {crecimiento:.1f}% para planificar inversiones. "
                    f"Analizar factores específicos que contribuyeron al éxito de {mes_mayor} (promociones, eventos, clima) "
                    "para replicar estrategias exitosas. Considerar la estacionalidad en programación de mantenimientos "
                    "y lanzamiento de campañas comerciales."
                ])
            ])
        ])
    
    # TAB 6: Duración Sesiones
    elif tab == 'tab-duracion':
        df_filtrado['duracion_minutos'] = (df_filtrado['end_date_time'] - df_filtrado['start_date_time']).dt.total_seconds() / 60
        
        fig = px.box(df_filtrado, y='duracion_minutos',
                     title='Distribución de Duración de Sesiones',
                     labels={'duracion_minutos': 'Duración (minutos)'},
                     color_discrete_sequence=['#9b59b6'])
        fig.update_layout(showlegend=False)
        
        dur_prom = df_filtrado['duracion_minutos'].mean()
        dur_med = df_filtrado['duracion_minutos'].median()
        sesiones_largas = len(df_filtrado[df_filtrado['duracion_minutos'] > 240])
        pct_largas = (sesiones_largas / len(df_filtrado)) * 100
        
        return html.Div([
            dcc.Graph(figure=fig),
            html.Div(style=analysis_style, children=[
                html.H4("Análisis de Duración de Sesiones"),
                html.P([
                    html.Strong("Duración promedio: "),
                    f"{dur_prom:.0f} minutos ({dur_prom/60:.1f} horas)"
                ]),
                html.P([
                    html.Strong("Duración mediana: "),
                    f"{dur_med:.0f} minutos ({dur_med/60:.1f} horas)"
                ]),
                html.P([
                    html.Strong("Sesiones prolongadas: "),
                    f"{sesiones_largas:,} sesiones superan las 4 horas ({pct_largas:.1f}% del total)."
                ]),
                html.P([
                    html.Strong("Interpretación: "),
                    f"La duración promedio de {dur_prom/60:.1f} horas indica el tiempo típico que los vehículos permanecen conectados. "
                    f"La diferencia entre promedio y mediana de {abs(dur_prom - dur_med):.0f} minutos sugiere la presencia de "
                    "sesiones atípicas muy prolongadas. Estas sesiones largas pueden indicar usuarios que dejan sus vehículos "
                    "conectados innecesariamente, reduciendo la disponibilidad para otros usuarios y afectando la eficiencia operativa."
                ]),
                html.P([
                    html.Strong("Recomendaciones: "),
                    f"Implementar política de tarifas por tiempo de ocupación para sesiones que superen {dur_med:.0f} minutos, "
                    "incentivando rotación eficiente. Desarrollar sistema de notificaciones automáticas cuando la carga alcance "
                    "80-90% para que usuarios liberen el punto más rápidamente. Considerar penalizaciones moderadas para "
                    "sesiones superiores a 4 horas que no estén asociadas a cargas activas."
                ])
            ])
        ])

if __name__ == '__main__':
    app.run(debug=True, port=8050)
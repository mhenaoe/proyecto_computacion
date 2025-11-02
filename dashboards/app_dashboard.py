import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# Cargar los datos
df = pd.read_csv('df_oasis_clean.csv')

# ===== CORRECCIÓN CRÍTICA: Dividir montos entre 100 =====
df['amount_transaction'] = df['amount_transaction'] / 100
df['amount_third'] = df['amount_third'] / 100

# Convertir fechas
df['start_date_time'] = pd.to_datetime(df['start_date_time'])
df['end_date_time'] = pd.to_datetime(df['end_date_time'])

# Crear variables temporales
df['mes'] = df['start_date_time'].dt.month
df['mes_nombre'] = df['start_date_time'].dt.strftime('%B')
df['dia_semana'] = df['start_date_time'].dt.day_name()
df['hora'] = df['start_date_time'].dt.hour
df['fecha'] = df['start_date_time'].dt.date

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

# Estilos CSS
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

# Layout de la aplicación
app.layout = html.Div(style=container_style, children=[
    
    # Encabezado
    html.Div([
        html.H1("📊 Dashboard Oasis - Estaciones de Carga", style=header_style),
        html.H4("Análisis de Estaciones de Carga de Vehículos Eléctricos en Colombia",
               style={'textAlign': 'center', 'color': colors['secondary'], 'marginBottom': '30px'})
    ]),
    
    # Filtros
    html.Div(style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '30px'}, children=[
        html.Div(style={'width': '45%'}, children=[
            html.Label("Seleccionar Estación:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='filtro-estacion',
                options=[{'label': 'Todas las estaciones', 'value': 'TODAS'}] + 
                        [{'label': est, 'value': est} for est in sorted(df['evse_uid'].unique())],
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
                        [{'label': mes, 'value': num} for num, mes in 
                         sorted(df.groupby('mes')['mes_nombre'].first().items())],
                value='TODOS',
                clearable=False,
                style={'marginTop': '5px'}
            )
        ])
    ]),
    
    # KPIs - Primera fila (3 KPIs)
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
    
    # KPIs - Segunda fila (3 KPIs)
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
    
    # Primera fila de gráficos
    html.Div(style={'display': 'flex', 'justifyContent': 'space-around', 'marginTop': '30px'}, children=[
        html.Div(style={'width': '48%'}, children=[
            dcc.Graph(id='grafico-uso-horario')
        ]),
        html.Div(style={'width': '48%'}, children=[
            dcc.Graph(id='grafico-uso-diario')
        ])
    ]),
    
    # Segunda fila de gráficos
    html.Div(style={'display': 'flex', 'justifyContent': 'space-around', 'marginTop': '20px'}, children=[
        html.Div(style={'width': '48%'}, children=[
            dcc.Graph(id='grafico-top-estaciones')
        ]),
        html.Div(style={'width': '48%'}, children=[
            dcc.Graph(id='grafico-distribucion-energia')
        ])
    ]),
    
    # Tercera fila de gráficos
    html.Div(style={'display': 'flex', 'justifyContent': 'space-around', 'marginTop': '20px'}, children=[
        html.Div(style={'width': '48%'}, children=[
            dcc.Graph(id='grafico-ingresos-mensuales')
        ]),
        html.Div(style={'width': '48%'}, children=[
            dcc.Graph(id='grafico-duracion-sesiones')
        ])
    ])
])

# Callback para actualizar todos los componentes
@app.callback(
    [Output('kpi-transacciones', 'children'),
     Output('kpi-energia', 'children'),
     Output('kpi-ingresos', 'children'),
     Output('kpi-usuarios', 'children'),
     Output('kpi-precio-kwh', 'children'),
     Output('kpi-duracion', 'children'),
     Output('grafico-uso-horario', 'figure'),
     Output('grafico-uso-diario', 'figure'),
     Output('grafico-top-estaciones', 'figure'),
     Output('grafico-distribucion-energia', 'figure'),
     Output('grafico-ingresos-mensuales', 'figure'),
     Output('grafico-duracion-sesiones', 'figure')],
    [Input('filtro-estacion', 'value'),
     Input('filtro-mes', 'value')]
)
def actualizar_dashboard(estacion, mes):
    # Filtrar datos
    df_filtrado = df.copy()
    
    if estacion != 'TODAS':
        df_filtrado = df_filtrado[df_filtrado['evse_uid'] == estacion]
    
    if mes != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['mes'] == mes]
    
    # Calcular KPIs
    total_transacciones = f"{len(df_filtrado):,}"
    total_energia = f"{df_filtrado['energy_kwh'].sum():,.0f}"
    total_ingresos = f"${df_filtrado['amount_transaction'].sum():,.0f}"
    usuarios_unicos = f"{df_filtrado['user_id'].nunique():,}"
    precio_kwh = f"${(df_filtrado['amount_transaction'].sum() / df_filtrado['energy_kwh'].sum()):,.0f}"
    
    # Calcular duración promedio
    df_filtrado['duracion_minutos'] = (df_filtrado['end_date_time'] - df_filtrado['start_date_time']).dt.total_seconds() / 60
    duracion_promedio = df_filtrado['duracion_minutos'].mean()
    if duracion_promedio >= 60:
        duracion_text = f"{duracion_promedio/60:.1f}h"
    else:
        duracion_text = f"{duracion_promedio:.0f}min"
    
    # Gráfico 1: Uso por hora
    uso_horario = df_filtrado.groupby('hora').size().reset_index(name='transacciones')
    fig1 = px.bar(uso_horario, x='hora', y='transacciones',
                  title='Transacciones por Hora del Día',
                  labels={'hora': 'Hora', 'transacciones': 'Número de Transacciones'},
                  color='transacciones',
                  color_continuous_scale='Blues')
    fig1.update_layout(showlegend=False)
    
    # Gráfico 2: Uso por día de la semana
    orden_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dias_esp = {'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles', 
                'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
    
    uso_diario = df_filtrado.groupby('dia_semana').size().reset_index(name='transacciones')
    uso_diario['dia_semana'] = pd.Categorical(uso_diario['dia_semana'], categories=orden_dias, ordered=True)
    uso_diario = uso_diario.sort_values('dia_semana')
    uso_diario['dia_esp'] = uso_diario['dia_semana'].map(dias_esp)
    
    fig2 = px.bar(uso_diario, x='dia_esp', y='transacciones',
                  title='Transacciones por Día de la Semana',
                  labels={'dia_esp': 'Día', 'transacciones': 'Número de Transacciones'},
                  color='transacciones',
                  color_continuous_scale='Greens')
    fig2.update_layout(showlegend=False)
    
    # Gráfico 3: Top 10 estaciones
    top_estaciones = df_filtrado.groupby('evse_uid').agg({
        'id': 'count',
        'amount_transaction': 'sum'
    }).reset_index()
    top_estaciones.columns = ['estacion', 'transacciones', 'ingresos']
    top_estaciones = top_estaciones.sort_values('transacciones', ascending=False).head(10)
    
    fig3 = px.bar(top_estaciones, x='transacciones', y='estacion',
                  orientation='h',
                  title='Top 10 Estaciones por Número de Transacciones',
                  labels={'estacion': 'Estación', 'transacciones': 'Transacciones'},
                  color='ingresos',
                  color_continuous_scale='Oranges')
    fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
    
    # Gráfico 4: Distribución de energía
    fig4 = px.histogram(df_filtrado, x='energy_kwh',
                        title='Distribución de Energía por Transacción',
                        labels={'energy_kwh': 'Energía (kWh)', 'count': 'Frecuencia'},
                        nbins=30,
                        color_discrete_sequence=['#3498db'])
    
    # Gráfico 5: Ingresos mensuales
    ingresos_mes = df_filtrado.groupby('mes').agg({
        'amount_transaction': 'sum',
        'mes_nombre': 'first'
    }).reset_index()
    ingresos_mes = ingresos_mes.sort_values('mes')
    
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(x=ingresos_mes['mes_nombre'], 
                              y=ingresos_mes['amount_transaction'],
                              mode='lines+markers',
                              name='Ingresos',
                              line=dict(color='#27ae60', width=3),
                              marker=dict(size=10)))
    fig5.update_layout(title='Tendencia de Ingresos Mensuales',
                      xaxis_title='Mes',
                      yaxis_title='Ingresos ($)')
    
    # Gráfico 6: Distribución de duración de sesiones
    fig6 = px.box(df_filtrado, y='duracion_minutos',
                  title='Distribución de Duración de Sesiones',
                  labels={'duracion_minutos': 'Duración (minutos)'},
                  color_discrete_sequence=['#9b59b6'])
    fig6.update_layout(showlegend=False)
    
    return (total_transacciones, total_energia, total_ingresos, usuarios_unicos, 
            precio_kwh, duracion_text, fig1, fig2, fig3, fig4, fig5, fig6)

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
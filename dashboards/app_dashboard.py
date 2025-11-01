import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime

# ===== CARGAR Y PREPARAR DATOS =====
# IMPORTANTE: Actualiza esta ruta con la ubicación de tu archivo CSV
df = pd.read_csv('df_oasis_clean.csv')

# Convertir columnas de fecha con formato mixto
df['start_date_time'] = pd.to_datetime(df['start_date_time'], format='mixed', errors='coerce')
df['end_date_time'] = pd.to_datetime(df['end_date_time'], format='mixed', errors='coerce')

# Extraer características temporales
df['date'] = df['start_date_time'].dt.date
df['hour'] = df['start_date_time'].dt.hour
df['day_of_week'] = df['start_date_time'].dt.day_name()
df['month'] = df['start_date_time'].dt.month
df['month_name'] = df['start_date_time'].dt.strftime('%B')
df['week'] = df['start_date_time'].dt.isocalendar().week

# Convertir duración a minutos
def duration_to_minutes(duration_str):
    try:
        if pd.isna(duration_str):
            return None
        parts = str(duration_str).split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(float, parts)
            return hours * 60 + minutes + seconds / 60
    except:
        return None

df['duration_minutes'] = df['duration'].apply(duration_to_minutes)

# Calcular ingresos en miles de pesos
df['revenue_thousands'] = df['amount_transaction'] / 1000

# ===== INICIALIZAR APP =====
app = dash.Dash(__name__)
app.title = "Dashboard - Estaciones de Carga EV Colombia"

# ===== CALCULAR MÉTRICAS PRINCIPALES =====
total_transactions = len(df)
total_energy = df['energy_kwh'].sum()
total_revenue = df['amount_transaction'].sum()
avg_duration = df['duration_minutes'].mean()
unique_users = df['user_id'].nunique()
unique_stations = df['evse_uid'].nunique()

# ===== LAYOUT DEL DASHBOARD =====
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Estaciones de Carga para Vehículos Eléctricos",
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '10px'}),
        html.H3("Análisis de Datos - Colombia 2025",
                style={'textAlign': 'center', 'color': '#7f8c8d', 'marginTop': '0px'})
    ], style={'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '10px'}),

    # KPIs principales
    html.Div([
        html.Div([
            html.Div([
                html.H4("Total Transacciones", style={'color': '#7f8c8d', 'fontSize': '16px'}),
                html.H2(f"{total_transactions:,}", style={'color': '#3498db', 'margin': '10px 0'})
            ], className='kpi-card'),
        ], style={'width': '16%', 'display': 'inline-block'}),

        html.Div([
            html.Div([
                html.H4("Energía Total (kWh)", style={'color': '#7f8c8d', 'fontSize': '16px'}),
                html.H2(f"{total_energy:,.0f}", style={'color': '#27ae60', 'margin': '10px 0'})
            ], className='kpi-card'),
        ], style={'width': '16%', 'display': 'inline-block'}),

        html.Div([
            html.Div([
                html.H4("Ingresos Totales", style={'color': '#7f8c8d', 'fontSize': '16px'}),
                html.H2(f"${total_revenue/1_000_000:,.1f}M", style={'color': '#e74c3c', 'margin': '10px 0'})
            ], className='kpi-card'),
        ], style={'width': '16%', 'display': 'inline-block'}),

        html.Div([
            html.Div([
                html.H4("Duración Promedio", style={'color': '#7f8c8d', 'fontSize': '16px'}),
                html.H2(f"{avg_duration:.0f} min", style={'color': '#9b59b6', 'margin': '10px 0'})
            ], className='kpi-card'),
        ], style={'width': '16%', 'display': 'inline-block'}),

        html.Div([
            html.Div([
                html.H4("Usuarios Únicos", style={'color': '#7f8c8d', 'fontSize': '16px'}),
                html.H2(f"{unique_users:,}", style={'color': '#f39c12', 'margin': '10px 0'})
            ], className='kpi-card'),
        ], style={'width': '16%', 'display': 'inline-block'}),

        html.Div([
            html.Div([
                html.H4("Estaciones", style={'color': '#7f8c8d', 'fontSize': '16px'}),
                html.H2(f"{unique_stations}", style={'color': '#16a085', 'margin': '10px 0'})
            ], className='kpi-card'),
        ], style={'width': '16%', 'display': 'inline-block'}),
    ], style={'marginTop': '20px', 'marginBottom': '20px'}),

    # Filtros
    html.Div([
        html.Div([
            html.Label("Seleccionar Estación:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='station-filter',
                options=[{'label': 'Todas las estaciones', 'value': 'ALL'}] + 
                        [{'label': station, 'value': station} for station in sorted(df['evse_uid'].unique())],
                value='ALL',
                style={'width': '100%'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%'}),

        html.Div([
            html.Label("Seleccionar Mes:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='month-filter',
                options=[{'label': 'Todos los meses', 'value': 'ALL'}] + 
                        [{'label': month, 'value': month} for month in sorted(df['month_name'].unique(), 
                         key=lambda x: datetime.strptime(x, '%B').month)],
                value='ALL',
                style={'width': '100%'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%'}),
    ], style={'marginBottom': '20px'}),

    # Gráficos - Fila 1
    html.Div([
        html.Div([
            dcc.Graph(id='hourly-usage')
        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%'}),

        html.Div([
            dcc.Graph(id='daily-usage')
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%'}),
    ]),

    # Gráficos - Fila 2
    html.Div([
        html.Div([
            dcc.Graph(id='top-stations')
        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%'}),

        html.Div([
            dcc.Graph(id='energy-distribution')
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%'}),
    ]),

    # Gráficos - Fila 3
    html.Div([
        html.Div([
            dcc.Graph(id='revenue-trend')
        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%'}),

        html.Div([
            dcc.Graph(id='duration-distribution')
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%'}),
    ]),

], style={'padding': '20px', 'fontFamily': 'Arial, sans-serif'})

# ===== CALLBACKS PARA INTERACTIVIDAD =====

@app.callback(
    [Output('hourly-usage', 'figure'),
     Output('daily-usage', 'figure'),
     Output('top-stations', 'figure'),
     Output('energy-distribution', 'figure'),
     Output('revenue-trend', 'figure'),
     Output('duration-distribution', 'figure')],
    [Input('station-filter', 'value'),
     Input('month-filter', 'value')]
)
def update_graphs(selected_station, selected_month):
    # Filtrar datos
    filtered_df = df.copy()
    
    if selected_station != 'ALL':
        filtered_df = filtered_df[filtered_df['evse_uid'] == selected_station]
    
    if selected_month != 'ALL':
        filtered_df = filtered_df[filtered_df['month_name'] == selected_month]

    # Gráfico 1: Uso por hora del día
    hourly_data = filtered_df.groupby('hour').agg({
        'id': 'count',
        'energy_kwh': 'sum'
    }).reset_index()
    hourly_data.columns = ['hour', 'transactions', 'total_energy']
    
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=hourly_data['hour'],
        y=hourly_data['transactions'],
        name='Transacciones',
        marker_color='#3498db'
    ))
    fig1.update_layout(
        title='Uso por Hora del Día',
        xaxis_title='Hora',
        yaxis_title='Número de Transacciones',
        hovermode='x unified',
        template='plotly_white'
    )

    # Gráfico 2: Uso por día de la semana
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_data = filtered_df.groupby('day_of_week').size().reindex(day_order).reset_index()
    daily_data.columns = ['day', 'transactions']
    daily_data['day_spanish'] = daily_data['day'].map({
        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    })
    
    fig2 = px.bar(daily_data, x='day_spanish', y='transactions',
                  title='Transacciones por Día de la Semana',
                  labels={'day_spanish': 'Día', 'transactions': 'Transacciones'},
                  color='transactions',
                  color_continuous_scale='Viridis')
    fig2.update_layout(template='plotly_white')

    # Gráfico 3: Top 10 estaciones
    station_data = filtered_df.groupby('evse_uid').agg({
        'id': 'count',
        'energy_kwh': 'sum',
        'amount_transaction': 'sum'
    }).reset_index()
    station_data.columns = ['station', 'transactions', 'energy', 'revenue']
    station_data = station_data.sort_values('transactions', ascending=False).head(10)
    
    fig3 = px.bar(station_data, x='transactions', y='station', orientation='h',
                  title='Top 10 Estaciones por Transacciones',
                  labels={'transactions': 'Transacciones', 'station': 'Estación'},
                  color='transactions',
                  color_continuous_scale='Blues')
    fig3.update_layout(template='plotly_white', yaxis={'categoryorder':'total ascending'})

    # Gráfico 4: Distribución de energía consumida
    fig4 = px.histogram(filtered_df, x='energy_kwh', nbins=50,
                        title='Distribución de Energía Consumida por Sesión',
                        labels={'energy_kwh': 'Energía (kWh)', 'count': 'Frecuencia'},
                        color_discrete_sequence=['#27ae60'])
    fig4.update_layout(template='plotly_white')

    # Gráfico 5: Tendencia de ingresos en el tiempo
    revenue_trend = filtered_df.groupby('date')['revenue_thousands'].sum().reset_index()
    
    fig5 = px.line(revenue_trend, x='date', y='revenue_thousands',
                   title='Tendencia de Ingresos Diarios',
                   labels={'date': 'Fecha', 'revenue_thousands': 'Ingresos (Miles COP)'},
                   markers=True)
    fig5.update_traces(line_color='#e74c3c', marker_size=4)
    fig5.update_layout(template='plotly_white')

    # Gráfico 6: Distribución de duración de sesiones
    fig6 = px.box(filtered_df, y='duration_minutes',
                  title='Distribución de Duración de Sesiones',
                  labels={'duration_minutes': 'Duración (minutos)'},
                  color_discrete_sequence=['#9b59b6'])
    fig6.update_layout(template='plotly_white')

    return fig1, fig2, fig3, fig4, fig5, fig6

# ===== EJECUTAR APP =====
if __name__ == '__main__':
    app.run(debug=True, port=8050)
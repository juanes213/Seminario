import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import os

# Load your data
df_10 = pd.read_excel('concatenado_10.xlsx')
df_30 = pd.read_excel('concatenado_30.xlsx')

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Análisis Exploratorio de Demanda de Cursos", className="header-title"),
    
    html.Div([
        html.Div([
            html.Label("Seleccione el periodo:"),
            dcc.RadioItems(
                id='radio_0',
                options=[
                    {'label': 'Periodos 10', 'value': 10},
                    {'label': 'Periodos 30', 'value': 30}
                ],
                value=10,
                className="radio-group"
            ),
        ], className="input-group"),
        
        html.Div([
            html.Label("Seleccione la variable:"),
            dcc.Dropdown(
                id='dropdown_0',
                options=[
                    {'label': 'Matrícula Estimada Histórica', 'value': 'Matrícula_Estimada_Historica'},
                    {'label': 'Proyectados Actual', 'value': 'Proyectados_Actual_(S)'},
                    {'label': 'Meta Nuevos', 'value': 'Meta_Nuevos'},
                    {'label': 'Demanda Máxima Estimada', 'value': 'Demanda_Max_Estimada'},
                    {'label': 'Número de Grupos (40)', 'value': 'Nro_Grupos_40'},
                    {'label': 'Número de Grupos (30)', 'value': 'Nro_Grupos_30'},
                    {'label': 'Número de Grupos (25)', 'value': 'Nro_Grupos_25'}
                ],
                value='Demanda_Max_Estimada',
                className="dropdown"
            ),
        ], className="input-group"),
    ], className="input-container"),

    dcc.Graph(id='descriptive-stats-table', className="graph full-width"),
    
    dcc.Graph(id='demand-stats-table-low', className="graph full-width"),
    
    dcc.Graph(id='demand-stats-table-high', className="graph full-width"),
    
    dcc.Graph(id='historical-trend', className="graph"),
    
    dcc.RangeSlider(
        id='range_slider',
        min=201710,
        max=202410,
        step=100,
        value=[201710, 202410],
        marks={i: str(i) for i in range(201710, 202510, 100)},
        className="range-slider"
    ),
    
    html.Div([
        html.Div([
            dcc.Graph(id='cumulative-line-plot', className="graph"),  
        ], className="graph-container"),
        html.Div([
            dcc.Graph(id='scatter-plot-trend', className="graph"),  
        ], className="graph-container"),
    ], className="row"),

    html.Div([
        html.Div([
            dcc.Graph(id='demand-boxplot-low', className="graph"),
        ], className="graph-container"),
        html.Div([
            dcc.Graph(id='demand-boxplot-high', className="graph"),
        ], className="graph-container"),
    ], className="row"),
    
    html.Div([
        html.Div([
            dcc.Graph(id='demand-histogram-low', className="graph"),
        ], className="graph-container"),
        html.Div([
            dcc.Graph(id='demand-histogram-high', className="graph"),
        ], className="graph-container"),
    ], className="row"),
    
    html.Div([
        html.Div([
            dcc.Graph(id='correlation-heatmap-low', className="graph"),
        ], className="graph-container"),
        html.Div([
            dcc.Graph(id='correlation-heatmap-high', className="graph"),
        ], className="graph-container"),
    ], className="row"),
    
], className="dashboard-container")


@app.callback(
    [Output('descriptive-stats-table', 'figure'),
     Output('demand-stats-table-low', 'figure'),
     Output('demand-stats-table-high', 'figure'),
     Output('historical-trend', 'figure'),
     Output('cumulative-line-plot', 'figure'),
     Output('scatter-plot-trend', 'figure'),
     Output('demand-boxplot-low', 'figure'),
     Output('demand-boxplot-high', 'figure'),
     Output('demand-histogram-low', 'figure'),
     Output('demand-histogram-high', 'figure'),
     Output('correlation-heatmap-low', 'figure'),
     Output('correlation-heatmap-high', 'figure')],
    [Input('radio_0', 'value'),
     Input('range_slider', 'value'),
     Input('dropdown_0', 'value')]
)
def update_graphs(period, slider_0, drpdwn_0):
    if period == 10:
        df = df_10
    else:
        df = df_30
    
    filtered_df = df[(df['Periodo'] >= slider_0[0]) & (df['Periodo'] <= slider_0[1])]
    # Descriptive Statistics Table
    describe_df = filtered_df.drop(['Titulo_Curso', 'Periodo', 'Codigo_Dpto'], axis=1).describe().reset_index()
    describe_df = describe_df.round(2)
    fig_desc_table = go.Figure(data=[go.Table(
        header=dict(values=list(describe_df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[describe_df[col] for col in describe_df.columns],
                   fill_color='lavender',
                   align='left'))
    ])
    fig_desc_table.update_layout(title='Estadísticas Descriptivas Generales')

    # Demand Statistics Tables
    df_low = filtered_df[filtered_df['Demanda_Max_Estimada'] <= 40]
    df_high = filtered_df[filtered_df['Demanda_Max_Estimada'] > 40]

    def create_demand_table(df, title):
        demand_stats = df.drop(['Titulo_Curso', 'Periodo', 'Codigo_Dpto'], axis=1).describe().reset_index()
        demand_stats = demand_stats.round(2)
        fig = go.Figure(data=[go.Table(
            header=dict(values=list(demand_stats.columns),
                        fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=[demand_stats[col] for col in demand_stats.columns],
                       fill_color='lavender',
                       align='left'))
        ])
        fig.update_layout(title=title)
        return fig

    fig_demand_table_low = create_demand_table(df_low, 'Estadísticas de Demanda Baja (≤ 40)')
    fig_demand_table_high = create_demand_table(df_high, 'Estadísticas de Demanda Alta (> 40)')

    # Historical Trend (Line Graph)
    fig_trend = px.line(filtered_df,  y=drpdwn_0, title=f'Tendencia Histórica: entre {slider_0[0]} y {slider_0[1]}')

    # Demand Distribution (Bar Charts)
    def create_bar_chart(df, title):
        counts = df['Demanda_Max_Estimada'].value_counts().sort_index()
        fig = px.bar(x=counts.values, y=counts.index, orientation='v',
                     title=title, labels={'x': 'Cantidad', 'y': 'Demanda'})
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        return fig

    fig_distribution = create_bar_chart(df_low, 'Distribución de la Demanda Baja (≤ 40)')
    fig_distribution_high = create_bar_chart(df_high, 'Distribución de la Demanda Alta (> 40)')

    # Boxplots
    fig_boxplot_low = px.box(df_low, y='Demanda_Max_Estimada', 
                             title='Distribución de Demanda Baja (≤ 40)')
    fig_boxplot_high = px.box(df_high, y='Demanda_Max_Estimada', 
                              title='Distribución de Demanda Alta (> 40)')
    
    # Histograms
    fig_histogram_low = px.histogram(df_low, x='Demanda_Max_Estimada', 
                                     title='Histograma de Demanda Baja (≤ 40)')
    fig_histogram_high = px.histogram(df_high, x='Demanda_Max_Estimada', 
                                      title='Histograma de Demanda Alta (> 40)')

    # Correlation Heatmaps
    cols_to_correlate = ['Matrícula_Estimada_Historica', 'Proyectados_Actual_(S)', 'Meta_Nuevos',
                         'Demanda_Max_Estimada', 'Nro_Grupos_40', 'Nro_Grupos_30', 'Nro_Grupos_25']
    
    edades_clasificadas = pd.cut(df_10['Demanda_Max_Estimada'], bins=[0,40,2300]).astype(str)
    frecuencia = edades_clasificadas.value_counts().sort_index()
    ttabla_frecuencias = pd.DataFrame({
            'Intervalo': frecuencia.index.astype(str),  
            'Frecuencia': frecuencia.values})
    ttabla_frecuencias =  ttabla_frecuencias.iloc[:-1]
    fig_scatter = px.pie(ttabla_frecuencias, values='Frecuencia', names='Intervalo', 
                title=f'Distribución de la Demanda Máxima Estimada',
                hole=0.3,
                color_discrete_sequence= ['#afeeee', '#3486eb']) 

    fig_cumulative = px.scatter(filtered_df, x='Matrícula_Estimada_Historica', y='Demanda_Max_Estimada', 
                         trendline="ols", title="Demanda vs Matrícula con Línea de Tendencia")

    
    def create_heatmap(df, title):
        corr = df[cols_to_correlate].corr()
        fig = px.imshow(corr, title=title, color_continuous_scale='Viridis')
        return fig

    fig_heatmap_low = create_heatmap(df_low, 'Correlación para Demanda Baja (≤ 40)')
    fig_heatmap_high = create_heatmap(df_high, 'Correlación para Demanda Alta (> 40)')

    return (fig_desc_table, fig_demand_table_low, fig_demand_table_high, fig_trend, 
            fig_cumulative, fig_scatter,
            fig_boxplot_low, fig_boxplot_high, fig_histogram_low, fig_histogram_high, 
            fig_heatmap_low, fig_heatmap_high)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True)

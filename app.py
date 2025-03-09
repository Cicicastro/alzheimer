import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
from flask import Flask

# Criar o servidor Flask (necessário para Hugging Face Spaces)
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# Carregar os datasets tratados
cross_sectional_path = "oasis_cross-sectional-processed.csv"
longitudinal_path = "oasis_longitudinal-processed.csv"

df_cross = pd.read_csv(cross_sectional_path)
df_long = pd.read_csv(longitudinal_path)

# Layout do Dashboard
app.layout = html.Div([
    html.H1("Alzheimer's Disease Dashboard", style={'textAlign': 'center'}),

    # Dropdown para seleção do grupo
    html.Label("Select Group:"),
    dcc.Dropdown(
        id='group-dropdown',
        options=[
            {'label': 'All', 'value': 'All'},
            {'label': 'Nondemented', 'value': 'Nondemented'},
            {'label': 'Demented', 'value': 'Demented'},
            {'label': 'Converted', 'value': 'Converted'}
        ],
        value='All',
        clearable=False
    ),

    # KPIs
    html.Div([
        html.Div([html.H3("Average Age"), html.P(id="avg-age")], className="kpi"),
        html.Div([html.H3("Average MMSE"), html.P(id="avg-mmse")], className="kpi"),
        html.Div([html.H3("Average CDR"), html.P(id="avg-cdr")], className="kpi"),
    ], className="kpi-container"),

    # Gráficos
    dcc.Graph(id='age-histogram'),
    dcc.Graph(id='mmse-boxplot'),
    dcc.Graph(id='etiv-boxplot'),
    dcc.Graph(id='correlation-heatmap')
])

# Callback para atualizar os gráficos e KPIs
@app.callback(
    [Output('avg-age', 'children'),
     Output('avg-mmse', 'children'),
     Output('avg-cdr', 'children'),
     Output('age-histogram', 'figure'),
     Output('mmse-boxplot', 'figure'),
     Output('etiv-boxplot', 'figure'),
     Output('correlation-heatmap', 'figure')],
    [Input('group-dropdown', 'value')]
)
def update_dashboard(selected_group):
    df_filtered = df_long if selected_group == "All" else df_long[df_long['Group'] == selected_group]

    avg_age = round(df_filtered['Age'].mean(), 2)
    avg_mmse = round(df_filtered['MMSE'].mean(), 2)
    avg_cdr = round(df_filtered['CDR'].mean(), 2)

    # Histogram de Idade
    fig_age = px.histogram(df_filtered, x="Age", title="Age Distribution")

    # Boxplot MMSE
    fig_mmse = px.box(df_filtered, x="Group", y="MMSE", title="MMSE by Group")

    # Boxplot eTIV
    fig_etiv = px.box(df_filtered, x="Group", y="eTIV", title="eTIV by Group")

    # Heatmap de correlação
    correlation_matrix = df_long[['Age', 'MMSE', 'CDR', 'eTIV', 'nWBV']].corr()
    fig_corr = px.imshow(correlation_matrix, text_auto=True, title="Correlation Heatmap")

    return avg_age, avg_mmse, avg_cdr, fig_age, fig_mmse, fig_etiv, fig_corr

# Rodar o app na porta 7860 (necessário para Hugging Face)
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=7860)
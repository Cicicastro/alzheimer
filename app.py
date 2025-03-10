import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import statsmodels.api as sm
from flask import Flask

# Criar servidor Flask
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# Carregar dataset cross-sectional
cross_sectional_path = "oasis_cross-sectional-processed.csv"
df_cross = pd.read_csv(cross_sectional_path)

# Calcular correlações relevantes
correlations = df_cross[['Educ', 'MMSE', 'CDR', 'eTIV', 'nWBV']].corr()['Educ'].drop('Educ')

# Layout do Dashboard
app.layout = html.Div([
    html.H1("Alzheimer's Disease Dashboard", style={'textAlign': 'center'}),

    # Dropdown para selecionar tipo de análise
    dcc.Dropdown(
        id='analysis-type',
        options=[
            {'label': 'Descriptive Analysis', 'value': 'descriptive'},
            {'label': 'Predictive Analysis', 'value': 'predictive'}
        ],
        value='descriptive',
        clearable=False
    ),

    # Conteúdo dinâmico
    html.Div(id='analysis-content', style={'margin-top': '20px'})
])

# Callback para atualizar o conteúdo
@app.callback(
    Output('analysis-content', 'children'),
    [Input('analysis-type', 'value')]
)
def update_analysis_content(selected_analysis):
    if selected_analysis == 'descriptive':
        # Scatter plot de Educ x MMSE
        fig_educ_mmse = px.scatter(df_cross, x="Educ", y="MMSE", trendline="ols",
                                   title="Education Level vs. MMSE Score",
                                   labels={"Educ": "Education Level", "MMSE": "MMSE Score"})

        # Scatter plot de Educ x CDR
        fig_educ_cdr = px.scatter(df_cross, x="Educ", y="CDR", trendline="ols",
                                  title="Education Level vs. CDR Score",
                                  labels={"Educ": "Education Level", "CDR": "CDR Score"})

        # Scatter plot de Educ x eTIV
        fig_educ_etiv = px.scatter(df_cross, x="Educ", y="eTIV", trendline="ols",
                                   title="Education Level vs. eTIV",
                                   labels={"Educ": "Education Level", "eTIV": "Estimated Total Intracranial Volume"})

        # Scatter plot de Educ x nWBV
        fig_educ_nwbv = px.scatter(df_cross, x="Educ", y="nWBV", trendline="ols",
                                   title="Education Level vs. Normalized Whole Brain Volume",
                                   labels={"Educ": "Education Level", "nWBV": "Normalized Brain Volume"})

        # Bar Chart para mostrar os coeficientes de correlação
        fig_correlation_bar = px.bar(x=correlations.index, y=correlations.values, 
                                     labels={'x': 'Variable', 'y': 'Correlation Coefficient'},
                                     title="Correlation between Education and Alzheimer-related Factors")

        return html.Div([
            html.H3("Does Education Influence Alzheimer's Risk?"),

            html.P("We analyze how Education Level relates to key indicators of cognitive function and brain health."),

            dcc.Graph(figure=fig_educ_mmse),
            dcc.Graph(figure=fig_educ_cdr),
            dcc.Graph(figure=fig_educ_etiv),
            dcc.Graph(figure=fig_educ_nwbv),

            dcc.Graph(figure=fig_correlation_bar),

            html.Div([
                html.H4("📌 Key Insights:"),
                html.P(f"• Educ x MMSE → Correlation: {correlations['MMSE']:.2f} (Weak to Moderate)"),
                html.P(f"• Educ x CDR → Correlation: {correlations['CDR']:.2f} (Weak)"),
                html.P(f"• Educ x eTIV → Correlation: {correlations['eTIV']:.2f} (Very Weak)"),
                html.P(f"• Educ x nWBV → Correlation: {correlations['nWBV']:.2f} (Very Weak)"),

                html.H4("💡 What Does This Mean?"),
                html.P("The relationship between education and Alzheimer's indicators is weaker than expected. "
                       "While higher education levels slightly correlate with better MMSE scores, the effect is not strong."),
            ], style={'padding': '20px', 'border': '1px solid #ddd', 'border-radius': '5px', 'background-color': '#f9f9f9'})
        ])

    elif selected_analysis == 'predictive':
        return html.Div([
            html.H3("Predictive Analysis Coming Soon"),
            html.P("This section will contain predictive modeling results.")
        ])

    return html.P("Select an analysis from the dropdown above.")

# Rodar o app no Hugging Face Spaces
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=7860)
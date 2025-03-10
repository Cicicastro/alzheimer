import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
from flask import Flask

# Create Flask server (required for Hugging Face Spaces)
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# Load datasets
cross_sectional_path = "oasis_cross-sectional-processed.csv"
df_cross = pd.read_csv(cross_sectional_path)

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Alzheimer's Disease Dashboard", style={'textAlign': 'center'}),

    # Dropdown to select between descriptive or predictive analysis
    html.Label("Select Analysis:"),
    dcc.Dropdown(
        id='analysis-type',
        options=[
            {'label': 'Descriptive Analysis', 'value': 'descriptive'},
            {'label': 'Predictive Analysis', 'value': 'predictive'}
        ],
        value='descriptive',
        clearable=False
    ),

    # Placeholder for analysis content
    html.Div(id='analysis-content', style={'height': '80vh', 'overflowY': 'scroll'})
])

# Callback to update the displayed content based on the selected analysis
@app.callback(
    Output('analysis-content', 'children'),
    [Input('analysis-type', 'value')]
)
def update_analysis_content(analysis_type):
    if analysis_type == 'descriptive':
        # Boxplot - Relationship between Education and MMSE Score
        fig_education_mmse = px.box(df_cross, x="Educ", y="MMSE", 
                                    title="Cognitive Function (MMSE) by Education Level",
                                    labels={"Educ": "Education Level", "MMSE": "MMSE Score"},
                                    color="Educ")

        return html.Div([
            html.H3("Descriptive Analysis"),
            
            html.H4("Education & Alzheimer"),
            dcc.Graph(figure=fig_education_mmse),
            html.P("Higher education levels are correlated with better cognitive function (higher MMSE scores).")
        ])

    elif analysis_type == 'predictive':
        return html.H3("Predictive Analysis (Placeholder) - We will add graphs here!")

    return html.P("Select an analysis from the dropdown above to view results.")

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=7860)
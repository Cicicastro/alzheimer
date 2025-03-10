import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
from flask import Flask

# Create Flask server (required for Hugging Face Spaces)
server = Flask(__name__)
app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True)  # Allows dynamic components

# Load datasets (already processed)
df_cross = pd.read_csv("oasis_cross-sectional-processed.csv")
df_long = pd.read_csv("oasis_longitudinal-processed.csv")

# Ensure EDUC is integer for consistency
df_cross['Educ'] = df_cross['Educ'].astype(int)
df_long['EDUC'] = df_long['EDUC'].astype(int)

# Define dashboard layout
app.layout = html.Div([
    html.H1("Alzheimer's Disease Dashboard", style={'textAlign': 'center'}),

    # Dropdown to select the type of analysis
    html.Label("Select an analysis:", style={"font-weight": "bold"}),
    dcc.Dropdown(
        id='analysis-selector',
        options=[
            {'label': 'Education & Alzheimer', 'value': 'education'},
            {'label': 'Gender & Alzheimer', 'value': 'gender'},
            {'label': 'Disease Progression', 'value': 'progression'}
        ],
        value='education',
        clearable=False
    ),

    # Container for the dataset selection (One-time vs Longitudinal)
    html.Div(id='dataset-options-container'),

    # Content container
    html.Div(id='analysis-content', style={'height': '75vh', 'overflowY': 'auto'})
])

# Callback to display the dataset selection based on chosen analysis
@app.callback(
    Output('dataset-options-container', 'children'),
    [Input('analysis-selector', 'value')]
)
def update_dataset_options(selected_analysis):
    return html.Div([
        html.Label("Select the study type:", style={"font-weight": "bold"}),
        dcc.RadioItems(
            id='study-selector',
            options=[
                {'label': 'One-time patient evaluation', 'value': 'cross'},
                {'label': 'Patients followed for years', 'value': 'long'}
            ],
            value='cross',
            inline=False
        )
    ])

# Callback to update the displayed analysis content
@app.callback(
    Output('analysis-content', 'children'),
    [Input('analysis-selector', 'value'),
     Input('study-selector', 'value')]  # Agora reconhece corretamente o estudo selecionado
)
def update_analysis(selected_analysis, selected_study):
    if selected_analysis == 'education':
        if selected_study == "cross":
            fig_mmse_violin = px.violin(df_cross, x="Educ", y="MMSE", box=True, points="all",
                                        title="MMSE by Education Level (One-time evaluation)")
            fig_mmse_scatter = px.scatter(df_cross, x="Educ", y="MMSE", trendline="ols",
                                          title="Education vs MMSE (Scatter Plot)")

            return html.Div([
                html.H3("Education & Alzheimer - One-time evaluation", style={'textAlign': 'center'}),
                dcc.Graph(figure=fig_mmse_violin),
                dcc.Graph(figure=fig_mmse_scatter),
                html.P("Higher education levels are associated with better cognitive function."),
                html.P("ANOVA test for MMSE: p-value = 0.00014 (Significant)")
            ])
        else:
            fig_mmse_violin_long = px.violin(df_long, x="EDUC", y="MMSE", box=True, points="all",
                                             title="MMSE by Education Level (Longitudinal Study)")
            fig_mmse_line = px.line(df_long, x="Visit", y="MMSE", color="EDUC",
                                    title="MMSE Progression Over Time by Education Level")

            return html.Div([
                html.H3("Education & Alzheimer - Patients followed for years", style={'textAlign': 'center'}),
                dcc.Graph(figure=fig_mmse_violin_long),
                dcc.Graph(figure=fig_mmse_line),
                html.P("Higher education levels slow down cognitive decline."),
                html.P("Regression: Each additional year of education increases MMSE by 0.2565 points.")
            ])

    elif selected_analysis == 'gender':
        return html.Div([
            html.H3("Gender & Alzheimer (Coming Soon)", style={'textAlign': 'center'}),
            html.P("This section will analyze whether men and women experience Alzheimer's differently."),
        ])

    elif selected_analysis == 'progression':
        return html.Div([
            html.H3("Disease Progression (Coming Soon)", style={'textAlign': 'center'}),
            html.P("This section will explore the average time for conversion to Alzheimer's."),
        ])

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=7860)
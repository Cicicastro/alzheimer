import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
from flask import Flask

# Create Flask server (required for Hugging Face Spaces)
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

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

    # Content container
    html.Div(id='analysis-content', style={'height': '75vh', 'overflowY': 'auto'})
])

# Callback to update the displayed analysis content
@app.callback(
    Output('analysis-content', 'children'),
    Input('analysis-selector', 'value')
)
def update_analysis(selected_analysis):
    if selected_analysis == 'education':
        # Best insights from both datasets
        fig_mmse_violin = px.violin(df_cross, x="Educ", y="MMSE", box=True, points="all",
                                    title="MMSE by Education Level")
        fig_mmse_scatter = px.scatter(df_cross, x="Educ", y="MMSE", trendline="ols",
                                      title="Education vs MMSE (Scatter Plot)")
        fig_cdr_bar = px.bar(df_cross.groupby("Educ")["CDR"].mean().reset_index(),
                             x="Educ", y="CDR", title="Average CDR Score by Education Level")
        fig_mmse_line = px.line(df_long, x="Visit", y="MMSE", color="EDUC",
                                title="MMSE Progression Over Time by Education Level")

        return html.Div([
            html.H3("How does education affect Alzheimer's?", style={'textAlign': 'center'}),
            dcc.Graph(figure=fig_mmse_violin),
            html.P("People with higher education levels tend to have better cognitive function."),
            dcc.Graph(figure=fig_mmse_scatter),
            html.P("Regression analysis shows that each additional year of education increases MMSE by 0.2565 points."),
            dcc.Graph(figure=fig_cdr_bar),
            html.P("Lower education levels are associated with more severe dementia (higher CDR)."),
            dcc.Graph(figure=fig_mmse_line),
            html.P("Cognitive decline is slower for people with higher education levels.")
        ])

    elif selected_analysis == 'gender':
        # Placeholder until analysis is added
        return html.Div([
            html.H3("Gender & Alzheimer (Coming Soon)", style={'textAlign': 'center'}),
            html.P("This section will analyze whether men and women experience Alzheimer's differently."),
        ])

    elif selected_analysis == 'progression':
        # Placeholder until analysis is added
        return html.Div([
            html.H3("Disease Progression (Coming Soon)", style={'textAlign': 'center'}),
            html.P("This section will explore the average time for conversion to Alzheimer's."),
        ])

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=7860)
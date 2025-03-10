import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
from flask import Flask

# Create Flask server (required for Hugging Face Spaces)
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# Allow dynamically generated components
app.config.suppress_callback_exceptions = True

# Load datasets
cross_sectional_path = "oasis_cross-sectional-processed.csv"
longitudinal_path = "oasis_longitudinal-processed.csv"

df_cross = pd.read_csv(cross_sectional_path)
df_long = pd.read_csv(longitudinal_path)

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

    # Display selected analysis
    html.Div(id='analysis-content', style={'height': '80vh', 'overflowY': 'scroll'})
])

# Callback to update the displayed content based on the selected analysis
@app.callback(
    Output('analysis-content', 'children'),
    [Input('analysis-type', 'value')]
)
def update_analysis_content(analysis_type):
    if analysis_type == 'descriptive':
        return html.Div([
            html.H3("Descriptive Analysis"),
            
            html.H4("Socioeconomic Status & Alzheimer"),
            dcc.Graph(figure=px.box(df_cross, x='SES', y='CDR', title='SES & Alzheimer')),
            html.P("Lower SES may be associated with higher dementia risk."),

            html.H4("Education & Alzheimer"),
            dcc.Graph(figure=px.box(df_cross, x='Educ', y='MMSE', title='Education & Alzheimer')),
            html.P("Higher education levels are correlated with better cognitive function."),

            html.H4("Gender & Alzheimer"),
            dcc.Graph(figure=px.histogram(df_cross, x='M/F', color='Group', title='Gender & Alzheimer')),
            html.P("Does gender influence Alzheimer’s prevalence?"),

            html.H4("Brain Volume & Alzheimer"),
            dcc.Graph(figure=px.box(df_cross, x='Group', y='eTIV', title='Brain Volume & Alzheimer')),
            html.P("Individuals with Alzheimer’s tend to have smaller brain volume.")
        ])

    elif analysis_type == 'predictive':
        return html.Div([
            html.H3("Predictive Analysis"),
            
            html.H4("CDR Progression Over Time"),
            dcc.Graph(figure=px.line(df_long, x='Visit', y='CDR', color='Group', title='CDR Progression Over Time')),
            html.P("How does dementia severity change over time?"),

            html.H4("Brain Volume Decline"),
            dcc.Graph(figure=px.line(df_long, x='Visit', y='nWBV', color='Group', title='Brain Volume Decline')),
            html.P("Does brain shrinkage occur faster in Alzheimer’s patients?"),

            html.H4("Education & Cognitive Decline"),
            dcc.Graph(figure=px.line(df_long, x='Visit', y='MMSE', color='EDUC', title='Education & Cognitive Decline')),
            html.P("Do individuals with higher education maintain cognitive function longer?"),

            html.H4("Time to Dementia Conversion"),
            dcc.Graph(figure=px.histogram(df_long[df_long['Group'] == 'Converted'], x='Visit', title='Time to Dementia Conversion')),
            html.P("How long does it take for individuals to develop dementia?"),

            html.H4("Gender & Disease Progression"),
            dcc.Graph(figure=px.line(df_long, x='Visit', y='CDR', color='M/F', title='Gender & Disease Progression')),
            html.P("Does dementia progression differ between men and women?")
        ])

    return html.P("Select an analysis from the dropdown above to view results.")

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=7860)
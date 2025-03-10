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

    # Dropdown to select the type of analysis
    dcc.Dropdown(
        id='analysis-type',
        options=[
            {'label': 'Descriptive Analysis', 'value': 'descriptive'},
            {'label': 'Predictive Analysis', 'value': 'predictive'}
        ],
        value='descriptive',
        clearable=False
    ),
    
    # Container for second dropdown
    html.Div(id='analysis-options-container'),

    # Display selected analysis
    html.Div(id='analysis-content', style={'height': '80vh', 'overflowY': 'scroll'})
])

# Callback to update the second dropdown based on the first selection
@app.callback(
    Output('analysis-options-container', 'children'),
    [Input('analysis-type', 'value')]
)
def update_analysis_dropdown(selected_analysis):
    if selected_analysis == 'descriptive':
        return dcc.Dropdown(
            id='descriptive-analysis',
            options=[
                {'label': 'SES & Alzheimer', 'value': 'ses'},
                {'label': 'Education & Alzheimer', 'value': 'education'},
                {'label': 'Gender & Alzheimer', 'value': 'gender'},
                {'label': 'Brain Volume & Alzheimer', 'value': 'brain_volume'}
            ],
            value='ses',
            clearable=False
        )
    elif selected_analysis == 'predictive':
        return dcc.Dropdown(
            id='predictive-analysis',
            options=[
                {'label': 'CDR Progression Over Time', 'value': 'cdr_progression'},
                {'label': 'Brain Volume Decline', 'value': 'brain_decline'},
                {'label': 'Education & Cognitive Decline', 'value': 'education_decline'},
                {'label': 'Time to Dementia Conversion', 'value': 'dementia_conversion'},
                {'label': 'Gender & Disease Progression', 'value': 'gender_progression'}
            ],
            value='cdr_progression',
            clearable=False
        )
    return None

# Callback to update the displayed content based on the selected analysis
@app.callback(
    Output('analysis-content', 'children'),
    [Input('analysis-type', 'value'),
     Input('descriptive-analysis', 'value'),
     Input('predictive-analysis', 'value')]
)
def update_analysis_content(analysis_type, descriptive_option, predictive_option):
    if analysis_type == 'descriptive':
        if descriptive_option == 'ses':
            fig = px.box(df_cross, x='SES', y='CDR', title='SES & Alzheimer')
            return [dcc.Graph(figure=fig), html.P("Lower SES may be associated with higher dementia risk.")]
        elif descriptive_option == 'education':
            fig = px.box(df_cross, x='Educ', y='MMSE', title='Education & Alzheimer')
            return [dcc.Graph(figure=fig), html.P("Higher education levels are correlated with better cognitive function.")]
        elif descriptive_option == 'gender':
            fig = px.histogram(df_cross, x='M/F', color='Group', title='Gender & Alzheimer')
            return [dcc.Graph(figure=fig), html.P("Does gender influence Alzheimer’s prevalence?")]
        elif descriptive_option == 'brain_volume':
            fig = px.box(df_cross, x='Group', y='eTIV', title='Brain Volume & Alzheimer')
            return [dcc.Graph(figure=fig), html.P("Individuals with Alzheimer’s tend to have smaller brain volume.")]
    
    elif analysis_type == 'predictive':
        if predictive_option == 'cdr_progression':
            fig = px.line(df_long, x='Visit', y='CDR', color='Group', title='CDR Progression Over Time')
            return [dcc.Graph(figure=fig), html.P("How does dementia severity change over time?")]
        elif predictive_option == 'brain_decline':
            fig = px.line(df_long, x='Visit', y='nWBV', color='Group', title='Brain Volume Decline')
            return [dcc.Graph(figure=fig), html.P("Does brain shrinkage occur faster in Alzheimer’s patients?")]
        elif predictive_option == 'education_decline':
            fig = px.line(df_long, x='Visit', y='MMSE', color='EDUC', title='Education & Cognitive Decline')
            return [dcc.Graph(figure=fig), html.P("Do individuals with higher education maintain cognitive function longer?")]
        elif predictive_option == 'dementia_conversion':
            fig = px.histogram(df_long[df_long['Group'] == 'Converted'], x='Visit', title='Time to Dementia Conversion')
            return [dcc.Graph(figure=fig), html.P("How long does it take for individuals to develop dementia?")]
        elif predictive_option == 'gender_progression':
            fig = px.line(df_long, x='Visit', y='CDR', color='M/F', title='Gender & Disease Progression')
            return [dcc.Graph(figure=fig), html.P("Does dementia progression differ between men and women?")]
    
    return None

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=7860)
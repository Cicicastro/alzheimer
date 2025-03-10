import dash
from dash import dcc, html, Input, Output
from flask import Flask

# Create Flask server (required for Hugging Face Spaces)
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

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
        return html.H3("Descriptive Analysis (Placeholder) - We will add graphs here!")
    elif analysis_type == 'predictive':
        return html.H3("Predictive Analysis (Placeholder) - We will add graphs here!")

    return html.P("Select an analysis from the dropdown above to view results.")

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=7860)
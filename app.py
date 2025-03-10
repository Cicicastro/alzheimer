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

# Convert "Years of Education" (EDUC) to "Education Level" (1 to 5)
def convert_years_to_level(years):
    if years <= 8:
        return 1  # Elementary
    elif years <= 11:
        return 2  # Middle School
    elif years <= 13:
        return 3  # High School
    elif years <= 15:
        return 4  # Associate/Bachelor
    else:
        return 5  # Postgraduate

df_long['Educ'] = df_long['EDUC'].apply(convert_years_to_level)

# Define color scheme (use same colors across graphs)
color_scheme = px.colors.qualitative.Dark24  

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
        # Bar chart for MMSE by Education Level
        fig_mmse_bar = px.bar(df_cross.groupby("Educ")["MMSE"].mean().reset_index(),
                              x="Educ", y="MMSE", 
                              title="Average MMSE Score by Education Level",
                              color="Educ",
                              color_discrete_sequence=color_scheme)

        # Scatter plot for MMSE & Education (OLS trendline)
        fig_mmse_scatter = px.scatter(df_cross, x="Educ", y="MMSE", trendline="ols",
                                      title="Education vs MMSE (Scatter Plot)",
                                      color="Educ",
                                      color_discrete_sequence=color_scheme)

        # Bar chart for CDR by education level
        fig_cdr_bar = px.bar(df_cross.groupby("Educ")["CDR"].mean().reset_index(),
                             x="Educ", y="CDR", 
                             title="Average CDR Score by Education Level",
                             color="Educ",
                             color_discrete_sequence=color_scheme)

        # Line chart for MMSE over time with grouped education levels
        fig_mmse_line = px.line(df_long.groupby(["Visit", "Educ"])["MMSE"].mean().reset_index(),
                                x="Visit", y="MMSE", color="Educ",
                                title="MMSE Progression Over Time by Education Level",
                                color_discrete_sequence=color_scheme)

        return html.Div([
            html.H3("How does education affect Alzheimer's?", style={'textAlign': 'center'}),

            dcc.Graph(figure=fig_mmse_bar),
            html.P("People with higher education levels tend to have better cognitive function."),
            
            dcc.Graph(figure=fig_mmse_scatter),
            html.P("Regression analysis: Each additional year of education increases MMSE by **0.2565 points**."),
            html.P("ANOVA test for MMSE: **p-value = 0.00055** (Statistically significant)."),
            
            dcc.Graph(figure=fig_cdr_bar),
            html.P("Lower education levels are associated with more severe dementia (higher CDR)."),
            html.P("ANOVA test for CDR: **p-value = 0.00156** (Statistically significant)."),

            dcc.Graph(figure=fig_mmse_line),
            html.P("Cognitive decline appears slower for higher education levels."),
            html.P("However, for **level 5**, there is a sharp decline after the third visit. This may suggest that people with more education can compensate for Alzheimer's in the early stages, but once the disease progresses, decline accelerates."),
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
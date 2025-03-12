import gradio as gr
import pandas as pd
import plotly.express as px
import scipy.stats as stats

# Carregar os datasets
df_cross = pd.read_csv("oasis_cross-sectional-processed.csv")
df_long = pd.read_csv("oasis_longitudinal-processed.csv")

# Função para gerar gráficos descritivos
def generate_graphs(dataset):
    df = df_cross if dataset == "Cross-Sectional" else df_long
    
    # Criar a variável Condition
    if "CDR" in df.columns:
        df["Condition"] = df["CDR"].apply(lambda x: "Healthy" if x == 0 else "Alzheimer")
    
    # Criar gráficos
    fig_age = px.histogram(df, x="Age", color="Condition", title="Age Distribution")
    fig_educ = px.histogram(df, x="Educ" if "Educ" in df.columns else "EDUC", color="Condition", title="Education Level Distribution")
    fig_ses = px.histogram(df, x="SES", color="Condition", title="Socioeconomic Status Distribution")
    fig_nwbv = px.histogram(df, x="nWBV", color="Condition", title="Brain Volume Distribution")

    # Testes estatísticos
    age_pval = stats.ttest_ind(df[df["Condition"] == "Healthy"]["Age"], df[df["Condition"] == "Alzheimer"]["Age"], nan_policy="omit").pvalue
    educ_pval = stats.ttest_ind(df[df["Condition"] == "Healthy"]["Educ" if "Educ" in df.columns else "EDUC"], df[df["Condition"] == "Alzheimer"]["Educ" if "Educ" in df.columns else "EDUC"], nan_policy="omit").pvalue
    ses_pval = stats.ttest_ind(df[df["Condition"] == "Healthy"]["SES"], df[df["Condition"] == "Alzheimer"]["SES"], nan_policy="omit").pvalue
    nwbv_pval = stats.ttest_ind(df[df["Condition"] == "Healthy"]["nWBV"], df[df["Condition"] == "Alzheimer"]["nWBV"], nan_policy="omit").pvalue

    p_values_text = f"""
    **Statistical tests for mean differences:**
    - Age p-value: {age_pval:.5f}
    - Education Level p-value: {educ_pval:.5f}
    - Socioeconomic Status p-value: {ses_pval:.5f}
    - Brain Volume p-value: {nwbv_pval:.5f}
    """

    return fig_age, fig_educ, fig_ses, fig_nwbv, p_values_text

# Criar interface Gradio
with gr.Blocks() as demo:
    gr.Markdown("# Alzheimer Analysis Dashboard")

    dataset_choice = gr.Radio(["Cross-Sectional", "Longitudinal"], label="Select Dataset")

    with gr.Row():
        output_age = gr.Plot(label="Age Distribution")
        output_educ = gr.Plot(label="Education Level Distribution")

    with gr.Row():
        output_ses = gr.Plot(label="Socioeconomic Status Distribution")
        output_nwbv = gr.Plot(label="Brain Volume Distribution")

    output_text = gr.Markdown()

    dataset_choice.change(generate_graphs, inputs=dataset_choice, outputs=[output_age, output_educ, output_ses, output_nwbv, output_text])

demo.launch()
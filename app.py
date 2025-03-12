import gradio as gr
import pandas as pd
import plotly.express as px
import scipy.stats as stats

# Carregar os datasets
df_cross = pd.read_csv("oasis_cross-sectional-processed.csv")
df_long = pd.read_csv("oasis_longitudinal-processed.csv")

# Padronizar nomes das colunas para manter consistência
df_long.rename(columns={"EDUC": "Educ"}, inplace=True)
df_cross.rename(columns={"EDUC": "Educ"}, inplace=True)

# Criar as colunas Condition corretamente
df_long["Condition"] = df_long["Group"]
df_long = df_long[df_long["Condition"].isin(["Nondemented", "Demented"])]
df_cross["Condition"] = df_cross["CDR"].apply(lambda x: "Healthy" if x == 0 else "Alzheimer")

# Definir cores personalizadas
custom_palette = {"Healthy": "#1f77b4", "Alzheimer": "#ff7f0e", "Nondemented": "#1f77b4", "Demented": "#ff7f0e"}

# Função para gerar gráficos descritivos
def generate_graphs(dataset):
    df = df_cross if dataset == "Cross-Sectional" else df_long
    condition_healthy = "Nondemented" if dataset == "Longitudinal" else "Healthy"
    condition_demented = "Demented" if dataset == "Longitudinal" else "Alzheimer"

    # Gerar gráficos com linha de tendência (kde=True)
    fig_age = px.histogram(df, x="Age", color="Condition", nbins=15, opacity=0.6, barmode="overlay",
                           title="Age Distribution", color_discrete_map=custom_palette, marginal="rug")

    fig_educ = px.histogram(df, x="Educ", color="Condition", nbins=10, opacity=0.6, barmode="overlay",
                            title="Education Level Distribution", color_discrete_map=custom_palette, marginal="rug")

    fig_ses = px.histogram(df, x="SES", color="Condition", nbins=5, opacity=0.6, barmode="overlay",
                           title="Socioeconomic Status Distribution", color_discrete_map=custom_palette, marginal="rug")

    fig_nwbv = px.histogram(df, x="nWBV", color="Condition", nbins=20, opacity=0.6, barmode="overlay",
                            title="Brain Volume Distribution", color_discrete_map=custom_palette, marginal="rug")

    fig_nwbv_boxplot = px.box(df, x="Condition", y="nWBV", color="Condition",
                               title="Brain Volume Boxplot", color_discrete_map=custom_palette)

    # Cálculo da prevalência por gênero
    total_gender_counts = df["M/F"].value_counts()
    demented_gender_counts = df[df["Condition"] == condition_demented]["M/F"].value_counts()
    prevalence_percentage = (demented_gender_counts / total_gender_counts) * 100

    # Gráfico de prevalência de Alzheimer por gênero
    fig_gender_prevalence = px.bar(
        x=prevalence_percentage.index,
        y=prevalence_percentage.values,
        color=prevalence_percentage.index,
        title="Prevalence of Alzheimer's by Gender (Percentage)",
        labels={"x": "Gender", "y": "Percentage of Demented Cases"},
        color_discrete_map={"M": "#1f77b4", "F": "#ff7f0e"}
    )

    # Calcular p-values
    age_pval = stats.ttest_ind(df[df["Condition"] == condition_healthy]["Age"],
                               df[df["Condition"] == condition_demented]["Age"], nan_policy="omit").pvalue

    educ_pval = stats.ttest_ind(df[df["Condition"] == condition_healthy]["Educ"],
                                df[df["Condition"] == condition_demented]["Educ"], nan_policy="omit").pvalue

    ses_pval = stats.ttest_ind(df[df["Condition"] == condition_healthy]["SES"],
                               df[df["Condition"] == condition_demented]["SES"], nan_policy="omit").pvalue

    nwbv_pval = stats.ttest_ind(df[df["Condition"] == condition_healthy]["nWBV"],
                                df[df["Condition"] == condition_demented]["nWBV"], nan_policy="omit").pvalue

    chi2, gender_pval, _, _ = stats.chi2_contingency(pd.crosstab(df["M/F"], df["Condition"]))

    # Texto de p-value abaixo de cada gráfico correspondente
    p_value_age = f"**p-value: {age_pval:.5f}**"
    p_value_educ = f"**p-value: {educ_pval:.5f}**"
    p_value_ses = f"**p-value: {ses_pval:.5f}**"
    p_value_nwbv = f"**p-value: {nwbv_pval:.5f}**"
    p_value_gender = f"**p-value: {gender_pval:.5f}**"

    return (fig_age, p_value_age, fig_educ, p_value_educ, fig_ses, p_value_ses, 
            fig_gender_prevalence, p_value_gender, fig_nwbv, p_value_nwbv, fig_nwbv_boxplot)

# Criar interface Gradio
with gr.Blocks() as demo:
    gr.Markdown("# Alzheimer Analysis Dashboard")

    dataset_choice = gr.Radio(["Cross-Sectional", "Longitudinal"], value="Cross-Sectional", label="Select Dataset")  # Default = Cross-Sectional

    with gr.Row():
        with gr.Column():
            output_age = gr.Plot(label="Age Distribution")
            output_pval_age = gr.Markdown()
        with gr.Column():
            output_educ = gr.Plot(label="Education Level Distribution")
            output_pval_educ = gr.Markdown()

    with gr.Row():
        with gr.Column():
            output_ses = gr.Plot(label="Socioeconomic Status Distribution")
            output_pval_ses = gr.Markdown()
        with gr.Column():
            output_gender = gr.Plot(label="Prevalence of Alzheimer's by Gender")
            output_pval_gender = gr.Markdown()

    with gr.Row():
        with gr.Column():
            output_nwbv = gr.Plot(label="Brain Volume Distribution")
            output_pval_nwbv = gr.Markdown()
        with gr.Column():
            output_nwbv_box = gr.Plot(label="Brain Volume Boxplot")

    dataset_choice.change(generate_graphs, 
                          inputs=dataset_choice, 
                          outputs=[output_age, output_pval_age, output_educ, output_pval_educ, 
                                   output_ses, output_pval_ses, output_gender, output_pval_gender, 
                                   output_nwbv, output_pval_nwbv, output_nwbv_box])

demo.launch()
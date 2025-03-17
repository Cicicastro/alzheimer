---
title: Alzheimer
emoji: 🌍
colorFrom: purple
colorTo: pink
sdk: gradio
sdk_version: 5.20.1
app_file: app.py
pinned: false
license: mit
short_description: Alzheimer Dashboard
---


__Alzheimer's Disease Dashboard__

__Overview__

This project aims to analyze patterns in MRI data from individuals with and without Alzheimer's disease. The goal is to identify key factors related to dementia progression and create an interactive dashboard to visualize insights.

__Objectives__

- Explore how age, education level, and socioeconomic status relate to dementia risk;
- Compare brain volume differences between healthy and Alzheimer's patients;
- Understand the impact of cognitive scores (MMSE & CDR) in differentiating dementia stages;
- Track the progression of Alzheimer's over time using longitudinal data;
- Develop predictive models to estimate dementia progression.

__Dataset__

The analysis uses data from the OASIS (Open Access Series of Imaging Studies) project:

Cross-Sectional Dataset: A snapshot of patients assessed once.

Longitudinal Dataset: Patients tracked over multiple years.

__Variables__
1. Subject ID - Subject Identification (i.e. OAS2_0001)
2. MRI ID - MRI Exam Identification (i.e. OAS2_0001_MR1)
3. Group - Class (i.e. Demented, Nondemented)
4. Visit - Number of visits (i.e. 1-5)
5. MR Delay - Number of days of delay between visits (i.e. 0-2639)
6. M/F - Gender (i.e. M, F)
7. Hand - Right or Left-Handed (i.e. R)
8. Age - Age at time of image acquisition (years). (i.e. 60-98)
9. EDUC - Years of education (i.e. 6-23)
10. SES - Socioeconomic status as assessed by the Hollingshead Index of Social Position and classified into categories from 1 (highest status) to 5 (lowest status) (i.e. 1-5)
11. MMSE - Mini-Mental State Examination (i.e. 4-30)
12. CDR - Clinical Dementia Rating (i.e. 0-2)
13. eTIV - Estimated total intracranial volume (cm^3) (i.e. 1106-2004)
14. nWBV - Normalized whole brain volume: expressed as a percent of all voxels in the atlas-masked image that are labeled as gray or white matter by the automated tissue segmentation process (i.e. 0.64-0.84)
15. ASF - Atlas scaling factor (unitless). Computed scaling factor that transforms native-space brain and skull to the atlas target (i.e. the determinant of the transform matrix) (i.e. 0.88-1.59)

__Exploratory Data Analysis (EDA)__

The project is divided into two main analyses:

Descriptive Analysis

- Education & Alzheimer's → Does education level influence cognitive health?
- SES & Alzheimer's → Does socioeconomic status affect dementia risk?
- Gender & Alzheimer's → Are there differences between men and women?
- Brain Volume & Alzheimer's → Do Alzheimer's patients have lower brain volume?

Predictive Analysis

- Dementia Progression Over Time → How do MMSE & CDR scores change over time?
- Brain Volume Reduction → Does nWBV decrease faster in Alzheimer's patients?
- Education & Progression → Does higher education slow cognitive decline?
- Time to Conversion → How long does it take for a non-demented patient to become demented?
- Gender Differences → Do men and women experience dementia differently?

__Dashboard__

The Alzheimer’s Disease Dashboard is hosted on Hugging Face Spaces using Gradio.

🔗 Access the Dashboard Here: [Alzheimer Dashboard](https://huggingface.co/spaces/cidaliacastro/alzheimer)


__How to Run the Project Locally__

Prerequisites:
Make sure you have Python 3.9+ installed along with the required libraries.

1. Clone this repository:
git clone https://github.com/cidaliacastro/Alzheimer-Dashboard.git
cd Alzheimer-Dashboard
2. Install dependencies:
pip install -r requirements.txt
3. Run the application:
python app.py
4. Open your browser and go to:
http://127.0.0.1:7860/

__Future Work__

Implement a machine learning model to predict dementia progression.
Expand the dataset to include genetic & lifestyle factors.
Improve UI/UX of the dashboard for a better user experience.

__Contributing__

If you have suggestions or want to contribute, feel free to fork the repo and submit a pull request!

__License__

This project is licensed under the MIT License.


__📧 Author: Cidália Castro__

__💡 [My Portfolio](https://cicicastro.github.io/portfolio/)__

__🔗 [LinkedIn](https://www.linkedin.com/in/cidaliadecastro/)__
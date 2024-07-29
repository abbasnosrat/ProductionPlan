import streamlit as st
import pandas as pd
from main import *


@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')



st.write("# Production Planning Using Discrete Optimization")
st.sidebar.write("Controls")
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=".csv")
use_sample_data = st.sidebar.checkbox("Use Sample Data")
budget = st.sidebar.number_input("Insert your budget in IRL", value=100000000000)
got_data = False
try:
    products = pd.read_csv(uploaded_file)
    got_data = True
except:
    if use_sample_data:
        products = pd.read_csv("sample_data.csv")
        got_data = True

if got_data:
    problem = OptimizationProblem(products, budget)

    solution = problem.solve()
    st.write(f'The algorithm found the {solution["Solution Type"]} solution')
    st.write(f'Your profit amount with this plan is {solution["objective_value"]:.2f} tomans')
    st.write(f'Your profit is {solution["objective_value"]/problem.budget:.2f}% of the budget')
    st.write(f'Your remaining budget is {solution["constraint"]:.2f} tomans')
    result= pd.concat([products,pd.DataFrame({"optimal_quantity": solution["quantities"]})],axis=1)
    nas = result.isna().mean().to_numpy()
    na_cols = list(result.columns[nas == 1])
    result = result.drop(columns=na_cols)
    st.dataframe(result)
else:
    st.write("Please upload your data")
    df = pd.read_csv("sample_data.csv")
    csv = convert_df(df)
    st.download_button("Sample Data", csv, "SampleData.csv","text/csv",
    key='download-csv')
    
    
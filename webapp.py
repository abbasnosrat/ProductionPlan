import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.optimize import LinearConstraint

def get_bounds(row):
    lower = 0 if np.isnan(row["LowerBound"]) else row["LowerBound"]
    upper = np.inf if np.isnan(row["UpperBound"]) else row["UpperBound"]
    return (lower, upper)

class OptimizationProblem:
    def __init__(self, products: pd.DataFrame, budget: float):
        self.products = products["GoodName"].to_list()
        self.budget = budget / 10000
        self.cost = products["ABCfee"].to_numpy()
        self.benefit = products["Costbenefit"].to_numpy()
        self.bounds =  []
        self.bounds = products.apply(get_bounds, axis=1).to_list()
        self.gain = lambda x: np.sum(x * self.benefit)

    def objective(self, x):
        return -self.gain(x)

    def budget_constraint(self, x):
        return self.budget - np.sum(self.cost * x)

def main():

    st.write("""
    # Production Optimization App
    "Optimize your production plan by allocating your budget to maximize profits."
             
    """)
    
    #uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    uploaded_file = pd.read_csv("sample_data.csv")
    if uploaded_file is not None:
        #products = pd.read_csv(uploaded_file)
        products = uploaded_file
        
        budget = st.number_input("Enter your budget(Rial)")

        solver = 'trust-constr'
        
        problem = OptimizationProblem(products, budget)

        constraints = LinearConstraint(problem.cost, lb=0, ub=problem.budget)
        solution = minimize(problem.objective,
                            x0=np.zeros(len(problem.products)),
                            constraints=constraints,
                            bounds=problem.bounds,
                            method=solver, options={"maxiter": 100000000, "disp": True})
        
        st.write(f"Budget: {problem.budget}")
        st.write(f"Maximum Profit: {problem.gain(solution.x.round()):.3f}")
        st.write(f"Remaining Budget: {problem.budget_constraint(solution.x.round()):.3f}")
        
        products["ProductionPlan"] = solution.x.round()
        # Drop 'LowerBound' and 'UpperBound' columns
        products = products.drop(columns=['LowerBound', 'UpperBound'])

        st.write("""
        ##### Production Plan Overview
        """)
        st.dataframe(products)


        # st.download_button(
        #     label="Download Production Plan",
        #     data=products.to_excel("result.xlsx",index=False, engine='openpyxl'),

        # )


if __name__ == "__main__":
    main()
    print("Done")

import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.optimize import LinearConstraint
import io
from ortools.init.python import init
from ortools.linear_solver import pywraplp

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


    def solve(self):
    # Create the solver
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            return None
        
        # Number of products
        num_products = len(self.products)
        
        # Variables: integer quantities for each product
        x = []
        for i in range(num_products):
            lower_bound, upper_bound = self.bounds[i]
            x.append(solver.IntVar(lower_bound, upper_bound, f'x_{i}'))
        
        # Objective function: maximize gain
        solver.Maximize(solver.Sum(self.benefit[i] * x[i] for i in range(num_products)))
        
        # Budget constraint: sum(cost * x) <= budget
        solver.Add(solver.Sum(self.cost[i] * x[i] for i in range(num_products)) <= self.budget)
        
        # Solve the problem
        status = solver.Solve()
        
        # Check the result
        if status == pywraplp.Solver.OPTIMAL:
            optimal_quantities = [x[i].solution_value() for i in range(num_products)]
            used_budget = np.sum(self.cost * np.array(optimal_quantities))
            remaining_budget = self.budget - used_budget
            max_profit = self.gain(np.array(optimal_quantities))
            result = {
                'objective_value': solver.Objective().Value(),
                'remaining_budget': remaining_budget,
                'max_profit': max_profit,
                'quantities':  optimal_quantities

            }
            return result
        else:
            return None
        
def main():

    st.write("""
    # Production Optimization App
    "Optimize your production plan by allocating your budget to maximize profits."         
    """)
    
    st.sidebar.header('User Input Features')

    # Sample data
    sample_data = pd.read_csv("sample_data.csv", encoding='utf-8')
    # Save sample data to a BytesIO object
    buffer = io.BytesIO()
    sample_data.to_csv(buffer, index=False, encoding='utf-8')
    buffer.seek(0)
    # Sidebar download button for the sample file
    st.sidebar.download_button(
        label="Download Sample Input File",
        data= buffer.getvalue(),
        file_name="sample_input.csv",
        mime="text/csv"
    )

    uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file is not None:

        products = pd.read_csv(uploaded_file)
        
        budget = st.sidebar.number_input("Enter your budget(Rial)", min_value=0, value= 0)
        
        problem = OptimizationProblem(products, budget)
        
        solution = problem.solve()


        if solution:
            initial_budget_divided = budget / 10
            max_profit = solution['max_profit'] * 1000
            profit_percentage = (max_profit / initial_budget_divided) * 100
            st.write(f"Initial Budget: {initial_budget_divided:,.0f} Toman")
            st.write(f"Remaining Budget: {solution['remaining_budget'] * 1000 :,.0f} Toman")
            st.write(f"Total Profit: {max_profit:,.0f} Toman")
            st.write(f"Profit as Percentage of Budget: {profit_percentage:.2f}%")
            products['optimal_quantity'] = solution['quantities']
            st.write("Here are the optimal quantities for each product:")
            st.write(products)
        else:
            st.write("No optimal solution found.")

        # Save result to a BytesIO object as Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            products.to_excel(writer, index=False, sheet_name='Sheet1')
        buffer.seek(0)

        # Download button for the result
        st.download_button(
            label="Download Production Plan",
            data=buffer,
            file_name="result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


    else :
        st.write("Awaiting CSV file to be uploaded.")


if __name__ == "__main__":
    main()
    print("Done")

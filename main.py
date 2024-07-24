import pandas as pd
import numpy as np
from ortools.init.python import init
from ortools.linear_solver import pywraplp


def get_bounds(row:pd.DataFrame):
    lower = 0 if np.isnan(row["LowerBound"]) else row["LowerBound"]
    upper = np.inf if np.isnan(row["UpperBound"]) else row["UpperBound"]
    return (lower, upper)

class OptimizationProblem:
    def __init__(self,products:pd.DataFrame, budget:float):
        self.products = products["GoodName"].to_list()
        self.budget = budget/10000
        self.cost = products["ABCfee"].to_numpy()
        self.benefit = products["Costbenefit"].to_numpy()
        self.bounds =  []
        self.bounds = products.apply(get_bounds, axis=1).to_list()

        
        self.gain = lambda x: np.sum(x*self.benefit)

    def objective(self, x):
        return -self.gain(x)
    
    def budget_constraint(self,x):
        return self.budget - np.sum(self.cost*x)
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
            result = {
                "Solution Type": "Optimal",
                'objective_value': solver.Objective().Value(),
                "constraint":self.budget_constraint(np.array([x[i].solution_value() for i in range(num_products)])),
                'quantities': [x[i].solution_value() for i in range(num_products)]
            }
            return result
        elif status == pywraplp.Solver.FEASIBLE:
            result = {
                "Solution Type": "Feasible",
                'objective_value': solver.Objective().Value(),
                "constraint":self.budget_constraint(np.array([x[i].solution_value() for i in range(num_products)])),
                'quantities': [x[i].solution_value() for i in range(num_products)]
            }
            return result
        else:
            return None
        
        
products = pd.read_csv("sample_data.csv")

budget = 1000000
problem = OptimizationProblem(products, budget)

solution = problem.solve()
print(solution["objective_value"])
result= pd.concat([products,pd.DataFrame({"optimal_quantity": solution["quantities"]})],axis=1)
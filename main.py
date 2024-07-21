import numpy as np 
import pandas as pd
from scipy.optimize import minimize
from scipy.optimize import LinearConstraint
from scipy.optimize import minimize


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
    
    
    
    
    
    
    
    
    
    
    
products = pd.read_csv("sample_data.csv")

budget = 100000000000
solver = 'trust-constr'

problem = OptimizationProblem(products, budget)

constraints = LinearConstraint(problem.cost,lb=0,ub=problem.budget)
solution = minimize(problem.objective,
                    x0= np.zeros(len(problem.products)),
                    constraints=constraints,
                    bounds=problem.bounds, 
                    method=solver,options={"maxiter":100000000, "disp":True})
print(f"{problem.budget}, {solver}: {problem.gain(solution.x.round())}, {problem.budget_constraint(solution.x.round())}")
products["ProductionPlan"] = solution.x.round()
products.to_excel("products.xlsx", index=False)
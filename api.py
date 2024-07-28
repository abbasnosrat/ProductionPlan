from fastapi import FastAPI, File, UploadFile
import pandas as pd
from typing import Annotated, List, Optional
from main import OptimizationProblem
app = FastAPI()

# Global variable to store CSV data
global_csv_data: pd.DataFrame = pd.DataFrame()
budget = 1000000000

@app.get("/")
async def home_page():
    return {"message": "Hi!!! Welcome to my optimization web app!"}
@app.post("/upload-data/")
async def upload_csv(file: Annotated[UploadFile, File(description="Some description")] = None, Budget:float = None):
    global global_csv_data
    # Read the uploaded CSV file into a pandas DataFrame
    global budget
    if Budget != None:
        budget = Budget
    if file != None:
        df = pd.read_csv(file.file)
        global_csv_data = df
    if file != None and Budget != None:
        return {"message": "values uploaded"}
    elif file ==None and Budget !=None:
        return {"message": "using default csv"}
    elif file !=None and Budget ==None:
        return {"message": "using default budget"}
    else: return {"message": "using default values for budget and dataset"}
    # Store the DataFrame in the global variable
    
    



@app.get("/process-csv/")
async def process_csv():
    global global_csv_data
    global budget
    if global_csv_data.empty:
        global_csv_data = pd.read_csv("sample_data.csv")
    products = global_csv_data.copy()
    
    problem = OptimizationProblem(products, budget)

    solution = problem.solve()
    result= pd.concat([products,pd.DataFrame({"optimal_quantity": solution["quantities"]})],axis=1)
    # Example operation: Get the number of rows and columns in the CSV
    
    return result.to_json()

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

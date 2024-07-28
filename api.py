from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
from typing import Annotated, List, Optional
from main import OptimizationProblem
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global variable to store CSV data
global_csv_data: pd.DataFrame = pd.DataFrame()
budget = 1000000000
default_budget = 1000000000
defualt_csv = pd.read_csv("sample_data.csv")
@app.get("/")
async def home_page():
    return FileResponse('static/index.html')
@app.post("/upload-data/")
async def upload_csv(file: Optional[UploadFile] = File(None), Budget: Optional[float] = Form(None)):
    global global_csv_data
    global budget
    response_message = ""
    got_csv=False
    got_budget = False
    if Budget is not None:
        budget = Budget
        got_budget = True
        response_message += "Budget set successfully. "
    
    if file is not None:
        try: 
            df = pd.read_csv(file.file)
        
            global_csv_data = df
            got_csv = True
            response_message += "File uploaded successfully. "
        except:
            got_csv=False
        
    if not got_csv:
        global defualt_csv
        global_csv_data = defualt_csv.copy()
    if not got_budget:
        global default_budget
        budget = default_budget
    if response_message == "":
        response_message = "Using default values for budget and dataset."
    print(global_csv_data)
    return {"message": response_message}
    
    



@app.get("/process-csv/")
async def process_csv():
    global global_csv_data
    global budget

    products = global_csv_data.copy()
    
    problem = OptimizationProblem(products, budget)

    solution = problem.solve()
    result= pd.concat([products,pd.DataFrame({"optimal_quantity": solution["quantities"]})],axis=1)
    result_dict = result.fillna("").to_dict(orient="split",index=False)
    # return result.to_json(index=False)
    return result_dict


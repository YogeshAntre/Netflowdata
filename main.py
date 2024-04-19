
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI,Query, HTTPException
from function import *
from model import *
from typing import Optional

app= FastAPI()


@app.post('/getallAssociatedInterface', tags=['All AssociatedInterface'], summary="This API give  all All AssociatedInterface name".upper())
def get_all_report(data: Interface ):
    data = data.dict()
    return getallreport(data)

@app.post("/getGraph")
def getGraph(data:Graph):
    data=data.dict()
    return getalltableAndGraph(data)

@app.post("/getAllSubnetData")
def getallSubnet(data:InGraphSubnet):
    data=data.dict()
    return getFinalData(data)

# @app.post("/getGraphSubnet")
# def getGraph(data:SubnetGraph,subnet1:str,subnet_mask:str):
#     data=data.dict()
#     print(data)
#     print(subnet1)
#     print(subnet_mask)

#     return getalltableAndGraphdataSubnet(data,subnet1,subnet_mask)


@app.post("/getGraphSubnet")
#def get_graph_subnet(data: SubnetGraph, subnet1: str = Query(...), subnet_mask: SubnetMaskEnum = Query(...)):
def get_graph_subnet(data: SubnetGraph, subnet_data: Optional[str] = Query(None), subnet_mask: SubnetMaskEnum = Query(None)):
    data_dict = data.dict()
    if subnet_data is None and subnet_mask is None and data.subnet is None:
        raise HTTPException(status_code=422, detail="Either subnet_data and subnet_mask must be provided as query parameters or subnet in the payload.")

    return getalltableAndGraphdataSubnet(data_dict, subnet_data, subnet_mask.value if subnet_mask else None)


@app.post("/getAllGraphData")
def get_graph_data_app(data: GraphData):
    data=data.dict()
    return getalltableAndGraphdata(data)
 
@app.get("/")
def m():
    return {"status":True}

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="localhost", port=8001, reload=True)
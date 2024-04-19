import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException,Query
from function import *
from model import *
from schmas import *
from passlib.context import CryptContext
from hassingpassword import *
from Oauth2 import *
from typing import Optional



app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
SECRET_KEY = 'revdau.com'

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.post('/user' , tags=['Users'])
def create_user (data :User):
    name = data.username
    email = data.email
    password = data.password
    hash = encyrptModule(text=password,key = SECRET_KEY )
    mapping = {
        "username":name,
        "email" :  email,
        "password" : hash
    }
    index = 'api_asses_credentials'
    res  = create(index_name = index ,mapping= mapping)
    return res

@app.post('/login' ,  tags=['Authentication'])
def login_api (data : Login):
    username = data.username
    password = data.password
    query = {"query":{"bool":{"must":[{"match":{"username.keyword":username}}]}}}
    index = "api_asses_credentials"
    res = get_by_query(index_name=index , query=query)
    if not res:
        return dict(status = False, msg = 'user is not found')
    hash = decryptModule(text= res[0]["password"] , key= SECRET_KEY)
    if not hash['msg'] == password :
        return dict(status = False )

    return dict(status = True)


@app.post('/getallAssociatedInterface', tags=['All AssociatedInterface'], summary="This API give  all All AssociatedInterface name".upper())
def get_all_report(data: Interface ):
    data = data.dict()
    return getallreport(data)

@app.post("/TableGraph")
def getGraph(data:Graph):
    data=data.dict()
    return getalltableAndGraph(data)

@app.post("/TableGraphDataofIPAllSubnet")
def getallSubnet(data:InGraphSubnet):
    data=data.dict()
    #return getalltableAndGraphdataAllSubnet(data)
    return getFinalData(data)

@app.post("/TableGraphDataofSubnetIP")
def get_graph_subnet(data: SubnetGraph, subnet_data: Optional[str] = Query(None), subnet_mask:SubnetMaskEnum = Query(None)):
    data_dict = data.dict()
    if subnet_data is None and subnet_mask is None and data.subnet is None:
        raise HTTPException(status_code=422, detail="Either subnet_data and subnet_mask must be provided as query parameters or subnet in the payload.")

    return getalltableAndGraphdataSubnet(data_dict, subnet_data, subnet_mask.value if subnet_mask else None)
#def getGraph(data:SubnetGraph):
    #data=data.dict()
    #return getalltableAndGraphdataSubnet(data)

@app.post("/TableGraphData")
def get_graph_data_app(data: GraphData):
    data=data.dict()
    return getalltableAndGraphdata(data)

@app.get('/allDevices', tags=['ALL_DEVICES'], summary="This API give  all device name".upper())
def getAllDevices():
    return allDevices()

@app.get("/")
def m():
    return {"status":True}

if __name__ == "__main__":
    uvicorn.run(app="main:app",
    host='0.0.0.0',
    port=8010,
    reload=True)


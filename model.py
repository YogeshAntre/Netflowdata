from pydantic import BaseModel,Field
from enum import Enum
from typing import Optional
class Interface(BaseModel):
    devname: str


class Graph(Interface):
    gte: str
    lte: str
    direction: str
    interface: str


class GraphData(Graph):
    # devname: str
    # gte: str
    # lte: str
    # direction: str
    # interface: str
    reportType: str


class SubnetGraph(BaseModel):
    devname: str
    gte: str
    lte: str
    direction: str
    interface: str
    reportType: str
    subnet:Optional[str] = Field(None, title="Subnet Mask")
    

class InGraphSubnet(Graph):
    reportType: str
    subnet: list=[]

class SubnetMaskEnum(str, Enum):
    _16 = "16"
    _17 = "17"
    _18 = "18"
    _19 = "19"
    _20 = "20"
    _21 = "21"
    _22 = "22"
    _23 = "23"
    _24 = "24"
    _25 = "25"
    _26 = "26"
    _27 = "27"
    _28 = "28"
    _29 = "29"
    _30 = "30"
    
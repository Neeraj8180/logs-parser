from pydantic import BaseModel, Field

class MySQLTPC_Hlog(BaseModel):
    Power_Size:float = Field(alias="Power@Size")
    Throughput_Size:float = Field(alias="Throughput@Size")
    QphH_Size:float = Field(alias="QphH@Size")

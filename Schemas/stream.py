from pydantic import BaseModel, Field

class OperationRate(BaseModel):
    best_rate_MBps: float = Field(..., description="Best Rate in MB/s")

class StreamLog(BaseModel):
    copy: OperationRate = Field(..., alias="Copy", description="Copy operation performance")
    scale: OperationRate = Field(..., alias="Scale", description="Scale operation performance")
    add: OperationRate = Field(..., alias="Add", description="Add operation performance")
    triad: OperationRate = Field(..., alias="Triad", description="Triad operation performance")

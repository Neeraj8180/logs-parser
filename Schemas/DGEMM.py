from pydantic import BaseModel, Field

class DGEMMResult(BaseModel):
    GFLOPS: float = Field(..., description="GFLOPS")

from pydantic import BaseModel, Field
from typing import Optional

class IOModel(BaseModel):
    BW: Optional[int] = Field(..., description="Bandwidth in KB/s or MB/s")

class LatencyModel(BaseModel):
    avg: Optional[float] = Field(..., description="Average latency in microseconds")

class FIOlog(BaseModel):
    IOPS: Optional[int] = Field(..., description="I/O operations per second")
    read: IOModel | None = Field(default=None, description="Read performance metrics (optional)")
    write: IOModel | None = Field(default=None, description="Write performance metrics (optional)")
    lat: LatencyModel = Field(..., alias="lat (usec)", description="Latency metrics (mandatory)")

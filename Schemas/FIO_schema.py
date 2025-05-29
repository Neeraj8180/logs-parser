from pydantic import BaseModel, Field

class IOModel(BaseModel):
    BW: int = Field(..., description="Bandwidth in KB/s or MB/s")

class LatencyModel(BaseModel):
    avg: float = Field(..., description="Average latency in microseconds")

class FIOlog(BaseModel):
    IOPS: int = Field(..., description="I/O operations per second")
    read: IOModel | None = Field(default=None, description="Read performance metrics (optional)")
    write: IOModel | None = Field(default=None, description="Write performance metrics (optional)")
    lat: LatencyModel = Field(..., alias="lat (usec)", description="Latency metrics (mandatory)")

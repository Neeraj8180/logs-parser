from pydantic import BaseModel, Field

class RunMetrics(BaseModel):
    power_at_size: float = Field(..., alias="Power@Size")
    throughput_at_size: float = Field(..., alias="Throughput@Size")
    qphh_at_size: float = Field(..., alias="QphH@Size")

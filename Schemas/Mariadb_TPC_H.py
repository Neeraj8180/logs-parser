from pydantic import BaseModel, Field

class TpchBenchmarkMetrics(BaseModel):
    power_size: float = Field(..., description="Power@Size metric")
    throughput_size: float = Field(..., description="Throughput@Size metric")
    qphh_size: float = Field(..., description="QphH@Size metric")

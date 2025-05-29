from pydantic import BaseModel, Field

class LatencyStats(BaseModel):
    min_latency_us: int = Field(..., description="Minimum latency in microseconds")
    max_latency_us: int = Field(..., description="Maximum latency in microseconds")
    mean_latency_us: float = Field(..., description="Mean latency in microseconds")

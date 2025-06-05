from pydantic import BaseModel, Field, RootModel
from typing import List, Dict, Union
from enum import Enum


# Enum for allowed metric names
class MetricName(str, Enum):
    BURST_SIZE = "Burst size"
    NO_OPS = "No_ops"
    THREADS = "threads"
    DECODE_THROUGHPUT_in_Mbps = "Decode Throughput"
    ENCODE_THROUGHPUT_in_Mbps = "Encode Throughput"


# Model for a single metric entry
class Metric(BaseModel):
    metricsName: MetricName
    metricsValue: Union[int, float]


# Pydantic v2-compliant root model for each test vector name and its metrics
class TestVectorEntry(RootModel[Dict[str, List[Metric]]]):
    pass


# Final model for the whole file
class ThroughputData(BaseModel):
    DPDK_Test_BBDEV_Throughput: List[TestVectorEntry] = Field(..., alias="DPDK-Test-BBDEV-Throughput")

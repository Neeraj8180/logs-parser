from pydantic import BaseModel

class Redislog(BaseModel):
    SET_throughput_summary: float
    GET_throughput_summary: float

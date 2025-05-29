from pydantic import BaseModel, Field

class Nginxlog(BaseModel):
    requests_per_sec: float = Field(..., description="Number of requests per second from Nginx log")
from typing import Optional
from pydantic import BaseModel, Field

class Nginxlog(BaseModel):
    requests_per_sec: Optional[float] = Field(default=None, description="Requests per second")
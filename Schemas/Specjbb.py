from pydantic import BaseModel, Field
from typing import Optional

class jOPS(BaseModel):
    max_jOPS: Optional[int] = Field(..., description="Maximum jOPS")
    critical_jOPS: Optional[int] = Field(..., description="Critical jOPS")

class Specjbblog(BaseModel):
    RUN_RESULT: jOPS = Field(..., description="Run result")
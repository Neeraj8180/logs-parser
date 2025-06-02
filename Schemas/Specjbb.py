from pydantic import BaseModel, Field


class jOPS(BaseModel):
    max_jOPS: int = Field(..., description="Maximum jOPS")
    critical_jOPS: int = Field(..., description="Critical jOPS")

class Specjbblog(BaseModel):
    RUN_RESULT: jOPS = Field(..., description="Run result")
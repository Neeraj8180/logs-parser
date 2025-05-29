from pydantic import BaseModel, Field

class Performanceresult(BaseModel):
    nopm : int = Field(..., description = "New orders per minutes")
    tpm : int = Field(..., description = "Transaction per minute")
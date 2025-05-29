from pydantic import BaseModel, Field

class Oracle_TPC_C( BaseModel ):
    nopm : int = Field(..., description = "New order Per minute")
    tcp : int = Field(..., description = "Transaction per minute")
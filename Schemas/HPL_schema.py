from pydantic import BaseModel, Field
from typing import Optional

class HPLlog(BaseModel):
    Gflops: Optional[str] = Field(default=None, description="In a table format we have Gflops value as a column")
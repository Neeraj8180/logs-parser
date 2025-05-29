from pydantic import BaseModel
from typing import Literal, List

class RoleBitrate(BaseModel):
    role: Literal["sender", "receiver"]
    bitrate_gbps: float

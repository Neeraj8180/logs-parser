from pydantic import BaseModel



class RoleBitrate(BaseModel):
    sender_bitrate_gbps: float
    receiver_bitrate_gbps: float

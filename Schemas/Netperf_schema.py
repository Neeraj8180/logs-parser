from pydantic import BaseModel, Field

class Netperflog(BaseModel):
    client_server_throughput: float = Field(alias="Client-->Server Throughput")
    server_client_throughput: float = Field(alias="Client<--Server Throughput")

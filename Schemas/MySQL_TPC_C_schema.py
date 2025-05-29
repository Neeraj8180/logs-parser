from pydantic import BaseModel


class MySQLTPC_Clog(BaseModel):
    NOPM: int
    TPM: int

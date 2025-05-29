#schemas
from .nginx_schema import Nginxlog
from .FIO_schema import FIOlog
from .Netperf_schema import Netperflog
from .redis_schema import Redislog
from .MySQL_TPC_C_schema import MySQLTPC_Clog
from .MySQL_TPC_H_schema import MySQLTPC_Hlog
from .stream import StreamLog
from .DGEMM import DGEMMResult
from .Iperf import RoleBitrate
from .Mariadb_TPC_C import Performanceresult
from .Mariadb_TPC_H import TpchBenchmarkMetrics
from .Oracle_TPC_C import Oracle_TPC_C
from .Oracle_TPC_H import RunMetrics
from .TCP_RR import LatencyStats
from .ffmpeg_schema import FFMPEGlog

# Map log types to schema classes
SCHEMA_MAP = {
    "nginx": Nginxlog,
    "FIO": FIOlog,
    "Netperf": Netperflog,
    "Redis": Redislog,
    "MySQL_TPC_C": MySQLTPC_Clog,
    "MySQL_TPC_H": MySQLTPC_Hlog,
    "Stream": StreamLog,
    "DGEMM": DGEMMResult,
    "Iperf": RoleBitrate,
    "Mariadb_TPC_C": Performanceresult,
    "Mariadb_TPC_H": TpchBenchmarkMetrics,
    "Oracle_TPC_C": Oracle_TPC_C,
    "Oracle_TPC_H": RunMetrics,
    "TCP_RR": LatencyStats,
    "FFMPEG": FFMPEGlog,
}
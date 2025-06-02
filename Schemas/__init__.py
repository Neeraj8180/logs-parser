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
from .HPL_schema import HPLlog
from .Specjbb import Specjbblog

# Map log types to schema classes
SCHEMA_MAP = {
    "nginx": Nginxlog,
    "fio": FIOlog,
    "netperf": Netperflog,
    "redis": Redislog,
    "mysqltpcc": MySQLTPC_Clog,
    "mysqltpch": MySQLTPC_Hlog,
    "stream": StreamLog,
    "dgemm": DGEMMResult,
    "iperf": RoleBitrate,
    "mariadbtpcc": Performanceresult,
    "mariadbtpch": TpchBenchmarkMetrics,
    "oracletpcc": Oracle_TPC_C,
    "oracletpch": RunMetrics,
    "tcprr": LatencyStats,
    "ffmpeg": FFMPEGlog,
    "hpl": HPLlog,
    "specjbb": Specjbblog,
}
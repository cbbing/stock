from config.settings import DATABASES
from sqlalchemy import create_engine

def get_w_engine():
    """
    获取write权限engine
    :return:
    """
    engine_db = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(
        DATABASES['tushare']['USER'],
        DATABASES['tushare']['PASSWORD'],
        DATABASES['tushare']['HOST'],
        DATABASES['tushare']['PORT'],
        DATABASES['tushare']['NAME'],
    ), connect_args={"charset": "utf8"})
    return engine_db

def get_r_engine():
    """
    获取read权限engine
    :return:
    """
    engine_db = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(
        DATABASES['strategy']['USER'],
        DATABASES['strategy']['PASSWORD'],
        DATABASES['strategy']['HOST'],
        DATABASES['strategy']['PORT'],
        DATABASES['strategy']['NAME'],
    ), connect_args={"charset": "utf8"})
    return engine_db
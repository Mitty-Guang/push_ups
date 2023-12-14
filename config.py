import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))  # 获取当前文件所在目录
UPLOAD_FOLDER = basedir + '/static/gravatar'
IMAGE = '../static/gravatar/'

# 数据库的配置信息
HOSTNAME = '39.101.122.176'
PORT = 3306
USERNAME = 'root'
PASSWORD = 'litongtong123'
DATABASE = 'localhost'
DB_URI = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8"

SQLALCHEMY_DATABASE_URI = DB_URI
SECRET_KEY="fkndjnvndfjn"
PERMANENT_SESSION_LIFETIME=timedelta(days=7)



# python连接FastDFS的驱动
from fdfs_client.client import Fdfs_client

# 根据配置文件创建连接的客户端
client = Fdfs_client()

# 调用方法上传文件
result = client.upload_appender_by_file('222.jpg')
print(result)
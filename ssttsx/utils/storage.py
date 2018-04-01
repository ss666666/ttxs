# django中提供文件存储类的基类
from django.core.files.storage import Storage
# python连接FastDFS服务器的驱动
from fdfs_client.client import Fdfs_client
from django.conf import settings


# 自定义存储类
class FdfsStorage(Storage):
    def save(self, name, content, max_length=None):

        # 从网络中读取文件数据
        buffer = content.read()

        # 根据配置文件创建连接的客户端
        client = Fdfs_client(settings.FDFS_CLIENT)
        # 上传文件
        """
        成功后会返回以下数据
        'Remote file_id': 'group1/M00/00/00/wKjCA1q7hMmERGY1AAAAAPQczbI642.jpg',
        'Local file name': '222.jpg',
        'Group name': 'group1',
        'Storage IP': '192.168.194.3',
        'Uploaded size': '178.00KB',
        'Status': 'Upload successed.'
        """
        try:
            result = client.upload_appender_by_buffer(buffer)
        except:
            raise

        if result.get('Status') == 'Upload successed.':
            return result.get('Remote file_id')
        else:
            raise Exception('上传失败')


    #当ImageField类型的对象image，调用属性url时，会调用对应的存储类的url()方法
    def url(self, name):
        return settings.FDFS_SERVER+name
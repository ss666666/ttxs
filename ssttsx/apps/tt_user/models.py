from django.db import models
from utils.models import BaseModel
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(BaseModel, AbstractUser):

    class Meta:
        db_table = 'df_user'


class AreaInfo(models.Model):

    title = models.CharField(max_length=20)
    aParent = models.ForeignKey('self',null=True,blank=True)

    class Meta:
        db_table = 'df_area'

class Address(BaseModel):
    # 收件人
    receiver = models.CharField(max_length=10)
    # 省
    province = models.ForeignKey(AreaInfo,related_name='province')
    # 市
    city = models.ForeignKey(AreaInfo,related_name='city')
    # 区
    district = models.ForeignKey(AreaInfo,related_name='district')
    # 详细地址
    addr = models.CharField(max_length=100)
    # 邮编
    code = models.CharField(max_length=6)
    # 电话
    phone_number = models.CharField(max_length=11)
    # 是否为默认地址
    isDefault = models.BooleanField(default=False)

    user=models.ForeignKey(User,null=True)


    class Meta:
        db_table = 'df_address'
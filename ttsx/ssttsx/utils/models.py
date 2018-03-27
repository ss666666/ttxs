from django.db import models


class BaseModel(models.Model):
    # 添加时间
    add_date = models.DateTimeField(auto_now_add=True)

    # 修改时间
    update_data = models.DateTimeField(auto_now=True)

    # 逻辑删除
    isDelete = models.BooleanField(default=False)


    class Meta:

        abstract = True
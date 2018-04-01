from django.conf.urls import url
from . import views


urlpatterns = [
    url('^fdfs_test$',views.fdfs_test),
    url('^index$',views.index),
    url(r'^(\d+)$', views.detail),
    url(r'^list(\d+)$', views.list_sku),
    url(r'^search/$', views.MySearchView.as_view()),
]
from django.conf.urls import url
from . import views

urlpatterns = [
    # url('^register$',views.register)
    url('^register$',views.RegisterView.as_view()),
    url('^active/(.+)$',views.active),
    url('^exists$',views.exists),
    url('^login$',views.LoginView.as_view()),
    url('^logout_user$',views.logout),
    url('^info$',views.info),
    url('^order$',views.order),
    url('^site$',views.SiteView.as_view()),
    url('^area$',views.area),
]
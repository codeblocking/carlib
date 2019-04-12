"""luffy_city URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from api.views import course, login, shopping,pay
from django.views.static import serve
from luffy_city import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^courses/$', course.CourseView.as_view({'get': 'get_list'})),
    url(r'^login/$', login.LoginView.as_view()),
    url(r'^courses/(?P<pk>\d+)', course.CourseView.as_view({'get': 'get_detail'})),
    url(r'^shopping/$', shopping.ShoppingView.as_view()),
    url(r'^payment/$', pay.PaymentView.as_view()),
    url(r'^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),

]

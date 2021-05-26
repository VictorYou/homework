"""example URL Configuration

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
from django.conf.urls import url, include
from rest_framework import serializers, viewsets, routers

from . import views

#router = routers.DefaultRouter()
#router.register(prefix='suts', viewset=SutVnfViewSet)
#router.register(prefix='testvnf', viewset=TvnfViewSet)

urlpatterns = [ 
  url(r'suts/(?P<sutId>\w+)/runTests', views.RunTestcaseReq.as_view(), name="executeTestsReq"),
  url(r'suts/(?P<sutId>\w+)', views.ResetReq.as_view(), name="ResetReq"),
  url(r'suts', views.SetupEnvReq.as_view(), name="SetupEnvReq"),
  url(r'abortTests/(?P<sessionId>(\w+-)+\w+)', views.AbortTestExecutionReq.as_view(), name="AbortTestExecutionReq"),
  url(r'connectTests/(?P<sessionId>\w+)', views.ConnectTestExecutionReq.as_view(), name="ConnectTestExecutionReq"),
#  url(r'^', include(router.urls)),
]


from rest_framework.serializers import ModelSerializer, CharField
from .models import Sut

class SutSerializer(ModelSerializer):
  class Meta:
    model = Sut
    fields = ("id", "version", "sutId", "sutStatus",)


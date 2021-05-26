from rest_framework.serializers import ModelSerializer, CharField
from .models import Tvnf, Sut

class TvnfSerializer(ModelSerializer):
  class Meta:
    model = Tvnf 
    fields = ("id", "tvnfId", "tvnfStatus",)

class SutSerializer(ModelSerializer):
  class Meta:
    model = Sut
    fields = ("id", "version", "sutId", "sutStatus",)


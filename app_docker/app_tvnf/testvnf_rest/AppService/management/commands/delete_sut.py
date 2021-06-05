from django.core.management.base import BaseCommand
from TvnfService.models import Sut

class Command(BaseCommand):
  help = "remove suts in database"

  def add_arguments(self, parser):
    pass

  def handle(self, *args, **options):
    sutlist = Sut.objects.all()
    for sut in sutlist:
      sut.delete()


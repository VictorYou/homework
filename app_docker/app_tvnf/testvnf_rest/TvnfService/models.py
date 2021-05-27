import random
# from __future__ import unicode_literals

from django.db import models


def generate_Id():
  return random.randint(0, 5)


class Sut(models.Model):
  A = 'A'
  U = 'U'
  F = 'F'
  STATUS_CHOICES = (
    (A, 'Available'),
    (U, 'Unavailable'),
    (F, 'Failed'),
  )
  sutId = models.CharField(max_length=128, unique=True)
  name = models.CharField(max_length=1024, default='')
  sutStatus = models.CharField(max_length=15, choices=STATUS_CHOICES, default=A)

  def __str__(self):
    return "{}".format(self.sutType)

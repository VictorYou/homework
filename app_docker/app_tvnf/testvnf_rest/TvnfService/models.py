import random
# from __future__ import unicode_literals

from django.db import models


def generate_Id():
  return random.randint(0, 5)


class Tvnf(models.Model):
  A = 'A'
  U = 'U'
  F = 'F'
  STATUS_CHOICES = (
    (A, 'Available'),
    (U, 'Unavailable'),
    (F, 'Failed'),
  )
  tvnfId = models.CharField(max_length=20, unique=True)
  tvnfStatus = models.CharField(max_length=15, choices=STATUS_CHOICES, default=A)

  def __str__(self):
    return "{}:{}".format(self.tvnfId, self.tvnfStatus)

  @property
  def name(self):
    return str(self)


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
  testcases = models.CharField(max_length=1024, default='')
  sutStatus = models.CharField(max_length=15, choices=STATUS_CHOICES, default=A)

  def __str__(self):
    return "{}".format(self.sutType)


class TestSession(models.Model):
  A = 'A'
  U = 'U'
  STATUS_CHOICES = (
    (A, 'Available'),
    (U, 'Unavailable'),
  )
  sessionId = models.CharField(max_length=128, default='', unique=True)
  status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=A)


class TestExecution(models.Model):
  A = 'A'
  U = 'U'
  STATUS_CHOICES = (
    (A, 'Available'),
    (U, 'Unavailable'),
  )
  testname = models.CharField(max_length=255, default='', unique=True)
  sessionId = models.CharField(max_length=128, default='')
  status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=A)


class Testcase(models.Model):
  name = models.CharField(max_length=255, default='', unique=True)
  tags = models.CharField(max_length=1024, default='')
  folder = models.CharField(max_length=128, default='')
  filename = models.CharField(max_length=128, default='')
  suite = models.CharField(max_length=128, default='')
  description = models.CharField(max_length=1024, default='')

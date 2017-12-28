from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Post(models.Model):
	image = models.ImageField(null=True,blank=True)
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follow_count = models.IntegerField()
    last_update = models.DateTimeField()

class Repository(models.Model):
    name = models.CharField(max_length=300)
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE)
    num_star = models.IntegerField()

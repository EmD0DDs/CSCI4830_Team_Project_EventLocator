from django.db import models

# Create your models here.

class UserSignup(models.Model):
    name = models.Charfield(max_length=100)
    username = models.Charfield(max_lenth=150, unique=True, )
    email = models.EmailField(unique=True)


class UserLogin(models.Model):
    username = models.Charfield(max_length=150, unique=True)
    email = models.EmailField(unique=True)


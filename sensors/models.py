from django.db import models

# Create your models here.
class Room(models.Model):
    managed = False
    room_id = models.CharField(max_length=36)
    name = models.CharField(max_length=10)
    description = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Sensor(models.Model):
    managed = False
    sensor_id = models.CharField(max_length=36)
    room_id = models.CharField(max_length=36)
    description = models.CharField(max_length=50)
    type = models.CharField(max_length=20)
    symbol = models.CharField(max_length=5)

    def __str__(self):
        return self.sensor_id

class Type(models.Model):
    managed = False
    type_id = models.IntegerField()
    metric = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    units = models.CharField(max_length=50)

    def __str__(self):
        return self.metric

class User(models.Model):
    managed = False
    user_id = models.CharField(max_length=36)
    email = models.CharField(max_length=50)
    admin = models.BooleanField()

    def __str__(self):
        return self.user_id
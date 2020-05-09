from django.db import models

# Create your models here.
class Room(models.Model):
    managed = False
    room_id = models.CharField(max_length=36, primary_key=True)
    name = models.CharField(max_length=10)
    description = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Sensor(models.Model):
    managed = False
    sensor_id = models.CharField(max_length=36)

    def __str__(self):
        return self.sensor_id

class Type(models.Model):
    managed = False
    metric = models.CharField(max_length=50)

    def __str__(self):
        return self.metric
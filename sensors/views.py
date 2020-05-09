#  from django.shortcuts import render

# Create your views here.
from django.http import Http404
from django.shortcuts import render
from django.views import generic
import requests

from .models import Room, Sensor, Type

def loadRooms():
    for i in range(3):
        requestRoomsID = requests.get('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1/rooms',headers={'debug' : 'qVFczKtLhkgJb7xMpbspzCm4JdL3bq4K'}, verify=False)
        if requestRoomsID.headers["Content-Type"]=="application/json":
            roomsList = []
            for room in requestRoomsID.json()["ids"]:
                request = requests.get('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1/room/'+room,headers={'debug' : 'qVFczKtLhkgJb7xMpbspzCm4JdL3bq4K'}, verify=False).json()
                roomsList.append(Room(room_id=room,name=request['name'],description=request['description']))
            return roomsList
    return []

def loadRoom(id):
    for i in range(3):
        requestRoomsID = requests.get('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1/rooms',headers={'debug' : 'qVFczKtLhkgJb7xMpbspzCm4JdL3bq4K'}, verify=False)
        if requestRoomsID.headers["Content-Type"]=="application/json":
            for room in requestRoomsID.json()["ids"]:
                if room==id:
                    request = requests.get('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1/room/'+room,headers={'debug' : 'qVFczKtLhkgJb7xMpbspzCm4JdL3bq4K'}, verify=False).json()
                    return Room(room_id=room,name=request['name'],description=request['description'])
            return []
    return []

class RoomsIndexView(generic.ListView):
    template_name = 'sensors/rooms.html'
    context_object_name = 'rooms_list'

    def get_queryset(self):
        rooms = loadRooms()
        if rooms != []:
            return rooms
        raise Http404("Não existe nenhuma sala")

def roomDetails(request, room_id):
    room = loadRoom(room_id)
    if room != []:
        return render(request, 'sensors/roomDetails.html', {'last': room})
    raise Http404("Sala não existente")


class SensorsIndexView(generic.ListView):
    template_name = 'sensors/sensors.html'
    context_object_name = 'sensors_list'

    def get_queryset(self):
        request = requests.get('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1/sensors',headers={'debug' : 'qVFczKtLhkgJb7xMpbspzCm4JdL3bq4K'}, verify=False)
        sensorsList = []
        for sensor in request.json()["ids"]:
            sensorsList.append(Sensor(sensor_id=sensor))
        return sensorsList


class TypesIndexView(generic.ListView):
    template_name = 'sensors/types.html'
    context_object_name = 'types_list'

    def get_queryset(self):
        request = requests.get('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1/types',headers={'debug' : 'qVFczKtLhkgJb7xMpbspzCm4JdL3bq4K'}, verify=False)
        typesList = []
        for type in request.json()["types"]:
            typesList.append(Type(metric=type))
        return typesList
#  from django.shortcuts import render

# Create your views here.
from django.http import Http404
from django.shortcuts import render
from django.views import generic
import requests

from .models import Room, Sensor, Type

class RoomsIndexView(generic.ListView):
    template_name = 'sensors/rooms.html'
    context_object_name = 'rooms_list'

    def get_queryset(self):
        rooms = self.loadRooms()
        if rooms != []:
            return rooms
        raise Http404("Não existe nenhuma sala")

    def loadRooms(self):
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

    def loadRoomSensors(room_id):
        for i in range(3):
            requestSensorsID = requests.get('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1/room/'+room_id+'/sensors',headers={'debug' : 'qVFczKtLhkgJb7xMpbspzCm4JdL3bq4K'}, verify=False)
            if requestSensorsID.headers["Content-Type"]=="application/json":
                sensorsList = []
                for sensor in requestSensorsID.json()["ids"]:
                    request = requests.get('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1/sensor/'+sensor,headers={'debug' : 'qVFczKtLhkgJb7xMpbspzCm4JdL3bq4K'}, verify=False).json()
                    sensorsList.append(Sensor(sensor_id=sensor,room_id=request['room_id'],description=request['description'],type=request['data']['type'],symbol=request['data']['unit_symbol']))
                return sensorsList
        return []

    def roomDetails(request, room_id):
        room = RoomsIndexView.loadRoom(room_id)
        if room != []:
            sensors = RoomsIndexView.loadRoomSensors(room_id)
            if sensors != []:
                return render(request, 'sensors/roomDetails.html', {'room': room, 'sensors': sensors})
            return render(request, 'sensors/roomDetails.html', {'room': room})
        raise Http404("Sala não existente")

class SensorsIndexView(generic.ListView):
    template_name = 'sensors/sensors.html'
    context_object_name = 'sensors_list'

    def get_queryset(self):
        sensors = self.loadSensors()
        if sensors != []:
            return sensors
        raise Http404("Não existe nenhum sensor")

#    def loadSensors(self):
#        for i in range(3):
#            requestSensors = requests.get('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1/sensors',headers={'debug' : 'qVFczKtLhkgJb7xMpbspzCm4JdL3bq4K'}, verify=False)
#            if requestSensors.headers["Content-Type"]=="application/json":
#                sensorsList = []
#                for sensor in requestSensors.json()["ids"]:
#                    #request = requests.get('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1/sensor/'+sensor,headers={'debug' : 'qVFczKtLhkgJb7xMpbspzCm4JdL3bq4K'}, verify=False).json()
#                    sensorsList.append(Sensor(sensor_id=sensor))
#                return sensorsList
#        return []
#
#    def loadSensor(id):
#        for i in range(3):
#            requestSensorsID = requests.get('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1/sensors',headers={'debug' : 'qVFczKtLhkgJb7xMpbspzCm4JdL3bq4K'}, verify=False)
#            if requestSensorsID.headers["Content-Type"]=="application/json":
#                for sensor in requestSensorsID.json()["ids"]:
#                    if sensor==id:
#                        request = requests.get('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1/sensor/'+sensor,headers={'debug' : 'qVFczKtLhkgJb7xMpbspzCm4JdL3bq4K'}, verify=False).json()
#                        print("1")
#                        return Sensor(sensor_id=id,room_id=request['room_id'],description=request['description'],type=request['data']['type'],symbol=request['data']['unit_symbol'])
#                return []
#        return []

#    def sensorDetails(request, sensor_id):
#        sensor = SensorsIndexView.loadSensor(sensor_id)
#        if sensor != []:
#            return render(request, 'sensors/sensorDetails.html', {'sensor': sensor})
#        raise Http404("Sala não existente")

class TypesIndexView(generic.ListView):
    template_name = 'sensors/types.html'
    context_object_name = 'types_list'

    def get_queryset(self):
        types = self.loadTypes()
        if types != []:
            return types
        raise Http404("Não existe nenhuma métrica")

    def loadTypes(self):
        for i in range(3):
            requestTypes = requests.get('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1/types',headers={'debug' : 'qVFczKtLhkgJb7xMpbspzCm4JdL3bq4K'}, verify=False)
            if requestTypes.headers["Content-Type"]=="application/json":
                typesList = []
                for type in requestTypes.json()["types"]:
                    #request = requests.get('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1/type/'+type,headers={'debug' : 'qVFczKtLhkgJb7xMpbspzCm4JdL3bq4K'}, verify=False).json()
                    typesList.append(Type(metric=type))
                return typesList
        return []


def template(request):
    return render(request, "sensors/index.html", {"data": ""})

# from django.shortcuts import render

# Create your views here.
from django.http import Http404
from django.shortcuts import render, redirect
from django.views import generic
import requests

from .models import Room, Sensor, Type

class RoomsIndexView(generic.ListView):
    template_name = 'sensors/rooms.html'
    context_object_name = 'rooms_list'

    def get_queryset(self):
        rooms = loadRooms(self)
        if rooms != []:
            return rooms
        raise Http404("Não existe nenhuma sala")

def loadRooms(self):
    for i in range(3):
        requestRoomsID = api_get_request('/rooms', self.request.session)
        if requestRoomsID.headers["Content-Type"]=="application/json":
            roomsList = []
            for room in requestRoomsID.json()["ids"]:
                request = api_get_request('/room/' + room, self.request.session).json()
                roomsList.append(Room(room_id=room,name=request['name'],description=request['description']))
            return roomsList
    return []

class SensorsIndexView(generic.ListView):
    template_name = 'sensors/sensors.html'
    context_object_name = 'rooms_list'

    def get_queryset(self):
        rooms = loadRooms(self)
        if rooms != []:
            return rooms
        raise Http404("Não existe nenhuma sala")

    def loadRoom(session, id):
        for i in range(3):
            requestRoomsID = api_get_request('/rooms', session)
            if requestRoomsID.headers["Content-Type"]=="application/json":
                for room in requestRoomsID.json()["ids"]:
                    if room==id:
                        request = api_get_request('/room/' + room, session).json()
                        return Room(room_id=room,name=request['name'],description=request['description'])
                return []
        return []

    def loadRoomSensors(session, room_id):
        for i in range(3):
            requestSensorsID = api_get_request('/room/' + room_id + '/sensors', session)
            if requestSensorsID.headers["Content-Type"]=="application/json":
                sensorsList = []
                for sensor in requestSensorsID.json()["ids"]:
                    request = api_get_request('/sensor/' + sensor, session).json()
                    sensorsList.append(Sensor(sensor_id=sensor,room_id=request['room_id'],description=request['description'],type=request['data']['type'],symbol=request['data']['unit_symbol']))
                return sensorsList
        return []

    def roomDetails(request, room_id):
        room = SensorsIndexView.loadRoom(request.session, room_id)
        if room != []:
            sensors = SensorsIndexView.loadRoomSensors(request.session, room_id)
            if sensors != []:
                types = loadTypes(request.session)
                return render(request, 'sensors/roomDetails.html', {'room': room, 'sensors': sensors, 'types': types})
            return render(request, 'sensors/roomDetails.html', {'room': room})
        raise Http404("Sala não existente")

class TypesIndexView(generic.ListView):
    template_name = 'sensors/types.html'
    context_object_name = 'types_list'

    def get_queryset(self):
        types = loadTypes(self.request.session)
        if types != []:
            return types
        raise Http404("Não existe nenhuma métrica")

def loadTypes(session):
    for i in range(3):
        requestTypes = api_get_request('/types', session)
        if requestTypes.headers["Content-Type"]=="application/json":
            typesList = []
            for type in requestTypes.json()["types"]:
                #request = api_get_request('/type/' + type, session).json()
                typesList.append(Type(metric=type))
            return typesList
    return []

def template(request):
    if 's' in request.GET:
        request.session['cookies'] = {'session': request.GET['s']}
        request.session['User-Agent'] = request.headers['User-Agent']
        return redirect('/')
    elif 'cookies' not in request.session:
        return redirect('/login')
    return render(request, "sensors/index.html")


def login(request):
    return render(request, "sensors/login.html")


def logout(request):
    for i in range(3):
        api_get_request('/logout', request.session)
    request.session.flush()
    return redirect('/login')


def api_login(request):
    return redirect('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1/login?app=gestao&redirect_url=' + request.build_absolute_uri('/'))


def api_get_request(endpoint, session):
    return requests.get('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1' + endpoint, headers={'User-Agent': session['User-Agent']}, verify=False, cookies=session['cookies'])
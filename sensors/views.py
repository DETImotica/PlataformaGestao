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

    def get(self, *args, **kwargs):
        if 'cookies' not in self.request.session:
            return redirect('/login')
        return super(RoomsIndexView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(RoomsIndexView, self).get_context_data(**kwargs)
        ctx['uname'] = self.request.session['uname']
        return ctx

    def get_queryset(self):
        if 'cookies' not in self.request.session:
            return redirect('/login')

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
                print(requestSensorsID.json())
                for sensor in requestSensorsID.json()["ids"]:
                    request = api_get_request('/sensor/' + sensor, session).json()
                    sensorsList.append(Sensor(sensor_id=sensor,room_id=request['room_id'],description=request['description'],type=request['data']['type'],symbol=request['data']['unit_symbol']))
                return sensorsList
        return []

    def roomDetails(request, room_id):
        if 'cookies' not in request.session:
            return redirect('/login')

        room = RoomsIndexView.loadRoom(request.session, room_id)
        if room != []:
            sensors = RoomsIndexView.loadRoomSensors(request.session, room_id)
            if sensors != []:
                types = loadTypes(request.session)
                return render(request, 'sensors/roomDetails.html', {'room': room, 'sensors': sensors, 'types': types, 'uname': request.session['uname']})
            return render(request, 'sensors/roomDetails.html', {'room': room, 'uname': request.session['uname']})
        raise Http404("Sala não existente")

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
    context_object_name = 'sensors_list'

    def get(self, *args, **kwargs):
        if 'cookies' not in self.request.session:
            return redirect('/login')
        return super(SensorsIndexView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(SensorsIndexView, self).get_context_data(**kwargs)
        ctx['uname'] = self.request.session['uname']
        return ctx

    def get_queryset(self):
        sensors = self.loadSensors()
        if sensors != []:
            return sensors
        raise Http404("Não existe nenhum sensor")

    def loadSensors(self):
        for i in range(3):
            requestSensors = api_get_request('/sensors', self.request.session)
            if requestSensors.headers["Content-Type"]=="application/json":
                sensorsList = []
                for sensor in requestSensors.json()["ids"]:
                    #request = api_get_request('/sensor/' + sensor, self.request.session).json()
                    sensorsList.append(Sensor(sensor_id=sensor))
                return sensorsList
        return []

    def loadSensor(self, id):
        for i in range(3):
            requestSensorsID = api_get_request('/sensors', self.request.session)
            if requestSensorsID.headers["Content-Type"]=="application/json":
                for sensor in requestSensorsID.json()["ids"]:
                    if sensor==id:
                        request = api_get_request('/sensor/' + sensor, self.request.session).json()
                        print("1")
                        return Sensor(sensor_id=id,room_id=request['room_id'],description=request['description'],type=request['data']['type'],symbol=request['data']['unit_symbol'])
                return []
        return []

class TypesIndexView(generic.ListView):
    template_name = 'sensors/types.html'
    context_object_name = 'types_list'

    def get(self, *args, **kwargs):
        if 'cookies' not in self.request.session:
            return redirect('/login')
        return super(TypesIndexView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(TypesIndexView, self).get_context_data(**kwargs)
        ctx['uname'] = self.request.session['uname']
        return ctx

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
        request.session['uname'] = "Diogo Gomes"
        return redirect('/')
    elif 'cookies' not in request.session:
        return redirect('/login')
    return render(request, "sensors/index.html", {'uname': request.session['uname']})


def login(request):
    return render(request, "sensors/login.html")


def logout(request):
    if 'cookies' not in request.session:
        return redirect('/login')
    for i in range(3):
        api_get_request('/logout', request.session)
    request.session.flush()
    return redirect('/login')


def forbidden(request):
    return render(request, "sensors/forbidden.html")


def api_login(request):
    return redirect('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1/login?app=gestao&redirect_url=' + request.build_absolute_uri('/'))


def api_get_request(endpoint, session):
    return requests.get('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1' + endpoint, headers={'User-Agent': session['User-Agent']}, verify=False, cookies=session['cookies'])


def handler404(request, exception):
    return render(request, 'sensors/404.html', status=404)


def handler500(request):
    return render(request, 'sensors/500.html', status=500)
# from django.shortcuts import render

# Create your views here.
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
import requests, json

from .models import Room, Sensor, Type

# Main views

class RoomsIndexView(generic.ListView):
    template_name = 'sensors/rooms.html'
    context_object_name = 'rooms_list'

    def get(self, *args, **kwargs):
        if 'cookies' not in self.request.session:
            return redirect('/login')

        try:
            return super(RoomsIndexView, self).get(*args, **kwargs)
        except ResponseException as r:
            if r.code == 401:
                return redirect('/logout')
            else:
                raise Exception

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

def loadRooms(self):
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
        requestRoomsID = api_get_request('/rooms', session)
        if requestRoomsID.headers["Content-Type"]=="application/json":
            for room in requestRoomsID.json()["ids"]:
                if room==id:
                    request = api_get_request('/room/' + room, session).json()
                    return Room(room_id=room,name=request['name'],description=request['description'])
            return []
        return []

    def loadRoomSensors(session, room_id):
        requestSensorsID = api_get_request('/room/' + room_id + '/sensors', session)
        if requestSensorsID.headers["Content-Type"]=="application/json":
            sensorsList = []
            for sensor in requestSensorsID.json()["ids"]:
                request = api_get_request('/sensor/' + sensor, session).json()
                sensorsList.append(Sensor(sensor_id=sensor,room_id=request['room_id'],description=request['description'],type=request['data']['type'],symbol=request['data']['unit_symbol']))
            return sensorsList
        return []

    def roomDetails(request, room_id):
        if 'cookies' not in request.session:
            return redirect('/login')

        try:
            room = SensorsIndexView.loadRoom(request.session, room_id)
            if room != []:
                sensors = SensorsIndexView.loadRoomSensors(request.session, room_id)
                if sensors != []:
                    types = loadTypes(request.session)
                    return render(request, 'sensors/roomDetails.html', {'room': room, 'sensors': sensors, 'types': types, 'uname': request.session['uname']})
                return render(request, 'sensors/roomDetails.html', {'room': room, 'uname': request.session['uname']})
            raise Http404("Sala não existente")
        except ResponseException as r:
            if r.code == 401:
                return redirect('/logout')
            else:
                raise Exception

class TypesIndexView(generic.ListView):
    template_name = 'sensors/types.html'
    context_object_name = 'types_list'

    def get(self, *args, **kwargs):
        if 'cookies' not in self.request.session:
            return redirect('/login')

        try:
            return super(TypesIndexView, self).get(*args, **kwargs)
        except ResponseException as r:
            if r.code == 401:
                return redirect('/logout')
            else:
                raise Exception

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

# API Requests

def key(request, uuid):
    try:
        return HttpResponse('{"key": "placeholder"}', content_type='application/json')
        #return HttpResponse(api_get_request('/key/' + uuid, request.session), content_type='application/json')
    except ResponseException as r:
        return HttpResponse(status=r.code)


# Session views

def login(request):
    return render(request, "sensors/login.html")


def logout(request):
    if 'cookies' not in request.session:
        return redirect('/login')
    try:
        api_get_request('/logout', request.session)
    except ResponseException as r:
        if r.code != 401:
            raise Exception
    request.session.flush()
    return redirect('/login')


def forbidden(request):
    return render(request, "sensors/forbidden.html")


def api_login(request):
    return redirect('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1/login?app=gestao&redirect_url=' + request.build_absolute_uri('/'))

# API Requests - Helper functions

def api_get_request(endpoint, session, tries=0):
    result = requests.get('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1' + endpoint, headers={'User-Agent': session['User-Agent']}, verify=False, cookies=session['cookies'])
    if result.status_code == 200:
        if tries < 3:
            return result if is_json(result.text) else api_get_request(endpoint, session, tries + 1)
        else:
            return None
    else:
        raise ResponseException(result.status_code)


def api_post_request(endpoint, data, session, tries=0):
    result = requests.post('https://detimotic-aulas.ws.atnog.av.it.pt/api/v1' + endpoint, json=data, headers={'User-Agent': session['User-Agent']}, verify=False, cookies=session['cookies'])
    if result.status_code == 200:
        if tries < 3:
            return result if is_json(result.text) else api_post_request(endpoint, data, session, tries + 1)
        else:
            return None
    else:
        raise ResponseException(result.status_code)


def is_json(data):
    try:
        json_object = json.loads(data)
    except ValueError as e:
        return False
    return True

# Handlers

def handler404(request, exception):
    return render(request, 'sensors/404.html', status=404)


def handler500(request):
    return render(request, 'sensors/500.html', status=500)

# Custom Exception

class ResponseException(Exception):
    def __init__(self, *args):
        self.code = args[0] if args else 500

# from django.shortcuts import render

# Create your views here.
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
import requests, json
import asyncio, aiohttp
from DETImotica.settings import API_URL
import urllib.parse

from .models import Room, Sensor, Type, User

# Main views

class RoomsIndexView(generic.ListView):
    template_name = 'sensors/rooms.html'
    context_object_name = 'rooms_list'

    def get(self, *args, **kwargs):
        if 'allow' not in self.request.session:
            return redirect('sensors:login')
        if not self.request.session['allow']:
            return redirect('sensors:forbidden')

        try:
            return super(RoomsIndexView, self).get(*args, **kwargs)
        except ResponseException as r:
            if r.code == 401:
                return redirect('sensors:logout')
            else:
                raise Exception

    def get_context_data(self, **kwargs):
        ctx = super(RoomsIndexView, self).get_context_data(**kwargs)
        ctx['uname'] = self.request.session['uname']
        return ctx

    def get_queryset(self):
        return loadRooms(self)

def loadRooms(self):
    requestRoomsID = api_get_request('/rooms', self.request.session)
    if requestRoomsID.headers["Content-Type"]=="application/json":
        roomsList = []
        for (id, request) in get_async_loop().run_until_complete(api_get_bulk_async('/room', requestRoomsID.json()["ids"], self.request.session)):
            roomsList.append(Room(room_id=id,name=request['name'],description=request['description']))
        return roomsList
    return []

class SensorsIndexView(generic.ListView):
    template_name = 'sensors/sensors.html'
    context_object_name = 'rooms_list'

    def get(self, *args, **kwargs):
        if 'allow' not in self.request.session:
            return redirect('sensors:login')
        if not self.request.session['allow']:
            return redirect('sensors:forbidden')

        try:
            return super(SensorsIndexView, self).get(*args, **kwargs)
        except ResponseException as r:
            if r.code == 401:
                return redirect('sensors:logout')
            else:
                raise Exception

    def get_queryset(self):
        return loadRooms(self)

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
            for (id, request) in get_async_loop().run_until_complete(api_get_bulk_async('/sensor', requestSensorsID.json()["ids"], session)):
                sensorsList.append(Sensor(sensor_id=id,room_id=request['room_id'],description=request['description'],type=request['data']['type'],symbol=request['data']['unit_symbol']))
            sensorsList.sort(key=lambda s: (s.type.lower(), s.symbol.lower(), s.description.lower() if s.description is not None else s.description))
            return sensorsList
        return []

    def deleteRoomSensors(request, room_id):
        requestSensorsID = api_get_request('/room/' + room_id + '/sensors', request.session)
        if requestSensorsID.headers["Content-Type"]=="application/json":
            get_async_loop().run_until_complete(api_delete_bulk_async('/sensor', requestSensorsID.json()["ids"], request.session))

    def roomDetails(request, room_id):
        if 'allow' not in request.session:
            return redirect('sensors:login')
        if not request.session['allow']:
            return redirect('sensors:forbidden')

        try:
            room = SensorsIndexView.loadRoom(request.session, room_id)
            if room != []:
                sensors = SensorsIndexView.loadRoomSensors(request.session, room_id)
                types = loadTypesInfo(request.session)
                return render(request, 'sensors/roomDetails.html', {'room': room, 'sensors': sensors, 'types': types, 'uname': request.session['uname']})
            raise Http404("Sala não existente")
        except ResponseException as r:
            if r.code == 401:
                return redirect('sensors:logout')
            else:
                raise Exception

class TypesIndexView(generic.ListView):
    template_name = 'sensors/types.html'
    context_object_name = 'types_list'

    def get(self, *args, **kwargs):
        if 'allow' not in self.request.session:
            return redirect('sensors:login')
        if not self.request.session['allow']:
            return redirect('sensors:forbidden')

        try:
            return super(TypesIndexView, self).get(*args, **kwargs)
        except ResponseException as r:
            if r.code == 401:
                return redirect('sensors:logout')
            else:
                raise Exception

    def get_context_data(self, **kwargs):
        ctx = super(TypesIndexView, self).get_context_data(**kwargs)
        ctx['uname'] = self.request.session['uname']
        return ctx

    def get_queryset(self):
        return loadTypesInfo(self.request.session)

def loadTypesInfo(session):
    requestTypes = api_get_request('/types', session)
    if requestTypes.headers["Content-Type"]=="application/json":
        typesList = []
        for (id, request) in get_async_loop().run_until_complete(api_get_bulk_async('/type', requestTypes.json()["ids"], session)):
            typesList.append(Type(type_id=id, name=request['name'],description=request['description'],units=", ".join(request['units'])))
        typesList.sort(key=lambda t: t.name)
        return typesList
    return []


class UsersIndexView(generic.ListView):
    template_name = 'sensors/users.html'
    context_object_name = 'users_list'

    def get(self, *args, **kwargs):
        if 'allow' not in self.request.session:
            return redirect('sensors:login')
        if not self.request.session['allow']:
            return redirect('sensors:forbidden')

        try:
            return super(UsersIndexView, self).get(*args, **kwargs)
        except ResponseException as r:
            if r.code == 401:
                return redirect('sensors:logout')
            else:
                raise Exception

    def get_context_data(self, **kwargs):
        ctx = super(UsersIndexView, self).get_context_data(**kwargs)
        ctx['uname'] = self.request.session['uname']
        return ctx

    def get_queryset(self):
        return loadUsers(self.request.session)

def loadUsers(session):
    requestUsers = api_get_request('/users/full', session)
    if requestUsers.headers["Content-Type"]=="application/json":
        usersList = []
        for user in requestUsers.json():
            usersList.append(User(user_id=user['id'], email=user['email'], admin=user['admin']))
        return usersList
    return []

def notifications(request):
    if 'allow' not in request.session:
        return redirect('sensors:login')
    if not request.session['allow']:
        return redirect('sensors:forbidden')
    return render(request, "sensors/notifications.html", {'uname': request.session['uname']})

class Policy:
    def __init__(self, subjects, actions, context, effect, description, uuid):
        self.subjects = ""
        self.actions = ', '.join(actions)
        self.context = ""
        self.effect = 'Allow' if effect == 'allow' else 'Deny'
        self.uuid = uuid
        self.description = description
        self.setSubjects(subjects)
        self.setContext(context)

    def setSubjects(self, subjects):
        res = []
        email = []
        for subject in subjects:
            subres = []
            for key in subject:
                if key == 'email':
                    email.append(subject[key])
                elif key == 'admin':
                    subres.append("Administradores")
                elif key == 'student':
                    subres.append("Estudantes")
                elif key == 'teacher':
                    subres.append("Docentes")
                elif 'courses' in key:
                    subres.append("Unidades Curriculares: " + ', '.join([str(x) for x in subject[key]]))
            if subres != []:
                res.append('- ' + ', '.join(subres))
        if email != []:
            res.append("- Email: " + ', '.join(email))
        self.subjects = '\n'.join(res)

    def setContext(self, context):
        res = []
        if context == {}:
            self.context = "Sempre"
        else:
            for key in context:
                if key == 'date':
                    res.append("- Dias: de " + context[key]['from'] + " a " + context[key]['to'])
                elif key == 'hour':
                    res.append("- Horas: de " + context[key]['from'] + " a " + context[key]['to'])
                elif key == 'ip':
                    res.append("- Rede: " + ('Interna' if context[key] == 'internal' else 'Externa'))
            self.context = '\n'.join(res)


def abac(request, type, id):
    if 'allow' not in request.session:
        return redirect('sensors:login')
    if not request.session['allow']:
        return redirect('sensors:forbidden')

    try:
        metadata = api_get_request('/' + type + '/' + id, request.session).json()
    except ResponseException:
        pass

    body = {
        'resources.'+type: id
    }
    data = api_get_request('/accessPolicies', request.session, data=body).json()

    policies = []
    for d in data:
        policies.append(Policy(d['subjects'], d['actions'], d['context'], d['effect'], d['description'], d['uid']))

    return render(request, "sensors/abac.html", {'uname': request.session['uname'], 'type': type, 'metadata': metadata, 'id': id, 'policies': policies})

def template(request):
    if 's' in request.GET:
        request.session['cookies'] = {'session': request.GET['s']}
        request.session['User-Agent'] = request.headers['User-Agent']
        user = api_get_request('/identity', request.session).json()
        request.session['uname'] = user['name'] + ' ' + user['surname']
        request.session['allow'] = True
        return redirect('sensors:template')
    elif 'allow' not in request.session:
        return redirect('sensors:login')
    elif not request.session['allow']:
        return redirect('sensors:forbidden')
    return render(request, "sensors/index.html", {'uname': request.session['uname']})

# API Requests

def key(request, uuid):
    try:
        return HttpResponse(api_get_request('/sensor/' + uuid + '/key', request.session), content_type='application/json')
    except ResponseException as r:
        return HttpResponse(status=r.code)

def postObject(request, object, id):
    if object == "room" or object == "type":
        data = {
            'name': request.POST.get("name"),
            'description': request.POST.get("description")
        }
    elif object == "sensor":
        data = {
            'room_id': request.POST.get("room_id"),
            'description': request.POST.get("description"),
            'data': {
                'unit_symbol': request.POST.get("symbol")[:3],
                'type': request.POST.get("type")
            }
        }
    elif object == "user":
        data = {
            'admin': request.POST.get("admin")
        }
    elif object == "mobile":
        data = {
            'title': request.POST.get("subject"),
            'message': request.POST.get("message"),
        }
        if "sensor" in request.POST:
            data['evalMatches'] = [{'metric': request.POST.get("sensor")}]
    elif object == "accessPolicy":
        data = json.loads(request.POST.get("policy"))
    try:
        if (id == "new"):
            print("Create New " + object + ": " + str(data))
            return HttpResponse(api_post_request('/'+object, data, request.session), content_type='application/json')
        print("Update " + object + ": " + str(data))
        return HttpResponse(api_post_request('/'+object+'/' + id, data, request.session), content_type='application/json')
    except ResponseException as r:
        return HttpResponse(status=r.code)

def deleteObject(request, object, id):
    try:
        print("Delete " + object + ": " + str(id))
        if object == "room":
            SensorsIndexView.deleteRoomSensors(request, id)
        return HttpResponse(api_delete_request('/'+object+'/' + id, request.session), content_type='application/json')
    except ResponseException as r:
        return HttpResponse(status=r.code)

# Session views

def login(request):
    return render(request, "sensors/login.html")


def logout(request):
    if 'allow' not in request.session:
        return redirect('sensors:login')
    try:
        api_get_request('/logout', request.session)
    except ResponseException as r:
        if r.code != 401:
            raise Exception
    request.session.flush()
    return redirect('sensors:login')


def forbidden(request):
    if 's' in request.GET:
        request.session['cookies'] = {'session': request.GET['s']}
        request.session['User-Agent'] = request.headers['User-Agent']
        user = api_get_request('/identity', request.session).json()
        request.session['uname'] = user['name'] + ' ' + user['surname']
        request.session['allow'] = False
        return redirect('sensors:forbidden')
    return render(request, "sensors/forbidden.html")


def api_login(request):
    return redirect(API_URL + '/login?app=gestao&redirect_url=' + urllib.parse.urlparse(request.build_absolute_uri('/gestao/'))._replace(scheme="https").geturl())

# API Requests - Helper functions

def api_get_request(endpoint, session, tries=0, data=""):
    if data:
        result = requests.get(API_URL + endpoint, json=data, headers={'User-Agent': session['User-Agent']}, cookies=session['cookies'])
    else:
        result = requests.get(API_URL + endpoint, headers={'User-Agent': session['User-Agent']}, cookies=session['cookies'])
    if result.status_code == 200:
        if tries < 4:
            if data:
                return result if is_json(result.text) else api_get_request(endpoint, session, tries + 1, data)
            return result if is_json(result.text) else api_get_request(endpoint, session, tries + 1)
        else:
            print('here')
            return None
    else:
        raise ResponseException(result.status_code)

async def api_get_async(url, id, session):
    for i in range(3):
        resp = await session.get(url + '/' + str(id))
        async with resp as response:
            if response.status == 200:
                if is_json(await response.text()):
                    return (id, await response.json())
                else:
                    continue
            else:
                raise ResponseException(response.status)
    return (id, None)


async def api_delete_async(url, id, session):
    for i in range(3):
        resp = await session.delete(url + '/' + str(id))
        async with resp as response:
            if response.status == 200:
                if is_json(await response.text()):
                    return
                else:
                    continue
            else:
                raise ResponseException(response.status)
    return

async def api_get_bulk_async(endpoint, ids, session):
    async with aiohttp.ClientSession(loop=get_async_loop(), headers={'User-Agent': session['User-Agent']}, cookies=session['cookies']) as s:
        results = await asyncio.gather(*[api_get_async(API_URL + endpoint, id, s) for id in ids])
        return results

async def api_delete_bulk_async(endpoint, ids, session):
    async with aiohttp.ClientSession(loop=get_async_loop(), headers={'User-Agent': session['User-Agent']}, cookies=session['cookies']) as s:
        results = await asyncio.gather(*[api_delete_async(API_URL + endpoint, id, s) for id in ids])
        return results

def api_post_request(endpoint, data, session, tries=0):
    result = requests.post(API_URL + endpoint, json=data, headers={'User-Agent': session['User-Agent']}, cookies=session['cookies'])
    if result.status_code == 200:
        if tries < 3:
            return result if is_json(result.text) else api_post_request(endpoint, data, session, tries + 1)
        else:
            return None
    else:
        raise ResponseException(result.status_code)

def api_delete_request(endpoint, session, tries=0):
    result = requests.delete(API_URL + endpoint, headers={'User-Agent': session['User-Agent']}, cookies=session['cookies'])
    if result.status_code == 200:
        if tries < 3:
            return result if is_json(result.text) else api_delete_request(endpoint, session, tries + 1)
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

# Misc. Helper functions

def get_async_loop():
    try:
        asyncio.get_event_loop()
    except:
        asyncio.set_event_loop(asyncio.new_event_loop())
    finally:
        return asyncio.get_event_loop()



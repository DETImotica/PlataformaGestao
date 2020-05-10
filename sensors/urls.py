#URL config
from django.urls import path
from . import views

app_name = 'sensors'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('rooms/', views.RoomsIndexView.as_view(), name='rooms'),
    path('sensors/', views.SensorsIndexView.as_view(), name='sensors'),
    path('types/', views.TypesIndexView.as_view(), name='types'),
    path('', views.template, name='template'),
    path('rooms/<slug:room_id>/', views.RoomsIndexView.roomDetails, name="roomDetails"),
    path('sensors/<slug:sensor_id>/', views.SensorsIndexView.sensorDetails, name='sensorDetails')
]
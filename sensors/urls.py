#URL config
from django.urls import path
from . import views

app_name = 'sensors'
urlpatterns = [
    path('rooms/', views.RoomsIndexView.as_view(), name='rooms'),
    path('sensors/', views.SensorsIndexView.as_view(), name='sensors'),
    path('types/', views.TypesIndexView.as_view(), name='types'),

    path('rooms/<slug:room_id>/', views.roomDetails, name="roomDetails"),
]
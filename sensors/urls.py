#URL config
from django.urls import path
from . import views

app_name = 'sensors'
urlpatterns = [
    path('', views.template, name='template'),
    path('rooms/', views.RoomsIndexView.as_view(), name='rooms'),
    path('sensors/', views.SensorsIndexView.as_view(), name='sensors'),
    path('types/', views.TypesIndexView.as_view(), name='types'),
    path('users/', views.UsersIndexView.as_view(), name='users'),
    path('sensors/<slug:room_id>/', views.SensorsIndexView.roomDetails, name="roomDetails"),

    path('login/', views.login, name='login'),
    path('api_login/', views.api_login, name='api_login'),
    path('logout/', views.logout, name='logout'),
    path('forbidden/', views.forbidden, name='forbidden'),

    path('get/key/<slug:uuid>/', views.key, name='api_key'),
    path('post/<slug:object>/<slug:id>', views.postObject, name='api_post'),
    path('delete/<slug:object>/<slug:id>', views.deleteObject, name='api_delete')
]
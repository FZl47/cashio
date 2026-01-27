from django.urls import path

from . import views

app_name = 'apps.comm'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),

    path('resource/<int:pk>/pin/change/state', views.ResourcePinChangeState.as_view(), name='resource__pin_change_state'),

    path('resource/folder/create', views.ResourceFolderCreate.as_view(), name='resource__folder__create'),
    path('resource/file/create', views.ResourceFileCreate.as_view(), name='resource__file__create'),

    path('file-raw/upload', views.FileRawUpload.as_view(), name='file_raw__upload'),
]

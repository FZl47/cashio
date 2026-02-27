from django.urls import path

from . import views

app_name = 'apps.public'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('settings', views.Settings.as_view(), name='settings'),
    path('set-lang/<str:lang>', views.SetLang.as_view(), name='set_lang'),

    path('yarmalli/settings/api-key/manage', views.YarMalliSettingsAPIKeyManage.as_view(), name='yarmalli_settings__api_key__manage'),
]

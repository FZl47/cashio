from django.urls import path

from . import views

app_name = 'apps.account'

urlpatterns = [
    path('login', views.Login.as_view(), name='login'),
    path('logout', views.Logout.as_view(), name='logout'),
    path('permissions/manage', views.Permissions.as_view(), name='permissions'),
    path('permission/group/<int:pk>/delete', views.PermissionGroupDelete.as_view(), name='permission_group__delete'),

    path('user/create', views.UserCreate.as_view(), name='user__create'),
    path('user/list', views.UserList.as_view(), name='user__list'),
    path('user/<int:pk>/update', views.UserUpdate.as_view(), name='user__update'),
    path('user/<int:pk>/permission/update', views.UserPermissionUpdate.as_view(), name='user_permission__update'),
    path('user/<int:pk>/detail', views.UserDetail.as_view(), name='user__detail'),
    path('user/<int:pk>/delete', views.UserDelete.as_view(), name='user__delete'),
]

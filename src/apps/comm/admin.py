from django.contrib import admin

from . import models

admin.site.register(models.ResourceBase)
admin.site.register(models.ResourcePin)
admin.site.register(models.FileResource)
admin.site.register(models.FolderResource)
admin.site.register(models.FileRaw)

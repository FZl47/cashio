from django.contrib import admin

from . import models

admin.site.register(models.Company)

admin.site.register(models.PettyCashFund)
admin.site.register(models.PettyCashHolder)
admin.site.register(models.PettyCashTransactionDocument)
admin.site.register(models.PettyCashTransaction)

admin.site.register(models.Document)
admin.site.register(models.DocumentStatus)





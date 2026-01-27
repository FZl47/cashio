from django.conf import settings

from openpyxl import Workbook

from . import models


class ExportFunds:

    def prepare(self):
        qs = models.PettyCashFund.objects.all()

        wb = Workbook()
        ws = wb.active
        ws.title = "Funds"

        # header
        ws.append([
            'Title', 'Balance'
        ])

        # data
        for obj in qs:
            ws.append(
                obj.title,
                obj.balance
            )

        # save
        wb.save(settings.MEDIA_ROOT / 'output.xlsx')

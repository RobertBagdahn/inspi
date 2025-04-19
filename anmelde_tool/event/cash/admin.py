from django.contrib import admin

from anmelde_tool.event.cash import models as cash_models

admin.site.register(cash_models.CashIncome)

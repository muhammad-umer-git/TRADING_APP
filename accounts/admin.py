from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Account, Position, Ledger, Stock, Trade

admin.site.register(CustomUser)
admin.site.register(Account)
admin.site.register(Position)
admin.site.register(Ledger)
admin.site.register(Stock)
admin.site.register(Trade)
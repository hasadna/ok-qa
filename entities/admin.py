from django.contrib import admin
from .models import Entity, Domain, Division

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    pass


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    pass


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    pass

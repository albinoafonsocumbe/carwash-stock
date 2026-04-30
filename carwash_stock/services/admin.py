from django.contrib import admin
from .models import Service, ServiceProduct


class ServiceProductInline(admin.TabularInline):
    model = ServiceProduct
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)
    inlines = [ServiceProductInline]


@admin.register(ServiceProduct)
class ServiceProductAdmin(admin.ModelAdmin):
    list_display = ('servico', 'produto', 'quantidade_usada')
    list_filter = ('servico',)

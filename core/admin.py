from django.contrib import admin
from core.models import User, Product, Order, OrderItem, Link


class UserAdmin(admin.ModelAdmin):
    """Custom user admin."""
    ordering = ('id',)


admin.site.register(User, UserAdmin)
admin.site.register(Product)
admin.site.register(Link)
admin.site.register(Order)
admin.site.register(OrderItem)

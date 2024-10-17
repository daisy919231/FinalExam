from django.contrib import admin
from texnomart.models import Category, Group, Product, Brand, Image, CharacteristicsKey, CharacteristicsValue, ProductCharacteristics
# Register your models here.
admin.site.register(Category)
admin.site.register(Group)
admin.site.register(Product)
admin.site.register(Brand)
admin.site.register(Image)
admin.site.register(CharacteristicsKey)
admin.site.register(CharacteristicsValue)
admin.site.register(ProductCharacteristics)
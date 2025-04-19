from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Professions, Crafting, craftingRequirements, Objects, ObjectCategorys, ObjectTypes,
    Races, Rarities, RolesCombatUnits, CombatUnits, HeroeTypes, Heroes, HeroeRoles, Pets, PetsTypes
)

# Método común para mostrar imágenes
def image_tag(obj):
    if obj.image:
        return format_html('<img src="{}" width="50" height="50" />'.format(obj.image.url))
    return "No Image"
image_tag.short_description = 'Image'

class CraftingRequirementsInline(admin.TabularInline):
    model = craftingRequirements
    extra = 1

@admin.register(Crafting)
class CraftingAdmin(admin.ModelAdmin):
    inlines = [CraftingRequirementsInline]
    list_display = ( 'object_image','linked_object_name', 'prof_name')
    inlines = [CraftingRequirementsInline]
    list_filter = ('level','proffesion')

    def prof_name(self, obj):
        return obj.proffesion.name
    prof_name.short_description = 'Profession'
    def linked_object_name(self, obj):
        # Create a link to the edit page of the related object
        url = f"/admin/valApp/objects/{obj.object.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.object.name)
    linked_object_name.short_description = 'Object'

    def object_image(self, obj):
        if obj.object.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.object.image.url)
        return "No Image"
    object_image.short_description = 'Image'

    

@admin.register(Objects)
class ObjectsAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'objectType', 'objectCategory', image_tag)

@admin.register(Professions)
class ProfessionsAdmin(admin.ModelAdmin):
    list_display = ('name', image_tag)

@admin.register(Races)
class RacesAdmin(admin.ModelAdmin):
    list_display = ('name', image_tag)

@admin.register(Heroes)
class HeroesAdmin(admin.ModelAdmin):
    list_display = ('name','race_name', image_tag)
    list_filter = ('race',)
    def race_name(self, obj):
        return obj.race.name
    race_name.short_description = 'Race'

@admin.register(CombatUnits)
class CombatUnitsAdmin(admin.ModelAdmin):
    list_display = ('name', image_tag)
    list_filter = ('race',)

    def race_name(self, obj):
        return obj.race.name
    race_name.short_description = 'Race'


@admin.register(Pets)
class PetsAdmin(admin.ModelAdmin):  # Renamed to PetsAdmin
    list_display = ('name', image_tag)
    list_filter = ('rarity',)

    def rarity_name(self, obj):  # Corrected method name
        return obj.rarity.name
    rarity_name.short_description = 'Rarity'  

# Registro de modelos sin personalización
admin.site.register(ObjectTypes)
admin.site.register(ObjectCategorys)
admin.site.register(Rarities)
admin.site.register(HeroeTypes)
admin.site.register(RolesCombatUnits)
admin.site.register(HeroeRoles)

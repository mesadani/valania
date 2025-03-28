from django.db import models

# Create your models here.

class Professions(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField() 
    image = models.ImageField(upload_to='objects/images/', blank=True, null=True)  # Nuevo campo de imagen


    def __str__(self):
        return self.name
    
class ObjectTypes(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
class ObjectCategorys(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Objects(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    objectType = models.ForeignKey(ObjectTypes, on_delete=models.CASCADE)
    objectCategory = models.ForeignKey(ObjectCategorys, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='objects/images/', blank=True, null=True)  # Nuevo campo de imagen


    def __str__(self):
        return self.name
    
class Crafting(models.Model):
    object = models.ForeignKey(Objects, on_delete=models.CASCADE)
    proffesion = models.ForeignKey(Professions, on_delete=models.CASCADE)
    level = models.IntegerField()
    quantity = models.IntegerField()
    probability = models.FloatField()
    time = models.IntegerField()

    def __str__(self):
        return self.object.name    
    

class craftingRequirements(models.Model):
    craft = models.ForeignKey(Crafting, on_delete=models.CASCADE)
    object = models.ForeignKey(Objects, on_delete=models.CASCADE)
    quantity = models.IntegerField() 


    def __str__(self):
        return self.craft.object.name + " - " + self.object.name        


class Races(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField() 
    image = models.ImageField(upload_to='objects/images/', blank=True, null=True)  # Nuevo campo de imagen


    def __str__(self):
        return self.name
    
class Rarities(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField() 
    def __str__(self):
        return self.name    
    
class HeroeTypes(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField() 
    
    def __str__(self):
        return self.name 

class Heroes(models.Model):
    name = models.CharField(max_length=200)
    type = models.ForeignKey(HeroeTypes, on_delete=models.CASCADE)
    race = models.ForeignKey(Races, on_delete=models.CASCADE)
    supply = models.IntegerField()
    rarity = models.ForeignKey(Rarities, on_delete=models.CASCADE)
    price = models.IntegerField()
    location = models.CharField(max_length=200)
    description = models.TextField()

    image = models.ImageField(upload_to='objects/images/', blank=True, null=True)  # Nuevo campo de imagen


    def __str__(self):
        return self.name       
    

class RolesCombatUnits(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField() 
    
    def __str__(self):
        return self.name     
class CombatUnits(models.Model):
    name = models.CharField(max_length=200)
    role = models.ForeignKey(RolesCombatUnits, on_delete=models.CASCADE)
    race = models.ForeignKey(Races, on_delete=models.CASCADE)
    supply = models.IntegerField()
    rarity = models.ForeignKey(Rarities, on_delete=models.CASCADE)
    price = models.IntegerField()
    location = models.CharField(max_length=200)
    troopPoints = models.IntegerField()
    description = models.TextField()

    image = models.ImageField(upload_to='objects/images/', blank=True, null=True)  # Nuevo campo de imagen


    def __str__(self):
        return self.name     
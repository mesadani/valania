from django.db import models
from cloudinary.models import CloudinaryField
# Create your models here.
from django.contrib.auth.models import User

class Professions(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField() 
    image = CloudinaryField('image', folder='professions')


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
    description = models.TextField(blank=True, null=True)  # Permitir nulo y vacío
    objectType = models.ForeignKey(ObjectTypes, on_delete=models.CASCADE)
    objectCategory = models.ForeignKey(ObjectCategorys, on_delete=models.CASCADE)
    image = CloudinaryField('image', folder='objects', blank=True, null=True)  # Permitir nulo y vacío
    mint = models.CharField(max_length=200)
    uri = models.CharField(max_length=200)
    nftImage = models.CharField(max_length=500,default=0)
    supply = models.IntegerField(default=0)

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
    craft = models.ForeignKey(Crafting, on_delete=models.CASCADE, related_name='requirements')
    object = models.ForeignKey(Objects, on_delete=models.CASCADE)
    quantity = models.IntegerField() 


    def __str__(self):
        return self.craft.object.name + " - " + self.object.name        


class Races(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField() 
    image = CloudinaryField('image', folder='races')


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
    
class HeroeRoles(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField() 
    
    def __str__(self):
        return self.name     

class HeroeRoles(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name

class Heroes(models.Model):
    name = models.CharField(max_length=200)
    type = models.ForeignKey(HeroeTypes, on_delete=models.CASCADE)
    role = models.ForeignKey(HeroeRoles, on_delete=models.CASCADE)
    race = models.ForeignKey(Races, on_delete=models.CASCADE)
    supply = models.IntegerField()
    rarity = models.ForeignKey(Rarities, on_delete=models.CASCADE)
    price = models.IntegerField()
    location = models.CharField(max_length=200)
    description = models.TextField()
    mint = models.CharField(max_length=200,default=0)
    uri = models.CharField(max_length=200,default=0)
    nftImage = models.CharField(max_length=500,default=0)

    image = CloudinaryField('image', folder='heroes')


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
    mint = models.CharField(max_length=200,default=0)
    uri = models.CharField(max_length=200,default=0)
    nftImage = models.CharField(max_length=500,default=0)

    image = CloudinaryField('image', folder='combatUnits')


    def __str__(self):
        return self.name     
    
class PetsTypes(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField() 

    def __str__(self):
        return self.name     

class Pets(models.Model):
    name = models.CharField(max_length=200)
    type = models.ForeignKey(PetsTypes, on_delete=models.CASCADE)
    supply = models.IntegerField()
    rarity = models.ForeignKey(Rarities, on_delete=models.CASCADE)
    price = models.IntegerField()
    location = models.CharField(max_length=200)
    description = models.TextField()

    image = CloudinaryField('image', folder='pets')

    def __str__(self):
        return self.name    

class ObjectsPrices(models.Model):
    object = models.ForeignKey(Objects, related_name='objectsprices_set', on_delete=models.CASCADE)
    price = models.FloatField() 
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name 


class Guilds(models.Model):
    uuid = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    avatar = models.CharField(max_length=500)
    tag = models.CharField(max_length=200)
    race = models.ForeignKey(Races, on_delete=models.CASCADE)
    description = models.TextField() 
    language = models.CharField(max_length=100)
    members = models.IntegerField()
    announce = models.TextField()
    leader = models.CharField(max_length=200)
    usdc = models.FloatField()
    ranking = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name 

class GuildMembers(models.Model):
    guild = models.ForeignKey(Guilds, on_delete=models.CASCADE,null=True)
    race = models.ForeignKey(Races, on_delete=models.CASCADE,null=True, related_name='members')
    name = models.CharField(max_length=200, null=True)
    idRank = models.CharField(max_length=200, null=True)
    uuid = models.CharField(max_length=200, null=True)
    roleuuid=models.CharField(max_length=200, null=True)
    address = models.CharField(max_length=500, null=True)
    uuidGuild = models.CharField(max_length=500, null=True)
    points = models.IntegerField(default=0)
    artisan = models.IntegerField(default=0)
    alchemist = models.IntegerField(default=0)
    architect = models.IntegerField(default=0)
    blacksmith = models.IntegerField(default=0)
    engineer = models.IntegerField(default=0)
    explorer = models.IntegerField(default=0)
    jeweler = models.IntegerField(default=0)
    miner = models.IntegerField(default=0)
    avatar = models.CharField(max_length=200, null=True)
    usdc = models.IntegerField(default=0)
    ranking = models.IntegerField( null=True)
    herokind = models.CharField(max_length=200, null=True) 
    heroLvl = models.IntegerField(default=0)
    profession = models.ForeignKey(Professions, on_delete=models.CASCADE, null=True, related_name='members')  # Permitir nulo
    professionMastery = models.IntegerField(default=0)  # Permitir nulo
    weeklyCrafts = models.IntegerField(default=0)  # Permitir nulo
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name               

class ObjectsBuyPrices(models.Model):
    object = models.ForeignKey(Objects, on_delete=models.CASCADE)
    price = models.FloatField() 
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name 
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notificación para {self.user.username}: {self.message}'    
    


class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    object = models.ForeignKey(Objects, on_delete=models.CASCADE)
    price = models.FloatField()
    amount = models.IntegerField(default=1)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Notificación para {self.user.username}: {self.message}'        
    


class ProfileUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet = models.CharField(max_length=100, blank=True)
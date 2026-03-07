from django.db import models
from common.models import BaseModel

class Washer(BaseModel):
    name = models.CharField(max_length = 100)
    capacity = models.CharField(max_length = 50)
    price = models.DecimalField(max_digits = 6, decimal_places = 2)
    is_active = models.BooleanField(default = True)

    def __str__(self):
        return self.name


class Dryer(BaseModel):
    name = models.CharField(max_length = 100)
    price_per_interval = models.DecimalField(max_digits = 6, decimal_places = 2)
    interval_minutes = models.PositiveIntegerField() 
    is_active = models.BooleanField(default = True)

    def __str__(self):
        return self.name


class Supply(BaseModel):
    class SupplyType(models.TextChoices):
        DETERGENT = 'DETERGENT', 'Detergente'
        SOFTENER = 'SOFTENER', 'Suavizante'

    name = models.CharField(max_length = 100)
    supply_type = models.CharField(max_length = 20, choices = SupplyType.choices)

    def __str__(self):
        return self.name


class SupplyPortion(BaseModel):
    """ Porciones fijas por precio. Ej: 8oz de detergente = $0.6$"""
    supply = models.ForeignKey(Supply, on_delete = models.PROTECT, related_name = 'portions')
    quantity_oz = models.DecimalField(max_digits = 5, decimal_places = 2)
    price = models.DecimalField(max_digits = 6, decimal_places = 2)
    is_active = models.BooleanField(default = True)

    def __str__(self):
        return f"{self.supply.name} {self.quantity_oz}oz - ${self.price}" 


class GasPurchase(BaseModel):
    purchase_date = models.DateField()
    tank_count = models.PositiveIntegerField()
    price_per_tank = models.DecimalField(max_digits = 6, decimal_places = 2)

    @property
    def total_cost(self):
        return self.tank_count * self.price_per_tank

    def __str__(self):
        return f"{self.purchase_date} - {self.tank_count} tanques"



class Bag(BaseModel):
    """Funda vendible al cliente."""
    name  = models.CharField(max_length=100, default="Funda")
    price = models.DecimalField(max_digits=6, decimal_places=2)  # $0.25
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"

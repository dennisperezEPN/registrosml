from django.db import models
from common.models import BaseModel

# TODO: Modelos de cada tabla para INVENTARIO
class InventoryItem(BaseModel):
    class InventoryItemType(models.TextChoices):
        DETERGENT = 'DETERGENT', 'Detergente'
        SOFTENER = 'SOFTENER', 'Suavizante'
        SOFTENER = 'BAG', 'Funda'
        GAS = 'GAS', 'Gas'
    
    class InventoryItemUnitType(models.TextChoices):
        OZ = 'OZ', 'oz'
        TANK = 'TANK', 'unit'

    name = models.CharField(max_length = 100)
    item_type = models.CharField(
                max_length = 20,
                choices = InventoryItemType.choices
            )
    unit = models.CharField(
                max_length = 20,
                choices = InventoryItemUnitType.choices
            )
    current_stock = models.DecimalField(max_digits = 6, decimal_places = 2)
    average_unit_cost = models.DecimalField(max_digits = 6, decimal_places = 2)
    is_active = models.BooleanField(default = True)
    
    def __str__(self):
        return self.name


class InventoryMovement(BaseModel):
    inventory_item = models.ForeignKey(
                        
            ) 

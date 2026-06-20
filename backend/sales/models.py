from django.db import models
from django.core.validators import MinValueValidator
from common.models import BaseModel
from customers.models import Customer
from resources.models import Washer, Dryer, SupplyPortion, Bag

# TODO: Revisar payment_status, puede quedar inconsistente 
#       Venta total: $10.00
#       Pagos registrados: $10.00
#       payment_status: PENDING
class Sale(BaseModel):
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        PAID = 'PAID', 'Pagado'

    class DeliveryStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        DELIVERED = 'DELIVERED', 'Entregado'


    customer = models.ForeignKey(
                Customer, on_delete = models.SET_NULL,
                null = True, blank = True, related_name = 'sales'
            )
    payment_status = models.CharField(
                max_length = 20,
                choices = PaymentStatus.choices,
                default = PaymentStatus.PENDING
            )
    delivery_status = models.CharField(
                max_length = 20,
                choices = DeliveryStatus.choices,
                default = DeliveryStatus.PENDING
            )
    delivered_at = models.DateTimeField(null = True, blank = True)
    notes = models.TextField(blank = True)

    @property
    def total(self):
        wash_total = sum(item.subtotal for item in self.wash_items.all())
        supply_total = sum(item.subtotal for item in self.supply_items.all())
        dry_total = sum(item.subtotal for item in self.dry_items.all())
        bag_total = sum(item.subtotal for item in self.bag_items.all())

        return wash_total + supply_total + dry_total + bag_total

    def __str__(self):
        client = str(self.customer) if self.customer else "Consumidor final"
        return f"Venta {self.created_at.date()} - {client}"


class SaleWashItem(BaseModel):
    """ Un uso de lavadora dentro de una venta. """
    sale = models.ForeignKey(Sale, on_delete = models.CASCADE, related_name = 'wash_items')
    washer = models.ForeignKey(Washer, on_delete = models.PROTECT)
    price_charged = models.DecimalField(max_digits = 6, decimal_places = 2)

    @property
    def subtotal(self):
        return self.price_charged 

    def __str__(self):
        return f"{self.washer.name} - Venta {self.sale_id}"


class SaleSupplyItem(BaseModel):
    """Porción de insumo (detergente/suavizante) asociada a una venta."""
    sale = models.ForeignKey(Sale, on_delete = models.CASCADE, related_name = 'supply_items')
    supply_portion = models.ForeignKey(SupplyPortion, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)]) # Cantidad de porciones del suplemento (Ej. 1 porcion de 2 oz, 2 porciones de 4 oz etc.) 
    price_charged = models.DecimalField(max_digits=6, decimal_places=2)  # snapshot del precio unitario
    cost_snapshot = models.DecimalField(max_digits=6, decimal_places=2)  # snapshot del costo por porcion  

    @property
    # TODO: Cambiar funcion subtotal para que se calcule bien el subtotal. 
    # Quanitty es el numero de porciones de 2 oz, 4 oz o 8 oz del SupplyItem
    def subtotal(self):
        return self.price_charged * self.quantity

    def __str__(self):
        return f"{self.supply_portion} x{self.quantity}"


class SaleDryItem(BaseModel):
    """Una tanda de secado dentro de una venta."""
    sale          = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='dry_items')
    dryer         = models.ForeignKey(Dryer, on_delete=models.PROTECT)
    intervals     = models.PositiveIntegerField(validators=[MinValueValidator(1)])  # ej: 6 intervalos = 42 min
    price_charged = models.DecimalField(max_digits=6, decimal_places=2)  # snapshot precio por intervalo

    @property
    def duration_minutes(self):
        return self.intervals * self.dryer.interval_minutes

    @property
    def subtotal(self):
        return self.price_charged * self.intervals

    def __str__(self):
        return f"{self.dryer.name} - {self.intervals} intervalos"


class SaleBagItem(BaseModel):
    """Fundas vendidas en una venta."""
    sale          = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='bag_items')
    bag           = models.ForeignKey(Bag, on_delete=models.PROTECT)
    quantity      = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price_charged = models.DecimalField(max_digits=6, decimal_places=2)  # snapshot
    cost_snapshot = models.DecimalField(max_digits=6, decimal_places=2)  # snapshot del costo

    @property
    def subtotal(self):
        return self.price_charged * self.quantity

    def __str__(self):
        return f"{self.quantity} funda(s) - Venta {self.sale_id}"


class Payment(BaseModel):
    class PaymentMethod(models.TextChoices):
        CASH     = 'CASH',     'Efectivo'
        TRANSFER = 'TRANSFER', 'Transferencia'
        APP      = 'APP',      'DeUna'

    sale       = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments')
    method     = models.CharField(max_length=20, choices=PaymentMethod.choices)
    amount     = models.DecimalField(max_digits=8, decimal_places=2)
    paid_at    = models.DateTimeField()

    def __str__(self):
        return f"{self.get_method_display()} ${self.amount} - Venta {self.sale_id}"

"""

Cómo queda la lógica

    Detergente / suavizante
    InventoryItem = producto físico en inventario
    Supply = suplemento vendible
    SupplyPortion = presentación o porción vendible
    SaleSupplyItem = lo vendido
    InventoryMovement = salida real del inventario

Ejemplo:

    InventoryItem:
    Detergente líquido, unit: oz

    Supply:
    Detergente líquido

    SupplyPortion:
    2 oz, precio $0.50

    SaleSupplyItem:
    2 porciones, price_charged $1.00, cost_snapshot $0.20

    InventoryMovement:
    quantity_delta -4 oz

Fundas
    InventoryItem = funda física en inventario
    Bag = funda vendible
    SaleBagItem = fundas vendidas
    InventoryMovement = salida real del inventario

    Ejemplo:

    SaleBagItem:
    quantity: 2
    price_charged: 0.50
    cost_snapshot: 0.12

    InventoryMovement:
    quantity_delta: -2

Gas

    El gas queda como inventario general, no asociado a cada secada:

    InventoryItem:
    Tanque de gas
    unit: tank

    InventoryPurchase:
    Compra de 2 tanques

    InventoryMovement:
    +2 tanques por compra
    -1 tanque cuando se acaba

    Eso está bien porque decidiste no calcular gas por intervalo.

Recomendación pequeña adicional

    En InventoryMovement, tuviste buena idea agregando:

    sale_supply_item_id int [null]
    sale_bag_item_id int [null]

    Yo solo aplicaría esta regla en tu lógica de aplicación:

    Si movement_type = purchase:
      inventory_purchase_id debe tener valor.

    Si movement_type = sale_usage por suplemento:
      sale_id y sale_supply_item_id deben tener valor.

    Si movement_type = sale_usage por funda:
      sale_id y sale_bag_item_id deben tener valor.

    Si movement_type = usage para gas:
      sale_id puede ser null.

    No necesariamente tienes que imponerlo en dbdiagram, pero sí en tu backend.

Veredicto

Con solo agregar estas dos relaciones:

Ref: InventoryItem.id < Supply.inventory_item_id
Ref: InventoryItem.id < Bag.inventory_item_id

tu modelo queda bastante completo y coherente.

Ya tienes una buena separación entre:

lo que vendes
lo que cobras
lo que compras
lo que consumes
lo que queda en inventario

Para el tamaño del negocio que describes, está muy bien diseñado.

"""

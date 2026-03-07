from django.db import models
from django.core.validators import MinValueValidator
from common.models import BaseModel
from customers.models import Customer
from resources.models import Washer, Dryer, SupplyPortion, Bag

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
        dry_total = sum(item.subtotal for item in self.dry_items.all())
        bag_total = sum(item.subtotal for item in self.bag_items.all())
        return wash_total + dry_total + bag_total

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
        supply_total = sum(s.subtotal for s in self.supplies.all())
        return self.price_charged + suply_total

    def __str__(self):
        return f"{self.washer.name} - Venta {self.sale_id}"


class SaleWashSupply(BaseModel):
    """Porción de insumo (detergente/suavizante) asociada a un ítem de lavado."""
    wash_item     = models.ForeignKey(SaleWashItem, on_delete=models.CASCADE, related_name='supplies')
    portion       = models.ForeignKey(SupplyPortion, on_delete=models.PROTECT)
    quantity      = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price_charged = models.DecimalField(max_digits=6, decimal_places=2)  # snapshot del precio unitario

    @property
    def subtotal(self):
        return self.price_charged * self.quantity

    def __str__(self):
        return f"{self.portion} x{self.quantity}"


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


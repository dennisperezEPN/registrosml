from django.db import models
from common.models import BaseModel

class Customer(BaseModel):
    first_name = models.CharField(max_length = 100)
    last_name = models.CharField(max_length = 100)
    phone = models.CharField(max_length = 20)
    id_number = models.CharField(max_length = 20, blank = True, null = True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

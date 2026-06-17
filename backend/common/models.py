import uuid
from django.db import models

class BaseModel(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    
    # Crea la clase abstracta BaseModel
    # No se crea una tabla BaseModel, pero si se crean
    # los campos en cada clase que hereda de BaseModel
    class Meta:
        abstract = True


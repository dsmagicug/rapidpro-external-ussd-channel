from django.db import models


# Create your models here.

class Contact(models.Model):
    urn = models.CharField(max_length=25,unique=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return self.urn

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
#import isbn_validator

# Create your models here.
class User(AbstractUser):
  date_of_membership = models.DateField(auto_now_add=True)
  is_active = models.BooleanField(default=True)

  class Meta:
    ordering = ['-date_joined']

  def __str__(self):
    return self.username
  

class Transaction(models.Model):
  CHECKOUT = 'CO'
  RETURN = 'RE'
  TRANSACTION_TYPES = [(CHECKOUT, 'Checkout'), (RETURN, 'Return')]

  user = models.ForeignKey(User, on_delete=models.CASCADE)
  transaction_type = models.CharField(max_length=2, choices=TRANSACTION_TYPES)
  transaction_date = models.DateTimeField(auto_now_add=True)
  due_date = models.DateField(null=True, blank=True)

  class Meta:
    ordering = ['-transaction_date']

  def __str__(self):
    return f"{self.user.username}"
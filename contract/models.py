from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from user.models import CustomUser
from job.models import Job, Proposal
from .enums import ContractStatus,PaymentStatus

class Contract(models.Model):
    contract_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='client_contracts')
    freelancer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='freelancer_contracts')
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)  # For contract details
    status = models.CharField(
        max_length=20, 
        choices=ContractStatus.choices, 
        default=ContractStatus.PENDING
    )
    total_amount = models.FloatField()
    start_date = models.DateField()
    end_date = models.DateField()
    terms = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contracts'

    def __str__(self):
        return f"Contract {self.contract_id} - {self.client} -> {self.freelancer}"

class Milestone(models.Model):
    milestone_id = models.AutoField(primary_key=True)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=255)
    description = models.TextField()
    amount = models.FloatField()
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'milestones'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    transaction_id = models.CharField(max_length=255, blank=True)  # External payment reference
    status = models.CharField(
        max_length=20, 
        choices=PaymentStatus.choices, 
        default=PaymentStatus.PENDING
    )
    contract = models.OneToOneField(Contract, on_delete=models.CASCADE, related_name='payment')
    screenshot = models.ImageField(upload_to='payment_screenshots/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment Verification'

    def __str__(self):
        return f"Payment for Contract {self.contract_id}"

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from user.models import CustomUser
from contract.models import Contract
from contract.enums import ContractStatus

from django.db import models
from django.utils.translation import gettext_lazy as _
from user.models import CustomUser
from contract.models import Contract
from contract.enums import ContractStatus

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='reviews_given'
    )
    freelancer = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='reviews_received'
    )
    contract = models.OneToOneField(
        Contract, 
        on_delete=models.CASCADE, 
        related_name='review'
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, f'{i} Stars') for i in range(1, 6)],
        default=5
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']

   

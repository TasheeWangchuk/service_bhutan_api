from django.db import models
from django.utils.translation import gettext_lazy as _

class Role(models.TextChoices):
    CLIENT = 'Client', _('Client')
    FREELANCER = 'Freelancer', _('Freelancer')
    ADMINISTRATOR = 'Administrator', _('Administrator')
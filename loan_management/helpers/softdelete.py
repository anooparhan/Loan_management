from django_acl.models import AbstractDateFieldMix
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel
from django.utils.translation import gettext_lazy as _


class DateFieldMixModel(AbstractDateFieldMix, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        abstract = True


    
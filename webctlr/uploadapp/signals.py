from django.db.models.signals import pre_save, pre_delete, post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from uploadapp.models import JSONConfig
import os.path

from remotectlr.config_parser_ctlr import ConfigParserCtlr

#ctlr = ConfigParserCtlr()
 

@receiver(post_save, sender=JSONConfig)
def model_post_save(sender, **kwargs):
    print('Saved: {}'.format(kwargs['instance'].__dict__))
#    ctlr.parse_configuration(kwargs['instance'])
#    ctlr.run_configuration()

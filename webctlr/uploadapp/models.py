from __future__ import unicode_literals

from django.db import models
from config_parser.config_parser import ConfigurationParser

parser = ConfigurationParser()

# Create your models here.
class JSONConfig(models.Model):
    configuration_text = models.CharField(max_length=10000)
    
    # Metadata - FIXME: what else?
    submit_time = models.DateTimeField('time received')
    user_name = models.CharField(max_length=20)


    def to_python(self, value):
        # TODO: This is necessary for validation.
        return parser.parse_configuration(value)

    def __str__(self):
        return "id: %s\n    submit_time: %s\n    user_name: %s\n    text: %s" % (self.id, self.submit_time, self.user_name, self.configuration_text)

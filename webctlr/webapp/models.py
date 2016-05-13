from __future__ import unicode_literals

from django.db import models

# Create your models here.
class OFField(models.Model):
    name_text = models.CharField(max_length=10)
    field_value = models.CharField(max_length=200) # To be parsed on the way out
    #optional_without =  #FIXME: how to?

    submit_time = models.DateTimeField('time received')

    # Validation
    #FIXME: how to? https://docs.djangoproject.com/en/1.9/ref/validators/



    def from_db_value(self, value, expression, connection, context):
        # Is this one needed?
        pass

    def to_python(self, value):
        # TODO: this is very much needed. Use MATCH_NAME_TO_CLASS lookup table
        pass


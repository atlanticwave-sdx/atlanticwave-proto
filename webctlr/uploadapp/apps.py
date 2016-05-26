from __future__ import unicode_literals

from django.apps import AppConfig


class UploadappConfig(AppConfig):
    name = 'uploadapp'

    instance = None

    def ready(self):
        import uploadapp.signals    
        
        # 
#        from time import sleep
#        from remotectlr.config_parser_ctlr import ConfigParserCtlr
#        instance = ConfigParserCtlr()
#        while instance.is_connected() == False:
#            print "Waiting for Local Controller connection"
#            sleep(.5)

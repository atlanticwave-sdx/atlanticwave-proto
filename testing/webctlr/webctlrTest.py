# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for Django implmentation

import unittest
import mock
import os
import json
import subprocess
from time import sleep 
from localctlr.LocalController import *




FNULL = open(os.devnull, 'w')

class RemoteControllerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.django = subprocess.Popen(["python", "../../webctlr/manage.py", "runserver"], stdout=subprocess.PIPE)
        sleep(3)

    
    @classmethod
    def asetUpClass(cls):
        # Taken and modified from  RyuControllerInterfaceTest.py

        # Setup the virtual switch
        print "Set up virtual switch"
        subprocess.check_call(['mn', '-c'], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call(['fuser', '-k', '55767/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call(['fuser', '-k', '55767/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call(['fuser', '-k', '5555/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call(['fuser', '-k', '5555/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.check_call(['ovs-vsctl', 'add-br', 'br_ovs'])
        subprocess.check_call(['ovs-vsctl', 'add-port', 'br_ovs', 'vi0', '--', 'set', 'Interface', 'vi0', 'type=internal'])
        subprocess.check_call(['ovs-vsctl', 'set', 'bridge', 'br_ovs', 'other-config:datapath-id=0000000000000001'])
        subprocess.check_call(['ovs-vsctl', 'set-controller', 'br_ovs', 'tcp:127.0.0.1:6633'])
        print "Virtual switch is setup\n"


        # Start the Local Controller
        cls.lc = subprocess.Popen(["python", "LocalControllerHarness.py"], stdout=subprocess.PIPE)
        cls.django = subprocess.Popen(["python", "../../webctlr/manage.py", "runserver"], stdout=subprocess.PIPE)


    def arun_test(self, testnum):
        # Based partially on https://stackoverflow.com/questions/21306515/how-to-curl-an-authenticated-django-app
        filename = "cookies.txt"
        url = "http://127.0.0.1:8000/upload/7/old/"
        post_url = "http://127.0.0.1:8000/upload/7/settext/"
        changed_val = "{\"rules\": [ {\"switch\":1, \"priority\":123, \"cookie\":1234, \"table\":1, \"match\":{\"ip_proto\":6, \"eth_type\":2048}, \"actions\":[{\"fwd\":1}], \"instruction\":\"apply_actions\"} ]}"
        #changed_val = "{\\\"rules\\\": [ {\\\"switch\\\":1, \\\"priority\\\":123, \\\"cookie\\\":1234, \\\"table\\\":1, \\\"match\\\":{\\\"ip_proto\\\":6, \\\"eth_type\\\":2048}, \\\"actions\\\":[{\\\"fwd\\\":1}], \\\"instruction\\\":\\\"apply_actions\\\"} ]}"
        
        # Get csrftoken
        get_csrftoken_call = "curl -s -c %s -b %s -e %s %s" % (filename, filename, url, url)
        print "Call to get token:\n    " + get_csrftoken_call
        subprocess.call(get_csrftoken_call.split(), stdout=FNULL)
        #subprocess.check_call(get_csrftoken_call.split())
        #subprocess.check_call(['curl', '-s', '-c', filename, '-b', filename, '-e', url, 
        #                      url])

        if not os.path.isfile(filename):
            self.fail("Could not get cookie")
        csrftoken = "csrfmiddlewaretoken=%s" % self.get_token(filename)
        change_str = "\"%s&configuration_text=%s\"" % (csrftoken, changed_val)

        # Push changes
        push_changes_call = "curl -s -c %s -b %s -e %s -d %s -X POST %s" % (filename, filename, url, change_str, post_url)
        print "Call to push changes:\n    " + push_changes_call
        subprocess.call(push_changes_call.split(), stdout=FNULL)
        #sleep (1)
#        subprocess.check_call(push_changes_call.split())
        #subprocess.check_call(['curl', '-s', '-c', filename, '-b', filename, '-e', url, 
        #                       '-d', change_str, '-X', 'POST', post_url])

        # Verify expected results
        verify_call = "curl -i -H \"Accept: application/json\" %s" % url
        print "Call to verify output:\n    " + verify_call
#        subprocess.check_call(verify_call.split())
#        subprocess.call(verify_call.split(), stdout=FNULL)
#        output = subprocess.check_output(['curl', '-i', '-H', '\"Accept: application/json\"', url])
#        print ""
#        print "Output for verification:"
#        print output
        
        # Cleanup
        #if os.path.isfile(filename):
        #    os.remove(filename)

    def run_test(self, testnum):
        filename = "cookies.txt"
        url = "http://127.0.0.1:8000/upload/7/old/"
        post_url = "http://127.0.0.1:8000/upload/7/settext/"
        #changed_val = "configuration_text={\"rules\": [ {\"switch\":1, \"priority\":123, \"cookie\":1234, \"table\":1, \"match\":{\"ip_proto\":6, \"eth_type\":2048}, \"actions\":[{\"fwd\":1}], \"instruction\":\"apply_actions\"} ]}"
        changed_val = "configuration_text={\"rules\": [ {\"switch\":1, \"priority\":234, \"cookie\":1235, \"table\":2, \"match\":{\"ip_proto\":6, \"eth_type\":2048, \"ipv4_src\":{\"value\":\"1.2.3.4\",\"mask\":\"255.255.255.255\"}}, \"actions\":{\"set\":{\"ipv4_src\":{\"value\":\"2.3.4.5\", \"mask\":\"255.255.255.255\"}}}, \"instruction\":\"apply_actions\"} ]}"

        # Run the shell script:
        subprocess.call(["bash", "./run_cmd.sh", url, post_url, filename, changed_val])


        output = subprocess.check_output(["bash", "./get_cmd.sh", url])
        print "Output of check output:"
        print output
        lines = output.split("\n")

        config = ""
        for line in lines:
            if "configuration_text" in line:
                #print "line        : " + line
                config = json.loads(line)

        # Best not to ask about this: It's due to weird formatting of what's returned by get_cmd.sh
        config = json.loads("{%s}" % config["configuration_text"][1:-1])
        replaced_val = changed_val.replace("\\\"", "\"").replace("configuration_text=", "")
        set_config = json.loads(replaced_val)

        #print "\n\n"
        #print "config     : " + str(config["rules"])
        #print "set_config : " + str(set_config["rules"])
        
        self.failUnlessEqual(config["rules"], set_config["rules"])
        
        
        


    def get_token(self, filename):
        cookies = open(filename, "r")
        for line in cookies:
            if "csrftoken" in line:
                return line.split()[-1]
        self.fail("No CSRF token")

    def test_1(self):
        self.run_test(1)




if __name__ == '__main__':
    unittest.main()

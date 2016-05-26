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

        # Parse test file
        with open("rctest.json") as data_file:
            data = json.load(data_file)
        cls.tests = data['tests']
    
    def run_test(self, testnum):
        if self.tests[testnum]['run_test'] == False:
            print "Skipping test %s" % testnum
            return

        filename = "cookies.txt"
        url = self.tests[testnum]['url']
        post_url = self.tests[testnum]['post_url']
        changed_val = self.tests[testnum]['changed_val']


        # Run the shell script:
        subprocess.call(["bash", "./run_cmd.sh", url, post_url, filename, changed_val])


        output = subprocess.check_output(["bash", "./get_cmd.sh", url])
        #print "Output of check output:"
        #print output
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
        sleep(.5)
        
        
        


    def get_token(self, filename):
        cookies = open(filename, "r")
        for line in cookies:
            if "csrftoken" in line:
                return line.split()[-1]
        self.fail("No CSRF token")

    def test_0(self):
        self.run_test(0)

    def test_1(self):
        self.run_test(1)




if __name__ == '__main__':
    unittest.main()

# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project

import unittest

from localctlr.LCRuleManager import *


class InitTest(unittest.TestCase):
    def test_singleton(self):
        firstManager = LCRuleManager.instance()
        secondManager = LCRuleManager.instance()

        print ">>>>>>>>>>>> %s" % (firstManager is secondManager)
        self.failUnless(firstManager is secondManager)

    def test_init_fields(self):
        m = LCRuleManager("lcrulemanagertest.db")
        # if this doesn't blow up, we should be good.
        #FIXME: how to verify the DB is good?

class AddRuleTest(unittest.TestCase):
    def test_good_add_rules(self):
        m = LCRuleManager()
        rule = "FAKE RULE"
        cookie = 1
        status = RULE_STATUS_INSTALLING
        m.add_rule(cookie, rule, status)
        # We'll test that we can get the rule in a bit.

    def test_add_bad_status(self):
        m = LCRuleManager()
        rule = "FAKE RULE"
        cookie = 1
        status = "NOT A REAL STATUS"
        self.failUnlessRaises(LCRuleManagerTypeError,
                              m.add_rule, cookie, rule, status)

    def test_duplicate_add(self):
        m = LCRuleManager()
        rule = "FAKE RULE"
        cookie = 1
        status = RULE_STATUS_INSTALLING
        m.add_rule(cookie, rule, status)

        self.failUnlessRaises(LCRuleManagerValidationError,
                              m.add_rule, cookie, rule, status)
    #FIXME: Should there be other check here?

    
class GetRuleTest(unittest.TestCase):
    def test_get_known_rule(self):
        # Add rule, then get it to confirm that it was correct.
        m = LCRuleManager()
        rule1 = "FAKE RULE"
        cookie1 = 1
        status1 = RULE_STATUS_INSTALLING
        m.add_rule(cookie1, rule1, status1)

        getrule = m.get_rule(cookie1)
        self.failUnlessEqual(rule1, getrule)

        rule2 = "TOTALLY REAL RULE"
        cookie2 = 2
        status2 = RULE_STATUS_INSTALLING
        m.add_rule(cookie2, rule2, status2)

        getrule = m.get_rule(cookie1)
        print ">>>>>>>>>", getrule
        self.failUnlessEqual(rule1, getrule)
        getrule = m.get_rule(cookie2)
        print ">>>>>>>>>", getrule
        self.failUnlessEqual(rule2, getrule)

    def test_get_unknown_rule(self):
        # Try to get a rule that doesn't exist, should return none
        m = LCRuleManager()
        rule1 = "FAKE RULE"
        cookie1 = 1
        status1 = RULE_STATUS_INSTALLING
        m.add_rule(cookie1, rule1, status1)


        rule2 = "TOTALLY REAL RULE"
        cookie2 = 2
        status2 = RULE_STATUS_INSTALLING
        # NOT ADDING THIS ONE!
        #m.add_rule(cookie2, rule2, status2)

        getrule = m.get_rule(cookie1)
        self.failUnlessEqual(rule1, getrule)
        getrule = m.get_rule(cookie2)
        self.failUnlessEqual(None, getrule)

    def test_get_rule_full_tuple(self):
        #FIXME
        pass
    

class FindRuleTest(unittest.TestCase):
    def test_find_all_empty_rules(self):
        # Immediately check for rules
        m = LCRuleManager()
        rules = m.find_rules()
        self.failUnlessEqual([], rules)

    def test_find_all_rules(self):
        m = LCRuleManager()
        rule1 = "FAKE RULE"
        cookie1 = 1
        status1 = RULE_STATUS_INSTALLING
        m.add_rule(cookie1, rule1, status1)

        rule2 = "TOTALLY REAL RULE"
        cookie2 = 2
        status2 = RULE_STATUS_INSTALLING
        m.add_rule(cookie2, rule2, status2)

        rules = m.find_rules()
        print ">>>> rules: %s" % rules
        self.failUnlessEqual(len(rules), 2)

    def test_find_filtered_cookie_rules(self):
        m = LCRuleManager()
        rule1 = "FAKE RULE"
        cookie1 = 1
        status1 = RULE_STATUS_INSTALLING
        m.add_rule(cookie1, rule1, status1)

        rule2 = "TOTALLY REAL RULE"
        cookie2 = 2
        status2 = RULE_STATUS_INSTALLING
        m.add_rule(cookie2, rule2, status2)

        rules = m.find_rules({'cookie':1})
        self.failUnlessEqual(len(rules), 1)

    def test_find_filtered_status_rules(self):
        m = LCRuleManager()
        rule1 = "FAKE RULE"
        cookie1 = 1
        status1 = RULE_STATUS_INSTALLING
        m.add_rule(cookie1, rule1, status1)

        rule2 = "TOTALLY REAL RULE"
        cookie2 = 2
        status2 = RULE_STATUS_ACTIVE
        m.add_rule(cookie2, rule2, status2)

        rules = m.find_rules({'status':RULE_STATUS_ACTIVE})
        self.failUnlessEqual(len(rules), 1)


    def test_find_filtered_rule_rules(self):
        #FIXME: This is impractical right now, so not going to test it.
        pass
    
    

class ChangeStatusTest(unittest.TestCase):
    def test_good_status_change(self):
        m = LCRuleManager()
        rule1 = "FAKE RULE"
        cookie1 = 1
        status1 = RULE_STATUS_INSTALLING
        m.add_rule(cookie1, rule1, status1)

        (pre_cookie, pre_rule, pre_status) = m.get_rule(cookie1, True)
        self.failUnlessEqual(pre_status, status1)

        status2 = RULE_STATUS_ACTIVE
        m.set_status(cookie1, status2)

        (post_cookie, post_rule, post_status) = m.get_rule(cookie1, True)
        self.failUnlessEqual(post_status, status2)
        self.failIfEqual(status1, status2)

    def test_invalid_status_change(self):
        m = LCRuleManager()
        rule1 = "FAKE RULE"
        cookie1 = 1
        status1 = RULE_STATUS_INSTALLING
        m.add_rule(cookie1, rule1, status1)

        (pre_cookie, pre_rule, pre_status) = m.get_rule(cookie1, True)
        self.failUnlessEqual(pre_status, status1)

        status2 = "FAKE STATUS!"
        self.failUnlessRaises(LCRuleManagerValidationError,
                              m.set_status, cookie1, status2)
    

class RemoveRuleTest(unittest.TestCase):
    def test_remove_known_rule(self):
        m = LCRuleManager()
        rule1 = "FAKE RULE"
        cookie1 = 1
        status1 = RULE_STATUS_INSTALLING
        m.add_rule(cookie1, rule1, status1)

        pre_rule = m.get_rule(cookie1)
        self.failUnlessEqual(pre_rule, rule1)

        m.rm_rule(cookie1)
        post_rule = m.get_rule(cookie1)
        self.failUnlessEqual(post_rule, None)
    
    def test_remove_unknown_rule(self):
        m = LCRuleManager()
        cookie1 = 1
        self.failUnlessRaises(LCRuleManagerDeletionError,
                              m.rm_rule, cookie1)

    def test_duplicate_remove_rule(self):
        m = LCRuleManager()
        rule1 = "FAKE RULE"
        cookie1 = 1
        status1 = RULE_STATUS_INSTALLING
        m.add_rule(cookie1, rule1, status1)

        pre_rule = m.get_rule(cookie1)
        self.failUnlessEqual(pre_rule, rule1)

        m.rm_rule(cookie1)
        post_rule = m.get_rule(cookie1)
        self.failUnlessEqual(post_rule, None)

        self.failUnlessRaises(LCRuleManagerDeletionError,
                              m.rm_rule, cookie1)
    
        


class InitialRulesTest(unittest.TestCase):
    def test_add_initial_rule(self):
        # Make sure it doesn't blow up
        m = LCRuleManager()
        cookie1 = 1
        rule1 = "FAKE RULE"
        m.add_initial_rule(rule1, cookie1)
    
    def test_add_initial_rule_in_db(self):
        # With empty DB, add initial rule, then call initial rules complete
        # Verify that rule was added
        m = LCRuleManager()
        cookie1 = 1
        rule1 = "FAKE RULE"
        status1 = RULE_STATUS_INSTALLING
        m.add_initial_rule(rule1, cookie1)

        (del_list, add_list) = m.initial_rules_complete()
        m.clear_initial_rules()
        for (r, c) in add_list:
            s = RULE_STATUS_INSTALLING
            m.add_rule(c, r, s)
        for (r, c) in del_list:
            m.rm_rule(c)

        self.failUnlessEqual(m.get_rule(1), rule1)

    def test_initial_rule_rm_rule(self):
        # Add two rules, add only one of them as an initial rule, call
        # initial rules complete, confirm that one still exists and the other is
        # removed.
        m = LCRuleManager()
        rule1 = "FAKE RULE"
        cookie1 = 1
        status1 = RULE_STATUS_INSTALLING
        m.add_rule(cookie1, rule1, status1)

        getrule = m.get_rule(cookie1)
        self.failUnlessEqual(rule1, getrule)

        rule2 = "TOTALLY REAL RULE"
        cookie2 = 2
        status2 = RULE_STATUS_INSTALLING
        m.add_rule(cookie2, rule2, status2)

        getrule = m.get_rule(cookie1)
        self.failUnlessEqual(rule1, getrule)
        getrule = m.get_rule(cookie2)
        self.failUnlessEqual(rule2, getrule)

        m.add_initial_rule(rule1, cookie1)
        
        (del_list, add_list) = m.initial_rules_complete()
        m.clear_initial_rules()
        for (r, c) in add_list:
            s = RULE_STATUS_INSTALLING
            m.add_rule(c, r, s)
        for (r, c) in del_list:
            m.rm_rule(c)


        getrule = m.get_rule(cookie1)
        self.failUnlessEqual(rule1, getrule)
        getrule = m.get_rule(cookie2)
        self.failUnlessEqual(None, getrule)
        

    def test_initial_rule_twice_rule(self):
        # Empty DB, add rule with initial_rules, remove same rule so DB's empty
        # again, add a different initial_rule, confirm that only the second
        # initial rule is added 
        m = LCRuleManager()
        rule1 = "FAKE RULE"
        cookie1 = 1
        status1 = RULE_STATUS_INSTALLING

        rule2 = "TOTALLY REAL RULE"
        cookie2 = 2
        status2 = RULE_STATUS_INSTALLING

        m.add_initial_rule(rule1, cookie1)

        (del_list, add_list) = m.initial_rules_complete()
        m.clear_initial_rules()
        for (r, c) in add_list:
            s = RULE_STATUS_INSTALLING
            m.add_rule(c, r, s)
        for (r, c) in del_list:
            m.rm_rule(c)


        rules = m.find_rules()
        self.failUnlessEqual(1, len(rules))
        getrule = m.get_rule(cookie1)
        self.failUnlessEqual(rule1, getrule)
        getrule = m.get_rule(cookie2)
        self.failUnlessEqual(None, getrule)

        m.rm_rule(cookie1)

        rules = m.find_rules()
        self.failUnlessEqual(0, len(rules)) #empty
        
        m.add_initial_rule(rule2, cookie2)

        (del_list, add_list) = m.initial_rules_complete()
        m.clear_initial_rules()
        for (r, c) in add_list:
            s = RULE_STATUS_INSTALLING
            m.add_rule(c, r, s)
        for (r, c) in del_list:
            m.rm_rule(c)

        rules = m.find_rules()
        print "((((((((RULES %s" %rules
        self.failUnlessEqual(1, len(rules))
        getrule = m.get_rule(cookie1)
        self.failUnlessEqual(None, getrule)
        getrule = m.get_rule(cookie2)
        self.failUnlessEqual(rule2, getrule)

if __name__ == '__main__':
    unittest.main()

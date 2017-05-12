tab="--tab"
foo=""

foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py -n sw1 -m ../demo/learneddestinationtest.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py -n sw2 -m ../demo/learneddestinationtest.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py -n sw3 -m ../demo/learneddestinationtest.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py -n sw4 -m ../demo/learneddestinationtest.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py -n sw5 -m ../demo/learneddestinationtest.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py -n sw6 -m ../demo/learneddestinationtest.manifest';bash")


gnome-terminal "${foo[@]}"

exit 0

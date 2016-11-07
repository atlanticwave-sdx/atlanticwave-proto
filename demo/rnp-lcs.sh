tab="--tab"
foo=""

#foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py ac ../demo/rnp-topo.manifest';bash")


foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py ac ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py al ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py ap ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py am ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py ba ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py ce ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py df ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py es ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py go ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py ma ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py mt ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py ms ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py mg ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py pa ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py pbj ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py pr ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py pe ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py pi ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py rj ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py rn ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py rs ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py ro ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py rr ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py sc ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py sp ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py se ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py to ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py pbc ../demo/rnp-topo.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py mia ../demo/rnp-topo.manifest';bash")
#echo "$foo"

gnome-terminal "${foo[@]}"

exit 0

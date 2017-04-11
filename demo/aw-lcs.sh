tab="--tab"
foo=""

#foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py ac ../demo/rnp-topo.manifest';bash")


foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py -n atl -m ../demo/aw-three-site.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py -n mia -m ../demo/aw-three-site.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py -n gru -m ../demo/aw-three-site.manifest';bash")
#echo "$foo"

gnome-terminal "${foo[@]}"

exit 0

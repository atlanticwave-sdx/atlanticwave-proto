tab="--tab"
foo=""

#foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py ac ../demo/rnp-topo.manifest';bash")


foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py atl ../demo/aw-three-site.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py mia ../demo/aw-three-site.manifest';bash")
foo+=($tab -e "bash -c 'cd ../localctlr; python LocalController.py gru ../demo/aw-three-site.manifest';bash")
#echo "$foo"

gnome-terminal "${foo[@]}"

exit 0

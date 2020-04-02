#!/bin/bash

echo "--- RENCI: Clean"
python delete-rate-limiting-switch-clean-renci.py
echo "--- DUKE: Clean"
python delete-rate-limiting-switch-clean-duke.py
echo "--- UNC: Clean"
python delete-rate-limiting-switch-clean-unc.py
echo "--- NCSU: Clean"
python delete-rate-limiting-switch-clean-ncsu.py
echo "--- RENCI-2: Clean"
python delete-rate-limiting-switch-clean-renci-2.py


echo "--- RENCI: Make"
python make-rate-limiting-switch-clean-renci.py
echo "--- DUKE: Make"
python make-rate-limiting-switch-clean-duke.py
echo "--- UNC: Make"
python make-rate-limiting-switch-clean-unc.py
echo "--- NCSU: Make"
python make-rate-limiting-switch-clean-ncsu.py
echo "--- RENCI-2: Make"
python make-rate-limiting-switch-clean-renci-2.py




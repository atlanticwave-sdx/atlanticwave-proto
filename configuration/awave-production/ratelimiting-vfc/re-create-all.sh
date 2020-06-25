#!/bin/bash

echo "--- MIAMI: Clean"
python delete-rate-limiting-switch-clean-miami.py
echo "--- SOX: Clean"
python delete-rate-limiting-switch-clean-sox.py

echo "--- MIAMI: Make"
python make-rate-limiting-switch-clean-miami.py
echo "--- SOX: Make"
python make-rate-limiting-switch-clean-sox.py




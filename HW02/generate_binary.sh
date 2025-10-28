#!/bin/bash
# Script to generate binary_2MB.bin file
# Creates a 2MB file filled with random binary data

dd if=/dev/urandom of=binary_2MB.bin bs=1M count=2
echo "File binary_2MB.bin created successfully!"

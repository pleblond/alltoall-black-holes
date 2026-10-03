#!/bin/bash
log="$1"; shift
echo "START $(date +%T) $*" >> "$log"
"$@" >> "$log" 2>&1
rc=$?
echo "END rc=$rc $(date +%T) $*" >> "$log"

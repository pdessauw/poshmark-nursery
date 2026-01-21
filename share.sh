#!/usr/bin/env bash
#
cd "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)" || exit 1
source .venv/bin/activate
python ./src/share.py -c $1 -d
echo "Job done!"


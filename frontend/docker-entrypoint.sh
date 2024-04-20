#!/usr/bin/env bash

set -e

export H2O_WAVE_ADDRESS="http://127.0.0.1:10101"

printf '\n$ ( cd %s && ./waved -listen ":%s" & )\n\n' "${WAVE_PATH}" "10101"
(cd "${WAVE_PATH}" && ./waved -listen ":10101" &)

sleep 10

printf '\n$ wave run --no-reload --no-autostart %s\n\n' "$PYTHON_MODULE"

exec wave run --no-reload --no-autostart "$PYTHON_MODULE"
#!/usr/bin/env bash
# Launch Grey Hat AI with proper virtualenv activation and Streamlit execution

VENV="${VENV:-$HOME/grey_hat_ai_venv}"

if [ ! -f "$VENV/bin/activate" ]; then
  echo "ERROR: Virtualenv not found at $VENV. Please run installation steps first."
  exit 1
fi

# shellcheck source=/dev/null
source "$VENV/bin/activate"

# Upgrade pip in the venv
pip install --upgrade pip

# Suppress webrtcvad pkg_resources deprecation warning
export PYTHONWARNINGS="ignore::UserWarning:webrtcvad"

# Ensure CAI is importable: add src/ to PYTHONPATH
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

# If no port is specified in args, default to 8501
EXTRA_ARGS=("$@")
if [[ ! " ${EXTRA_ARGS[*]} " =~ "--server.port" ]]; then
  EXTRA_ARGS+=(--server.port 8501)
fi

# Run Streamlit using the venv's binary, forwarding all args
"$VENV/bin/streamlit" run grey_hat_ai/app.py "${EXTRA_ARGS[@]}"

# Handle deactivate gracefully
if type deactivate &>/dev/null; then
  deactivate
fi
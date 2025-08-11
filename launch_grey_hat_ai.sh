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

ARGS=("$@")
# If no --server.port in args, add default
has_port=false
for a in "${ARGS[@]}"; do
  if [[ "$a" == --server.port ]]; then has_port=true; break; fi
done
if ! $has_port; then
  ARGS+=("--server.port" "8501")
fi
"$VENV/bin/streamlit" run grey_hat_ai/app.py "${ARGS[@]}"

# Handle deactivate gracefully
if type deactivate &>/dev/null; then
  deactivate
fi
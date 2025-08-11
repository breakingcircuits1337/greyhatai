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

ARGS=()
has_port=false
has_addr=false
i=0
while [ $i -lt $# ]; do
  arg="${@:$((i+1)):1}"
  if [[ "$arg" == "--port" ]]; then
    # Translate --port X to --server.port X
    next_arg="${@:$((i+2)):1}"
    ARGS+=("--server.port")
    if [[ -n "$next_arg" && ! "$next_arg" =~ ^-- ]]; then
      ARGS+=("$next_arg")
      i=$((i+1))
    fi
    has_port=true
  elif [[ "$arg" == "--server.port" ]]; then
    ARGS+=("$arg")
    next_arg="${@:$((i+2)):1}"
    if [[ -n "$next_arg" && ! "$next_arg" =~ ^-- ]]; then
      ARGS+=("$next_arg")
      i=$((i+1))
    fi
    has_port=true
  elif [[ "$arg" == "--address" ]]; then
    # Translate --address X to --server.address X
    next_arg="${@:$((i+2)):1}"
    ARGS+=("--server.address")
    if [[ -n "$next_arg" && ! "$next_arg" =~ ^-- ]]; then
      ARGS+=("$next_arg")
      i=$((i+1))
    fi
    has_addr=true
  elif [[ "$arg" == "--server.address" ]]; then
    ARGS+=("$arg")
    next_arg="${@:$((i+2)):1}"
    if [[ -n "$next_arg" && ! "$next_arg" =~ ^-- ]]; then
      ARGS+=("$next_arg")
      i=$((i+1))
    fi
    has_addr=true
  else
    ARGS+=("$arg")
  fi
  i=$((i+1))
done

if ! $has_port; then
  ARGS+=("--server.port" "8501")
fi
if ! $has_addr; then
  ARGS+=("--server.address" "0.0.0.0")
fi

"$VENV/bin/streamlit" run grey_hat_ai/app.py "${ARGS[@]}"

# Handle deactivate gracefully
if type deactivate &>/dev/null; then
  deactivate
fi
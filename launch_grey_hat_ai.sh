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

# Ensure CAI is importable: if src/cai does not exist, extract cai.zip
if [ ! -d "src/cai" ]; then
  echo "CAI package not found in src/cai. Attempting to extract cai.zip..."
  mkdir -p src
  if ! unzip -o cai.zip -d src/; then
    echo "ERROR: Failed to unzip cai.zip into src/. Please ensure cai.zip is present and valid."
    exit 1
  fi
fi

# Locate the actual cai package directory inside src/
candidate=$(find src -maxdepth 2 -type d -name cai | head -n 1)

if [ -n "$candidate" ]; then
  cai_parent=$(dirname "$candidate")
  echo "Detected CAI package at: $candidate"
  echo "Adding $cai_parent to PYTHONPATH"
  export PYTHONPATH="$(pwd)/src:$PWD/$cai_parent:$PYTHONPATH"
  # Optionally create symlink at src/cai for stability
  if [ "$candidate" != "src/cai" ] && [ ! -L "src/cai" ]; then
    ln -sf "$(realpath "$candidate")" src/cai
    echo "Created symlink: src/cai -> $candidate"
  fi
else
  if [ -f "cai.zip" ]; then
    echo "WARNING: CAI package directory not found after unzip. Falling back to importing from cai.zip."
    export PYTHONPATH="$(pwd)/src:$(pwd)/cai.zip:$PYTHONPATH"
  else
    echo "ERROR: CAI package not found and cai.zip missing. Cannot continue."
    exit 1
  fi
fi

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
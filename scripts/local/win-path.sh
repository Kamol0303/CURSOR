#!/usr/bin/env bash
# Windows Git Bash: Node, PostgreSQL, Python ni PATH dan tashqarida topish
# Boshqa skriptlar: source "$(dirname "$0")/win-path.sh"

_win_path_prepend() {
  local dir="$1"
  if [ -d "$dir" ]; then
  case ":$PATH:" in
    *":$dir:"*) ;;
    *) export PATH="$dir:$PATH" ;;
  esac
  fi
}

_win_path_glob_dirs() {
  local pattern="$1"
  local d
  for d in $pattern; do
    if [ -d "$d" ]; then
      echo "$d"
    fi
  done
}

setup_win_paths() {
  # Node.js (Windows installer)
  _win_path_prepend "/c/Program Files/nodejs"
  _win_path_prepend "/c/Program Files (x86)/nodejs"
  if [ -n "${LOCALAPPDATA:-}" ] && [ -d "$LOCALAPPDATA/Programs/nodejs" ]; then
    _win_path_prepend "$LOCALAPPDATA/Programs/nodejs"
  fi
  if [ -n "${APPDATA:-}" ] && [ -d "$APPDATA/npm" ]; then
    _win_path_prepend "$APPDATA/npm"
  fi

  # PostgreSQL
  local pg_dir
  for pg_dir in $(_win_path_glob_dirs "/c/Program Files/PostgreSQL/"*"/bin"); do
    _win_path_prepend "$pg_dir"
  done
  for pg_dir in $(_win_path_glob_dirs "/c/Program Files (x86)/PostgreSQL/"*"/bin"); do
    _win_path_prepend "$pg_dir"
  done

  # Python (Microsoft Store / py launcher odatda PATH da)
  _win_path_prepend "/c/Users/$USER/AppData/Local/Programs/Python/Python312"
  _win_path_prepend "/c/Users/$USER/AppData/Local/Programs/Python/Python312/Scripts"
  _win_path_prepend "/c/Users/$USER/AppData/Local/Programs/Python/Python313"
  _win_path_prepend "/c/Users/$USER/AppData/Local/Programs/Python/Python313/Scripts"
  _win_path_prepend "/c/Python312"
  _win_path_prepend "/c/Python312/Scripts"
}

resolve_python() {
  setup_win_paths
  local py
  for py in python python3 py; do
    if command -v "$py" >/dev/null 2>&1; then
      if $py -c "import sys; exit(0 if sys.version_info >= (3,12) else 1)" 2>/dev/null; then
        echo "$py"
        return 0
      fi
    fi
  done
  if command -v py >/dev/null 2>&1; then
    if py -3.12 -c "import sys; exit(0)" 2>/dev/null; then
      echo "py -3.12"
      return 0
    fi
    if py -3 -c "import sys; exit(0 if sys.version_info >= (3,12) else 1)" 2>/dev/null; then
      echo "py -3"
      return 0
    fi
  fi
  return 1
}

resolve_pip() {
  local py="$1"
  if command -v pip >/dev/null 2>&1; then
    echo "pip"
    return 0
  fi
  if command -v pip3 >/dev/null 2>&1; then
    echo "pip3"
    return 0
  fi
  echo "$py -m pip"
}

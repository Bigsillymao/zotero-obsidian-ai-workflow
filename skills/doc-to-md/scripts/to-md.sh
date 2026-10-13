#!/usr/bin/env bash
# to-md.sh -- convert a document to Markdown with MinerU.
#
# Tested on Windows Git Bash; also intended for Linux / macOS (bash 3.2+).
# Requires MinerU 4.x:   pip install "mineru[core]"
# Local tiers need the parse server running:   mineru server start   (once per boot)

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: to-md.sh <document> [options]

  -o, --out <path>   output markdown (default: <name>_md.md next to the source)
  -p, --pages <sel>  page selection for PDF inputs: 'all' | '1-5,8' | 'r3-r1'   (default: all)
  -t, --tier <tier>  flash | basic | standard | advanced   (default: flash)
  -r, --remote       parse via the mineru.net cloud service
  -h, --help         show this help

Non-PDF files (images, docx, pptx...) always parse the full document; MinerU
rejects --pages for them, so it is omitted automatically.

MinerU discovery: $MINERU_EXE -> mineru on PATH -> <python scripts dir>/mineru
EOF
}

IN=''; OUT=''; PAGES='all'; PAGES_SET=0; TIER='flash'; REMOTE=0
while [ $# -gt 0 ]; do
  case "$1" in
    -o|--out)    OUT="${2:?missing value for $1}"; shift 2 ;;
    -p|--pages)  PAGES="${2:?missing value for $1}"; PAGES_SET=1; shift 2 ;;
    -t|--tier)   TIER="${2:?missing value for $1}"; shift 2 ;;
    -r|--remote) REMOTE=1; shift ;;
    -h|--help)   usage; exit 0 ;;
    -*)          echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
    *)           IN="$1"; shift ;;
  esac
done

if [ -z "$IN" ]; then usage >&2; exit 2; fi
if [ ! -f "$IN" ]; then echo "input not found: $IN" >&2; exit 2; fi

: "${MINERU_MODEL_SOURCE:=modelscope}"
export MINERU_MODEL_SOURCE

MINERU_CMD=''
if [ -n "${MINERU_EXE:-}" ] && [ -x "${MINERU_EXE}" ]; then
  MINERU_CMD="$MINERU_EXE"
elif command -v mineru >/dev/null 2>&1; then
  MINERU_CMD="$(command -v mineru)"
else
  for py in python3 python; do
    if command -v "$py" >/dev/null 2>&1; then
      sc="$("$py" -c 'import sysconfig;print(sysconfig.get_path("scripts"))' 2>/dev/null || true)"
      if [ -n "$sc" ] && [ -x "$sc/mineru" ]; then MINERU_CMD="$sc/mineru"; break; fi
      if [ -n "$sc" ] && [ -x "$sc/mineru.exe" ]; then MINERU_CMD="$sc/mineru.exe"; break; fi
    fi
  done
fi
if [ -z "$MINERU_CMD" ]; then
  echo 'mineru not found. Install: pip install "mineru[core]"; or set MINERU_EXE.' >&2
  exit 3
fi

if [ -z "$OUT" ]; then
  d="$(dirname "$IN")"; f="${IN##*/}"; stem="${f%.*}"
  if [ "$stem" = "$f" ]; then OUT="$d/${f}_md.md"; else OUT="$d/${stem}_md.md"; fi
fi

IS_PDF=0
case "$(printf '%s' "${IN##*.}" | tr '[:upper:]' '[:lower:]')" in
  pdf) IS_PDF=1 ;;
esac

PAGES_SHOWN="$PAGES"
if [ "$PAGES_SET" = 0 ]; then
  if [ "$IS_PDF" = 1 ]; then PAGES_SHOWN='all (pdf default)'; else PAGES_SHOWN='n/a (non-PDF: full document)'; fi
fi

echo "[to-md] input  : $IN"
echo "[to-md] output : $OUT"
echo "[to-md] pages  : $PAGES_SHOWN | tier: $TIER | models: $MINERU_MODEL_SOURCE"

# --pages is PDF-only in MinerU; passing it for other file types fails the parse.
PAGES_FLAG=()
if [ "$PAGES_SET" = 1 ]; then
  PAGES_FLAG=(--pages "$PAGES")
elif [ "$IS_PDF" = 1 ]; then
  PAGES_FLAG=(--pages all)
fi
REMOTE_FLAG=()
if [ "$REMOTE" = 1 ]; then REMOTE_FLAG=(--remote); fi

status=0
"$MINERU_CMD" parse "$IN" ${PAGES_FLAG[@]+"${PAGES_FLAG[@]}"} --tier "$TIER" --wait 600 -o "$OUT" ${REMOTE_FLAG[@]+"${REMOTE_FLAG[@]}"} || status=$?

if [ "$status" -ne 0 ]; then
  echo "[to-md] mineru failed (exit $status). hints:" >&2
  echo "  - local tiers need the parse server:  mineru server start" >&2
  echo '  - install: pip install "mineru[core]"' >&2
  echo '  - if the error mentions xethub.hf.co (401): set model.source to modelscope in ~/.mineru/config.yaml, then restart the server' >&2
  exit "$status"
fi

if [ -f "$OUT" ]; then
  echo "[to-md] MD: $OUT"
else
  echo '[to-md] warning: output file was not created' >&2
  exit 2
fi

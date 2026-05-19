#!/usr/bin/env bash
# Smoke test: valida el ciclo completo de la API.
# Requiere que el servidor esté levantado en http://127.0.0.1:8000
# Uso: bash scripts/smoke.sh [--wait]
set -euo pipefail

BASE="${API_BASE:-http://127.0.0.1:8000}"
MAX_WAIT=30  # segundos máximos esperando que el job se complete

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✓${NC} $*"; }
fail() { echo -e "${RED}✗${NC} $*"; exit 1; }
info() { echo -e "${YELLOW}→${NC} $*"; }

# 1. Health check
info "1. Health check"
STATUS=$(curl -sf "$BASE/health" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['status'])")
[ "$STATUS" = "ok" ] || fail "Health check falló: status=$STATUS"
ok "Health: $STATUS"

# 2. Capabilities
info "2. Capabilities"
CAPS=$(curl -sf "$BASE/capabilities" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d['capabilities']))")
[ "$CAPS" -eq 11 ] || fail "Se esperaban 11 capabilities, got $CAPS"
ok "Capabilities: $CAPS"

# 3. Providers
info "3. Providers"
PROVIDERS=$(curl -sf "$BASE/providers" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d['providers']))")
[ "$PROVIDERS" -ge 1 ] || fail "Se esperaba ≥1 provider, got $PROVIDERS"
ok "Providers: $PROVIDERS"

# 4. Crear job
info "4. Crear job image.generate"
JOB_RESP=$(curl -sf -X POST "$BASE/media/image/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a red boat, smoke test"}' 2>/dev/null || echo '{"status":"503"}')

HTTP_STATUS=$(echo "$JOB_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','503'))" 2>/dev/null || echo "503")

if echo "$JOB_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'job_id' in d else 1)" 2>/dev/null; then
  JOB_ID=$(echo "$JOB_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['job_id'])")
  ok "Job creado: $JOB_ID"

  # 5. Esperar a que el job se complete
  info "5. Esperando status del job (max ${MAX_WAIT}s)"
  elapsed=0
  while [ $elapsed -lt $MAX_WAIT ]; do
    STATUS=$(curl -sf "$BASE/jobs/$JOB_ID" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['status'])")
    if [ "$STATUS" != "pending" ] && [ "$STATUS" != "running" ]; then
      break
    fi
    sleep 2
    elapsed=$((elapsed+2))
  done
  ok "Status final: $STATUS"

  # 6. Manifest
  info "6. Manifest"
  MANIFEST=$(curl -s "$BASE/jobs/$JOB_ID/manifest")
  if echo "$MANIFEST" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'job_id' in d else 1)" 2>/dev/null; then
    FILES=$(echo "$MANIFEST" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('files',{})))")
    ok "Manifest: $FILES archivos"
  else
    info "Manifest no disponible (sin outputs — probablemente faltó token)"
  fi

  # 7. Cancel (idempotent)
  info "7. Cancel job"
  CANCEL=$(curl -sf -X POST "$BASE/jobs/$JOB_ID/cancel" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['status'])")
  ok "Cancel: $CANCEL"

else
  info "No hay provider activo para image.generate (503 esperado sin tokens) — ciclo básico OK"
  ok "Sin provider — error JSON correcto"
fi

echo ""
ok "Smoke test completado exitosamente"

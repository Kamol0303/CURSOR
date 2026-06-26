#!/usr/bin/env bash
# End-to-end MFA login test (uses server-side TOTP secret — for staging debug)
set -euo pipefail

HOST="${PUBLIC_HOST:-tamor.staging.local}"
USER="${1:-admin.tmb}"
PASS="${2:-Tmb#2026Admin!}"
COMPOSE="docker compose -f docker-compose.staging.yml --env-file .env.staging"

echo "=== 1) Login (expect requires_mfa) ==="
LOGIN=$(curl -sSk -X POST "https://${HOST}/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${USER}\",\"password\":\"${PASS}\"}")
echo "$LOGIN" | head -c 300
echo ""

MFA_TOKEN=$(echo "$LOGIN" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('mfa_token',''))" 2>/dev/null || true)
if [ -z "$MFA_TOKEN" ]; then
  echo "FAIL: no mfa_token — check username/password or use admin.aspect (no MFA)"
  exit 1
fi

echo ""
echo "=== 2) Current TOTP from database ==="
CODE=$($COMPOSE exec -T backend python -c "
import asyncio, pyotp, sys
sys.path.insert(0, '.')
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from app.core.security import decrypt_totp_secret
from app.models.identity import User

async def main():
    engine = create_async_engine(settings.DATABASE_URL)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        user = (await session.execute(select(User).where(User.username == '${USER}'))).scalar_one()
        secret = decrypt_totp_secret(user.mfa_secret_encrypted)
        print(pyotp.TOTP(secret).now())
    await engine.dispose()

asyncio.run(main())
")
echo "Server kod: $CODE"
echo "Google Authenticator shu kodni ko'rsatishi kerak. Farq bo'lsa — QR ni qayta skanerlang."

echo ""
echo "=== 3) MFA verify ==="
VERIFY=$(curl -sSk -w "\nHTTP:%{http_code}" -X POST "https://${HOST}/api/v1/auth/mfa/verify" \
  -H "Content-Type: application/json" \
  -d "{\"mfa_token\":\"${MFA_TOKEN}\",\"code\":\"${CODE}\"}")
echo "$VERIFY"

if echo "$VERIFY" | grep -q access_token; then
  echo ""
  echo "OK: MFA login works on server."
else
  echo ""
  echo "FAIL: MFA verify failed. Run: ./scripts/show-mfa-qr.sh ${USER}"
  exit 1
fi

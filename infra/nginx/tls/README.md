# TLS certificates for nginx (not committed)

Place mkcert output here:

- `fullchain.pem`
- `privkey.pem`

Generate:

```bash
./infra/nginx/generate-mkcert.sh
```

Fallback (browser warning):

```bash
./infra/nginx/generate-dev-certs.sh
```

# Project Management MVP

## Run in Docker

```bash
./scripts/start-mac.sh
```

Open http://127.0.0.1:8000 and sign in with `user` / `password`.

## Run frontend locally

```bash
cd frontend
npm install
export NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
npm run dev
```

Open http://127.0.0.1:3000.

## Tests

```bash
cd frontend
npm run test:unit
npm run test:e2e
```

AI e2e requires `OPENROUTER_API_KEY` from the project root:

```bash
cd ..
set -a && source .env && set +a
cd frontend
npm run test:e2e
```

## Notes

See frontend details in frontend/README.md.

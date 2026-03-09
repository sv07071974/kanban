# Kanban Studio

## Run

```bash
npm install
npm run dev
```

If you run the backend in Docker on port 8000, set the API base URL before
starting the dev server:

```bash
export NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

To run the full app in Docker:

```bash
../scripts/start-mac.sh
```

## Tests

```bash
npm run test:unit
npm run test:e2e
```

The AI e2e test requires OPENROUTER_API_KEY. Load it from the project root:

```bash
cd ..
set -a && source .env && set +a
cd frontend
npm run test:e2e
```

# LearnPath-AI

## Development

Install dependencies with either package manager:

```bash
npm install
```

or:

```bash
pnpm install
```

Start the frontend from the project root:

```bash
npm run dev
```

The development server listens on port `8084`.

For production, configure `VITE_BACKEND_WS_URL` when the backend is on a separate host;
the root Compose deployment exposes the backend on port `8086` and the frontend on port `8084`.

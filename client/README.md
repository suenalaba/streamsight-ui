This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

1. Obtain environment variables by running:
```bash
cp .env.example .env.local
```

2. obtain the supabase anon key and update the environment variables.

3. Install dependencies using:
```bash
npm install
# or
yarn install
```

4. Run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

5. Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Testing

# End-To-End Tests
1. To run the end-to-end tests.
```bash
npx playwright test
```
2. To show report
```bash
npx playwright show-report
```

3. Run tests in interactive UI mode.
```bash
  npx playwright test --ui
```
    
4. Runs the tests only on Desktop Chrome.
```bash
npx playwright test --project=chromium
```

5. Runs tests in only specific files.
```bash
npx playwright test example
```

6. Runs the tests in debug mode.
```bash
npx playwright test --debug
```

7. Auto generate tests with Codegen.
```bash
npx playwright codegen
```

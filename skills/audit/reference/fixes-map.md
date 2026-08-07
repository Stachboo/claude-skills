# Fix target map (where to apply header/security fixes)
| Finding | Vercel | Netlify | Astro | Next | Generic |
|---|---|---|---|---|---|
| Missing CSP/HSTS/headers | `vercel.json` `headers[]` | `netlify.toml` `[[headers]]` | `public/_headers` | `next.config.js` `headers()` | `public/_headers` |
| Dep CVE | `pnpm up <pkg>` / `npm i <pkg>@<fixed>` | same | same | same | upgrade lockfile |
| Exposed secret | rotate immediately + `git filter-repo` history | same | same | same | rotate + purge |
| Cert expiry | renew via host/ACME | — | — | — | renew |
| Accessibility (contrast/alt/labels) | fix in the component/template | — | — | — | fix markup |

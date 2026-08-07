<!-- Documents the sections renderReport() emits, in order. Not a runtime template. -->
# Audit — {{name|url}}
1. Header (url, localPath, timestamp, tool versions, field/lab legend)
2. Overall badge + per-dimension sub-scores line
3. Performance — Core Web Vitals table (mobile/desktop × field/lab)
4. Accessibility — failed audits
5. SEO — failed audits
6. Best-Practices — failed audits
7. Security — headers table + TLS block
8. Security (code) — deps table + secrets table
9. Top fixes (LLM-advice, injected separately)
10. Fleet table (only in --all aggregate)

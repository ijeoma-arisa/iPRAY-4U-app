## Testing RLS
Before applying RLS changes to production:

1. Load the staging environment variables.
2. Run: 

```bash
python scripts/verify_rls.py
```

The script signs into the staging Supabase project using two test accounts and verifies the RLS policies.

## Staging/Production Rate Limits
Render staging and production services must set `RATELIMIT_STORAGE_URI` to a
shared Redis/Valkey Flask-Limiter backend, such as `redis://...` or `rediss://...`.
`memory://` is only for local development and tests.

Set `APP_ENV` to `staging` or `production` in deployed environments. Leave it
unset for local development.

The app enables Werkzeug `ProxyFix` for one trusted Render proxy hop in deployed
environments, which lets Flask and Flask-Limiter use the real client IP from
`X-Forwarded-For`. If the proxy topology changes, set `TRUSTED_PROXY_COUNT` to
the exact number of trusted proxy hops.

## Testing RLS
Before applying RLS changes to production:

1. Load the staging environment variables.
2. Run: 

```bash
python scripts/test_rls.py
```

The script signs into the staging Supabase project using two test accounts and verifies the RLS policies.
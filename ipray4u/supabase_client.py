import os
from supabase import create_client

_supabase = None

def get_supabase():
    global _supabase
    
    if _supabase is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_PUBLISHABLE_KEY"]
        
        _supabase = create_client(url, key)
        
    return _supabase
from supabase import create_client

url = "https://gaxngnkvfquwfbshzkcd.supabase.co"
key = "sb_publishable_5zpZhDEILKL-9GIcLlc78Q_dNGIJ1PK"

def main():
    try:
        print("Testing Supabase client...")
        client = create_client(url, key)
        # Try a simple select
        result = client.table("conversations").select("*").limit(1).execute()
        print(f"✅ Supabase connection successful! Data: {result.data}")
    except Exception as e:
        print(f"❌ Supabase test failed: {e}")

if __name__ == "__main__":
    main()

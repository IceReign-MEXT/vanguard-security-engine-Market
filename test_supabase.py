import asyncio
import asyncpg

# YOUR NEW PASSWORD IS IN THIS LINK
DATABASE_URL = "postgresql://postgres.ylpxxgvaetykmswzrpmi:IceGodsMaster2026@aws-1-eu-west-3.pooler.supabase.com:6543/postgres?sslmode=require"

async def run_test():
    print("🔄 Connecting to Supabase Vault (Paris Server)...")
    try:
        # statement_cache_size=0 is required for Supabase Pooler
        conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
        
        print("✅ CONNECTION SUCCESSFUL!")
        
        # Test 1: Ping the database version
        version = await conn.fetchval("SELECT version();")
        print(f"🖥️ Server Info: {version[:35]}...")
        
        # Test 2: See what tables exist
        tables = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        table_list = [t['table_name'] for t in tables]
        
        print(f"📂 Found {len(table_list)} Tables:")
        for t in table_list:
            print(f"   - {t}")
            
        await conn.close()
        print("\n🚀 STATUS: 100% READY FOR RENDER DEPLOYMENT.")

    except Exception as e:
        print(f"\n❌ CONNECTION FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())

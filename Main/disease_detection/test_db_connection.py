import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disease_detection.settings')
django.setup()

from django.db import connection
from django.core.management.color import no_style
from django.db import transaction

def test_connection():
    try:
        print("🔄 Testing connection to Supabase Transaction Pooler...")
        
        # Test basic connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            print(f"✅ Successfully connected to PostgreSQL via Transaction Pooler!")
            print(f"📊 Database version: {db_version[0]}")
            
        # Test connection info
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database(), current_user, inet_server_addr(), inet_server_port();")
            db_info = cursor.fetchone()
            print(f"📊 Database: {db_info[0]}")
            print(f"👤 User: {db_info[1]}")
            print(f"🌐 Server IP: {db_info[2]}")
            print(f"🔌 Server Port: {db_info[3]}")
            
        # Test if we can create tables
        print("🔄 Testing table creation permissions...")
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id SERIAL PRIMARY KEY,
                    test_field VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert a test record
            cursor.execute("INSERT INTO test_connection (test_field) VALUES (%s);", ["pooler_test"])
            
            # Query the test record
            cursor.execute("SELECT * FROM test_connection WHERE test_field = %s;", ["pooler_test"])
            test_record = cursor.fetchone()
            print(f"✅ Table operations working! Test record: {test_record}")
            
            # Clean up
            cursor.execute("DROP TABLE test_connection;")
            print("✅ Table creation/deletion permissions working!")
            
        # Test Django ORM
        print("🔄 Testing Django ORM...")
        try:
            from django.contrib.auth.models import Permission
            permissions_count = Permission.objects.count()
            print(f"✅ Django ORM working! Found {permissions_count} permissions in database.")
        except Exception as orm_error:
            print(f"⚠️ ORM test failed (migrations may be needed): {orm_error}")
            
        # Test transaction support
        print("🔄 Testing transaction support...")
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                result = cursor.fetchone()
                print(f"✅ Transaction support working! Result: {result[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print(f"🔍 Error details: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("🔄 Testing Supabase PostgreSQL connection via Transaction Pooler...")
    print("🌐 Host: aws-0-eu-north-1.pooler.supabase.com:6543")
    print("=" * 60)
    
    if test_connection():
        print("\n🎉 All database tests passed! Ready for deployment.")
    else:
        print("\n💥 Database connection failed. Please check your configuration.")
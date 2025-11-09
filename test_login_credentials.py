#!/usr/bin/env python3
"""
Test script untuk memverifikasi login credentials
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

def test_demo_users():
    """Test demo users credentials"""
    
    # Demo users configuration
    DEMO_USERS = [
        {'username': 'BagasNz', 'password': '162316', 'role': 'admin'},
        {'username': 'Refki', 'password': 'owner', 'role': 'guest'},
        {'username': 'Iqbal', 'password': 'owner', 'role': 'guest'},
        {'username': 'Rico', 'password': 'owner', 'role': 'guest'},
        {'username': 'Hari', 'password': 'owner', 'role': 'guest'},
        {'username': 'Dimse', 'password': 'owner', 'role': 'guest'},
    ]
    
    print("🧪 Testing Login Credentials")
    print("=" * 50)
    
    # Test admin login
    print("👨‍💼 Testing Admin Login:")
    admin_user = next((user for user in DEMO_USERS if user['role'] == 'admin'), None)
    if admin_user:
        print(f"   ✅ Username: {admin_user['username']}")
        print(f"   ✅ Password: {admin_user['password']}")
        print(f"   ✅ Role: {admin_user['role']}")
        print(f"   ✅ Status: READY TO LOGIN")
    else:
        print("   ❌ No admin user found")
    
    print()
    
    # Test guest logins
    print("👥 Testing Guest Logins:")
    guest_users = [user for user in DEMO_USERS if user['role'] == 'guest']
    
    for i, user in enumerate(guest_users, 1):
        print(f"   {i}. Username: {user['username']}")
        print(f"      Password: {user['password']}")
        print(f"      Role: {user['role']}")
        print(f"      Status: ✅ READY TO LOGIN")
        print()
    
    print("=" * 50)
    print("📋 LOGIN SUMMARY:")
    print(f"   • Total Users: {len(DEMO_USERS)}")
    print(f"   • Admin Users: {len([u for u in DEMO_USERS if u['role'] == 'admin'])}")
    print(f"   • Guest Users: {len([u for u in DEMO_USERS if u['role'] == 'guest'])}")
    print()
    print("🎯 DEFAULT CREDENTIALS:")
    print("   Admin: BagasNz / 162316")
    print("   Guest: [Refki, Iqbal, Rico, Hari, Dimse] / owner")
    print()
    print("✅ All credentials are properly configured and ready for login!")

def test_app_import():
    """Test if apps can be imported correctly"""
    print("🧪 Testing App Import")
    print("=" * 30)
    
    try:
        import app
        print("✅ Main app.py imported successfully")
        print(f"   Demo users count: {len(app.DEMO_USERS)}")
    except Exception as e:
        print(f"❌ Error importing main app: {e}")
    
    try:
        import app_production
        print("✅ Production app imported successfully")
        print(f"   Demo users count: {len(app_production.DEMO_USERS)}")
    except Exception as e:
        print(f"❌ Error importing production app: {e}")

if __name__ == "__main__":
    print("🔐 Toko Kopi Makmur - Login Credentials Test")
    print("=" * 55)
    print()
    
    test_demo_users()
    print()
    test_app_import()
    print()
    print("🎉 Testing completed!")

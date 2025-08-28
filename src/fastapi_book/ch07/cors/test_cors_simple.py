"""
Simple CORS Testing Script
Run this after starting your FastAPI server: uvicorn main:app --reload
"""

import requests
import json

def test_cors_simple():
    """Simple CORS tests using only requests library"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Testing CORS functionality...")
    print("=" * 50)
    
    # Test 1: Valid origin from localhost:3000
    print("\n1️⃣  Testing VALID origin (localhost:3000)")
    try:
        response = requests.get(
            base_url + "/",
            headers={"Origin": "http://localhost:3000"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        cors_header = response.headers.get('access-control-allow-origin')
        print(f"   ✅ CORS Header: {cors_header}")
        
        if cors_header == "http://localhost:3000":
            print("   ✅ CORS working correctly for valid origin!")
        else:
            print("   ❌ CORS not working as expected")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Invalid origin
    print("\n2️⃣  Testing INVALID origin (evil-site.com)")
    try:
        response = requests.get(
            base_url + "/",
            headers={"Origin": "http://evil-site.com"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        cors_header = response.headers.get('access-control-allow-origin')
        
        if cors_header is None:
            print("   ✅ Good! No CORS header for invalid origin")
        else:
            print(f"   ⚠️  CORS Header present: {cors_header}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Preflight request (OPTIONS)
    print("\n3️⃣  Testing PREFLIGHT request (OPTIONS)")
    try:
        response = requests.options(
            base_url + "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        print(f"   Status: {response.status_code}")
        print(f"   Allow-Origin: {response.headers.get('access-control-allow-origin')}")
        print(f"   Allow-Methods: {response.headers.get('access-control-allow-methods')}")
        print(f"   Allow-Headers: {response.headers.get('access-control-allow-headers')}")
        print(f"   Allow-Credentials: {response.headers.get('access-control-allow-credentials')}")
        
        if response.status_code == 200:
            print("   ✅ Preflight request handled correctly!")
        else:
            print("   ❌ Preflight request failed")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Request with credentials
    print("\n4️⃣  Testing request WITH credentials")
    try:
        response = requests.get(
            base_url + "/",
            headers={
                "Origin": "http://localhost:3000",
                "Cookie": "session=test123"
            }
        )
        print(f"   Status: {response.status_code}")
        credentials = response.headers.get('access-control-allow-credentials')
        print(f"   Allow-Credentials: {credentials}")
        
        if credentials == "true":
            print("   ✅ Credentials are allowed!")
        else:
            print("   ❌ Credentials not allowed")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_cors_browser_simulation():
    """Simulate browser CORS behavior"""
    
    print("\n" + "=" * 50)
    print("🌐 Simulating Browser CORS Behavior")
    print("=" * 50)
    
    # Simulate a browser making a cross-origin request
    print("\n📍 Simulating browser from http://localhost:3000 making API call")
    
    try:
        # First, browser would make a preflight request for certain HTTP methods
        preflight = requests.options(
            "http://localhost:8000/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "content-type"
            }
        )
        
        print(f"   Preflight Status: {preflight.status_code}")
        
        if preflight.status_code == 200:
            # If preflight passes, browser makes the actual request
            actual_request = requests.get(
                "http://localhost:8000/",
                headers={"Origin": "http://localhost:3000"}
            )
            
            print(f"   Actual Request Status: {actual_request.status_code}")
            print(f"   Response: {actual_request.json()}")
            print("   ✅ Browser would allow this request!")
        else:
            print("   ❌ Browser would block this request!")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 CORS Testing Tool")
    print("Make sure your FastAPI server is running:")
    print("   uvicorn main:app --reload")
    print()
    
    try:
        test_cors_simple()
        test_cors_browser_simulation()
        
        print("\n" + "=" * 50)
        print("📝 Testing Complete!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to http://localhost:8000")
        print("   Make sure your FastAPI server is running:")
        print("   uvicorn main:app --reload")

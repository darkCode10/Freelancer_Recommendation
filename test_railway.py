import requests
import json

# Replace with your Railway URL
RAILWAY_URL = "https://your-app.up.railway.app"  # ⚠️ UPDATE THIS!

print("=" * 60)
print("Testing Railway Deployment")
print("=" * 60)

# Test 1: Health check
print("\n1. Testing health endpoint...")
try:
    response = requests.get(f"{RAILWAY_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Home endpoint
print("\n2. Testing home endpoint...")
try:
    response = requests.get(f"{RAILWAY_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Recommendations
print("\n3. Testing recommendations...")
try:
    payload = {
        "skills": ["Python", "Django", "React"],
        "top_n": 3
    }
    response = requests.post(f"{RAILWAY_URL}/recommend", json=payload)
    print(f"Status: {response.status_code}")
    
    data = response.json()
    if data.get("success"):
        print(f"✅ Success! Found {data['total']} recommendations")
        for i, rec in enumerate(data['recommendations'], 1):
            print(f"\n{i}. {rec['name']}")
            print(f"   Match: {rec['match']:.1f}%")
            print(f"   Rating: {rec['rating']:.1f} stars")
            print(f"   Experience: {rec['experience']} years")
            print(f"   Projects: {rec['completed_projects']}")
            print(f"   Skills: {rec['skills']}")
    else:
        print(f"❌ Error: {data}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)


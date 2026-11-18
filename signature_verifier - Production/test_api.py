import os
import cv2
import numpy as np
import requests

BASE_URL = "http://127.0.0.1:5000"

def create_dummy_signature_image(filename):
    """Generates a synthetic white image with black handwritten-like strokes for testing."""
    img = np.ones((155, 220, 3), dtype=np.uint8) * 255
    # Draw random geometric shapes/lines acting as a signature stroke
    cv2.putText(img, "SignTest", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
    cv2.line(img, (20, 120), (200, 120), (0, 0, 0), 2)
    cv2.imwrite(filename, img)
    return filename

def run_tests():
    print("==================================================")
    print("🚀 Starting Automated API & Multi-Sample Test Suite")
    print("==================================================")

    # 1. Generate dummy sample signature image files for testing
    print("\n[1/4] Generating temporary test signature image files...")
    sig_file_1 = create_dummy_signature_image("sample_1.png")
    sig_file_2 = create_dummy_signature_image("sample_2.png")
    test_query_file = create_dummy_signature_image("test_query.png")

    try:
        # 2. Test Multi-Sample Registration Endpoint (/register) via HTML Form POST simulation
        print("\n[2/4] Testing Multi-Sample User Registration (`/register`)...")
        reg_url = f"{BASE_URL}/register"
        
        # Prepare form fields and multiple files under the key 'signatures'
        payload = {
            "name": "Alan Turing",
            "email": "alan.turing@ai-secure.org"
        }
        
        files_to_upload = [
            ('signatures', ('sample_1.png', open(sig_file_1, 'rb'), 'image/png')),
            ('signatures', ('sample_2.png', open(sig_file_2, 'rb'), 'image/png'))
        ]

        response = requests.post(reg_url, data=payload, files=files_to_upload, allow_redirects=True)
        
        # Close file handles safely
        for _, (_, f_obj, _) in files_to_upload:
            f_obj.close()

        if response.status_code == 200:
            print("✅ Registration request sent successfully!")
        else:
            print(f"⚠️ Registration responded with status code: {response.status_code}")

        # 3. Test API Versioned Endpoint: Get Users List (`/api/v1/users`)
        print("\n[3/4] Fetching users list from Versioned REST API (`/api/v1/users`)...")
        users_api_url = f"{BASE_URL}/api/v1/users"
        api_res = requests.get(users_api_url)
        
        if api_res.status_code == 200:
            data = api_res.json()
            print(f"✅ API Success! Found {data.get('count')} registered user(s).")
            users_list = data.get("users", [])
            
            # Extract the newly registered user ID
            target_user = next((u for u in users_list if u['email'] == "alan.turing@ai-secure.org"), None)
            
            if target_user:
                user_id = target_user['id']
                print(f"   Target User Identified -> ID: {user_id}, Name: {target_user['name']}, Samples Enrolled: {target_user['sample_count']}")
                
                # 4. Test Versioned API Signature Verification Endpoint (`/api/v1/verify`)
                print(f"\n[4/4] Testing REST API Verification Endpoint (`/api/v1/verify`) for User ID {user_id}...")
                verify_api_url = f"{BASE_URL}/api/v1/verify"
                
                verify_payload = {
                    "user_id": str(user_id)
                }
                verify_file = {
                    "signature": ('test_query.png', open(test_query_file, 'rb'), 'image/png')
                }

                verify_res = requests.post(verify_api_url, data=verify_payload, files=verify_file)
                verify_file['signature'][1].close()

                if verify_res.status_code == 200:
                    result_data = verify_res.json()
                    print("✅ Verification API Response Received Successfully:")
                    print(f"   - User Name : {result_data.get('user_name')}")
                    print(f"   - Is Genuine: {result_data.get('is_genuine')}")
                    print(f"   - Similarity: {result_data.get('similarity_percentage')}%")
                    print(f"   - Threshold Met: {result_data.get('threshold_met')}")
                else:
                    print(f"❌ Verification API Failed: {verify_res.text}")
            else:
                print("❌ Error: Could not locate the newly registered test user in the API payload response.")
        else:
            print(f"❌ Failed to query users API: {api_res.status_code}")

    finally:
        # Cleanup temporary files created for testing
        for filename in [sig_file_1, sig_file_2, test_query_file]:
            if os.path.exists(filename):
                os.remove(filename)
        print("\n🧹 Temporary test files cleaned up successfully.")
        print("==================================================")

if __name__ == "__main__":
    run_tests()
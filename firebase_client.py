import keys
import json
try:
    import urequests as requests
except ImportError:
    try:
        import requests
    except ImportError:
        print("❌ Neither urequests nor requests module found")
        print("Please install urequests for MicroPython")
        requests = None


class FirebaseClient:
    def __init__(self):
        self.base_url = keys.FIREBASE_URL.rstrip('/')
        self.secret = keys.FIREBASE_SECRET

    def _build_url(self, path):
        """Build complete Firebase URL"""
        url = f"{self.base_url}/{path}.json"
        if self.secret:
            url += f"?auth={self.secret}"
        return url

    def _make_request(self, method, url, data=None):
        """Make HTTP request to Firebase"""
        if requests is None:
            return False, "Requests module not available"

        try:
            headers = {'Content-Type': 'application/json'}

            if method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'GET':
                response = requests.get(url, headers=headers)
            else:
                return False, f"Unsupported method: {method}"

            # Check response
            if response.status_code in [200, 201]:
                return True, "Success"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:100]}"

        except Exception as e:
            return False, f"Request error: {e}"
        finally:
            if 'response' in locals():
                response.close()

    def push(self, path, data):
        """Push data to Firebase (creates new entry with auto-generated key)"""
        url = self._build_url(path)
        return self._make_request('POST', url, data)

    def set(self, path, data):
        """Set data at specific path in Firebase"""
        url = self._build_url(path)
        return self._make_request('PUT', url, data)

    def get(self, path):
        """Get data from Firebase path"""
        url = self._build_url(path)
        return self._make_request('GET', url)


def test_firebase_connection():
    """Test Firebase connection"""
    print("🔥 Testing Firebase connection...")

    firebase = FirebaseClient()

    # Import time for timestamp
    from time import time

    test_data = {
        "test": True,
        "timestamp": time(),
        "message": "Connection test from weather station"
    }

    success, message = firebase.push("test", test_data)

    if success:
        print("✅ Firebase connection successful!")
        return True
    else:
        print(f"❌ Firebase connection failed: {message}")
        return False


if __name__ == "__main__":
    # Test the connection
    test_firebase_connection()

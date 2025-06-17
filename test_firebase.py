"""
Simple test script to verify Firebase connection
Run this before running the main weather station
"""

from firebase_client import test_firebase_connection
import keys


def main():
    print("🔥 Firebase Connection Test")
    print("="*40)
    print(f"Firebase URL: {keys.FIREBASE_URL}")
    print("="*40)

    if test_firebase_connection():
        print("\n✅ Your Firebase setup is working!")
        print("🚀 You can now run weather_station.py")
    else:
        print("\n❌ Firebase connection failed")
        print("Please check:")
        print("1. Your internet connection")
        print("2. Firebase URL in keys.py")
        print("3. Firebase database rules (should allow public access for now)")


if __name__ == "__main__":
    main()

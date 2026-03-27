import firebase_admin
from firebase_admin import credentials, firestore
import os

# Path to your Firebase service account JSON key file
# Download this from Firebase Console > Project Settings > Service Accounts
SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT", "serviceAccountKey.json")

def initialize_firebase():
    """Initialize Firebase Admin SDK. Call once at app startup."""
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)
    return firestore.client()

# Global Firestore client
db = initialize_firebase()

# Collection names
DONORS_COLLECTION      = "donors"
REQUESTS_COLLECTION    = "blood_requests"
HISTORY_COLLECTION     = "donation_history"
ADMINS_COLLECTION      = "admins"

import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

def initialize_firebase():
    """Initialize Firebase Admin SDK"""

    if not firebase_admin._apps:
        firebase_key = os.environ.get("FIREBASE_KEY")

        if not firebase_key:
            raise ValueError("FIREBASE_KEY not set in environment variables")

        cred = credentials.Certificate(json.loads(firebase_key))
        firebase_admin.initialize_app(cred)

    return firestore.client()


# Global Firestore client
db = initialize_firebase()

# Collection names
DONORS_COLLECTION = "donors"
REQUESTS_COLLECTION = "blood_requests"
HISTORY_COLLECTION = "donation_history"
ADMINS_COLLECTION = "admins"
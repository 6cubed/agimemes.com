import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from cachetools import cached

cred = credentials.Certificate('./gae_app/serviceaccount.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

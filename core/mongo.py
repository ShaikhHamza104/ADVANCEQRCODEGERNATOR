from pymongo import MongoClient
from django.conf import settings

class MongoConnection:
    _client = None
    _db = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            try:
                cls._client = MongoClient(
                    settings.MONGO_URI,
                    serverSelectionTimeoutMS=5000,  # 5 second timeout
                    connectTimeoutMS=5000
                )
                # Test connection
                cls._client.admin.command('ping')
            except Exception as e:
                if settings.DEBUG:
                    print(f"Warning: MongoDB connection failed: {e}")
                    print("Using in-memory storage fallback (DEBUG only)")
                    cls._client = None
                else:
                    print(f"CRITICAL: MongoDB connection failed: {e}")
                    raise e
        return cls._client

    @classmethod
    def get_db(cls):
        if cls._db is None:
            client = cls.get_client()
            if client:
                # Parse database name from URI or use default
                try:
                    db_name = settings.MONGO_URI.split('/')[-1].split('?')[0] or 'ktvs'
                except:
                    db_name = 'ktvs'
                cls._db = client[db_name]
            else:
                if settings.DEBUG:
                    # Return a mock db object for fallback
                    cls._db = MockDB()
                else:
                     raise Exception("Database connection failed in production")
        return cls._db

class MockDB:
    """Fallback in-memory storage when MongoDB is not available"""
    def __init__(self):
        self._profiles = []
        self._logs = []
    
    @property
    def totp_profiles(self):
        return MockCollection(self._profiles)
    
    @property
    def audit_logs(self):
        return MockCollection(self._logs)

class MockCollection:
    """Mock MongoDB collection for in-memory storage"""
    def __init__(self, storage):
        self._storage = storage
        self._id_counter = 1
    
    def insert_one(self, data):
        from bson import ObjectId
        data['_id'] = ObjectId()
        self._storage.append(data.copy())
        return type('Result', (), {'inserted_id': data['_id']})()
    
    def find_one(self, query):
        for doc in self._storage:
            if self._matches(doc, query):
                return doc.copy()
        return None
    
    def find(self, query=None):
        if query is None:
            return MockCursor(self._storage)
        results = [doc for doc in self._storage if self._matches(doc, query)]
        return MockCursor(results)
    
    def update_one(self, query, update):
        for i, doc in enumerate(self._storage):
            if self._matches(doc, query):
                if '$set' in update:
                    doc.update(update['$set'])
                if '$push' in update:
                    for key, value in update['$push'].items():
                        if key not in doc:
                            doc[key] = []
                        doc[key].append(value)
                self._storage[i] = doc
                return
    
    def delete_many(self, query):
        self._storage.clear()
    
    def count_documents(self, query):
        if query == {}:
            return len(self._storage)
        return len([doc for doc in self._storage if self._matches(doc, query)])
    
    def _matches(self, doc, query):
        for key, value in query.items():
            if key not in doc or doc[key] != value:
                return False
        return True

class MockCursor:
    """Mock MongoDB cursor"""
    def __init__(self, data):
        self._data = data
        self._limit = None
    
    def limit(self, count):
        self._limit = count
        return self
    
    def sort(self, key, direction=-1):
        return self
    
    def __iter__(self):
        data = self._data[:self._limit] if self._limit else self._data
        return iter([doc.copy() for doc in data])

db = MongoConnection.get_db()

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from main import app, Base, get_db, get_engine_and_session

# Set TESTING=True Before Importing Anything Else
os.environ["TESTING"] = "True"

# Create a New Engine and Session for Testing
test_engine, TestingSessionLocal = get_engine_and_session()

# Create Tables for Testing
Base.metadata.create_all(bind=test_engine)

# Override the get_db Dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Test Client Setup
@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client

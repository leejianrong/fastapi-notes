import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session, text

from app.main import app
from app.db.deps import get_session

from app.db.models import Note  # Make sure this import is here

test_engine = create_engine("sqlite://", connect_args={"check_same_thread": False})

@pytest.fixture(autouse=True)
def setup_db():
    print(f"🔍 Available tables in metadata: {list(SQLModel.metadata.tables.keys())}")
    print(f"🔍 Note model table name: {Note.__tablename__ if hasattr(Note, '__tablename__') else 'No __tablename__'}")
    
    SQLModel.metadata.create_all(test_engine)
    
    # Verify tables were actually created
    with Session(test_engine) as session:
        result = session.exec(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in result]
        print(f"🔍 Tables actually created in test DB: {tables}")
    
    yield
    SQLModel.metadata.drop_all(test_engine)

def get_test_session():
    print("Test session is being used!")
    with Session(test_engine) as s:
        yield s

# Override the app's DB dependency for tests
app.dependency_overrides[get_session] = get_test_session

client = TestClient(app)

def test_create_and_get_note():
    r = client.post("/notes", json={"title": "First", "content": "Hello"})
    assert r.status_code == 201, r.text
    created = r.json()
    assert created["id"] >= 1
    assert created["title"] == "First"
    assert "created_at" in created and "updated_at" in created

    note_id = created["id"]
    r2 = client.get(f"/notes/{note_id}")
    assert r2.status_code == 200
    got = r2.json()
    assert got["title"] == "First"
    assert got["content"] == "Hello"

def test_list_pagination():
    for i in range(1, 6):
        client.post("/notes", json={"title": f"t{i}", "content": "x"})
    r = client.get("/notes?limit=2&offset=0")
    assert r.status_code == 200
    assert len(r.json()) == 2

    r2 = client.get("/notes?limit=2&offset=2")
    assert len(r2.json()) == 2

def test_patch_update_and_delete():
    r = client.post("/notes", json={"title": "Old", "content": "Old body"})
    nid = r.json()["id"]

    r2 = client.patch(f"/notes/{nid}", json={"content": "New body"})
    assert r2.status_code == 200
    assert r2.json()["content"] == "New body"

    r3 = client.delete(f"/notes/{nid}")
    assert r3.status_code == 204

    r4 = client.get(f"/notes/{nid}")
    assert r4.status_code == 404

import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, SQLModel, Session, select
from sqlmodel.pool import StaticPool
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from database.crud import lesson_add, create_show, lesson_show
from database.database import get_session
from database.models import Plan
from main import app


@pytest.fixture(name='session')
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

@pytest.fixture(name='client')
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield  client
    app.dependency_overrides.clear()
async def add_lesson_for_test(session: Session):
    lesson1 = Plan(day="Понедельник", start_time="10:00", names="Вася")
    lesson2 = Plan(day="Понедельник", start_time="12:00", names="Марк")
    lesson3 = Plan(day="Вторник", start_time="10:00", names="петя")
    await lesson_add(session, lesson1)
    await lesson_add(session, lesson2)
    await lesson_add(session, lesson3)

def test_add_lesson_ok (client: TestClient):
    response = client.post(
        "/schedule/api/add_lesson",
        json={"day": "понедельник", "start_time": "10:00", "names": "Марк", "duration": "1"})
    data = response.json()
    assert response.status_code == 200
    assert data['lesson'] == 'success'

@pytest.mark.asyncio
async def test_update_lesson_ok(session:Session, client: TestClient):
    await add_lesson_for_test(session)
    response_put = client.put(
         "/update-lesson",
        json={"times":{'2': '17:00-18:20', '1': '15:00-16:00'}, "days":{'1': 'Вторник', '3': 'Понедельник'}}
    )
    # Проверяем, что расписание изменено
    les = select(Plan).where(Plan.day == "Понедельник")
    result = session.exec(les).all()
    assert result[0].start_time == '17:00'
    assert result[1].start_time == '10:00'
    les_th = select(Plan).where(Plan.day == "Вторник")
    result = session.exec(les_th).all()
    assert result[0].start_time == '15:00'


def test_add_lesson_inwalid(client:TestClient):
    response = client.post(
        "/schedule/api/add_lesson",
        json={"start_time": "10:00", "names": "Марк", "duration": "1"})
    data = response.json()
    assert response.status_code == 400
#
# def test_get_lesson(session:Session, client: TestClient):
#     add_lesson_for_test(session)
#     response_get = client.get("/schedule/", params={"day":"Понедельник" })
#     data = response_get.json()
#     assert response_get.status_code == 200
#     assert data[0]["day"] == "Понедельник"
#
#
# def test_delete_lesson(session: Session, client: TestClient):
#     add_lesson_for_test(session)
#     response_delete = client.delete("/schedule/delete", params={"name":"Вася", "day":"Понедельник"})
#     assert response_delete.status_code == 200
#     data = response_delete.json()
#     assert data['lesson'] == 'delete success'
#     # Проверяем, что урок был удалён
#     les = select(Plan).where(Plan.day == "Понедельник")
#     result = session.exec(les).all()
#     assert len(result) == 1
#
# def test_delete_lesson_invalid(session: Session, client: TestClient):
#     add_lesson_for_test(session)
#     response_delete = client.delete("/schedule/delete", params={"name":"Петя", "day":"понедельник"})
#     assert response_delete.status_code == 200
#     data = response_delete.json()
#     assert data['lesson'] == 'error name or day'
#
# def test_show(session: Session, client:TestClient):
#     add_lesson_for_test(session)
#     response_show = client.get("/schedule/show")
#     data = response_show.json()
#     assert response_show.status_code == 200
#     assert len(data) == 5
#
# def test_show_http(session: Session):
#     add_lesson_for_test(session)
#     data = create_show(session)
#     assert len(data["Понедельник"]) == 2


import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Depends, Response, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from requests import Session
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse

from accessory import TITLE_SHOW
from database.crud import lesson_add, request_lesson, lesson_delete, lesson_show, create_show, lesson_edit
from database.database import create_db_and_tables, get_session
from database.models import Plan, EditTimeDay, DeleteLessonRequest
from pydantic import BaseModel
from typing import List, Dict

logger_error = logging.getLogger("log_error")
logger_debug = logging.getLogger("log_debug")
templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger_debug.debug("test")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

# добавление урока через API
@app.post("/schedule/api/add_lesson", response_model=dict)
async def add_lesson(plan: Plan, session: Session = Depends(get_session)) -> dict:
    les = await lesson_add(session=session, lesson=plan)
    if les:
        return {"lesson": "success"}
    logger_error.exception("Error adding lesson")
    raise HTTPException(status_code=400, detail="Error adding lesson")

@app.delete("/schedule/api/delete", response_model=dict)
async def delete_lesson(request: DeleteLessonRequest, session: Session = Depends(get_session)) -> dict:
    del_result = lesson_delete(session, request.name, request.day)
    if del_result == "error":
        raise HTTPException(status_code=400, detail="Error: name or day not found")
    return {"lesson": "delete success"}

# посмотреть уроки через API
@app.get("/schedule/api", response_model = dict)
async def show (*, session: Session = Depends(get_session))-> dict:
    return create_show(session)

# посмотреть уроки через HTTP
@app.get("/", response_class=HTMLResponse)
async def show(request: Request, session: Session=Depends(get_session)):
    lessons_of_week = create_show(session)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": TITLE_SHOW, "lessons": {"lesson":lessons_of_week}})

# добавить урок через HTTP
@app.post("/schedule/add", response_class=HTMLResponse)
async def show_add(request: Request, session: Session = Depends(get_session)):
    lessons_of_week = create_show(session)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": TITLE_SHOW, "lessons": {"lesson": lessons_of_week}}
    )

@app.put("/update-lesson", response_model=dict)
async def update_lesson(*, session: Session = Depends(get_session), order_data: EditTimeDay, response: Response) -> dict:
    edit_lesson: Plan | None = lesson_edit(session=session, order_data=order_data)
    if edit_lesson:
        return {"lesson": "success"}
    logger_error.exception("Error updating lesson")
    raise HTTPException(status_code=400, detail="Error updating lesson")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger_error.exception("Unhandled exception occurred")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

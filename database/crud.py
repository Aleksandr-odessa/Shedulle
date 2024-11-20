import logging
from datetime import timedelta, datetime

from sqlalchemy import Sequence
from sqlmodel import select, Session
from typing import Optional, List, Dict

from .models import PlanBase, Plan, EditTimeDay
from accessory import list_days

logger_debug = logging.getLogger('log_debug')


async def lesson_add(session:Session, lesson:PlanBase) -> Optional:
    time_start: datetime = datetime.strptime(lesson.start_time, '%H:%M')
    if lesson.duration is None:
        lesson.duration = "1"
    time_finish: datetime = time_start + timedelta(hours=float(lesson.duration))
    lesson.finish_time = str(time_finish.time())[:5]
    try:
        les: Plan = Plan.model_validate(lesson)
        logger_debug.debug("write to db sucess")
    except ValueError:
        return None
    session.add(les)
    session.commit()
    session.refresh(les)
    return les

def request_lesson(session:Session, day:str)-> List:
    les = select(Plan).where(Plan.day == day)
    return session.exec(les).all()

def lesson_delete (session:Session, name:str, day:str)-> Optional:
    les = select(Plan).where(Plan.names == name).where(Plan.day == day)
    less = session.exec(les).first()
    if less is None:
        return "error"
    session.delete(less)
    session.commit()
#
def lesson_show(session: Session)-> Sequence[Plan]:
    # less = select(Plan)
    result = session.exec(select(Plan)).all()
    return result

def create_show(session: Session)-> dict:
    mon, tues, wed, thu, fri = [], [], [], [], []
    lessons = lesson_show(session)
    for les in lessons:
        sample_output: list = [les.day, les.start_time, les.finish_time, les.names, les.id]
        match les.day:
            case "Понедельник":
                mon.append(sample_output)
            case "Вторник":
                tues.append(sample_output)
            case "Среда":
                wed.append(sample_output)
            case "Четверг":
                thu.append(sample_output)
            case "Пятница":
                fri.append(sample_output)
    day_for_dict: list = [mon, tues, wed, thu, fri]
    lessons_of_week = {day: day_for_dict[num] for num, day in enumerate(list_days)}
    return lessons_of_week

def lesson_edit(session:Session, order_data:EditTimeDay) -> Optional:
    day = order_data.days
    time = order_data.times
    lesson_to_save:list =[]
    if day:
        lesson_ids = list(day.keys())
        try:
            lessons = session.exec(select(Plan).where(Plan.id.in_(lesson_ids))).all()
            logger_debug.debug("Request to db, days is sucess")
        except ValueError:
            return None
        for les in lessons:
            str_id = str(les.id)
            if str_id in lesson_ids:
                les.day = day[str_id]
                lesson_to_save.append(les)
    if time:
        lesson_ids = list(time.keys())
        try:
            lessons = session.exec(select(Plan).where(Plan.id.in_(lesson_ids))).all()
            logger_debug.debug("Request to db, times is sucess")
        except ValueError:
            return None
        for les in lessons:
            str_id = str(les.id)
            if str_id in lesson_ids:
                times:list = time[str_id].split("-")
                les.start_time = times[0]
                les.finish_time = times[1]
                lesson_to_save.append(les)
    session.bulk_save_objects(lesson_to_save)
    session.commit()
    return True
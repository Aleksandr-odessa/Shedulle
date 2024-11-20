from datetime import datetime, timedelta

TITLE_SHOW = "Расписание"
TITLE_ADD_LESSON = "Добавить занятие"

list_days: tuple = ("Понедельник", "Вторник", "Среда", "Четверг", "Пятница")
times = [(datetime.strptime('09.00', '%H.%M')+timedelta(minutes=minutes)).strftime('%H.%M')
             for minutes in range(0, 660, 30) if minutes not in (270,300,330,360,390,)]
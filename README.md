TimeToDoBot - Время делать! Mirea Version TelegramBot
===================
#### 👋 __Привет, это любительский университетский телеграм-бот для студентов: Расписание+ToDo+новости_из_группы_вк__
# Проект заброшен :( Появился Notion, да и приоритеты изменились.
![](4.png)
![](task_preview.gif)
### Функционал💻
- __Дает расписание пар/экзаменов выбранной группы в хорошем виде.__ *а не убивать время на поиски расписания на сайте и долго и нудно листать excel таблицу.* 
- __Рассылка уведомления о паре за 10 минут до начала.__ *(Можно выключить)*
- __Проверка нового расписания и уведомление о изменениях.__
- __Свой список задач и заметок.__ 
На каждый предмет пользователь может создать задачи. Это может быть ДЗ, Напоминание подготовится к контрольной и т.д. и указать срок выполнения.
> __Как по мне, это круто и мне этого не хватало.__
## В планах 💡
- [ ] 🔍 __Поиск преподавателя__ 
Возможность искать преподавателя и выдавать его расписание пар.
- [ ] 📰 __Сводка дня__ 
Пользователю каждое утро/вечером будет приходить отчет какие пары буду, какие задачи/напоминания необходимо сделать. Погода и что лучше одеть. И кратко последние новости университета с гиперссылками(С возможность выбора источника - Новости с официального сайта/группы вк/группы студенческого союза и т.д)
- [ ] 🗜 __Автообновление кода и Docker__
- [ ] 🎉 __Релиз в следующем семестре__

## 🤔Я могу скачать и использовать для своего университета? 
Побочной целью я поставил себе сделать бота масштабируемым и модульным. То есть любой программист может скачать себе и настроить бота для своего университета. Необходимо будет только соблюдать структуру и наследование, а также настроить парсинг расписания с сайта или xlsx.
## ⚙ Что под копотом?
- __Python ~~3.5~~ 3.9__
- __aiogram__ - библиотека с работой Telegram
- __pandas__ - для расшифровки xlsx расписания университета
- __Yandex_API__ - для погоды и главных новостей *(для будущей сводки дня)*
- __BeatifulSoup__ - парсинг университетского сайта и других
- __SQLAlchemy__ - мощная библиотека для работы с базой данных
Я использую базу данных __PostgreSQL__. Однако после множество экспериментов с разными библиотеками, я выбрал наиболее мощную библиотеку __SQLAlchemy__, благодаря которой можно подключить абсолютно любую базу данных и будет работать без конфликтов ООП и других нюансов. 

__Проект open-source, делал для себя и попрактиковать свои навыки 


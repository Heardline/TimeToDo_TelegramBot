TimeToDoBot - Время делать! RTU Mirea Version #telegrambot
===================
👋 __Привет, это любительский университетский телеграм-бот для студентов: Расписание+ToDo+новости_из_группы_вк
*Тут должны быть скриншоты позже*
### Функционал💻
- __Выдача расписания пар/экзаменов выбранной группы в хорошем виде.__ *а не убивать время на поиски расписания на сайте и долго и нудно листать excel таблицу.* 
- __Рассылка уведомления о паре за 10 минут до начала.__ *(Можно выключить)*
- __Автоматическое обновления и уведомление о изменениях в расписание.
- __Свой список задач и заметок.__ 
На каждый предмет пользователь может создать задачи. Это может быть ДЗ, Напоминание подготовится к контрольной и т.д. и указать срок выполнения.
> __Как по мне, это круто и мне этого не хватало.__
## В планах 💡
- [] __Сводка дня.__ *(Пока что идея,которая реальна,но над которой надо много времени посидеть и довести до ума)*
Пользователю каждое утро/вечером будет приходить отчет какие пары буду, какие задачи/напоминания необходимо сделать. Погода и что лучше одеть. И кратко последние новости университета с гиперссылками(С возможность выбора источника - Новости с официального сайта/группы вк/группы студенческого союза и т.д)
- [] __Автообновление кода и Docker__
- [] __Релиз в следующем семестре__

## 😮Я из Мирэа, можно ссылочку на бота?
Пока лето, не вижу смысла его размещать. В следующем семестре как кстати до пилю и запущу.
## 🤔Я могу скачать и использовать для своего университета? 
Побочной целью я поставил себе сделать бота масштабируемым и модульным. То есть любой программист может скачать себе код и настроить бота для своего университета. Необходимо будет только соблюдать структуру и наследование, а также настроить парсинг расписания с сайта или xlsx. *документация и доведение до ума этой концепции будет на финальной стадии*
## ⚙ Что под копотом?
- __Python ~~3.5~~ 3.9
- __aiogram__ - библиотека с работой Telegram
- __pandas__ - для расшифровки xlsx расписания университета
- __Yandex_API__ - для погоды и главных новостей *(для будущей сводки дня)*
- __BeatifulSoup__ - парсинг университетского сайта и других
- __SQLAlchemy__ - мощная библиотека для работы с базой данных
Я использоваю базу данных __PostreSQL__. Однако после множество экспериментов с разными библиотеками, я выбрал наиболее мощную библиотеку __SQLAlchemy__, благодаря которой можно подключить абсолютно любую базу данных и будет работать без конфликтов ООП и другие нюансов. 
## Структура базы данных
├── student
│   ├── telegram_id
│   │           └── task
│   ├── group*        ├── name
│   └── notify        ├── lesson
│                     ├── student_id*
│                     ├── desc
│                     └── day
└── lesson 
    ├── id
    ├── name
    ├── group
    │     └── group
    └── ...    ├── name
               └── univer
## Структура файлов
*Лень делать, в следующем коммите допилю*
## Я нашел баг 😲 / 😎Я хочу добавить свой код /🤯 У МЕНЯ ЕСТЬ ИДЕЯ!
📣Все это кидать в раздел Issues. Если хотите привнести свой вклад, смело скачивайте репозиторий, ковыряйте код, пишите, что можно было улучшить, готовый код тоже рассмотрю как будет время.
Идеи пока сохраняю, но если будет ПРЯМ ОГОНЬ, то сделаю."

__Проект open-source, делал для себя и попрактиковать свои навыки и в итог развил идею до этого. Пилю его в свободное время и когда есть мотивация.__  


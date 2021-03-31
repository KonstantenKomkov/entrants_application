Подача документов на поступление в Российский Государственный Аграрный Университет - МСХА им. К.А. Тимирязева
========================
О проекте
-------------------------
Основная цель проета расширить и автоматизировать способы взаимодействия с абитуриентами. Чем проще, понятнее и быстрее абитуриенту заполнить форму, тем лучше впечатления у него складываются об университете.  
Взаимодействие с абитуриентом на протяжении всего поступления должно полностью отражать статус абитуриента, поэтому, замечу, что данный проект использовался в связке с:
- личным кабинетом абитуриента;
- списками на поступление;
- помощником выбора направления подготовки в рамках сданных ЕГЭ;
- электронная очередь для подачи документов лично.

Зачем этот проект?
-------------------------
Один из моих первых проектов. Изначально был реализован на Python 2.7, передавался через протокол http и был развёрнут на веб-сервере IIS 8 в MS Windows Server 2012. Впоследствии проект был переведён на Python 3.7 передаётся через протокол https и развёрнут на веб-сервере IIS 10 в MS Windows Server 2019.  
Проект выложен для ознакомительных целей. Развёртывание данного проекта маловероятно, по следующим причинам: потребуются соответствующие БД;
файл конфигурации db.py (можно взять из репозитория web2py) и его последующая настройка. При разработке особое внимание уделялось серверной части: соответствие PEP8, оптимизации количества SQL запросов и их кешированию.  
Моя работа над проетом закончилась 7 августа 2020 года, в связи с переходом на другую работу.

Структура проекта
-------------------------
Проект  использует концепцию MVC. Где файл tables.py представляет собой модель. Папка views содержит файлы представлений. Папка controllers содержит контроллеры. Контроллеры bak.py, mag.py, asp.py описывают формы подачи документов на бакалавриат, в магистратуру и аспирантуру соответственно. Общий код из этих контроллеров вынесен в модуль bak_and_mak.py в папке modules. За подтверждение почты отвечает контроллер validationEmail.py.

Где посмотреть?
-------------------------
[Google][1]


[1]: http://google.com/        "Google"
[Подача документов на поступление]:https://oas.timacad.ru/application
[Личный кабинет абитуриента]:https://oas.timacad.ru/webabit
[Личный кабинет студента]:https://oas.timacad.ru/stud
[Списки на поступление]:https://oas.timacad.ru/forabit
[Электронная очередь]:https://oas.timacad.ru/queue

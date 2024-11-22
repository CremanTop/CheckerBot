# CheckerBot — Телеграмм-бот для игры в шашки
Целью данной курсовой работы является разработка телеграмм-бота для игры в шашки.  

## Команда проекта:
- Бикбулатов Тимур 4215
- Андреев Богдан 4215

## Правила игры в шашки:
Цель игры — "съесть" все шашки противника или заблокировать его так, чтобы он не мог сделать ход.

Размер игрового поля — 8x8 клеток (всего 64 клетки).

Правила перемещения и захвата шашек:
- Игроки ходят по очереди.
- Шашки могут двигаться только по диагонали вперед на одну клетку.
- Если одна из шашек игрока стоит рядом с шашкой противника, а за ней есть свободная клетка, игрок обязан "съесть" шашку противника, перескочив через нее на пустую клетку.
- Если в одном ходе возможно несколько захватов (через несколько шашек), игрок обязан выполнить все доступные захваты.
- Когда шашка достигнет последнего ряда поля (на стороне противника), она превращается в дамку.
- Дамка может двигаться по диагонали вперед или назад на несколько клеток за один ход.
  
Возможные исходы игры:
- Игрок побеждает, съев все шашки противника.
- Игрок побеждает, не оставив противнику ходов.
- Игрок досрочно проигрывает при нажатии на кнопку "сдаться".
- Игроки соглашаются на ничью, нажав соответствующую кнопку.


## Стек технологий:
1.  Язык программирования:
    * **Python** — основной язык для разработки бота. Python используется благодаря своей простоте и широким возможностям для работы с различными библиотеками и фреймворками.
      
2.  Библиотека для работы с Telegram API:
    * **aiogram** — это мощный и гибкий фреймворк для создания телеграмм‑ботов на Python. С его помощью мы можем быстро и легко реализовать сложные сценарии взаимодействия, предоставляя пользователям интуитивно понятный интерфейс.
      
3.  Работа с БД:
    * **SQLAlchemy** — библиотека для работы с базой данных, которая позволяет взаимодействовать с реляционными базами данных через объектно-ориентированную модель. Используется для удобной работы с данными и их хранением.
   
## To-do list
- [x] Поддержка одновременного подключения множества игроков (2 человека) для совместной игры
- [x] Режим одиночной игры с ботом
- [x] Система достижений
- [x] Система получения и выбора скинов за достижения
- [x] Реализация базы данных на SQLAlchemy
- [ ] ...

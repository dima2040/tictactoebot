# tictactoebot

Бот для игры в крестики-нолики.

## Установка и настройка

Создайте и активируйте окружение
```sh
python3 -m venv .venv
source .venv/bin/activate
```

Укажите нужную переменную окружения
```sh
export TTT_API_TOKEN=***
```

Запустите бота
```sh
python tictactoebot.py
```

## TODO

- [x] Реализовать бота для одного игрока
- [x] Добавить возможность играть с разных устройств с ботом
- [x] Добавить рандомный ИИ для игры
- [x] Реализовать игровой поле в виде последовательных ответов в чате
- [x] Реализовать оттображение игрового поля в виде кнопок клавиатуры
- [x] Добавить выбор между ноликом и крестиком перед началом игры
- [x] Добавить сохранение счёта побед
- [x] Добавить возможность начать игру заново после окончания
- [x] Добавить подсчет ничейных результатов
- [ ] Сделать игровое поле не в виде ответа на команду /start
- [ ] Перенести информацию о победах в сообщение о конце игры
- [ ] Добавить minimax алгоритм для расчета хода бота

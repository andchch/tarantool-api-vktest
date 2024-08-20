# API Tarantool

## Описание

Этот проект представляет собой API для работы с базой данных Tarantool, 
обеспечивая базовую аутентификацию с использованием JWT токенов. 
API поддерживает операции записи и чтения данных, а также включает в себя проверку пользователей.

## Инструкция по запуску

### Требования

- Python 3.10+
- Docker и Docker compose

### Инструкция по запуску

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/andchch/tarantool-api-vktest.git
   cd tarantool-api-vktest
   ```
2. Запустите API и базу данных
   ```bash
   docker compose up -d
   ```
3. API будет доступен по адресу:
```
http://localhost:8000/api
```
4. Автоматическая документация доступна по адресу:
```
http://localhost:8000/docs
```

## Документация API

Существующий пользователь: 
```
username: admin
password: presale
```
Существующее пространство в базе данных: `space`

### Авторизация

### POST `/api/login`

Создает JWT токен для авторизации.

### Параметры
* `username` - имя пользователя
* `password` - пароль

### Запрос
   ```
      /api/login?username=admin&password=presale
   ```

### Ответ:
   ```json
      {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyNDE4MzkzMn0.Hg8k-9geSDakA9IY50yMrKQOqrjO8qgcgjv9H-fkRvM"
      }
   ```

### Ошибки:
* `401 Unauthorized`: Неверное имя пользователя или пароль.

### Запись данных

### POST `/api/write`

Записывает пары ключ-значение в указанное пространство базы данных.

### Заголовки
* `Authorization: Bearer <token>`

### Параметры
* `space` - пространство в базе данных

### Запрос
   ```
      /api/write?space=data
   
   {
      "1": "test1",
      "2": "test2"
   }
   ```

### Ответы:
200 Успех
   ```json
      {
        "status": "success"
      }
   ```
200 Частичный успех (некоторые ключи уже существуют)
   ```json
   {
      "status": "partial success",
      "info": "key(s) already exists",
      "duplicated keys": {
        "1": "Key already exists"
      },
      "success": {
        "3": "successfully written"
      }
    }
   ```
### Ошибки
* `400 Bad Request`: Дублирование ключей в запросе.
* `400 Bad Request`: Указанного пространства не существует.
* Не удается подключиться к базе данных.


### Чтение данных

### POST `/api/read`

Возвращает значения по указанным ключам из базы данных.

### Заголовки
* `Authorization: Bearer <token>`

### Параметры
* `space` - пространство в базе данных

### Запрос
   ```
      /api/read?space=data
   
   {
      "keys": [1, 2]
   }
   ```

### Ответы:
200 Успех
   ```json
      {
        "status": "success",
        "data": {
           "1": "test1",
           "2": "test2"
        }
      }
   ```
200 Частичный успех (некоторые ключи не найдены)
   ```json
   {
      "status": "partial success",
      "info": "missing keys are in request",
      "missing keys": {
         "20": "No such key in database"
      },
      "data": {
         "1": "test1"
      }
}
   ```
### Ошибки
* `400 Bad Request`: Указанного пространства не существует.
* Некорректный запрос. Допустимы только положительные числа в качестве ключей
* Не удается подключиться к базе данных.
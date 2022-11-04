# TESTAPI: ТЕСТОВОЕ E-COMMERCE API

Simple e-commerce api written with Python3 and Sanic.


## Стек
Python 3.10, Sanic, Tortoise ORM, Sanic-jwt. DB: postgres.

## Модель данных
Пользователь – репрезентация пользователей в приложении. В приложении определены две пользовательские роли: администратор и пользователь.
Товар – cостоит из заголовка, описания и цены.
Счёт – имеет идентификатор счёта и баланс. Привязан к пользователю. У пользователя может быть несколько счетов.
Транзакция – история зачисления на счёт, хранит сумму зачисления и идентификатор счёта

## Функционал пользователя

1.  	Регистрация (по паролю и логину, возвращает ссылку активации);
2.  	Логин;
3.  	Просмотр списка товаров;
4.  	Покупка товара: списывает с баланса стоимость товара, при условии наличия на балансе счёта достаточного количества средств;
5.  	Просмотр баланса всех счетов и историю транзакций;
6.  	Зачисление средств на счёт, выполняется с помощью эндпоинта [POST] /payments/webhook симулирует начисление со стороннего сервиса.


## Функционал администратора

1.  	Видеть все товары;
2.  	Видеть всех пользователей и их счета;
3.  	Включать/отключать пользователей;
4.  	Создавать/редактировать/удалять товары.

## Регистрация, аутентификация, активация

Для регистрации существует эндпоинт users/register, на который с помощью POST-запроса отправляются credentials пользователя: username и password.
После регистрации необходимо активировать пользователя, отправив POST-запрос по uri, полученному в ответе.

Активированный пользователь может пройти аутентификацию и получить JWT-токен, отправив POST-запрос на эндпоинт /auth. Токен аутентификации с префиксом Bearer нужно установить в хедер Authorization для получения доступа к ресурсам.



### Доступные эндпоинты и методы:
метод                                                         | GET | POST | PUT | PATCH | DEL |
--------------------------------------------------------------|-----|------|-----|-------|-----|
/auth/ | - | V | - | - | - |
/users/register/| - | V | - | - | - |
/users/activate/{generated acivation uuid}| - | V | - | - | - |
/users/me | V | - | - | - | - |
/users/me/accounts | V | - | - | - | - |
/users/me/transactions | V | - | - | - | - |
/users/{id: int}  | V | - | - | - | - |
/users/{id: int}/accounts | V | - | - | - | - |
/users/{id: int}/transactions | V | - | - | - | - |
/users/{id: int}/activate | - | V | - | - | - |
/users/{id: int}/deactivate | - | V | - | - | - |
/items/ | V | V | - | - | - |
/items/{item_id} | V | - | - | V | V |
/items/{item_id}/buy | - | V | - | - | - |
/payments/webhook | - | V | - | - | - |


###  JSON-схемы 

<b> POST users/register </b>

```
{
    "username": <str: name>,
    "password": <str: password>
}
```

<b> POST /items </b>

```
{
    "title": <str: title>,
    "description": <str: description>
    "price": <decimal: price>
}
```
<b> [POST, PATCH] /items/<item_id: int> </b>

```
{
    "title": <str: title>,
    "description": <str: description>
    "price": <decimal: price>
}
```
<b> [POST] /items/<item_id: int>/buy </b>

```
{
    "id": <account_id: int>
}
```

<b> [POST] payments/webhook </b>

```
{
    {
	    “signature”: “f4eae5b2881d8b6a1455f62502d08b2258d80084”,
	    “transaction_id”: 1234567,
	    “user_id”: 123456,
	    “bill_id”: 123456,
	    “amount”: 100
    }

}
```
Сигнатура формируется по правилу:
```
from Crypto.Hash import SHA1

signature = SHA1.new()\
.update(f'{private_key}:{transaction_id}:{user_id}:{bill_id}:{amount}'.encode())\
.hexdigest()
```
Где private_key – приватный ключ, задаётся в свойствах приложения, transaction_id – уникальный идентификатор транзакции, user_id – пользователь на чей счёт произойдёт зачисление, bill_id – идентификатор счёта (если счёта с таким айди не существует, то он должен быть создан), amount – сумма транзакции.

## Запуск на локальной машине
В консоли в директории проекта нужно выполнить команду:
> docker compose up 

## TODO:
- unit-tests
- openapi documentation

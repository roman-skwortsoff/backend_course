from datetime import date
from fastapi import HTTPException


class MyAllExceptions(Exception):
    detail = "Общая ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(MyAllExceptions):
    detail = "Объект не найден"


class RoomNotFoundException(ObjectNotFoundException):
    detail = "Номер не найден"


class HotelNotFoundException(ObjectNotFoundException):
    detail = "Отель не найден"


class AllRoomsAreBookedException(MyAllExceptions):
    detail = "Не осталось свободных номеров"


class DataBaseIntegrityException(MyAllExceptions):
    detail = "Ошибка добавления/удаления/изменения"


class IncorrectDatesException(MyAllExceptions):
    detail = "Дата выезда должна быть позже даты заезда"


class ObjectAlreadyExistException(MyAllExceptions):
    detail = "Объект уже существует"


class UserNotFoundException(MyAllExceptions):
    detail = "Нет пользователя с таким email"


class IncorrectPasswordException(MyAllExceptions):
    detail = "Неверный пароль"


class UserAlreadyExistException(MyAllExceptions):
    detail = "Пользователь уже зарегистрирован"


class NotTokenException(MyAllExceptions):
    detail = "Отсутствует токен"


def check_date_to_after_date_from(date_from: date, date_to: date) -> None:
    if date_from >= date_to:
        raise HTTPException(
            status_code=422, detail="Дата выезда должна быть позже даты заезда"
        )


class MyHTTPException(HTTPException):
    status_code = 500
    detail = None

    def __init__(self, *args, **kwargs):
        super().__init__(
            status_code=self.status_code, detail=self.detail, *args, **kwargs
        )


class HotelNotFoundHTTPException(MyHTTPException):
    status_code = 404
    detail = "Отель не найден"


class RoomNotFoundHTTPException(MyHTTPException):
    status_code = 404
    detail = "Номер не найден"


class DBIntegrityHTTPException(MyHTTPException):
    status_code = 409
    detail = "Нужно сначала удалить взаимосвязанные данные"


class UserNotFoundHTTPException(MyHTTPException):
    status_code = 401
    detail = "Пользователь с таким email не зарегистрирован"


class IncorrectPasswordHTTPException(MyHTTPException):
    status_code = 401
    detail = "Пароль неверный"


class UserAlreadyExistHTTPException(MyHTTPException):
    status_code = 409
    detail = "Пользователь уже зарегистрирован"


class NotTokenHTTPException(MyHTTPException):
    status_code = 401
    detail = "Вы не предоставили токен"


class AllRoomsAreBookedHTTPException(MyHTTPException):
    status_code = 409
    detail = "Не осталось свободных номеров"

class ObjectNotFoundHTTPException(MyHTTPException):
    status_code = 404
    detail = "Объект не найден"
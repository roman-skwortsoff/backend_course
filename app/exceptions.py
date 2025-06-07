class MyAllExceptions(Exception):
    detail = "Общая ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(MyAllExceptions):
    detail = "Объект не найден"


class AllRoomsAreBookedException(MyAllExceptions):
    detail = "Не осталось свободных номеров"


class DataBaseIntegrityException(MyAllExceptions):
    detail = "Ошибка добавления/удаления/изменения"


class IncorrectDatesException(MyAllExceptions):
    detail = "Дата выезда должна быть позже даты заезда"

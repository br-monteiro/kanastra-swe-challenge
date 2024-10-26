from json import dumps


class DebitDetails():
    name: str = None
    government_id: int = None
    email: str = None
    debt_amount: float = None
    debt_due_date: str = None
    debt_id: str = None

    def to_json(self):
        return dumps(self.__dict__)

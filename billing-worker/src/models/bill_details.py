from json import dumps


class BillDetails():
    name: str = None
    government_id: int = None
    email: str = None
    debt_amount: float = None
    debt_due_date: str = None
    debt_id: str = None
    has_been_processed: bool = False
    has_been_notified: bool = False

    def to_json(self):
        return dumps(self.__dict__)

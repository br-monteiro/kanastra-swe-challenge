from src.models.data_status import DataStatus
from src.models.debit_details import DebitDetails


class DataContext():
    def __init__(self, debit_details: DebitDetails = None, status: DataStatus = DataStatus.UNPROCESSED):
        self.debit_details = debit_details
        self.status = status

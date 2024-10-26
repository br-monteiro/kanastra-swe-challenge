from src.models.data_status import DataStatus
from src.models.bill_details import BillDetails


class DataContext():
    def __init__(self, bill_details: BillDetails = None, status: DataStatus = DataStatus.UNPROCESSED):
        self.bill_details = bill_details
        self.status = status

class SQSMessage:
    def __init__(self, message: dict):
        self.content = message
        self.body = message.get("Body")
        self.receipt_handle = message.get("ReceiptHandle")

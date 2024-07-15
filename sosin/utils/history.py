class HistoryManager:

    history: list
    
    def __init__(self) -> None:
        self.history = []
    
    def add_history(self, r):
        self.history.append(r)

    def get_histories(self):
        return self.history
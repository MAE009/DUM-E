class Memo:
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key, None)

    def forget(self, key):
        if key in self.data:
            del self.data[key]

    def clear(self):
        self.data.clear()

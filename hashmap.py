"""
CustomHashMap module.

This implementation was adapted from: https://www.youtube.com/watch?v=9HFbhPscPU0 and was provided to the class as a learning
resource.
"""
class CustomHashMap:
    """
    Separate-chaining hash map.

    """
    def __init__(self, size=40, max_load=0.75):
        self.size = max(1, int(size))
        self.map = [[] for _ in range(self.size)]
        self.count = 0
        self.max_load = float(max_load)

    def _get_hash(self, key):
        h = 0
        for char in str(key):
            h = (h * 31 + ord(char)) % self.size
        return h

    def _resize(self, new_size):
        old_items = [(pair[0], pair[1]) for bucket in self.map for pair in bucket]
        self.size = max(1, int(new_size))
        self.map = [[] for _ in range(self.size)]
        self.count = 0
        for k, v in old_items:
            self.add(k, v)

    def add(self, key, value):
        idx = self._get_hash(key)
        bucket = self.map[idx]
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return True
        bucket.append([key, value])
        self.count += 1
        if (self.count / self.size) > self.max_load:
            self._resize(self.size * 2)
        return True

    def get(self, key):
        idx = self._get_hash(key)
        for pair in self.map[idx]:
            if pair[0] == key:
                return pair[1]
        return None

    def delete(self, key):
        idx = self._get_hash(key)
        bucket = self.map[idx]
        for i, pair in enumerate(bucket):
            if pair[0] == key:
                bucket.pop(i)
                self.count -= 1
        return False

    def keys(self):
        return [pair[0] for bucket in self.map for pair in bucket]

    def items(self):
        return [(pair[0], pair[1]) for bucket in self.map for pair in bucket]

    def __len__(self):
        return self.count

    def __setitem__(self, key, value):
        self.add(key, value)

    def __getitem__(self, key):
        val = self.get(key)
        if val is None:
            raise KeyError(key)
        return val

    def __str__(self):
        return str(self.items())
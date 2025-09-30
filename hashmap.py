"""CustomHashMap module.

This implementation was adapted from: https://www.youtube.com/watch?v=9HFbhPscPU0.

Process:
  - Provide a small separate-chaining hash map used to store Package objects
    keyed by package id. The map grows automatically when the load factor
    exceeds `max_load`.

Flow:
  - Callers create the map, add items with add(key, value) or map[key] = value,
    retrieve with get(key) or map[key], and remove with delete(key).

Complexity notes:
  - Average-case add/get/delete are O(1) when the load factor is kept low.
  - Resizing is O(n) and happens occasionally; amortized cost of add remains A(1).
"""


class CustomHashMap:
    """
    Separate-chaining hash map with simple automatic growth.

    The implementation uses a list of buckets where each bucket is a Python
    list of [key, value] pairs. Collisions are resolved by appending to the
    bucket (chaining). The number of buckets is doubled when the load factor
    exceeds `max_load` to keep bucket lengths small.
    """

    def __init__(self, size=40, max_load=0.75):
        # store number of buckets and initialize empty bucket lists
        self.size = max(1, int(size))
        self.map = [[] for _ in range(self.size)]
        # count of stored key/value pairs
        self.count = 0
        self.max_load = float(max_load)

    def _get_hash(self, key):
        """
        Compute a simple polynomial rolling hash and return bucket index.

        Process: build an integer hash from the string form of the key, then
        reduce it modulo `self.size` to obtain the bucket index.
        Flow: used by add/get/delete to choose which bucket to operate on.
        Complexity: O(k) where k is length of str(key) (usually small).
        """
        h = 0
        for char in str(key):
            h = (h * 31 + ord(char)) % self.size
        return h

    def _resize(self, new_size):
        """
        Resize the bucket array to new_size and rehash all items.

        Process: snapshot existing items, allocate a new bucket list of the
        requested size, reset counters, and re-insert each item (which
        recomputes bucket indices under the new size).
        Flow: invoked by add() when the load factor exceeds `max_load`.
        Complexity: O(n) where n is number of stored items.
        """
        old_items = [(pair[0], pair[1]) for bucket in self.map for pair in bucket]
        self.size = max(1, int(new_size))
        self.map = [[] for _ in range(self.size)]
        self.count = 0
        for k, v in old_items:
            # re-inserting will increment self.count appropriately
            self.add(k, v)

    def add(self, key, value):
        """
        Insert or update a key/value pair.

        Process: compute bucket index, update if key exists, otherwise append
        a new pair and increment count. If load factor exceeds `max_load`,
        trigger a resize (doubling the bucket count).

        Flow: callers use add() to populate the map during CSV parsing.
        Complexity: average O(1), occasional O(n) during resize.
        """
        idx = self._get_hash(key)
        bucket = self.map[idx]
        for pair in bucket:
            if pair[0] == key:
                # update existing entry
                pair[1] = value
                return True
        # append new key/value pair
        bucket.append([key, value])
        self.count += 1
        # check load factor and grow if necessary
        if (self.count / self.size) > self.max_load:
            self._resize(self.size * 2)
        return True

    def get(self, key):
        """
        Retrieve value by key or return None if missing.

        Process: hash to locate bucket and linear-scan the bucket for key.
        Complexity: average O(1), worst-case O(n) if many items collide.
        """
        idx = self._get_hash(key)
        for pair in self.map[idx]:
            if pair[0] == key:
                return pair[1]
        return None

    def delete(self, key):
        """
        Remove key and return True if removed, False otherwise.

        Process: locate bucket and pop the matching pair. Decrement count so
        load factor remains accurate.
        Complexity: average O(1).
        """
        idx = self._get_hash(key)
        bucket = self.map[idx]
        for i, pair in enumerate(bucket):
            if pair[0] == key:
                bucket.pop(i)
                self.count -= 1
                return True
        return False

    def keys(self):
        """
        Return a list of keys in bucket order.

        Note: bucket order depends on the current number of buckets and the
        hash function; it does not reflect numeric ordering of keys.
        Complexity: O(n).
        """
        return [pair[0] for bucket in self.map for pair in bucket]

    def items(self):
        """
        Return a list of (key, value) pairs in bucket order.

        Complexity: O(n).
        """
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
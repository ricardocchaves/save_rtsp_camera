from threading import Lock

# Thread-safe, non-duplicates list.
class SafeList():
    def __init__(self):
        self.lock = Lock()
        self.data = []

    # Check if val is in `self.data`
    def contains(self, val):
        ret = False
        self.lock.acquire()
        if val in self.data:
            ret = True
        self.lock.release()
        return ret

    # Insert val in `self.data`, if not already there
    def put(self, val):
        self.lock.acquire()
        ret = True
        if val in self.data:
            ret = False
            self.lock.release()
            return ret
        self.data.append(val)
        self.lock.release()
        return True

    # Remove val from `self.data`, if not already there
    def take(self, val):
        if not self.contains(val):
            return False
        self.lock.acquire()
        self.data.remove(val)
        self.lock.release()
        return True

    # Returns a copy of the current state of `self.data`
    def snapshot(self):
        ret = []
        self.lock.acquire()
        for v in self.data:
            ret.append(v)
        self.lock.release()
        return ret

if __name__ == "__main__":
    sl = SafeList()
    sl.put(2)
    sl.put(9)
    sl.put(2)
    print(sl.contains(2))
    print(sl.contains(3))
    print(sl.snapshot())
    sl.take(2)
    sl.take(3)
    print(sl.snapshot())
    print("""--- Expected: ---
True
False
[2, 9]
[9]""")

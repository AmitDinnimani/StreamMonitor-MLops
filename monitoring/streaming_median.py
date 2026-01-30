class StreamingMedian:
    """
    Maintains the median of a stream using:
    - Max Heap for lower half
    - Min Heap for upper half
    """

    def __init__(self):
        self.max_heap = []  # lower half (max heap)
        self.min_heap = []  # upper half (min heap)

    # ---------- MAX HEAP HELPERS ----------
    def _insert_max(self, value):
        self.max_heap.append(value)
        i = len(self.max_heap) - 1

        while i > 0:
            parent = (i - 1) // 2
            if self.max_heap[i] > self.max_heap[parent]:
                self.max_heap[i], self.max_heap[parent] = (
                    self.max_heap[parent],
                    self.max_heap[i],
                )
                i = parent
            else:
                break

    def _delete_max(self):
        root = self.max_heap[0]
        self.max_heap[0] = self.max_heap.pop()
        self._heapify_max(0)
        return root

    def _heapify_max(self, i):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < len(self.max_heap) and self.max_heap[left] > self.max_heap[largest]:
            largest = left
        if right < len(self.max_heap) and self.max_heap[right] > self.max_heap[largest]:
            largest = right

        if largest != i:
            self.max_heap[i], self.max_heap[largest] = (
                self.max_heap[largest],
                self.max_heap[i],
            )
            self._heapify_max(largest)

    # ---------- MIN HEAP HELPERS ----------
    def _insert_min(self, value):
        self.min_heap.append(value)
        i = len(self.min_heap) - 1

        while i > 0:
            parent = (i - 1) // 2
            if self.min_heap[i] < self.min_heap[parent]:
                self.min_heap[i], self.min_heap[parent] = (
                    self.min_heap[parent],
                    self.min_heap[i],
                )
                i = parent
            else:
                break

    def _delete_min(self):
        root = self.min_heap[0]
        self.min_heap[0] = self.min_heap.pop()
        self._heapify_min(0)
        return root

    def _heapify_min(self, i):
        smallest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < len(self.min_heap) and self.min_heap[left] < self.min_heap[smallest]:
            smallest = left
        if right < len(self.min_heap) and self.min_heap[right] < self.min_heap[smallest]:
            smallest = right

        if smallest != i:
            self.min_heap[i], self.min_heap[smallest] = (
                self.min_heap[smallest],
                self.min_heap[i],
            )
            self._heapify_min(smallest)

    # ---------- PUBLIC API ----------
    def insert(self, value):
        """
        Insert value into stream
        Time complexity: O(log n)
        """
        if not self.max_heap or value <= self.max_heap[0]:
            self._insert_max(value)
        else:
            self._insert_min(value)

        # Balance heaps
        if len(self.max_heap) > len(self.min_heap) + 1:
            self._insert_min(self._delete_max())
        elif len(self.min_heap) > len(self.max_heap) + 1:
            self._insert_max(self._delete_min())

    def get_median(self):
        """
        Returns current median
        Time complexity: O(1)
        """
        if len(self.max_heap) == len(self.min_heap):
            if not self.max_heap:
                return None
            return (self.max_heap[0] + self.min_heap[0]) / 2

        if len(self.max_heap) > len(self.min_heap):
            return self.max_heap[0]

        return self.min_heap[0]

import sys
sys.path.append('../doubly_linked_list')
from doubly_linked_list import DoublyLinkedList


class Queue:
    def __init__(self):
        self.size = 0
        # Why is our DLL a good choice to store our elements?
        # We're using a DLL because Queues only add to end or remove from the ends
        # Those are fast operations for a DLL, but not for lists
        self.storage = DoublyLinkedList()

    def enqueue(self, value):
        self.storage.add_to_tail(value)

    def dequeue(self):
        if self.len() == 0:
            return None
        else:
            next = self.storage.head.value
            self.storage.remove_from_head()
            return next

    def len(self):
        return self.storage.length

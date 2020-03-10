import sys
sys.path.append('../doubly_linked_list')
from doubly_linked_list import DoublyLinkedList

class Stack:
    def __init__(self):
        self.size = 0
        # Why is our DLL a good choice to store our elements?
        # We're using a DLL because stacks only add to end or remove from the end
        # Those are fast operations for a DLL, but not for lists
        self.storage = DoublyLinkedList()

    def push(self, value):
        self.storage.add_to_tail(value)

    def pop(self):
        if self.len() == 0:
            return None
            
        else:
            next = self.storage.tail.value
            self.storage.remove_from_tail()
        return next

    def len(self):
        return self.storage.length

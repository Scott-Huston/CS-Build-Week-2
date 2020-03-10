from dll_queue import Queue
from dll_stack import Stack
import requests
import time
import json

class Player:
    def __init__(self, num_rooms=500, load=False):
        headers = {
            'Authorization': 'Token 4741bd08a455ca22daa39dcebf0b619d129eea1f',
            }

        response = requests.get('https://lambda-treasure-hunt.herokuapp.com/api/adv/init/', headers=headers)

        self.current_room = response.json()
        # example of current room
        # {
        # "room_id": 0,
        # "title": "Room 0",
        # "description": "You are standing in an empty room.",
        # "coordinates": "(60,60)",
        # "players": [],
        # "items": ["small treasure"],
        #  *** note *** exits gets converted to dict
        # exits[direction] = '?' or exits[direction] = room_id
        # "exits": ["n", "s", "e", "w"],
        # "cooldown": 60.0,
        # "errors": [],
        # "messages": []
        # }
        exits = {}
        for exit in self.current_room['exits']:
            exits[exit] = '?'
        self.current_room['exits'] = exits
        self.num_rooms = num_rooms
        self.traversal_path = []
        self.last_move = time.time()
        self.cooldown = self.current_room['cooldown']
        
        if load:
            with open('seen.json') as json_file:
                self.seen = json.load(json_file)
        else:
            self.seen = {str(self.current_room['room_id']) : self.current_room}


    def travel(self, direction, show_rooms = False):
        """
        Method for moving rooms
        """

        # check that we've waited for cooldown
        elapsed = time.time() - self.last_move
        # if necessary, sleep until cooldown period has passed
        if elapsed < self.cooldown:
            wait_time = self.cooldown - elapsed
            print(f'waiting {wait_time} seconds ')
            time.sleep(wait_time)

        # get next room

        # wise traveler predictions after running maze
        next_id = int(self.seen[str(self.current_room['room_id'])]['exits'][direction])

        headers = {
            'Authorization': 'Token 4741bd08a455ca22daa39dcebf0b619d129eea1f',
            'Content-Type': 'application/json',
        }

        if next_id == '?':
            data = f'{{"direction":"{direction}"}}'
        
        else:
            data = f'{{"direction":"{direction}", "next_room_id": "{next_id}"}}'

        # send post request to move and receive response for new room
        response = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/move/', headers=headers, data=data)
        response = response.json()

        if response['errors'] != []:
            print(response['errors'])
            return 1

        # update time of last move (after move to be conservative)
        self.last_move = time.time()

        # update cooldown
        self.cooldown = response['cooldown']

        # update current room exits with the room id we went to
        self.seen[str(self.current_room['room_id'])]['exits'][direction] = response['room_id']

        # TODO error handling for invalid movements?
        self.current_room = response
        
        # convert exits in new room to dict
        exits = {}
        for exit in self.current_room['exits']:
            exits[exit] = '?'
        self.current_room['exits'] = exits

        self.traversal_path.append(direction)

        # if current room not in seen yet, add current room to seen
        if str(self.current_room['room_id']) not in self.seen:
            self.seen[str(self.current_room['room_id'])] = self.current_room

        if (show_rooms):
            print(self.current_room['description'])
        # else:
        #     print("You cannot move in that direction.")
    

    def find_room(self, title):
        """
        Return a list containing the shortest path from
        starting room to room with matching title in
        breadth-first order.
        """

        # # initialize queue with starting vertex
        q = Queue()
        q.enqueue((self.seen[str(self.current_room['room_id'])], []))
        
        # # set to keep track of vertexes already seen
        visited = set()

        # # while queue is not empty
        while q.len() > 0:
            # get path and vertex
            room, path = q.dequeue()

            # if room title matches, return path
            if room['title'] == title:
                return path

            # else, add room_id to visited
            if room['room_id'] not in visited:
                visited.add(room['room_id'])      
                # and add paths to the queue for each exit 
                for direction, next_room in room['exits'].items():
                    path_copy = path.copy()
                    path_copy.append(direction)
                    q.enqueue((self.seen[str(next_room)], path_copy))
        
        raise ValueError('Room not found')

    def find_room_by_id(self, id):
        """
        Return a list containing the shortest path from
        starting room to room with matching id in
        breadth-first order.
        """

        # # initialize queue with starting vertex
        q = Queue()
        q.enqueue((self.seen[str(self.current_room['room_id'])], []))
        
        # # set to keep track of vertexes already seen
        visited = set()

        # # while queue is not empty
        while q.len() > 0:
            # get path and vertex
            room, path = q.dequeue()

            # if room title matches, return path
            if room['room_id'] == id:
                return path

            # else, add room_id to visited
            if room['room_id'] not in visited:
                visited.add(room['room_id'])      
                # and add paths to the queue for each exit 
                for direction, next_room in room['exits'].items():
                    path_copy = path.copy()
                    path_copy.append(direction)
                    q.enqueue((self.seen[str(next_room)], path_copy))
        
        raise ValueError('Room not found')

    def find_new_room(self):
        """
        Return a list containing the shortest path from
        starting room to unknown room in
        breadth-first order.
        """

        # # initialize queue with starting vertex
        q = Queue()
        q.enqueue((self.seen[str(self.current_room['room_id'])], []))
        
        # # set to keep track of vertexes already seen
        visited = set()

        # # while queue is not empty
        while q.len() > 0:
            # get path and vertex
            room, path = q.dequeue()

            # if room contains directions that have not been seen, 
            # append direction and return path
            for direction, next_room in room['exits'].items():
                if next_room == '?':
                    path.append(direction)
                    return path
            # else, add room_id to visited
            if room['room_id'] not in visited:
                visited.add(room['room_id'])      
                # and add paths to the queue for each exit 
                for direction, next_room in room['exits'].items():
                    path_copy = path.copy()
                    path_copy.append(direction)
                    q.enqueue((self.seen[str(next_room)], path_copy))
        
        raise ValueError('Room not found')

    def run_maze(self):

        print('run-maze')
        while len(self.seen)<self.num_rooms:
            # if len(self.seen)%10 == 0:
            #     print('rooms seen: ', len(self.seen))
            path = self.find_new_room()
            for direction in path:
                print('direction: ', direction)
                self.travel(direction)
                print('current_room', self.current_room['room_id'])
                print('total rooms seen: ', len(self.seen))
        print()

    def collect_treasure(self):
        status = self.get_status()
        print('Gold: ', status['gold'])
        space = status['strength'] - status['encumbrance']

        explored = set()
        
        while space > 5:
            # if room has treasure:
            for item in self.current_room['items']:
                if 'treasure' in item and space>3:
                    # pick up treasure
                    headers = {
                        'Authorization': 'Token 4741bd08a455ca22daa39dcebf0b619d129eea1f',
                        'Content-Type': 'application/json', 
                    }

                    data = '{"name":"treasure"}'

                    response = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/take/', headers=headers, data=data)
                    print('Picked up treasure!')

                    # update space
                    status = self.get_status()
                    print('Gold: ', status['gold'])
                    space = status['strength'] - status['encumbrance']
                                
            # bfs for nearest unexplored room
            path = self.find_nearest_unexplored(explored)

            # move to that room
            for direction in path:
                self.travel(direction)
        
        # head back to shop

        path = self.find_room('Shop')
        for direction in path:
            self.travel(direction)
        
        # TODO head back to shop but still pick up treasure if it fits

    def change_name(self, name):
        headers = {
            'Authorization': 'Token 4741bd08a455ca22daa39dcebf0b619d129eea1f',
            'Content-Type': 'application/json',
        }

        data = f'{{"name":"[{name}]"}}'

        response = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/change_name/', headers=headers, data=data)

    def get_status(self):

        headers = {
        'Authorization': 'Token 4741bd08a455ca22daa39dcebf0b619d129eea1f',
        'Content-Type': 'application/json',
        }

        response = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/status/', headers=headers)

        return response.json()

    def find_nearest_unexplored(self, explored):
        """
        Return a list containing the shortest path from
        starting room to unexplored room in
        breadth-first order.
        """

        # initialize queue with starting vertex
        q = Queue()
        q.enqueue((self.seen[str(self.current_room['room_id'])], []))

        # while queue is not empty
        while q.len() > 0:
            # get path and vertex
            room, path = q.dequeue()

            # if unexplored room, return path
            if room['room_id'] in explored:
                return path

            # else, add room_id to explored
            else:
                explored.add(room['room_id'])      
                # and add paths to the queue for each exit 
                for direction, next_room in room['exits'].items():
                    path_copy = path.copy()
                    path_copy.append(direction)
                    q.enqueue((self.seen[str(next_room)], path_copy))
        
        raise ValueError('No more rooms to explore')

    def sell_treasure(self):
        headers = {
            'Authorization': 'Token 4741bd08a455ca22daa39dcebf0b619d129eea1f',
            'Content-Type': 'application/json',
        }

        data = '{"name":"treasure", "confirm":"yes"}'

        response = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/sell/', headers=headers, data=data)

        print(response.json())

        status = self.get_status()
        print(status)
        print('Gold: ', status['gold'])

    def examine(self, name):
        headers = {
            'Authorization': 'Token 4741bd08a455ca22daa39dcebf0b619d129eea1f',
            'Content-Type': 'application/json',
        }

        data = f'{{"name":"{name}"}}'

        response = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/examine/', headers=headers, data=data)

        return response.json()


"""

\n10000010\n00000001\n01001101\n01001000\n00000001\n10000010\n00000001\n01101001\n01001000\n00000001\n10000010\n00000001\n01101110\n01001000\n00000001\n10000010\n00000001\n01100101\n01001000\n00000001\n10000010\n00000001\n00100000\n01001000\n00000001\n10000010\n00000001\n01111001\n01001000\n00000001\n10000010\n00000001\n01101111\n01001000\n00000001\n10000010\n00000001\n01110101\n01001000\n00000001\n10000010\n00000001\n01110010\n01001000\n00000001\n10000010\n00000001\n00100000\n01001000\n00000001\n10000010\n00000001\n01100011\n01001000\n00000001\n10000010\n00000001\n01101111\n01001000\n00000001\n10000010\n00000001\n01101001\n01001000\n00000001\n10000010\n00000001\n01101110\n01001000\n00000001\n10000010\n00000001\n00100000\n01001000\n00000001\n10000010\n00000001\n01101001\n01001000\n00000001\n10000010\n00000001\n01101110\n01001000\n00000001\n10000010\n00000001\n00100000\n01001000\n00000001\n10000010\n00000001\n01110010\n01001000\n00000001\n10000010\n00000001\n01101111\n01001000\n00000001\n10000010\n00000001\n01101111\n01001000\n00000001\n10000010\n00000001\n01101101\n01001000\n00000001\n10000010\n00000001\n00100000\n01001000\n00000001\n10000010\n00000001\n00110100\n01001000\n00000001\n10000010\n00000001\n00111000\n01001000\n00000001\n10000010\n00000001\n00110101\n01001000\n00000001\n00000001

"""
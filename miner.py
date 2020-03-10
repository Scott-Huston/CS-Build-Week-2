import hashlib
import requests

import sys

from uuid import uuid4

from timeit import default_timer as timer
import time

import random


def proof_of_work(last_proof, difficulty):
    """
    Multi-Ouroboros of Work Algorithm
    - Find a number p' such that the last six digits of hash(p) are equal
    to the first six digits of hash(p')
    - IE:  last_hash: ...AE9123456, new hash 123456888...
    - p is the previous proof, and p' is the new proof
    - Use the same method to generate SHA-256 hashes as the examples in class
    """

    start = timer()

    print("Searching for next proof")
    proof = random.randint(-1000000000,1000000000)
    
    found = True
    while valid_proof(last_proof, proof, difficulty) is False:
        # adjust integer number to control reset time
        if (timer() - start) > 60*30:
            found = False
            break
        proof += 1

    if found:
        print("Proof found: " + str(proof) + " in " + str(timer() - start))
        return proof
    else:
        print('else statement')
        return False


def valid_proof(last_proof, proof, difficulty):
    """
    Validates the Proof:  Multi-ouroborus:  Do the last six characters of
    the hash of the last proof match the first six characters of the hash
    of the new proof?

    IE:  last_hash: ...AE9123456, new hash 123456E88...
    """

    guess = f'{last_proof}{proof}'.encode()

    guess_hash = hashlib.sha256(guess).hexdigest()
    # return True or False
    return guess_hash[:difficulty] == '0'*difficulty


if __name__ == '__main__':
    coins_mined = 0

    # Run forever until interrupted
    while True:

        headers = {
            'Authorization': 'Token 4741bd08a455ca22daa39dcebf0b619d129eea1f',
        }

        r = requests.get('https://lambda-treasure-hunt.herokuapp.com/api/bc/last_proof/', headers=headers)
        # Handle non-json response
        try:
            data = r.json()
        except ValueError:
            print("Error:  Non-json response")
            print("Response returned:")
            print(r)
            break
        
        old_proof = data['proof']
        difficulty = data['difficulty']

        new_proof = proof_of_work(old_proof, difficulty)
        if new_proof != False:
            print(f'new proof = {new_proof}')

            # TODO: Get the block from `data` and use it to look for a new proof
            # new_proof = ???

            # When found, POST it to the server
            headers = {
                'Authorization': 'Token 4741bd08a455ca22daa39dcebf0b619d129eea1f',
                'Content-Type': 'application/json',
            }

            data = f'{{"proof":{new_proof}}}'

            response = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/bc/mine/', headers=headers, data=data)
            data = response.json()

            # if cooldown exists, sleep that amount, else sleep 0
            time.sleep(data.get('cooldown',0))

            if data.get('message') == 'New Block Forged':
                coins_mined += 1
                print("Total coins mined: " + str(coins_mined))

            print(response.json())
            # TODO: If the server responds with a 'message' 'New Block Forged'
            # add 1 to the number of coins mined and print it.  Otherwise,
            # print the message from the server.


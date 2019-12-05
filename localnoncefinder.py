#!/usr/bin/env python
# Everything working as intended, benchmarks taken.

import time
import hashlib
import random


intmax = 2 ** 32 - 1
secretmessage = "deadbeef"
# secretmessage = str(random.randrange(200))
minnonce = 0
maxnonce = intmax
difficulty_bits = 19


def find_golden_nonce():
    target = 2 ** (256 - difficulty_bits)
    nonce = minnonce
    while nonce < maxnonce:
        to_hash = (str(secretmessage) + str(nonce)).encode("utf-8")
        nonce_hashed = hashlib.sha256(to_hash).hexdigest()
        if int(nonce_hashed, 16) < target:
            print("Nonce found: ", nonce)
            print("Hash value: ", nonce_hashed)
            return nonce
        nonce += 1
    return -1


if __name__ == "__main__":

    for i in range(0, 5):
        min_nonce = 0
        start_time = time.time()

        found_nonce = find_golden_nonce()

        end_time = time.time()

        time_taken = end_time - start_time
        print("Elapsed time: ", time_taken, " seconds")
        difficulty_bits += 1

# Original file from
# https://github.com/clcert/beacon-random-comments/blob/cbbb638a63590e9571e33a709c8e4b519425e3ff/verification/chacha20generator.py

import math
from Crypto.Cipher import ChaCha20


def zero_fill_right_shift(val, n):
    return (val >> n) if val >= 0 else ((val + 0x100000000) >> n)


class ChaChaRand:

    def __init__(self, seed='00'*40):
        self.zeros = bytes.fromhex('00' * 64)
        self.reseed(seed)

    def reseed(self, seed='00'*40):
        self.seed = seed
        self.key = bytes.fromhex(seed[0:64])
        self.iv = bytes.fromhex(seed[64:80])
        self.cipher = ChaCha20.new(key=self.key, nonce=self.iv)
        self._rand_block = self.cipher.encrypt(self.zeros)
        self._next_byte_index = 0;
        self._block_counter = 1;

    def generated_blocks_count(self):
        return self._block_counter

    def used_bits_count(self):
        return self._next_byte_index*8 + ((self._block_counter - 1)*(64*8))

    def _new_rand_block(self):
        self._rand_block = self.cipher.encrypt(self.zeros)
        self._next_byte_index = 0;
        self._block_counter += 1;

    def get_bytes(self, n):
        end_index = self._next_byte_index + n
        ret = self._rand_block[self._next_byte_index:end_index]
        self._next_byte_index += n
        # If the current block wasn't enough, then:
        while len(ret) < n:
            missing = n - len(ret)
            self._new_rand_block()
            old_ret = ret
            new_bytes = self._rand_block[:missing]
            ret = old_ret + new_bytes
            self._next_byte_index = missing
        return ret

    def get_byte(self):
        return self.get_bytes(1)

    def get_rand_bits(self, nbits):
        needed_bytes = math.ceil(nbits / 8)
        bytes = self.get_bytes(needed_bytes)
        ret = 0
        extra_bits = nbits % 8
        bitmask = (1<<extra_bits) - 1 if extra_bits else -1
        ret = bytes[0] & bitmask
        for i in range(1, needed_bytes):
            ret *= 256
            ret += bytes[i]
        return ret

    def rand_uint(self, max):
        maxbits = math.floor(math.log2(max)) + 1
        ret = self.get_rand_bits(maxbits)
        while ret > max:
            ret = self.get_rand_bits(maxbits)
        return ret

    def rand_int(self, min, max):
        return self.rand_uint(max - min) + min

    def random(self):
        width = 256
        chunks = 6
        digits = 52
        startdenom = pow(width, chunks)
        significance = pow(2, digits)
        overflow = significance * 2
        n = self.get_rand_bits(chunks*8)
        d = startdenom
        x = 0
        while n < significance:
            n = (n + x) * width
            d *= width
            x = self.get_rand_bits(8)
        while n >= overflow:
            n /= 2
            d /= 2
            x = zero_fill_right_shift(x, 1)
        return (n + x) / d

    def _fisher_yates(self, arr, steps=None):
        n = len(arr)
        complete = (steps is None)
        if complete:
            steps = n - 1
        if steps <= 0 or steps > (n - 1):
            pass
        j = n
        selections = 0
        while selections < steps:
            k = self.rand_uint(j - 1)
            aux = arr[k]
            arr[k] = arr[j - 1]
            arr[j - 1] = aux
            j -= 1
            selections += 1
        return arr if complete else arr[(n - steps):][::-1]

    def shuffle(self, arr):
        return self._fisher_yates(arr)

    def sample(self, arr, sample_size, order_matters=True):
        n = len(arr)
        if sample_size <= 0 or sample_size > n:
            pass
        indices = [i for i in range(n)]
        indices_sample = []
        if sample_size == n:
            if order_matters:
                self.shuffle(indices)
                indice_sample = indices[::-1]
            else:
                indices_sample = indices
        elif sample_size <= n/2 or order_matters:
            indices_sample = self._fisher_yates(indices, sample_size)
        else:
            anti_size = n - sample_size
            anti_sample = self._fisher_yates(indices, anti_size)
            aux_set = {}
            for i in range(anti_size):
                aux_set[anti_sample[i]] = True
            for i in range(n):
                try:
                    aux_set[i]
                except KeyError:
                    indices_sample.append(i)
        return [arr[i] for i in indices_sample]

    def choice(self, arr):
        n = len(arr)
        chosen = self.rand_uint(n - 1)
        return arr[chosen]

    def choices(self, arr, choices_size):
        n = len(arr)
        if choices_size <= 0 or choices_size > (n - 1):
            pass
        res = []
        for i in range(choices_size):
            chosen = self.rand_uint(n-1)
            res.append(arr[chosen])
        return res

import os
from itertools import combinations
import base64
import string
import gradio as gr

def generate_xor_key(key, length):
    """repeats a key to the desired length
    Arguments:
        key {bytes} -- bytes to repeat
        length {int} -- length of the repeated key
    Returns:
        keykeykey to length specified"""
    return (key * (length // len(key) + 1))[:length]


def xor_byte(key, data):
    """xors two equal length strings together
    Arguments:
        key {bytes} -- bytes to xor with
        data {bytes} -- bytes to xor
    Returns:
        """
    # using zip
    return bytes(a ^ b for a, b in zip(key, data))


def calculate_hamming_distance(data1, data2):
    # assert len(data1) == len(data2)
    dist = 0
    for bit1, bit2 in zip(data1, data2):
        diff = bit1 ^ bit2
        dist += sum([1 for bit in bin(diff) if bit == '1'])
    return dist


def keylength_finder(input_data, sample_max=20, minkey=2, maxkey=40):
    """Finds the key length of the input data
    from utf-8 (or ascii? TODO: check format)
    Arguments:
        input_data {bytes} -- bytes to find key length of
        sample_max {int} -- max number of samples to take
        minkey {int} -- minimum key length to try
        maxkey {int} -- maximum key length to try
    Returns:
        int -- key length"""

    keysize_differences = {}
    for keysize in range(minkey,maxkey):
        try:
            # get sample_max identically sized samples of the data as a list of bytes
            samples = []
            for segment in range(0, sample_max):
                sample = input_data[(segment*keysize):((segment+1)*keysize)]
                samples.append(sample)
            # calculate the hamming distance between each pair of samples
            keysize_difference = sum([calculate_hamming_distance(sample1, sample2) for sample1, sample2 in combinations(samples, 2)])
            # normalize keysize difference by dividing by the number of sample combinations and keysize 
            keysize_difference = keysize_difference / (((sample_max-1)*(sample_max/2)) * keysize)
            # add the keysize and its difference to the dictionary
            keysize_differences[keysize] = keysize_difference
        except:
            # sample size has exceeded the length of the data
            if sample_max >= 4:
                return keylength_finder(input_data, sample_max/2, minkey, maxkey)
            else:
                return keylength_finder(input_data, sample_max, minkey, maxkey/2)

    # print("(Keysize, Difference)")
    # print all keysizes and their differences, sorted by difference
    # for keysize in sorted(keysize_differences.items(), key=lambda x: x[1]):
        # print(f'{keysize}')

    # print keysizes with the lowest hamming distance
    # print(f"Best candidates: {sorted(keysize_differences.items(), key=lambda x: x[1])[:10]}")

    # print keysizes with the highest hamming distance
    # print(f"Worst candidates: {sorted(keysize_differences.items(), key=lambda x: x[1], reverse=True)[:10]}")

    # pick shortest hamming distance for the keysize
    final_key_length = sorted(keysize_differences.items(), key=lambda x: x[1])[0][0]
    # print(f"Final key length: {final_key_length}")
    return final_key_length


def crack_repeating_key_xor(input_data, key_length):
    """Cracks the input data using the key length
    Arguments:
        input_data {bytes} -- bytes to crack
        key_length {int} -- key length to use
    Returns:
        TODO: data type -- key guessed
        TODO: data type -- decrypted data"""
    # Make a block with all the first bytes from each block, up to the final key length
    blocks = []
    for i in range(0, key_length):
        # get the first byte of each block
        blocks.append(input_data[i::key_length])

    total_answer_guess = ''
    # Solve each block like a single byte xor
    for block in blocks:
        # get all ascii characters and punctuation
        block_answer_dict = {}
        possible_keys = list(string.printable)

        for char in possible_keys:
            # key to bytes
            key = generate_xor_key(char, len(block))
            key_bytes = bytes(key, 'utf-8')
            answer = xor_byte(key_bytes, block)
            
            # convert answer to string
            answer_string = answer.decode('utf-8')

            # calculate score
            score = 0
            for character in answer_string.upper():
                if character in frequency_dict:
                    char_u = character.upper()
                    score += frequency_dict[char_u]
            block_answer_dict[f"{char}"] = round(score, 3)
        # Get key with highest value from dict and make it the answer
        answer = sorted(block_answer_dict.items(), key=lambda x: x[1], reverse=True)[0][0]
        total_answer_guess += answer

    # XOR whole message using total_answer_guess
    # print(f"key\n\n{total_answer_guess}")
    key = generate_xor_key(total_answer_guess, len(input_data))
    key_bytes = bytes(key, 'utf-8')
    answer = xor_byte(key_bytes, input_data)
    # print(f"answer\n\n{answer.decode('utf-8')}")
    return total_answer_guess, answer.decode('utf-8')


def xor_cracker(input_data):
    """Cracks the input data using the key length
    Arguments:
        input_data {bytes} -- bytes to crack
    Returns:
        string -- key guessed
        string -- decrypted data"""
    # get key length
    key_length = keylength_finder(input_data)
    # crack the data
    return crack_repeating_key_xor(input_data, key_length)


def xor_cracker_from_b64(input_b64):
    """Cracks the input data using the key length
    Arguments:
        input_b64 {base64} -- b64 encoded bytes to crack
    Returns:
        string -- key guessed
        string -- decrypted data"""
    # decode b64
    input_data = base64.b64decode(input_b64)
    # get key length
    key_length = keylength_finder(input_data)
    # crack the data
    return crack_repeating_key_xor(input_data, key_length)


frequency_dict = {
        'E': 56.88,
        'A': 43.31,
        'R': 38.64,
        'I': 38.45,
        'O': 36.51,
        'T': 35.43,
        'N': 33.92,
        'S': 29.23,
        'L': 27.98,
        'C': 23.13,
        'U': 18.51,
        'D': 17.25,
        'P': 16.14,
        'M': 15.36,
        'H': 15.31,
        'G': 12.59,
        'B': 10.56,
        'F': 9.24,
        'Y': 9.06,
        'W': 6.57,
        'K': 5.61,
        'V': 5.13,
        'X': 1.48,
        'Z': 1.39,
        'J': 1.00,
        'Q': 0.98,
        ' ': 20.00
    }

# Main logic
def __main__():
    # decode from base64
    # input_data = base64.b64decode(open('challenge6.txt', 'r').read())
    # find key length
    # key_length = keylength_finder(input_data)
    # crack xor
    # key, answer = xor_cracker(input_data)

    # Using gradio for frontend
    iface = gr.Interface(fn=xor_cracker_from_b64, inputs="text", outputs="text")
    iface.launch(share=False, server_port=7860, server_name="0.0.0.0")

if __name__ == "__main__":
    __main__()

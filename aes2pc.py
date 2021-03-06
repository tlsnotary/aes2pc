# pieces put together from 
# https://medium.com/wearesinch/building-aes-128-from-the-ground-up-with-python-8122af44ebf9

# At the start of the protocol parties have their XOR shares of AES round key
# and their XOR shares of the message.
# At the end, they will have their XOR shares of the ciphertext

# Bandwidth complexity: 40 KB
# Round complexity: 0.5 rounds (1 message from Master to Slave)

import random

aes_sbox = [
    [int('63', 16), int('7c', 16), int('77', 16), int('7b', 16), int('f2', 16), int('6b', 16), int('6f', 16), int('c5', 16), int(
        '30', 16), int('01', 16), int('67', 16), int('2b', 16), int('fe', 16), int('d7', 16), int('ab', 16), int('76', 16)],
    [int('ca', 16), int('82', 16), int('c9', 16), int('7d', 16), int('fa', 16), int('59', 16), int('47', 16), int('f0', 16), int(
        'ad', 16), int('d4', 16), int('a2', 16), int('af', 16), int('9c', 16), int('a4', 16), int('72', 16), int('c0', 16)],
    [int('b7', 16), int('fd', 16), int('93', 16), int('26', 16), int('36', 16), int('3f', 16), int('f7', 16), int('cc', 16), int(
        '34', 16), int('a5', 16), int('e5', 16), int('f1', 16), int('71', 16), int('d8', 16), int('31', 16), int('15', 16)],
    [int('04', 16), int('c7', 16), int('23', 16), int('c3', 16), int('18', 16), int('96', 16), int('05', 16), int('9a', 16), int(
        '07', 16), int('12', 16), int('80', 16), int('e2', 16), int('eb', 16), int('27', 16), int('b2', 16), int('75', 16)],
    [int('09', 16), int('83', 16), int('2c', 16), int('1a', 16), int('1b', 16), int('6e', 16), int('5a', 16), int('a0', 16), int(
        '52', 16), int('3b', 16), int('d6', 16), int('b3', 16), int('29', 16), int('e3', 16), int('2f', 16), int('84', 16)],
    [int('53', 16), int('d1', 16), int('00', 16), int('ed', 16), int('20', 16), int('fc', 16), int('b1', 16), int('5b', 16), int(
        '6a', 16), int('cb', 16), int('be', 16), int('39', 16), int('4a', 16), int('4c', 16), int('58', 16), int('cf', 16)],
    [int('d0', 16), int('ef', 16), int('aa', 16), int('fb', 16), int('43', 16), int('4d', 16), int('33', 16), int('85', 16), int(
        '45', 16), int('f9', 16), int('02', 16), int('7f', 16), int('50', 16), int('3c', 16), int('9f', 16), int('a8', 16)],
    [int('51', 16), int('a3', 16), int('40', 16), int('8f', 16), int('92', 16), int('9d', 16), int('38', 16), int('f5', 16), int(
        'bc', 16), int('b6', 16), int('da', 16), int('21', 16), int('10', 16), int('ff', 16), int('f3', 16), int('d2', 16)],
    [int('cd', 16), int('0c', 16), int('13', 16), int('ec', 16), int('5f', 16), int('97', 16), int('44', 16), int('17', 16), int(
        'c4', 16), int('a7', 16), int('7e', 16), int('3d', 16), int('64', 16), int('5d', 16), int('19', 16), int('73', 16)],
    [int('60', 16), int('81', 16), int('4f', 16), int('dc', 16), int('22', 16), int('2a', 16), int('90', 16), int('88', 16), int(
        '46', 16), int('ee', 16), int('b8', 16), int('14', 16), int('de', 16), int('5e', 16), int('0b', 16), int('db', 16)],
    [int('e0', 16), int('32', 16), int('3a', 16), int('0a', 16), int('49', 16), int('06', 16), int('24', 16), int('5c', 16), int(
        'c2', 16), int('d3', 16), int('ac', 16), int('62', 16), int('91', 16), int('95', 16), int('e4', 16), int('79', 16)],
    [int('e7', 16), int('c8', 16), int('37', 16), int('6d', 16), int('8d', 16), int('d5', 16), int('4e', 16), int('a9', 16), int(
        '6c', 16), int('56', 16), int('f4', 16), int('ea', 16), int('65', 16), int('7a', 16), int('ae', 16), int('08', 16)],
    [int('ba', 16), int('78', 16), int('25', 16), int('2e', 16), int('1c', 16), int('a6', 16), int('b4', 16), int('c6', 16), int(
        'e8', 16), int('dd', 16), int('74', 16), int('1f', 16), int('4b', 16), int('bd', 16), int('8b', 16), int('8a', 16)],
    [int('70', 16), int('3e', 16), int('b5', 16), int('66', 16), int('48', 16), int('03', 16), int('f6', 16), int('0e', 16), int(
        '61', 16), int('35', 16), int('57', 16), int('b9', 16), int('86', 16), int('c1', 16), int('1d', 16), int('9e', 16)],
    [int('e1', 16), int('f8', 16), int('98', 16), int('11', 16), int('69', 16), int('d9', 16), int('8e', 16), int('94', 16), int(
        '9b', 16), int('1e', 16), int('87', 16), int('e9', 16), int('ce', 16), int('55', 16), int('28', 16), int('df', 16)],
    [int('8c', 16), int('a1', 16), int('89', 16), int('0d', 16), int('bf', 16), int('e6', 16), int('42', 16), int('68', 16), int(
        '41', 16), int('99', 16), int('2d', 16), int('0f', 16), int('b0', 16), int('54', 16), int('bb', 16), int('16', 16)]
]


def expand_key(key, rounds):

    rcon = [[1, 0, 0, 0]]

    for _ in range(1, rounds):
        rcon.append([rcon[-1][0]*2, 0, 0, 0])
        if rcon[-1][0] > 0x80:
            rcon[-1][0] ^= 0x11b

    key_grid = break_in_grids_of_16(key)[0]

    for round in range(rounds):
        last_column = [row[-1] for row in key_grid]
        last_column_rotate_step = rotate_row_left(last_column)
        last_column_sbox_step = [lookup(b) for b in last_column_rotate_step]
        last_column_rcon_step = [last_column_sbox_step[i]
                                 ^ rcon[round][i] for i in range(len(last_column_rotate_step))]

        for r in range(4):
            key_grid[r] += bytes([last_column_rcon_step[r]
                                  ^ key_grid[r][round*4]])

        # Three more columns to go
        for i in range(len(key_grid)):
            for j in range(1, 4):
                key_grid[i] += bytes([key_grid[i][round*4+j]
                                      ^ key_grid[i][round*4+j+3]])

    return key_grid

def rotate_row_left(row, n=1):
    return row[n:] + row[:n]

def multiply_by_2(v):
    s = v << 1
    s &= 0xff
    if (v & 128) != 0:
        s = s ^ 0x1b
    return s


def multiply_by_3(v):
    return multiply_by_2(v) ^ v


def mix_columns(grid):
    new_grid = [[], [], [], []]
    for i in range(4):
        col = [grid[j][i] for j in range(4)]
        col = mix_column(col)
        for i in range(4):
            new_grid[i].append(col[i])
    return new_grid


def mix_column(column):
    r = [
        multiply_by_2(column[0]) ^ multiply_by_3(
            column[1]) ^ column[2] ^ column[3],
        multiply_by_2(column[1]) ^ multiply_by_3(
            column[2]) ^ column[3] ^ column[0],
        multiply_by_2(column[2]) ^ multiply_by_3(
            column[3]) ^ column[0] ^ column[1],
        multiply_by_2(column[3]) ^ multiply_by_3(
            column[0]) ^ column[1] ^ column[2],
    ]
    return r


def add_sub_key(block_grid, key_grid):
    r = []

    # 4 rows in the grid
    for i in range(4):
        r.append([])
        # 4 values on each row
        for j in range(4):
            r[-1].append(block_grid[i][j] ^ key_grid[i][j])
    return r


def enc(expanded_key, data):

    # First we need to padd the data with \x00 and break it into blocks of 16
    pad = bytes(16 - len(data) % 16)
    
    if len(pad) != 16:
        data += pad
    grids = break_in_grids_of_16(data)

    # Now we need to expand the key for the multiple rounds
    # expanded_key = expand_key(key, 11)

    # And apply the original key to the blocks before start the rounds
    # For now on we will work with integers
    temp_grids = []
    round_key = extract_key_for_round(expanded_key, 0)

    for grid in grids:
        temp_grids.append(add_sub_key(grid, round_key))

    grids = temp_grids

    # Now we can move to the main part of the algorithm
    for round in range(1, 10):
        temp_grids = []
        for grid in grids:
            sub_bytes_step = [[lookup(val) for val in row] for row in grid]
            shift_rows_step = [rotate_row_left(
                sub_bytes_step[i], i) for i in range(4)]
            mix_column_step = mix_columns(shift_rows_step)
            round_key = extract_key_for_round(expanded_key, round)
            add_sub_key_step = add_sub_key(mix_column_step, round_key)
            temp_grids.append(add_sub_key_step)

        grids = temp_grids

    # A final round without the mix columns
    temp_grids = []
    round_key = extract_key_for_round(expanded_key, 10)

    for grid in grids:
        sub_bytes_step = [[lookup(val) for val in row] for row in grid]
        shift_rows_step = [rotate_row_left(
            sub_bytes_step[i], i) for i in range(4)]
        add_sub_key_step = add_sub_key(shift_rows_step, round_key)
        temp_grids.append(add_sub_key_step)

    grids = temp_grids

    # Just need to recriate the data into a single stream before returning
    int_stream = []
    
    for grid in grids:
        for column in range(4):
            for row in range(4):
                int_stream.append(grid[row][column])

    return bytes(int_stream)


def lookup(byte):
    x = byte >> 4
    y = byte & 15
    return aes_sbox[x][y]


def break_in_grids_of_16(s):
    all = []
    for i in range(len(s)//16):
        b = s[i*16: i*16 + 16]
        grid = [[], [], [], []]
        for i in range(4):
            for j in range(4):
                grid[i].append(b[i + j*4])
        all.append(grid)
    return all


def extract_key_for_round(expanded_key, round):
  return [row[round*4: round*4 + 4] for row in expanded_key]


# returns a 4x4 byte random grid representing the AES state
def get_random_state():
    state = []
    for x in range(0,4):
        row = []
        for y in range(0,4):
            row.append(random.randint(0, 255))
        state.append(row)
    return state


# given 2 grids of the same dimension, xor each pair of elements in the same
# position and return the result
def xor_grids(a,b):
    assert(len(a) == len(b))
    result = []
    for x in range(0, len(a)):
        assert(len(a[x]) == len(b[x]))
        row = []
        for y in range(0, len(a[x])):
            row.append(a[x][y] ^ b[x][y])
        result.append(row)
    return result


# Same as the original enc except at the SubBytes step
# - gets his new AES state from the masked LUT sent by master
# - continues the normal AES flow
def enc_slave(expanded_key, data):
    # First we need to padd the data with \x00 and break it into blocks of 16
    pad = bytes(16 - len(data) % 16)
    
    if len(pad) != 16:
        data += pad
    grids = break_in_grids_of_16(data)

    # Now we need to expand the key for the multiple rounds
    # expanded_key = expand_key(key, 11)

    # And apply the original key to the blocks before start the rounds
    # For now on we will work with integers
    temp_grids = []
    round_key = extract_key_for_round(expanded_key, 0)

    for grid in grids:
        temp_grids.append(add_sub_key(grid, round_key))

    grids = temp_grids

    # Now we can move to the main part of the algorithm
    for round in range(1, 10):
        temp_grids = []
        
        for grid in grids:
            # get new AES state share from a LUT from Master
            luts = luts_for_all_rounds.pop(0)
            # TODO: not implemented. In production we need to check that each
            # LUT contains exactly 256 non-repeating entries from 0 to 255. Otherwise
            # the Master can doctor those LUTs and learn some biases 
            my_state_share = lookup_in_masked_lut(grid, luts)
            #continue normal AES flow
            
            shift_rows_step = [rotate_row_left(
                my_state_share[i], i) for i in range(4)]
            mix_column_step = mix_columns(shift_rows_step)
            round_key = extract_key_for_round(expanded_key, round)
            add_sub_key_step = add_sub_key(mix_column_step, round_key)
            temp_grids.append(add_sub_key_step)

        grids = temp_grids

    # A final round without the mix columns
    temp_grids = []
    round_key = extract_key_for_round(expanded_key, 10)

    for grid in grids:
        # get new AES state share from a LUT from Master
        luts = luts_for_all_rounds.pop(0)
        my_state_share = lookup_in_masked_lut(grid, luts)
        #continue normal AES flow

        shift_rows_step = [rotate_row_left(
            my_state_share[i], i) for i in range(4)]
        add_sub_key_step = add_sub_key(shift_rows_step, round_key)
        temp_grids.append(add_sub_key_step)

    grids = temp_grids

    # Just need to recriate the data into a single stream before returning
    int_stream = []
    
    for grid in grids:
        for column in range(4):
            for row in range(4):
                int_stream.append(grid[row][column])

    return bytes(int_stream)


# Same as the original enc except at the SubBytes stage
# - compute a masked LUT for the slave and our new AES state share
# - continues the normal AES flow
def enc_master(expanded_key, data):
    # First we need to padd the data with \x00 and break it into blocks of 16
    pad = bytes(16 - len(data) % 16)
    
    if len(pad) != 16:
        data += pad
    grids = break_in_grids_of_16(data)

    # Now we need to expand the key for the multiple rounds
    # expanded_key = expand_key(key, 11)

    # And apply the original key to the blocks before start the rounds
    # For now on we will work with integers
    temp_grids = []
    round_key = extract_key_for_round(expanded_key, 0)

    for grid in grids:
        temp_grids.append(add_sub_key(grid, round_key))

    grids = temp_grids

    # Now we can move to the main part of the algorithm
    for round in range(1, 10):
        temp_grids = []
        
        for grid in grids:
            # prepare LUTs for the slave and our new state
            his_luts, my_state_share = prepare_lut_share(grid)
            luts_for_all_rounds.append(his_luts)
            #continue normal AES flow
            shift_rows_step = [rotate_row_left(
                my_state_share[i], i) for i in range(4)]
            mix_column_step = mix_columns(shift_rows_step)
            round_key = extract_key_for_round(expanded_key, round)
            add_sub_key_step = add_sub_key(mix_column_step, round_key)
            temp_grids.append(add_sub_key_step)

        grids = temp_grids

    # A final round without the mix columns
    temp_grids = []
    round_key = extract_key_for_round(expanded_key, 10)

    for grid in grids:
        # prepare LUTs for the slave and our nestate
        his_luts, my_state_share = prepare_lut_share(grid)
        luts_for_all_rounds.append(his_luts)
        #continue normal AES flow
        shift_rows_step = [rotate_row_left(
            my_state_share[i], i) for i in range(4)]
        add_sub_key_step = add_sub_key(shift_rows_step, round_key)
        temp_grids.append(add_sub_key_step)

    grids = temp_grids

    # Just need to recreate the data into a single stream before returning
    int_stream = []
    
    for grid in grids:
        for column in range(4):
            for row in range(4):
                int_stream.append(grid[row][column])

    return bytes(int_stream)

# For every byte of our AES state share we prepare a masked lookup table
# such that the other party byte is the key and the looked up value becomes 
# its new AES state share.
# For each byte's masked LUT, we apply the same mask.
# 
# The algorithm above is run for every byte (for a total of 16 bytes) of the
# AES state. The masks become our new AES state  

# my_keys are my XOR shares of the AES state which serve as the keys of the LUT
def prepare_lut_share(my_keys):
    my_new_state = []
    # all 16 masked LUTs will go here
    his_luts = []

    for row in my_keys:
        # his luts for one row of the AES state
        his_luts_row = []
        my_new_state_row = []

        for byte in row:
            # for each byte construct a masked LUT for the other party 

            # imagine that the other party's key share is 0, 1, ... 255
            # construct the lookup table for the other party so they could
            # lookup the correct value. Then mask that value. Masks become
            # out new AES state shares
            his_lut = []
            mask = random.randint(0, 255)
            my_new_state_row.append(mask)

            for x in range(0, 256):
                looked_up_value = lookup(byte ^ x)
                his_lut.append(looked_up_value ^ mask)
            his_luts_row.append(his_lut)
        his_luts.append(his_luts_row)
        my_new_state.append(my_new_state_row)

    return his_luts, my_new_state


# for every byte in out state, look up a value and make it
# our new state. The index of the value in the LUT is the key
# by which we perform the lookup
def lookup_in_masked_lut(my_state, lut):
    new_state = []

    for i, row in enumerate(lut):
        new_state_row = []
        for j, col in enumerate(row):
            # lookup a value using our key as the index of the array
            looked_up_val = col[my_state[i][j]]
            new_state_row.append(looked_up_val)
        new_state.append(new_state_row)
    
    return new_state




# master's LUTs will go here
luts_for_all_rounds = []

if __name__ == "__main__":
    # random AES key and random message
    msg_array = [random.randint(0, 255)]*16
    msg = bytes(msg_array)
    key = bytes([random.randint(0, 255)]*16)
    key_sched = expand_key(key, 11)
   
    # split up key schedule into random shares
    master_key_sched_share = [[random.randint(0, 255)]*48]*4
    slave_key_sched_share = []
    for j in range(4):
        row = []
        for i in range(48):
            row.append(key_sched[j][i] ^ master_key_sched_share[j][i])
        slave_key_sched_share.append(row)

    # split up the message into random shares
    master_msg_share_array = [random.randint(0, 255)]*16
    master_msg_share = bytes(master_msg_share_array)
    slave_msg_share_array = []
    for j in range(0,16):
        slave_msg_share_array.append(master_msg_share_array[j] ^ msg_array[j])
    slave_msg_share = bytes(slave_msg_share_array)

    # compute normal AES
    expected = enc(key_sched, msg)

    # Compute master's output. The LUTs which must be passed to slave are put
    # into the global var luts_for_all_rounds
    master_output = enc_master(master_key_sched_share, master_msg_share)
    slave_output = enc_slave(slave_key_sched_share, slave_msg_share)

    aes2pc_output = hex(int.from_bytes(master_output, 'big') ^ int.from_bytes(slave_output, 'big'))

    if '0x'+expected.hex() == aes2pc_output:
        print("aes2pc output matches the expected output")
    else:
        print('Error')
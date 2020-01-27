''' 
prog: algorithm for SDES    
author: Akshay Jadhav
date: 27-01-2020
''' 
import random
from itertools import permutations


# fun: to predict SBOX value 
def getSboxValue(boxNo, bits):
    s0 =    [['01', '00', '11', '10'], 
            ['11', '10', '01', '00'], 
            ['00', '10', '01', '11'], 
            ['11', '01', '11', '10']]
    s1 =    [['00', '01', '10', '11'], 
            ['10', '00', '01', '11'], 
            ['11', '00', '01', '00'], 
            ['10', '01', '00', '11']]

    # find numbers
    rowNo = int(bits[0]+bits[3], 2)
    colNo = int(bits[1]+bits[2], 2)

    if boxNo == 0:
        rowNo = int(bits[0]+bits[3], 2)
        colNo = int(bits[1]+bits[2], 2)
        # return value from s0
        return s0[rowNo][colNo]
    else:
        # return value from s1
        return s1[rowNo][colNo]

# fun: to generate 2 keys
def keyGenerator():
    # 1. generate key 1
    p10 = [str(int(random.random()*100) %2) for _ in range(10)]
    print("random number of 10 bits:", p10)

    # 2. permute the key
    p10 = p10[2] + p10[4] + p10[1] + p10[6] + p10[3] + p10[9] + p10[0] + p10[8] + p10[7] + p10[5] 
    print("after putting into P.10 table: ", p10)

    # 3. divide key into 2 parts
    p10_l = p10[:5]
    p10_r = p10[5:]
    print("dividing key into 2 halves: ", p10_l, " | ", p10_r)

    # 4. apply the one bit Round shift on each half
    p10_l = p10_l[1:] + p10_l[:1]
    p10_r = p10_r[1:] + p10_r[:1]
    print("after 1 bit round shift: ", p10_l, " | ", p10_r)

    # 5. once again combine both halve of the bits, right and left. Put them into the P8 table
    p8 = p10_l + p10_r
    print("before Permute into 8bit table:", p8)

    p8 = p8[5] + p8[2] + p8[6] + p8[3] + p8[7] + p8[4] + p8[9] + p8[8]
    print("after Permute into 8bit table (key1):", p8)

    # 6. use p10_l & p10_r for second key formation
    # 7. apply two round shift circulate on each half of the bits
    p10_l = p10_l[2:] + p10_l[:2]
    p10_r = p10_r[2:] + p10_r[:2]
    print("after 2 bit round shift: ", p10_l, " | ", p10_r)

    # 8. put the bits into 8-P Table, what you get, that will be your second key
    _8p = p10_l + p10_r

    _8p = _8p[5] + _8p[2] + _8p[6] + _8p[3] + _8p[7] + _8p[4] + _8p[9] + _8p[8]
    print("after Permute into 8bit table (key2): ", _8p)

    p8 = ''.join([str(x) for x in p8])
    _8p = ''.join([str(x) for x in _8p])

    return [p8, _8p]


# fun: Encryption of Plain text into Cipher text in S-DES
def partialEncryptor(PT, k):
    k = k
    # 2. Put the plain text into IP-8(initial permutation) table and permute the bits
    ip8 = PT
    print("before IP8:", ip8)
    ip8 = ip8[1] + ip8[5] + ip8[2] + ip8[0] + ip8[3] + ip8[7] + ip8[4] + ip8[6]
    print("after IP8:", ip8)

    # 3. Now break the bits into two halves, each half will consist of 4 bits
    ip8_l = ip8[:4]
    ip8_r = ip8[4:]

    # 4. Take the right 4 bits and put them into E.P (expand and per-mutate) Table
    ep = ip8_r + ip8_r
    print("before putting into EP table: ", ep)
    op = ep[3] + ep[0] + ep[1] + ep[2] + ep[1] + ep[2] + ep[3] + ep[0]
    print("after putting into EP table: ", op)

    # 5. take the output and XOR it with First key Or K 1
    op2 = bin(int(op, 2) ^ int(k, 2))[2:]
    print("output of XOR (op2): ", op2)

    # adjust output for 8 bits
    if len(op2) < 8: op2 = ''.join(['0' for _ in range(8-len(op2))]) + op2 
    print("adjusted op2: ", op2)


    # 6. Once again split the output of XOR’s bit into two halves and each half will  consist of 4 bits
    op2_l = op2[:4] 
    op2_r = op2[4:] 

    #7. now get Values of Sbox & combine together & store into p4
    op3 = getSboxValue(0, op2_l) + getSboxValue(1, op2_r)
    print("op3:", op3)

    # 8. generate value with P4 table
    op4 = op3[1] + op3[3] + op3[2] + op3[0]

    # 9. get XOR the output with left 4 bits of Initial Per-mutation
    # The left bits of initial per-mutation are in step 3

    op5 = bin(int(op4, 2) ^ int(ip8_l, 2))[2:]
    print("op5: ", op5)# adjust output for 8 bits
    if len(op5) < 4: op5 = ''.join(['0' for _ in range(4-len(op5))]) + op5 
    print("adjusted op5: ", op5)

    # 10.  get the right half of the initial permutation, which is step 3, and combine that with this out- put
    op6 = op5 + ip8_r

    # 11. once again break the out-put into two halves, left and right
    op6_l = op6[:4]
    op6_r = op6[4:]

    # 12. Now swap both halves, which means put the left half in place of right and vice versa
    op6_l, op6_r = op6_r, op6_l

    return [op6_l, op6_r]




# 1. take plain text and generate keys
PT = '01110010'
k1, k2 = tuple(keyGenerator())

presult = partialEncryptor(PT, k1)
presult = presult[0] + presult[1]
print("partial result after round 1:", presult)

presult2 = partialEncryptor(presult, k1)
print("partial result after round 2:", presult2)

# 2. Now put result into IP-1 Table which is 
ct = presult[1] + presult[5] + presult[2] + presult[0] + presult[3] + presult[7] + presult[4] + presult[6] 
print("cipher text: ", ct)
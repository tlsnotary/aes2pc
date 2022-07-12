This PoC implements a method of computing AES in the 2PC setting.

At the start of the protocol parties have their XOR shares of AES round keys
and their XOR shares of the message.
At the end, they will have their XOR shares of the ciphertext.

Bandwidth complexity: 40 KB
Round complexity: 0.5 rounds (1 message from Master to Slave)
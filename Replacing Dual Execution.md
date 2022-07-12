#### The problem:

With garbled circuits dual execution (`DE`) approach, it is possible for a malicious `Notary` to leak 1 bit of plaintext with 1/2 success probability.
The approach described below replaces `DE` with `AES2PC`. With this approach a malicious `Notary` can flip arbitrary plaintext bits in 1 AES block (16 bytes) with 1/2^{40} success probability. In other words we will have 2^40 statistical security against `Notary` succeeding in flipping bits.


#### Preliminaries:

Using `AES2PC`(https://github.com/tlsnotary/aes2pc), the `User` and the `Notary` encrypt the counter block with their XOR shares of the AES key to obtain XOR shares of the encrypted counter block (`ECB`). Then the `Notary` passes his `ECB` share to the `User` who gets the full `ECB` and XORs it with his plaintext to obtain the ciphertext which the `User` sends to the webserver.
If the `Notary` cheats about his `ECB` share, then any bits he flipped in his `ECB` share will also be flipped in the plaintext which the webserver will get.


#### Reducing the probability of success:

We describe how to reduce the probability of the Notary succeeding in flipping the bits.

##### Round 1.
Suppose, the `User` needs to produce 32 AES blocks. To do so, the parties run `AES2PC` on 32 inputs. The `Notary` must guess which of the 32 block to attack and to flip its bits. The success rate is 1/2^5.

##### Round 2.
The Parties will again run `AES2PC` on 32 blocks. But this time the `User` will re-randomize the XOR input shares (remember that the input is a counter block which can be split up into XOR shares by the `User` in any way). The `User` knows which instances of `AES2PC` in Round 2 are run on the same inputs as in Round 1. He checks that `ECB`s from Round1 match those from Round2. 
For the `Notary` to succeed, he again has to guess which block in Round 2 to attack and to flip the same bits in that bock as he did in Round 1.
The success rate after 2 rounds is 1/2^5 * 1/2^5 = 1/2^10

##### Following rounds.
We repeat Round2 until we get enough statistical security against the attack. 40 bits is widely considered acceptable.


##### One minor attack.

Instead of guessing the block, the `Notary` can flip the same bits in ALL blocks. To detect this, the `User` does the following:

1. Adds 1 extra block (random bytes) to the 32 blocks, so that starting from Round1 the parties run `AES2PC` on 33 blocks.
2. The parties run `DE` to encrypt this extra block. The `User` checks that the `DE` output matches the output of `AES2PC` for this extra block.

In other words, if the `Notary` was flipping bits in ALL blocks, he would have flipped them also in the extra block. Thanks to `DE` this will be detected. 
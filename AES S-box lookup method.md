AES S-box lookup method.

We describe how two parties (M and S) start with their XOR shares of the key `K` they want to use to lookup some value `V` in the AES S-Box. At the end both parties will obtain their XOR shares of `V`. Neither party will learn `K` or `V`.

Stage 1.
`M` prepares a lookup table (`LUT`) of 256 elements, where:
`LUT` key (a byte from 0 to 255) = potential `S`'s XOR share of the key `K` 
`LUT` value = the value from the S-box which would have been looked up with the `LUT` key


Stage 2.
`M` randomly selects a mask and XOR-masks each `LUT` value. The random mask becomes `M`'s XOR share of `V`.

Stage 3. 
Upon receiving the masked `LUT` from `M`, `S` uses his XOR share of K as the key in the masked `LUT` and looks up the masked value. This masked value becomes `S`'s XOR share of `V`. 

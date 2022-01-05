# `ADT M117` Switches

If you're here, chances are you just want what each switch setting does. Use
the following table as a quick reference, where "X" means "either 'ON' or 'OFF'
is fine":

|SW 4|SW 3|SW 2|SW 1|Start Address  |End Address    |4164 DRAM Banks|41256 DRAM Banks|
|----|----|----|----|---------------|---------------|---------------|----------------|
|X   | OFF| OFF| OFF|This setting does not appear to have been programmed.           |
|X   | OFF| OFF|  ON|0x40000 (256kB)|0x8FFFF (576kB)|2              |1               |
|X   | OFF|  ON| OFF|This setting does not appear to have been programmed.           |
|X   | OFF|  ON|  ON|0x40000 (256kB)|0x9FFFF (640kB)|1,2            |3               |
|X   |  ON| OFF| OFF|This setting does not appear to have been programmed.           |
|X   |  ON| OFF|  ON|0x20000 (128kB)|0x9FFFF (640kB)|None           |2, 3            |
|X   |  ON|  ON| OFF|0x10000 (64kB) |0x9FFFF (640kB)|1              |2, 3            |
|X   |  ON|  ON|  ON|0x60000 (384kB)|0x9FFFF (640kB)|None           |1               |
|OFF |   X|   X|   X|Disable `/IOCHCK` signal/parity checking.                       |
|ON  |   X|   X|   X|Enable `/IOCHCK` signal/parity checking.                        |

If you don't have enough RAM chips to populate all the used banks for a given
switch setting, _always populate Bank 1, then 2, then 3_, or if Bank 1 is unused,
_populate Bank 2, then 3_.

If you want to know more about how I derived the above, read on :)!

## PAL Output Equations

For minimizing, I found it easiest to analyze the PAL for each possible switch
setting. The switch order in each section below from left-to-right is `SW 3`,
`SW 2`, then `SW 1`. _A `SW` == `0` means the switch is in the **ON** position._
So for example, the section "SWs == 100" below means `SW 3` os OFF,
`SW 2` is ON, and `SW 1` is ON. Since `SW 4` enables `/IOCHCHK` and doesn't
connect to the PAL at all, I don't include it in the sections below.

`/` is part of the name of active low signals; it is _not_ part of logic
expressions. `!` is used for logical NOT, e.g. in "`!/REFRESH`". `A16-A19` is
shorthand for concatenating the ISA bus address signals into a 4-bit value,
with `A16` least significant bit and `A19` most significant.

TODO: I have not minimized `/WE All Banks` or `Data Bus /OE` for all possible
switch settings yet.

### SWs == 000

* `/CAS Bank 1 == !((A16-A19 == 6, 7, 8, or 9) && !/REFRESH)`
* `/CAS Bank 2 == 1`
* `/CAS Bank 3 == 1`

### SWs == 001

* `/CAS Bank 1 == !((A16-A19 == 1) && !/REFRESH)`
* `/CAS Bank 2 == !((A16-A19 == 2, 3, 4, or 5) && !/REFRESH)`
* `/CAS Bank 3 == !((A16-A19 == 6, 7, 8, or 9) && !/REFRESH)`

### SWs == 010

* `/CAS Bank 1 == 1`
* `/CAS Bank 2 == !((A16-A19 == 2, 3, 4, or 5) && !/REFRESH)`
* `/CAS Bank 3 == !((A16-A19 == 6, 7, 8, or 9) && !/REFRESH)`

### SWs == 011

* `/WE All Banks == 1`
* `Data Bus /OE == 1`
* `/CAS Bank 1 == 1`
* `/CAS Bank 2 == 1`
* `/CAS Bank 3 == 1`

### SWs == 100

* `/CAS Bank 1 == !((A16-A19 == 4) && !/REFRESH)`
* `/CAS Bank 2 == !((A16-A19 == 5) && !/REFRESH)`
* `/CAS Bank 3 == !((A16-A19 == 6, 7, 8, or 9) && !/REFRESH)`

### SWs == 101

* `/WE All Banks == 1`
* `Data Bus /OE == 1`
* `/CAS Bank 1 == 1`
* `/CAS Bank 2 == 1`
* `/CAS Bank 3 == 1`

### SWs == 110

* `/CAS Bank 1 == !((A16-A19 == 4, 5, 6, or 7) && !/REFRESH)`
* `/CAS Bank 2 == !((A16-A19 == 8) && !/REFRESH)`
* `/CAS Bank 3 == 1`

### SWs == 111

* `/WE All Banks == 1`
* `Data Bus /OE == 1`
* `/CAS Bank 1 == 1`
* `/CAS Bank 2 == 1`
* `/CAS Bank 3 == 1`

### Same regardless of SW:

* `/RAS All Banks == /REFRESH && /SMEMW && /SMEMR`
  * `/CAS Bank 1-3` not being asserted during `/REFRESH` implies RAS-only
    refresh.
* `A8 DRAM All == (!Delayed /SMEM{R,W} && A16) || (Delayed /SMEM{R,W} && A17)`
  * This signal says: "If `A16` is set, then make sure DRAM pin `A8` is set
    when sending the column address. If `A17` is set, make sure DRAM pin `A8`
    is set when sending the row address." The CAS Bank logic ensures only one
    bank of 41256 DRAM responds to `A8` for any given read/write.

    I'm unsure if there's any particular reason to prefer sending `A16` to the
    column address and `A17` to the row address over vice-versa. As long as the
    mapping of each 64kB granularity to each quadrant of 41256 DRAM is
    consistent for read, write, and refresh, the net result should (I hope!) be
    the same.

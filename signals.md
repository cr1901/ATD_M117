# PAL16L8 Signals

This page describes in prose what each pin is doing on the M117's PAL16L8.
Logic equations relating the PAL inputs to the PAL outputs _in terms of switch
settings_ can be found on the [switches](switches.md) page.

## Signal Table

|Signal Name       |Pin Direction|PAL Pin|
|------------------|-------------|-------|
|SW 1              |I            |1      |
|SW 2              |I            |2      |
|SW 3              |I            |3      |
|A16               |I            |4      |
|A17               |I            |5      |
|A18               |I            |6      |
|A19               |I            |7      |
|Delayed /SMEM{R,W}|I            |8      |
|/REFRESH          |I            |9      |
|/SMEMR            |I            |11     |
|DRAM A8 All Banks |O            |12     |
|/CAS Bank 3       |O            |13     |
|/CAS Bank 2       |O            |14     |
|/CAS Bank 1       |O            |15     |
|Data Bus /OE      |O            |16     |
|/RAS All Banks    |O            |17     |
|/SMEMW            |I            |18     |
|/WE All Banks     |O            |19     |

On the PAL16L8, Pins 10 and 20 are GND and Vcc respectively. Pins 13 through 18
inclusive are bidirectional. I had to figure out whether these pins were
input-only, output-only, or bidirectional via REing the schematic. More elegant
solutions like [`pal866`](https://github.com/JohnDMcMaster/pal866) may be able
to automate extracting pin directions.

## Signal Descriptions

* `SW1-3`: These are inputs from switches 1,2, and 3 from the DIP switch
  block in the top-right corner.
* `A16-A19`: ISA bus signals `A16`, `A17`, `A18`, and `A19`. This means the PAL
  decodes addresses with 64kB granularity.
* `Delayed /SMEM{R,W}`: This signal reflects the logic level of (`/SMEMR` AND
  `/SMEMW`) during the _previous_ cycle of the 14.31818 MHz clock. It is used
  as a delay line to split a full DRAM address into a row and column address
  components when a memory access is occurring; row and column addresses are
  multiplexed on the same pins.
* `/REFRESH`: ISA bus `/REFRESH` signal.
* `/SMEMR`: ISA bus `/SMEMR` signal.
* `DRAM A8 All Banks`: On 4164 DRAM, pin 1 is unused and ignored. On 41256 DRAM,
  pin 1 becomes the 9th row and column address input `A8`. The PAL
  automatically determines when its necessary to bring `A8` high. This signal
  goes to all 3 banks of DRAM; see `/CAS Bank` signals.
* `/CAS Bank 3-/CAS Bank 1`: Goes to the `/CAS` pins of DRAM in Banks 3, 2, and
  1 respectively. These signals are one hot; `/CAS` is used to qualify which
  bank actually responds to a read or write, as some signals in this list are
  common to all banks.
* `Data Bus /OE`: _FIXME_: I call this `Data Bus Direction` elsewhere, which is
  a mistake. This signal gates the card from sending/receiving (?) a value
  to/from (?) the entire ISA bus. It connects to the `/OE` of the 74LS245.
* `/RAS All Banks`: Goes to the `/RAS` signal of all DRAM; see `/CAS Bank`
  signals. Useful for DRAM refresh :).
* `/SMEMW`: ISA bus `/SMEMW` signal.
* `/WE All Banks`: Goes to the `/WE` signal of all DRAM; see `/CAS Bank`
  signals.

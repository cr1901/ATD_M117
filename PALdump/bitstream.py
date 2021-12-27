from amaranth import *
from amaranth.lib.cdc import ResetSynchronizer
from amaranth.sim import Simulator

class UARTOut(Elaboratable):
    def __init__(self, div):
        self.tx = Signal(1)
        self.wr = Signal(1)
        self.busy = Signal(1)
        self.dat_w = Signal(8)
        self.div = div

    def elaborate(self, platform):
        if platform:
            uart = platform.request("uart", 0)

        out_count = Signal(range(9))
        shift_count = Signal(range(self.div))
        reg = Signal(10)
        shift_out_stb = Signal(1)

        ###

        m = Module()

        # tx output
        with m.If(self.busy):
            m.d.comb += self.tx.eq(reg[0])
        with m.Else():
            m.d.comb += self.tx.eq(1)

        if platform:
            m.d.comb += uart.tx.eq(self.tx)

        # timing
        with m.If(self.busy):
            m.d.sync += shift_out_stb.eq(0)

            with m.If(shift_count == (self.div - 1)):
                m.d.sync += [
                    shift_out_stb.eq(1),
                    shift_count.eq(0)
                ]
            with m.Else():
                m.d.sync += shift_count.eq(shift_count + 1)

        with m.Else():
            m.d.sync += [
                shift_count.eq(0),
                shift_out_stb.eq(0)
            ]

        # shift reg
        with m.If(self.wr):
            m.d.sync += [
                reg.eq(Cat(0, self.dat_w, 1)),
                self.busy.eq(1)
            ]

        with m.If(self.busy & shift_out_stb):
            m.d.sync += [
                reg[0:9].eq(reg[1:10]),
                reg[9].eq(0)
            ]

            with m.If(out_count == 9):
                m.d.sync += [
                    self.busy.eq(0),
                    out_count.eq(0)
                ]
            with m.Else():
                m.d.sync += [
                    out_count.eq(out_count + 1)
                ]

        return m

def sim_uart():
    uart = UARTOut(int(12e6/3e6))
    sim = Simulator(uart)
    sim.add_clock(1.0/12e6)

    def timer_proc():
        count = 0
        while count < 200:
            yield
            count = count + 1

    sim.add_sync_process(timer_proc)

    def out_proc():
        def write_data(dat):
            yield uart.dat_w.eq(dat)
            yield uart.wr.eq(1)
            yield

            yield uart.wr.eq(0)
            yield

            assert (yield uart.busy)

        def wait():
            while (yield uart.busy):
                yield

        assert not (yield uart.busy)
        yield from write_data(0xAA)
        yield from wait()
        yield from write_data(0x55)
        yield from wait()
        yield from write_data(0x00)
        yield from wait()
        yield from write_data(0xFF)

    sim.add_sync_process(out_proc)

    with sim.write_vcd("uart.vcd", "uart.gtkw"):
        sim.run()


class ClockResetGen(Elaboratable):
    def __init__(self, reset=255):
        self.reset = reset

    def elaborate(self, platform):
        clk = platform.request("clk12", 0)
        rst_button = platform.request("button", 0)
        delay = Signal(range(256), reset=255)

        ###

        m = Module()
        cd_por  = ClockDomain(reset_less=True)
        cd_sync = ClockDomain()
        m.domains += cd_por, cd_sync

        # clk
        m.d.comb += ClockSignal("por").eq(clk)
        m.d.comb += ClockSignal().eq(cd_por.clk)

        # reset
        rst_signal = Signal()
        m.submodules.reset_sync = ResetSynchronizer(rst_signal, domain="sync")
        m.d.comb += rst_signal.eq(rst_button | delay != 0)

        # POR logic
        with m.If(delay != 0):
            m.d.por += delay.eq(delay - 1)

        return m


class PALDumpCore(Elaboratable):
    def __init__(self):
        self.uart = UARTOut(int(12e6/115200))
        self.reset_gen = ClockResetGen()

    def elaborate(self, platform):
        pal_in0 = platform.request("pal_in", 0)
        pal_in1 = platform.request("pal_in", 1)
        pal_out = platform.request("pal_out", 0)
        oe = platform.request("oe", 0)

        led_busy = platform.request("led", 0)
        led_done = platform.request("led", 1)

        in_count = Signal(len(Cat(pal_in0, pal_in1)))

        ###

        m = Module()
        m.submodules.uart = self.uart
        m.submodules.reset_gen = self.reset_gen

        m.d.comb += [
            pal_in0.eq(in_count[0:8]),
            pal_in1.eq(in_count[8:12]),
            self.uart.dat_w[0:7].eq(pal_out),
            self.uart.dat_w[7].eq(0),

            # pal_out[7].eq(1) # OE for level shifter.
            oe.eq(1),

            led_busy.eq(self.uart.busy),
        ]

        with m.FSM() as fsm:
            with m.State("START"):
                m.next = "READ"

            with m.State("READ"):
                with m.If(~self.uart.busy):
                    m.next = "WRITE"

            with m.State("WRITE"):
                m.d.comb += self.uart.wr.eq(1)

                with m.If(in_count == 2047):
                    m.next = "DONE"
                with m.Else():
                    m.d.sync += in_count.eq(in_count + 1)
                    m.next = "READ"

            m.d.comb += led_done.eq(fsm.ongoing("DONE"))
            with m.State("DONE"):
                pass

        return m

if __name__ == "__main__":
    sim_uart()

from . import bitstream
from . import client

import argparse
import sys
from amaranth.build import *
from amaranth_boards import icebreaker
from amaranth_boards.extensions import pmod

def PALResources():
    return [
        Resource("pal_in", 0,
            Pins("1 2 3 4 7 8 9 10", dir="o", conn=("pmod", 0)),
            Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("pal_in", 1,
            Pins("1 2 3", dir="o", conn=("pmod", 1)),
            Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("pal_out", 0,
            Pins("1 2 3 4 7 8 9", dir="i", conn=("pmod", 2)),
            Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("oe", 0,
            Pins("10", dir="o", conn=("pmod", 2)),
            Attrs(IO_STANDARD="SB_LVCMOS")),
    ]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    p_action = parser.add_subparsers(dest="action")
    p_action.add_parser("bitstream")
    p_action.add_parser("client")

    args = parser.parse_args()
    if args.action == "bitstream":
        p = icebreaker.ICEBreakerPlatform()
        p.add_resources(PALResources())
        plan = p.build(bitstream.PALDumpCore(), do_build=False)
        products = plan.execute_local(run_script=True)
        p.toolchain_program(products, "top")

    if args.action == "client":
        pass

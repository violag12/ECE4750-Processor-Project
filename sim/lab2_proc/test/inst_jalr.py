#=========================================================================
# jalr
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """

    # Use r3 to track the control flow pattern
    addi  x3, x0, 0           # 0x0200
                              #
    lui x1,      %hi[label_a] # 0x0204
    addi x1, x1, %lo[label_a] # 0x0208
                              #
    nop                       # 0x020c
    nop                       # 0x0210
    nop                       # 0x0214
    nop                       # 0x0218
    nop                       # 0x021c
    nop                       # 0x0220
    nop                       # 0x0224
    nop                       # 0x0228
                              #
    jalr  x31, x1, 0          # 0x022c
    addi  x3, x3, 0b01        # 0x0230

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

  label_a:
    addi  x3, x3, 0b10

    # Check the link address
    csrw  proc2mngr, x31 > 0x0230

    # Only the second bit should be set if jump was taken
    csrw  proc2mngr, x3  > 0b10

  """


def gen_src_dep_test():
	return [
		gen_jalr_src_dep_test(0, "jalr", 0x210),
		gen_jalr_src_dep_test(1, "jalr", 0x234),
		gen_jalr_src_dep_test(2, "jalr", 0x25c),
		gen_jalr_src_dep_test(3, "jalr", 0x288),
		gen_jalr_src_dep_test(4, "jalr", 0x2b8),
		gen_jalr_src_dep_test(5, "jalr", 0x2ec),
	]

def gen_dest_dep_test():
	return [
		gen_jalr_dest_dep_test(0, "jalr", 0x210),
		gen_jalr_dest_dep_test(1, "jalr", 0x230),
		gen_jalr_dest_dep_test(2, "jalr", 0x254),
		gen_jalr_dest_dep_test(3, "jalr", 0x27c),
		gen_jalr_dest_dep_test(4, "jalr", 0x2a8),
		gen_jalr_dest_dep_test(5, "jalr", 0x2d8),
	]

def gen_value_dep_test():
	return [
		gen_jalr_value_test("jalr", 0x210),
		gen_jalr_value_test("jalr", 0x230),
		gen_jalr_value_test("jalr", 0x250),
		gen_jalr_value_test("jalr", 0x270),
	]




# ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define additional directed and random test cases.
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

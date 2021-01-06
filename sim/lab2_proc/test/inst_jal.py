#=========================================================================
# jal
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
    addi  x3, x0, 0     # 0x0200
                        #
    nop                 # 0x0204
    nop                 # 0x0208
    nop                 # 0x020c
    nop                 # 0x0210
    nop                 # 0x0214
    nop                 # 0x0218
    nop                 # 0x021c
    nop                 # 0x0220
                        #
    jal   x1, label_a   # 0x0224
    addi  x3, x3, 0b01  # 0x0228

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
    csrw  proc2mngr, x1 > 0x0228 

    # Only the second bit should be set if jump was taken
    csrw  proc2mngr, x3 > 0b10

  """

# ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define additional directed and random test cases.
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def gen_multijump_test():
  return """
    
    # use x3 to trac the control flow pattern
    addi x3, x0, 0                                    #0x00000200
    jal  x1, label_a                                  #0x00000204
    addi x3, x3, 0b000001                             #0x00000208
    
  label_b:
    addi x3, x3, 0b000010                             #0x0000020c
    addi x5, x1, 0                                    #0x00000210
    jal  x1, label_c                                  #0x00000214
    addi x1, x3, 0b000100                             #0x00000218

  label_a:
    addi x3, x3, 0b001000                             #0x0000021c
    addi x4, x1, 0                                    #0x00000220
    jal  x1, label_b                                  #0x00000224
    addi x3, x3, 0b010000                             #0x00000228

  label_c:
    addi x3, x3, 0b100000                             #0x0000022c
    addi x6, x1, 0                                    #0x00000230

    csrw proc2mngr, x3 > 0b101010

    #check link addresses
    csrw proc2mngr, x4 > 0x00000208
    csrw proc2mngr, x5 > 0x00000228
    csrw proc2mngr, x6 > 0x00000218
 
  """

def gen_dest_dep_test():
	return[
		gen_jal_dest_dep_test( 5, "jal", 0x00000208),
		gen_jal_dest_dep_test( 4, "jal", 0x00000234),
		gen_jal_dest_dep_test( 3, "jal", 0x0000025c),
		gen_jal_dest_dep_test( 2, "jal", 0x00000280),
		gen_jal_dest_dep_test( 1, "jal", 0x000002a0),
		gen_jal_dest_dep_test( 0, "jal", 0x000002bc),
]

def gen_value_dep_test():
	return[
		gen_jal_value_test("jal", 0x00000208),
		gen_jal_value_test("jal", 0x00000220),
		gen_jal_value_test("jal", 0x00000238),
		gen_jal_value_test("jal", 0x00000250),
		gen_jal_value_test("jal", 0x00000268),
]






#=========================================================================
# lui
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    lui x1, 0x0001
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x1 > 0x00001000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

# ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define additional directed and random test cases.
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
def gen_dest_dep_test():
  return [
    gen_lui_template( 8, 5, "x1", 0x00001, 0x00001000),
    gen_lui_template( 8, 4, "x1", 0x00010, 0x00010000),
    gen_lui_template( 8, 3, "x1", 0x00100, 0x00100000),
    gen_lui_template( 8, 2, "x1", 0x01000, 0x01000000),
    gen_lui_template( 8, 1, "x1", 0x10000, 0x10000000),
    gen_lui_template( 8, 0, "x1", 0x11000, 0x11000000),
  ]

def gen_base_dep_test():
  return [
    gen_lui_template( 5, 8, "x1", 0x00001, 0x00001000),
    gen_lui_template( 4, 8, "x1", 0x00010, 0x00010000),
    gen_lui_template( 3, 8, "x1", 0x00100, 0x00100000),
    gen_lui_template( 2, 8, "x1", 0x01000, 0x01000000),
    gen_lui_template( 1, 8, "x1", 0x10000, 0x10000000),
    gen_lui_template( 0, 8, "x1", 0x11000, 0x11000000),
  ]

#-----------------------------------------------------------------------
# gen_random_test
#-----------------------------------------------------------------------

def gen_random_test():
  asm_code =[]
  for i in xrange(25):
    result = 0
    imm_val = Bits(20, random.randint(0, 0xfffff))
    imm = Bits(32, imm_val * (2**12))
    asm_code.append( gen_lui_template( 0, 0, "x1", imm_val.uint(), imm.uint() ) )
  return asm_code

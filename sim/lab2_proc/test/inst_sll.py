#=========================================================================
# sll
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 0x80008000
    csrr x2, mngr2proc < 0x00000003
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sll x3, x1, x2
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x00040000
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


#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------

def gen_dest_dep_test():
  return [
    gen_rr_dest_dep_test( 5, "sll", 1, 1, 2 ),
    gen_rr_dest_dep_test( 4, "sll", 2, 1, 4 ),
    gen_rr_dest_dep_test( 3, "sll", 3, 1, 6 ),
    gen_rr_dest_dep_test( 2, "sll", 4, 1, 8 ),
    gen_rr_dest_dep_test( 1, "sll", 5, 1, 10 ),
    gen_rr_dest_dep_test( 0, "sll", 6, 1, 12 ),
  ]

#-------------------------------------------------------------------------
# gen_src0_dep_test
#-------------------------------------------------------------------------

def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "sll",  7, 1,  14 ),
    gen_rr_src0_dep_test( 4, "sll",  8, 1,  16 ),
    gen_rr_src0_dep_test( 3, "sll",  9, 1,  18),
    gen_rr_src0_dep_test( 2, "sll", 10, 1,  20),
    gen_rr_src0_dep_test( 1, "sll", 11, 1,  22),
    gen_rr_src0_dep_test( 0, "sll", 12, 1,  24),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_test
#-------------------------------------------------------------------------

def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "sll", 1, 13, 8192 ),
    gen_rr_src1_dep_test( 4, "sll", 1, 14, 16384 ),
    gen_rr_src1_dep_test( 3, "sll", 1, 15, 32768 ),
    gen_rr_src1_dep_test( 2, "sll", 1, 16, 65536 ),
    gen_rr_src1_dep_test( 1, "sll", 1, 17, 131072 ),
    gen_rr_src1_dep_test( 0, "sll", 1, 18, 262144 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_test
#-------------------------------------------------------------------------

def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "sll", -12, 3, -96 ),
    gen_rr_srcs_dep_test( 4, "sll", -23, 3, -184 ),
    gen_rr_srcs_dep_test( 3, "sll", -34, 4, -544 ),
    gen_rr_srcs_dep_test( 2, "sll", -45, 5, -1440 ),
    gen_rr_srcs_dep_test( 1, "sll", -56, 6, -3584 ),
    gen_rr_srcs_dep_test( 0, "sll", -67, 7, -8576 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "sll", 25, 1, 50 ),
    gen_rr_src1_eq_dest_test( "sll", -26, 1, -52 ),
    #gen_rr_src0_eq_src1_test( "sll", 27, 0 ),
    #gen_rr_srcs_eq_dest_test( "sll", 28, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_rr_value_test( "sll", 0, 0, 0 ),
    gen_rr_value_test( "sll", 1, 1, 2 ),
    gen_rr_value_test( "sll", -3, 7, -384),

    gen_rr_value_test( "sll", 0, 14, 0 ),
    gen_rr_value_test( "sll", -2147483648, 0, -2147483648 ),
    gen_rr_value_test( "sll", -2147483648, 14, 0 ),

    gen_rr_value_test( "sll", 32767, 0, 32767 ),
    gen_rr_value_test( "sll", 2147483647, 0, 2147483647 ),
    gen_rr_value_test( "sll", 2147483647, 14, -16384),

    gen_rr_value_test( "sll", 32769, 11, 67110912 ),
    gen_rr_value_test( "sll", -32769, 12, -134221824 ),

    gen_rr_value_test( "sll", 0, 1, 0 ),
    gen_rr_value_test( "sll", 1000, 1, 2000 ),
    gen_rr_value_test( "sll", -100, 1, -200 ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(0,0xffffffff) )
    src1 = Bits( 32, random.randint(0,31) )
    dest = src0 << src1
    asm_code.append( gen_rr_value_test( "sll", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code









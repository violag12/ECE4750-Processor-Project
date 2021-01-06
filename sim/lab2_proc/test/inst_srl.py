#=========================================================================
# srl
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 0x00008000
    csrr x2, mngr2proc < 0x00000003
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    srl x3, x1, x2
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x00001000
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
    gen_rr_dest_dep_test( 5, "srl", 1, 1, 0 ),
    gen_rr_dest_dep_test( 4, "srl", 2, 1, 1 ),
    gen_rr_dest_dep_test( 3, "srl", 3, 1, 1 ),
    gen_rr_dest_dep_test( 2, "srl", 4, 1, 2 ),
    gen_rr_dest_dep_test( 1, "srl", 5, 1, 2 ),
    gen_rr_dest_dep_test( 0, "srl", 6, 1, 3 ),
  ]

#-------------------------------------------------------------------------
# gen_src0_dep_test
#-------------------------------------------------------------------------

def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "srl",  7, 1,  3 ),
    gen_rr_src0_dep_test( 4, "srl",  8, 1,  4 ),
    gen_rr_src0_dep_test( 3, "srl",  9, 1,  4),
    gen_rr_src0_dep_test( 2, "srl", 10, 1,  5),
    gen_rr_src0_dep_test( 1, "srl", 11, 1,  5),
    gen_rr_src0_dep_test( 0, "srl", 12, 1,  6),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_test
#-------------------------------------------------------------------------

def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "srl", 91,  3, 11 ),
    gen_rr_src1_dep_test( 4, "srl", 101, 4, 6 ),
    gen_rr_src1_dep_test( 3, "srl", 111, 5, 3 ),
    gen_rr_src1_dep_test( 2, "srl", 121, 6, 1 ),
    gen_rr_src1_dep_test( 1, "srl", 131, 7, 1 ),
    gen_rr_src1_dep_test( 0, "srl", 1410,8, 5 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_test
#-------------------------------------------------------------------------

def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "srl", -12, 3, 536870910 ),
    gen_rr_srcs_dep_test( 4, "srl", -23, 3, 536870909 ),
    gen_rr_srcs_dep_test( 3, "srl", -34, 4, 268435453 ),
    gen_rr_srcs_dep_test( 2, "srl", -45, 5, 134217726 ),
    gen_rr_srcs_dep_test( 1, "srl", -56, 6, 67108863 ),
    gen_rr_srcs_dep_test( 0, "srl", -67, 7, 33554431 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "srl", 25, 1, 12 ),
    gen_rr_src1_eq_dest_test( "srl", -26,1, 2147483635),
    #gen_rr_src0_eq_src1_test( "srl", 27, 0 ),
    #gen_rr_srcs_eq_dest_test( "srl", 28, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_rr_value_test( "srl", 0, 0, 0 ),
    gen_rr_value_test( "srl", 1, 1, 0 ),
    gen_rr_value_test( "srl", -3, 7, 33554431),

    gen_rr_value_test( "srl", 0, 14, 0 ),
    gen_rr_value_test( "srl", -2147483648, 0, -2147483648 ),
    gen_rr_value_test( "srl", -2147483648, 14, 131072 ),

    gen_rr_value_test( "srl", 32767, 0, 32767 ),
    gen_rr_value_test( "srl", 2147483647, 0, 2147483647 ),
    gen_rr_value_test( "srl", 2147483647, 14, 131071 ),

    gen_rr_value_test( "srl", 32769, 11, 16 ),
    gen_rr_value_test( "srl", -32769, 12, 1048567 ),

    gen_rr_value_test( "srl", 0, 1, 0 ),
    gen_rr_value_test( "srl", 1000, 1, 500 ),
    gen_rr_value_test( "srl", -100, 1, 2147483598),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(0,0xffffffff) )
    src1 = Bits( 32, random.randint(0,31) )
    dest = src0 >> src1
    asm_code.append( gen_rr_value_test( "srl", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code






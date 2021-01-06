#=========================================================================
# slt
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 4
    csrr x2, mngr2proc < 5
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slt x3, x1, x2
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 1
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
    gen_rr_dest_dep_test( 5, "slt", 1, 1, 0 ),
    gen_rr_dest_dep_test( 4, "slt", 2, 1, 0 ),
    gen_rr_dest_dep_test( 3, "slt", 3, 1, 0 ),
    gen_rr_dest_dep_test( 2, "slt", 4, 1, 0 ),
    gen_rr_dest_dep_test( 1, "slt", 5, 1, 0 ),
    gen_rr_dest_dep_test( 0, "slt", 6, 1, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_src0_dep_test
#-------------------------------------------------------------------------

def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "slt",  7, 1,  0 ),
    gen_rr_src0_dep_test( 4, "slt",  8, 1,  0 ),
    gen_rr_src0_dep_test( 3, "slt",  9, 1,  0 ),
    gen_rr_src0_dep_test( 2, "slt", 10, 1,  0 ),
    gen_rr_src0_dep_test( 1, "slt", 11, 1,  0 ),
    gen_rr_src0_dep_test( 0, "slt", 12, 1,  0 ),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_test
#-------------------------------------------------------------------------

def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "slt", 1, 13, 1 ),
    gen_rr_src1_dep_test( 4, "slt", 1, 14, 1 ),
    gen_rr_src1_dep_test( 3, "slt", 1, 15, 1 ),
    gen_rr_src1_dep_test( 2, "slt", 1, 16, 1 ),
    gen_rr_src1_dep_test( 1, "slt", 1, 17, 1 ),
    gen_rr_src1_dep_test( 0, "slt", 1, 18, 1 ),
  ]


#-------------------------------------------------------------------------
# gen_srcs_dep_test
#-------------------------------------------------------------------------

def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "slt", 12, 2,  0 ),
    gen_rr_srcs_dep_test( 4, "slt", -13, 3, 1 ),
    gen_rr_srcs_dep_test( 3, "slt", 14, -4, 0 ),
    gen_rr_srcs_dep_test( 2, "slt", 15, 5,  0 ),
    gen_rr_srcs_dep_test( 1, "slt", 16, -6, 0 ),
    gen_rr_srcs_dep_test( 0, "slt", -17, 7, 1 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "slt", 25, 1, 0 ),
    gen_rr_src1_eq_dest_test( "slt", 26, 1, 0 ),
    gen_rr_src0_eq_src1_test( "slt", 27, 0 ),
    gen_rr_srcs_eq_dest_test( "slt", 28, 0 ),
  ]


#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_rr_value_test( "slt", 0, 0, 0 ),
    gen_rr_value_test( "slt", 1, 1, 0 ),
    gen_rr_value_test( "slt", 3, 7, 1 ),

    gen_rr_value_test( "slt", 0, -32768, 0 ),
    gen_rr_value_test( "slt", -2147483648, 0, 1 ),
    gen_rr_value_test( "slt", -2147483648, -32768, 1 ),

    gen_rr_value_test( "slt", 0, 32767, 1 ),
    gen_rr_value_test( "slt", 2147483647, 0, 0 ),
    gen_rr_value_test( "slt", 2147483647, 32767, 0 ),

    gen_rr_value_test( "slt", -2147483648, -32769, 1 ),
    gen_rr_value_test( "slt", 2147483647, -32768, 0 ),

    gen_rr_value_test( "slt", 0, -1, 0 ),
    gen_rr_value_test( "slt", -1, 1, 1 ),
    gen_rr_value_test( "slt", -1, -1, 0 ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(0,0xffffffff) )
    src1 = Bits( 32, random.randint(0,0xffffffff) )
    temp = sext(src0, 33) - sext(src1, 33)
    dest = temp[32]
    asm_code.append( gen_rr_value_test( "slt", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code


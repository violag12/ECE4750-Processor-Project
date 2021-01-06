#=========================================================================
# sra
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
    sra x3, x1, x2
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
    gen_rr_dest_dep_test( 5, "sra", 1, 1, 0 ),
    gen_rr_dest_dep_test( 4, "sra", 2, 1, 1 ),
    gen_rr_dest_dep_test( 3, "sra", 3, 1, 1 ),
    gen_rr_dest_dep_test( 2, "sra", 4, 1, 2 ),
    gen_rr_dest_dep_test( 1, "sra", 5, 1, 2 ),
    gen_rr_dest_dep_test( 0, "sra", 6, 1, 3 ),
  ]

#-------------------------------------------------------------------------
# gen_src0_dep_test
#-------------------------------------------------------------------------

def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "sra",  7, 1,  3 ),
    gen_rr_src0_dep_test( 4, "sra",  8, 1,  4 ),
    gen_rr_src0_dep_test( 3, "sra",  9, 1,  4 ),
    gen_rr_src0_dep_test( 2, "sra", 10, 1,  5 ),
    gen_rr_src0_dep_test( 1, "sra", 11, 1,  5 ),
    gen_rr_src0_dep_test( 0, "sra", 12, 1,  6 ),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_test
#-------------------------------------------------------------------------

def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "sra", 1, 13, 0 ),
    gen_rr_src1_dep_test( 4, "sra", 1, 14, 0 ),
    gen_rr_src1_dep_test( 3, "sra", 1, 15, 0 ),
    gen_rr_src1_dep_test( 2, "sra", 1, 16, 0 ),
    gen_rr_src1_dep_test( 1, "sra", 1, 17, 0 ),
    gen_rr_src1_dep_test( 0, "sra", 1, 18, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_test
#-------------------------------------------------------------------------

def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "sra", -12, 3, -2 ),
    gen_rr_srcs_dep_test( 4, "sra", -23, 3, -3 ),
    gen_rr_srcs_dep_test( 3, "sra", -34, 4, -3 ),
    gen_rr_srcs_dep_test( 2, "sra", -45, 5, -2 ),
    gen_rr_srcs_dep_test( 1, "sra", -56, 6, -1 ),
    gen_rr_srcs_dep_test( 0, "sra", -67, 7, -1 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "sra", 25, 1, 12 ),
    gen_rr_src1_eq_dest_test( "sra", 26, 1, 13 ),
    #gen_rr_src0_eq_src1_test( "sra", 27, 0 ),
    #gen_rr_srcs_eq_dest_test( "sra", 28, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_rr_value_test( "sra", 0, 0, 0 ),
    gen_rr_value_test( "sra", 1, 1, 0 ),
    gen_rr_value_test( "sra", -3, 7, -1),

    gen_rr_value_test( "sra", 0, 14, 0 ),
    gen_rr_value_test( "sra", -2147483648, 0, -2147483648 ),
    gen_rr_value_test( "sra", -2147483648, 14, -131072 ),

    gen_rr_value_test( "sra", 32767, 0, 32767 ),
    gen_rr_value_test( "sra", 2147483647, 0, 2147483647 ),
    gen_rr_value_test( "sra", 2147483647, 14, 131071 ),

    gen_rr_value_test( "sra", -2147483648, 12, -524288 ),
    gen_rr_value_test( "sra", 2147483647, 12, 524287 ),

    gen_rr_value_test( "sra", 0, 1, 0 ),
    gen_rr_value_test( "sra", 1000, 1, 500 ),
    gen_rr_value_test( "sra", -100, 1, -50 ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(0,0xffffffff) )
    src1 = Bits( 32, random.randint(0,31) )
    temp = sext(src0, 64) >> src1
    dest = temp[0:32]
    asm_code.append( gen_rr_value_test( "sra", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code

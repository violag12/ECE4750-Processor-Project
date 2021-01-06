#=========================================================================
# srli
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
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    srli x3, x1, 0x03
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
    gen_rimm_dest_dep_test( 5, "srli", 1, 1, 0 ),
    gen_rimm_dest_dep_test( 4, "srli", 2, 1, 1 ),
    gen_rimm_dest_dep_test( 3, "srli", 3, 1, 1 ),
    gen_rimm_dest_dep_test( 2, "srli", 4, 1, 2 ),
    gen_rimm_dest_dep_test( 1, "srli", 5, 1, 2 ),
    gen_rimm_dest_dep_test( 0, "srli", 6, 1, 3 ),
  ]

#-------------------------------------------------------------------------
# gen_src_dep_test
#-------------------------------------------------------------------------

def gen_src_dep_test():
  return [
    gen_rimm_src_dep_test( 5, "srli", 91,  3, 11 ),
    gen_rimm_src_dep_test( 4, "srli", 101, 4, 6 ),
    gen_rimm_src_dep_test( 3, "srli", 111, 5, 3 ),
    gen_rimm_src_dep_test( 2, "srli", 121, 6, 1 ),
    gen_rimm_src_dep_test( 1, "srli", 131, 7, 1 ),
    gen_rimm_src_dep_test( 0, "srli", 1410,8, 5 ),
    
    gen_rimm_src_dep_test( 5, "srli", -12, 3, 536870910 ),
    gen_rimm_src_dep_test( 4, "srli", -23, 3, 536870909 ),
    gen_rimm_src_dep_test( 3, "srli", -34, 4, 268435453 ),
    gen_rimm_src_dep_test( 2, "srli", -45, 5, 134217726 ),
    gen_rimm_src_dep_test( 1, "srli", -56, 6, 67108863 ),
    gen_rimm_src_dep_test( 0, "srli", -67, 7, 33554431 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rimm_src_eq_dest_test( "srli", 25, 1, 12 ),
    gen_rimm_src_eq_dest_test( "srli", -26,1, 2147483635),
    #gen_rr_src0_eq_src1_test( "srl", 27, 0 ),
    #gen_rr_srcs_eq_dest_test( "srl", 28, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_rimm_value_test( "srli", 0, 0, 0 ),
    gen_rimm_value_test( "srli", 1, 1, 0 ),
    gen_rimm_value_test( "srli", -3, 7, 33554431),

    gen_rimm_value_test( "srli", 0, 14, 0 ),
    gen_rimm_value_test( "srli", -2147483648, 0, -2147483648 ),
    gen_rimm_value_test( "srli", -2147483648, 14, 131072 ),

    gen_rimm_value_test( "srli", 32767, 0, 32767 ),
    gen_rimm_value_test( "srli", 2147483647, 0, 2147483647 ),
    gen_rimm_value_test( "srli", 2147483647, 14, 131071 ),

    gen_rimm_value_test( "srli", 32769, 11, 16 ),
    gen_rimm_value_test( "srli", -32769, 12, 1048567 ),

    gen_rimm_value_test( "srli", 0, 1, 0 ),
    gen_rimm_value_test( "srli", 1000, 1, 500 ),
    gen_rimm_value_test( "srli", -100, 1, 2147483598),

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
    asm_code.append( gen_rimm_value_test( "srli", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code





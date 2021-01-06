#=========================================================================
# srai
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
    srai x3, x1, 0x03
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
    gen_rimm_dest_dep_test( 5, "srai", 1, 1, 0 ),
    gen_rimm_dest_dep_test( 4, "srai", 2, 1, 1 ),
    gen_rimm_dest_dep_test( 3, "srai", 3, 1, 1 ),
    gen_rimm_dest_dep_test( 2, "srai", 4, 1, 2 ),
    gen_rimm_dest_dep_test( 1, "srai", 5, 1, 2 ),
    gen_rimm_dest_dep_test( 0, "srai", 6, 1, 3 ),
  ]

#-------------------------------------------------------------------------
# gen_src_dep_test
#-------------------------------------------------------------------------

def gen_src_dep_test():
  return [
    gen_rimm_src_dep_test( 5, "srai",  7, 1,  3 ),
    gen_rimm_src_dep_test( 4, "srai",  8, 1,  4 ),
    gen_rimm_src_dep_test( 3, "srai",  9, 1,  4 ),
    gen_rimm_src_dep_test( 2, "srai", 10, 1,  5 ),
    gen_rimm_src_dep_test( 1, "srai", 11, 1,  5 ),
    gen_rimm_src_dep_test( 0, "srai", 12, 1,  6 ),
                                  
    gen_rimm_src_dep_test( 5, "srai", 1, 13, 0 ),
    gen_rimm_src_dep_test( 4, "srai", 1, 14, 0 ),
    gen_rimm_src_dep_test( 3, "srai", 1, 15, 0 ),
    gen_rimm_src_dep_test( 2, "srai", 1, 16, 0 ),
    gen_rimm_src_dep_test( 1, "srai", 1, 17, 0 ),
    gen_rimm_src_dep_test( 0, "srai", 1, 18, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rimm_src_eq_dest_test( "srai", 25, 1, 12 ),
    gen_rimm_src_eq_dest_test( "srai", 26, 1, 13),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_rimm_value_test( "srai", 0, 0, 0 ),
    gen_rimm_value_test( "srai", 1, 1, 0 ),
    gen_rimm_value_test( "srai", -3, 7, -1),

    gen_rimm_value_test( "srai", 0, 14, 0 ),
    gen_rimm_value_test( "srai", -2147483648, 0, -2147483648 ),
    gen_rimm_value_test( "srai", -2147483648, 14, -131072 ),

    gen_rimm_value_test( "srai", 32767, 0, 32767 ),
    gen_rimm_value_test( "srai", 2147483647, 0, 2147483647 ),
    gen_rimm_value_test( "srai", 2147483647, 14, 131071 ),

    gen_rimm_value_test( "srai", -2147483648, 12, -524288 ),
    gen_rimm_value_test( "srai", 2147483647, 12, 524287 ),

    gen_rimm_value_test( "srai", 0, 1, 0 ),
    gen_rimm_value_test( "srai", 1000, 1, 500 ),
    gen_rimm_value_test( "srai", -100, 1, -50),
    
    gen_rimm_value_test( "srai", 2147483647, 31, 0),
    gen_rimm_value_test( "srai", -2147483648, 31, -1),
    
    

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(0,0xffffffff) )
    src1 = Bits( 12, random.randint(0,31) )
    temp = sext(src0, 64) >> src1
    dest = temp[0:32]
    asm_code.append( gen_rimm_value_test( "srai", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code

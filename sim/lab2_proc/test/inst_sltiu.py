#=========================================================================
# sltiu
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 5
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sltiu x3, x1, 6
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

#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------

def gen_dest_dep_test():
  return [
    gen_rimm_dest_dep_test( 5, "sltiu", 1, 1, 0 ),
    gen_rimm_dest_dep_test( 4, "sltiu", 2, 1, 0 ),
    gen_rimm_dest_dep_test( 3, "sltiu", 3, 1, 0 ),
    gen_rimm_dest_dep_test( 2, "sltiu", 4, 1, 0 ),
    gen_rimm_dest_dep_test( 1, "sltiu", 5, 1, 0 ),
    gen_rimm_dest_dep_test( 0, "sltiu", 6, 1, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_src_dep_test
#-------------------------------------------------------------------------

def gen_src_dep_test():
  return [
    gen_rimm_src_dep_test( 5, "sltiu", 7,  1, 0 ),
    gen_rimm_src_dep_test( 4, "sltiu", 8,  1, 0 ),
    gen_rimm_src_dep_test( 3, "sltiu", 9,  1, 0 ),
    gen_rimm_src_dep_test( 2, "sltiu", 10, 1, 0 ),
    gen_rimm_src_dep_test( 1, "sltiu", 11, 1, 0 ),
    gen_rimm_src_dep_test( 0, "sltiu", 12, 1, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rimm_src_eq_dest_test( "sltiu",  25, 1,  0 ),
    gen_rimm_src_eq_dest_test( "sltiu", -26, 1,  0 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [
    gen_rimm_value_test( "sltiu", 0, 0, 0 ),
    gen_rimm_value_test( "sltiu", 1, 1, 0 ),
    gen_rimm_value_test( "sltiu", 3, 7, 1 ),
        
    gen_rimm_value_test( "sltiu", 0, -120, 1 ),
    gen_rimm_value_test( "sltiu", -2147483648, 0, 0 ),
    gen_rimm_value_test( "sltiu", -2147483648, -128, 1 ),
    
    gen_rimm_value_test( "sltiu", -1000, 0x800, 0 ),
    gen_rimm_value_test( "sltiu", 2047, -128, 1 ),
    gen_rimm_value_test( "sltiu", 1000, 4095, 1 ),
         
    gen_rimm_value_test( "sltiu", 0, 2040, 1 ),
    gen_rimm_value_test( "sltiu", 2147483647, 0, 0 ),
    gen_rimm_value_test( "sltiu", 2147483647, 1012, 0 ),
    gen_rimm_value_test( "sltiu", 2147483647, -128, 1 ),
         
    gen_rimm_value_test( "sltiu", 0, -1, 1 ),
    gen_rimm_value_test( "sltiu", -1, 1, 0 ),
    gen_rimm_value_test( "sltiu", -1, -1, 0 ),
    
    gen_rimm_value_test( "sltiu", 4294967168, -128, 0),
  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(0,0xffffffff) )
    src1 = Bits( 12, random.randint(0,0xfff) )
    dest = Bits(32, src0 < sext(src1,32))
    asm_code.append( gen_rimm_value_test( "sltiu", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code

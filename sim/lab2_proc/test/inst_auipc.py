#=========================================================================
# auipc
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    auipc x1, 0x00010                       # PC=0x200
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw  proc2mngr, x1 > 0x00010200
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

#------------------------------------------------------------------------
# gen_template_test
#------------------------------------------------------------------------

def gen_dest_dep_test():
  return [
    gen_auipc_template( 8, 5, "x1", 0x00001, 0x00001200),
    gen_auipc_template( 8, 4, "x1", 0x00010, 0x0001023c),
    gen_auipc_template( 8, 3, "x1", 0x00100, 0x00100274),
    gen_auipc_template( 8, 2, "x1", 0x01000, 0x010002a8),
    gen_auipc_template( 8, 1, "x1", 0x10000, 0x100002d8),
    gen_auipc_template( 8, 0, "x1", 0x11000, 0x11000304),
  ]

def gen_base_dep_test():
  return [
    gen_auipc_template( 5, 8, "x1", 0x00001, 0x00001200),
    gen_auipc_template( 4, 8, "x1", 0x00010, 0x0001023c),
    gen_auipc_template( 3, 8, "x1", 0x00100, 0x00100274),
    gen_auipc_template( 2, 8, "x1", 0x01000, 0x010002a8),
    gen_auipc_template( 1, 8, "x1", 0x10000, 0x100002d8),
    gen_auipc_template( 0, 8, "x1", 0x11000, 0x11000304),
  ]



#Make immidiate random
#for destination start with pc = 0x200

#-----------------------------------------------------------------------
# gen_random_test
#-----------------------------------------------------------------------

def gen_random_test():
  asm_code =[]
  PC = 0x200
  for i in xrange(25):
    result = 0
    imm_val = Bits(20, random.randint(0, 0xfffff))
    imm = Bits(32, imm_val * (2**12))
    pcb = Bits(32, PC)
    result = imm + pcb
    asm_code.append( gen_auipc_template( 0, 0, "x1", imm_val.uint(), result.uint() ) )
    PC = PC + 8
  return asm_code

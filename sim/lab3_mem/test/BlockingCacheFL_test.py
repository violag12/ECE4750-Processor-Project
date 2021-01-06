#=========================================================================
# BlockingCacheFL_test.py
#=========================================================================

from __future__ import print_function

import pytest
import random
import struct
import math

random.seed(0xa4e28cc2)

from pymtl      import *
from pclib.test import mk_test_case_table, run_sim
from pclib.test import TestSource
from pclib.test import TestMemory

from pclib.ifcs import MemMsg,    MemReqMsg,    MemRespMsg
from pclib.ifcs import MemMsg4B,  MemReqMsg4B,  MemRespMsg4B
from pclib.ifcs import MemMsg16B, MemReqMsg16B, MemRespMsg16B

from TestCacheSink   import TestCacheSink
from lab3_mem.BlockingCacheFL import BlockingCacheFL

# We define all test cases here. They will be used to test _both_ FL and
# RTL models.
#
# Notice the difference between the TestHarness instances in FL and RTL.
#
# class TestHarness( Model ):
#   def __init__( s, src_msgs, sink_msgs, stall_prob, latency,
#                 src_delay, sink_delay, CacheModel, check_test, dump_vcd )
#
# The last parameter of TestHarness, check_test is whether or not we
# check the test field in the cacheresp. In FL model we don't care about
# test field and we set cehck_test to be False because FL model is just
# passing through cachereq to mem, so all cachereq sent to the FL model
# will be misses, whereas in RTL model we must set check_test to be True
# so that the test sink will know if we hit the cache properly.

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Model ):

  def __init__( s, src_msgs, sink_msgs, stall_prob, latency,
                src_delay, sink_delay, 
                CacheModel, num_banks, check_test, dump_vcd ):

    # Messge type

    cache_msgs = MemMsg4B()
    mem_msgs   = MemMsg16B()

    # Instantiate models

    s.src   = TestSource   ( cache_msgs.req,  src_msgs,  src_delay  )
    s.cache = CacheModel   ( num_banks = num_banks )
    s.mem   = TestMemory   ( mem_msgs, 1, stall_prob, latency )
    s.sink  = TestCacheSink( cache_msgs.resp, sink_msgs, sink_delay, check_test )

    # Dump VCD

    if dump_vcd:
      s.cache.vcd_file = dump_vcd

    # Connect

    s.connect( s.src.out,       s.cache.cachereq  )
    s.connect( s.sink.in_,      s.cache.cacheresp )

    s.connect( s.cache.memreq,  s.mem.reqs[0]     )
    s.connect( s.cache.memresp, s.mem.resps[0]    )

  def load( s, addrs, data_ints ):
    for addr, data_int in zip( addrs, data_ints ):
      data_bytes_a = bytearray()
      data_bytes_a.extend( struct.pack("<I",data_int) )
      s.mem.write_mem( addr, data_bytes_a )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace() + " " + s.cache.line_trace() + " " \
         + s.mem.line_trace() + " " + s.sink.line_trace()

#-------------------------------------------------------------------------
# make messages
#-------------------------------------------------------------------------

def req( type_, opaque, addr, len, data ):
  msg = MemReqMsg4B()

  if   type_ == 'rd': msg.type_ = MemReqMsg.TYPE_READ
  elif type_ == 'wr': msg.type_ = MemReqMsg.TYPE_WRITE
  elif type_ == 'in': msg.type_ = MemReqMsg.TYPE_WRITE_INIT

  msg.addr   = addr
  msg.opaque = opaque
  msg.len    = len
  msg.data   = data
  return msg

def resp( type_, opaque, test, len, data ):
  msg = MemRespMsg4B()

  if   type_ == 'rd': msg.type_ = MemRespMsg.TYPE_READ
  elif type_ == 'wr': msg.type_ = MemRespMsg.TYPE_WRITE
  elif type_ == 'in': msg.type_ = MemRespMsg.TYPE_WRITE_INIT

  msg.opaque = opaque
  msg.len    = len
  msg.test   = test
  msg.data   = data
  return msg

#----------------------------------------------------------------------
# Test Case: read hit path
#----------------------------------------------------------------------
# The test field in the response message: 0 == MISS, 1 == HIT

def read_hit_1word_clean( base_addr ):
  return [
    #    type  opq  addr      len data                type  opq  test len data
    req( 'in', 0x0, base_addr, 0, 0xdeadbeef ), resp( 'in', 0x0, 0,   0,  0          ),
    req( 'rd', 0x1, base_addr, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0xdeadbeef ),
  ]

#----------------------------------------------------------------------
# Test Case: read hit path -- for set-associative cache
#----------------------------------------------------------------------
# This set of tests designed only for alternative design
# The test field in the response message: 0 == MISS, 1 == HIT

def read_hit_asso( base_addr ):
  return [
    #    type  opq  addr       len data                type  opq  test len data
    req( 'wr', 0x0, 0x00000000, 0, 0xdeadbeef ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'wr', 0x1, 0x00001000, 0, 0x00c0ffee ), resp( 'wr', 0x1, 0,   0,  0          ),
    req( 'rd', 0x2, 0x00000000, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0xdeadbeef ),
    req( 'rd', 0x3, 0x00001000, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x00c0ffee ),
  ]

#----------------------------------------------------------------------
# Test Case: read hit path -- for direct-mapped cache
#----------------------------------------------------------------------
# This set of tests designed only for baseline design

def read_hit_dmap( base_addr ):
  return [
    #    type  opq  addr       len data                type  opq  test len data
    req( 'wr', 0x0, 0x00000000, 0, 0xdeadbeef ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'wr', 0x1, 0x00000080, 0, 0x00c0ffee ), resp( 'wr', 0x1, 0,   0,  0          ),
    req( 'rd', 0x2, 0x00000000, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0xdeadbeef ),
    req( 'rd', 0x3, 0x00000080, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x00c0ffee ),
  ]

#-------------------------------------------------------------------------
# Test Case: write hit path
#-------------------------------------------------------------------------

def write_hit_1word_clean( base_addr ):
  return [
    #    type  opq   addr      len data               type  opq   test len data
    req( 'in', 0x00, base_addr, 0, 0x0a0b0c0d ), resp('in', 0x00, 0,   0,  0          ), # write word  0x00000000
    req( 'wr', 0x01, base_addr, 0, 0xbeefbeeb ), resp('wr', 0x01, 1,   0,  0          ), # write word  0x00000000
    req( 'rd', 0x02, base_addr, 0, 0          ), resp('rd', 0x02, 1,   0,  0xbeefbeeb ), # read  word  0x00000000
  ]

#-------------------------------------------------------------------------
# Test Case: read miss path
#-------------------------------------------------------------------------

def read_miss_1word_msg( base_addr ):
  return [
    #    type  opq   addr      len  data               type  opq test len  data
    req( 'rd', 0x00, 0x00000000, 0, 0          ), resp('rd', 0x00, 0, 0, 0xdeadbeef ), # read word  0x00000000
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ), # read word  0x00000004
  ]

# Data to be loaded into memory before running the test

def read_miss_1word_mem( base_addr ):
  return [
    # addr      data (in int)
    0x00000000, 0xdeadbeef,
    0x00000004, 0x00c0ffee,
  ]

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# LAB TASK: Add more test cases
#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def write_miss_read_hit( base_addr ):
  return [
	#    type  opq  addr       len data                type  opq  test len data
    req( 'wr', 0x0, 0x00000000, 0, 0xdeadbeef ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'wr', 0x1, 0x00000010, 0, 0x00c0ffee ), resp( 'wr', 0x1, 0,   0,  0          ),
	req( 'wr', 0x2, 0x00000020, 0, 0x0a0b0c0d ), resp( 'wr', 0x2, 0,   0,  0          ),
    req( 'wr', 0x3, 0x00000040, 0, 0x09876543 ), resp( 'wr', 0x3, 0,   0,  0          ),
	
	req( 'rd', 0x4, 0x00000000, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0xdeadbeef ),
    req( 'rd', 0x5, 0x00000010, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x00c0ffee ),
	req( 'rd', 0x6, 0x00000020, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x0a0b0c0d ),
    req( 'rd', 0x7, 0x00000040, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x09876543 ),
  ]

def WER_2wrM_2wrEv_2rdH_2rdM_dmap( base_addr ):
  return [
	#    type  opq  addr       len data                type  opq  test len data
    req( 'wr', 0x0, 0x00000000, 0, 0xdeadbeef ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'wr', 0x1, 0x00000080, 0, 0x00c0ffee ), resp( 'wr', 0x1, 0,   0,  0          ),
	req( 'wr', 0x2, 0x00000100, 0, 0x0a0b0c0d ), resp( 'wr', 0x2, 0,   0,  0          ),
    req( 'wr', 0x3, 0x00000180, 0, 0x09876543 ), resp( 'wr', 0x3, 0,   0,  0          ),
	
	req( 'rd', 0x6, 0x00000100, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x0a0b0c0d ),
    req( 'rd', 0x7, 0x00000180, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x09876543 ),
	req( 'rd', 0x4, 0x00000000, 0, 0          ), resp( 'rd', 0x4, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x5, 0x00000080, 0, 0          ), resp( 'rd', 0x5, 0,   0,  0x00c0ffee ),
  ]

def read_hit_clean( base_addr ):
  return [
    #    type  opq  addr            len data                type  opq  test len data
    req( 'in', 0x0, base_addr + 0x0, 0, 0xdeadbeef ),  resp('in', 0x0, 0,   0,  0          ),
    req( 'wr', 0x1, base_addr + 0x14, 0,0x00c0ffee ), resp( 'wr', 0x1, 0,   0,  0          ),
    req( 'wr', 0x2, base_addr + 0x28, 0,0x0a0b0c0d ), resp( 'wr', 0x2, 0,   0,  0          ),
    req( 'wr', 0x3, base_addr + 0x3c, 0,0x09876543 ), resp( 'wr', 0x3, 0,   0,  0          ),

    req( 'rd', 0x4, base_addr + 0x0, 0, 0          ),  resp( 'rd', 0x4, 1,   0,  0xdeadbeef ),
    req( 'rd', 0x5, base_addr + 0x14, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x00c0ffee ),
    req( 'rd', 0x6, base_addr + 0x28, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x0a0b0c0d ),
    req( 'rd', 0x7, base_addr + 0x3c, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x09876543 ),
  ]

#having trouble changing the tags in this test below
#read hit path
def read_hit_dmap_G( base_addr ):
  return [
    #    type  opq  addr       len data                type  opq  test len data
    req( 'wr', 0x0, 0x00002000, 0, 0xdeadbeef ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'wr', 0x1, 0x00003080, 0, 0x00c0ffee ), resp( 'wr', 0x1, 0,   0,  0          ),
    req( 'rd', 0x2, 0x00002000, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0xdeadbeef ),
    req( 'rd', 0x3, 0x00003080, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x00c0ffee ),
    req( 'wr', 0x0, 0x00001000, 0, 0x0a0b0c0d ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'wr', 0x1, 0x00004080, 0, 0x00c0ffee ), resp( 'wr', 0x1, 0,   0,  0          ),
    req( 'rd', 0x2, 0x00002000, 0, 0          ), resp( 'rd', 0x2, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x3, 0x00003080, 0, 0          ), resp( 'rd', 0x3, 0,   0,  0x00c0ffee ),
    req( 'rd', 0x2, 0x00001000, 0, 0          ), resp( 'rd', 0x2, 0,   0,  0x0a0b0c0d ),
    req( 'rd', 0x3, 0x00004080, 0, 0          ), resp( 'rd', 0x3, 0,   0,  0x00c0ffee ),
  ]

def write_hit_clean( base_addr ):
  return [
    #    type  opq   addr      len data               type  opq   test len data
    req( 'wr', 0x00,  base_addr, 0, 0xdeadbeef ), resp('wr', 0x00, 0,   0,  0          ),
    req( 'wr', 0x03, 0x00000080, 0, 0xdeadbeef ), resp('wr', 0x03, 0,   0,  0          ),
    req( 'wr', 0x01,  base_addr, 0, 0x09876543 ), resp('wr', 0x01, 1,   0,  0          ),
    req( 'rd', 0x02,  base_addr, 0, 0          ), resp('rd', 0x02, 1,   0,  0x09876543 ),
    req( 'wr', 0x01, 0x00000080, 0, 0x09876543 ), resp('wr', 0x01, 1,   0,  0          ),
    req( 'rd', 0x02, 0x00000080, 0, 0          ), resp('rd', 0x02, 1,   0,  0x09876543 ),
  ]

def read_hit_dirty( base_addr ):
   return [
     #    type  opq   addr      len data               		type  opq   test len data
     req( 'wr', 0x0, base_addr + 0x0, 0, 0xdeadbeef ), resp( 'wr', 0x0, 0,   0,  0          ),
     req( 'wr', 0x1, base_addr + 0x4, 0, 0x09876543 ), resp( 'wr', 0x1, 1,   0,  0          ),
     req( 'wr', 0x2, base_addr + 0x8, 0, 0x00c0ffee ), resp( 'wr', 0x2, 1,   0,  0          ),
     req( 'wr', 0x3, base_addr + 0xc, 0, 0x0a0b0c0d ), resp( 'wr', 0x3, 1,   0,  0          ),

     req( 'rd', 0x4, base_addr + 0x0, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0xdeadbeef ),
     req( 'rd', 0x5, base_addr + 0x4, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x09876543 ),
     req( 'rd', 0x6, base_addr + 0x8, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x00c0ffee ),
     req( 'rd', 0x7, base_addr + 0xc, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x0a0b0c0d ),
     req( 'wr', 0x4, base_addr + 0x0, 0, 0x12345678 ), resp( 'wr', 0x4, 1,   0,  0          ),
     req( 'wr', 0x5, base_addr + 0x4, 0, 0xace0ace0 ), resp( 'wr', 0x5, 1,   0,  0          ),
     req( 'wr', 0x6, base_addr + 0x8, 0, 0x32101230 ), resp( 'wr', 0x6, 1,   0,  0          ),
     req( 'wr', 0x7, base_addr + 0xc, 0, 0x1a1a1a1a ), resp( 'wr', 0x7, 1,   0,  0          ),
     req( 'rd', 0x4, base_addr + 0x0, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x12345678 ),
     req( 'rd', 0x5, base_addr + 0x4, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0xace0ace0 ),
     req( 'rd', 0x6, base_addr + 0x8, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x32101230 ),
     req( 'rd', 0x7, base_addr + 0xc, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x1a1a1a1a ),
   ]

def write_hit_dirty( base_addr ):
  return [
    #    type  opq   addr      len data               type  opq   test len data
    req( 'in', 0x00, base_addr, 0, 0x0a0b0c0d ), resp('in', 0x00, 0,   0,  0          ),
    req( 'wr', 0x01, base_addr, 0, 0xdeadbeef ), resp('wr', 0x01, 1,   0,  0          ),
    req( 'rd', 0x02, base_addr, 0, 0          ), resp('rd', 0x02, 1,   0,  0xdeadbeef ),
    req( 'wr', 0x01, base_addr, 0, 0x0a0b0c0d ), resp('wr', 0x01, 1,   0,  0          ),
    req( 'rd', 0x02, base_addr, 0, 0          ), resp('rd', 0x02, 1,   0,  0x0a0b0c0d ),
  ]

def read_miss_mem( base_addr ):
  return [
    # addr      data (in int)
    0x00000000, 0xdeadbeef,
    0x00000004, 0x00c0ffee,
    0x00021000, 0xace0ace0,
    0x00021004, 0x1a1a1a1a,
  ]

#Read miss with refill and no eviction
def read_miss_refill_NoEv( base_addr ):
  return [
    #    type  opq   addr      len  data               type  opq test len  data
    req( 'rd', 0x00, 0x00000000, 0, 0          ), resp('rd', 0x00, 0, 0, 0xdeadbeef ), 
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
  ]

#Read miss with refill and eviction
def read_miss_refill_NoEv_dmap( base_addr ):
   return [
     #    type  opq   addr      len  data               type  opq test len  data
     req( 'rd', 0x00, 0x00000000, 0, 0          ), resp('rd', 0x00, 0, 0, 0xdeadbeef ),
     req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
     req( 'rd', 0x00, 0x00021000, 0, 0          ), resp('rd', 0x00, 0, 0, 0xace0ace0 ),
     req( 'rd', 0x00, 0x00021004, 0, 0          ), resp('rd', 0x00, 1, 0, 0x1a1a1a1a ),
     req( 'rd', 0x00, 0x00000000, 0, 0          ), resp('rd', 0x00, 0, 0, 0xdeadbeef ),
     req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
   ]

def write_miss_mem( base_addr ):
  return [
    # addr      data (in int)
    0x00000000, 0xdeadbeef,
    0x00000004, 0xdeadbeef,
    0x00021000, 0xdeadbeef,
    0x00021004, 0xdeadbeef,
  ]

#Write miss with refill and no eviction
def write_miss_refill_NoEv( base_addr ):
  return [
    #    type  opq   addr       len  data               type  opq test len  data
    req( 'wr', 0x00, 0x00000000, 0, 0x00c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0xdeadbeef ),
    req( 'wr', 0x00, 0x00000004, 0, 0x00c0ffee ), resp('wr', 0x00, 1, 0, 0          ),
    req( 'rd', 0x01, 0x00000000, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
  ]

def write_miss_refill_NoEv_dmap( base_addr ):
   return [
     #    type  opq   addr      len  data               type  opq test len  data
    req( 'wr', 0x00, 0x00000000, 0, 0x00c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0xdeadbeef ),
    req( 'wr', 0x00, 0x00000004, 0, 0x00c0ffee ), resp('wr', 0x00, 1, 0, 0          ),
    req( 'rd', 0x01, 0x00000000, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
    req( 'wr', 0x00, 0x00021000, 0, 0x00c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'rd', 0x01, 0x00021004, 0, 0          ), resp('rd', 0x01, 1, 0, 0xdeadbeef ),
    req( 'wr', 0x00, 0x00021004, 0, 0x00c0ffee ), resp('wr', 0x00, 1, 0, 0          ),
    req( 'rd', 0x01, 0x00021000, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
    req( 'rd', 0x01, 0x00021004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
    req( 'rd', 0x01, 0x00000000, 0, 0          ), resp('rd', 0x01, 0, 0, 0x00c0ffee ),
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
   ]

#read miss with eviction
def read_miss_mem_2( base_addr ):
  return [
    # addr      data (in int)
    0x00000000, 0xdeadbeef,
    0x00000004, 0x00c0ffee,
    0x00001000, 0x98765432,
    0x00001004, 0xace0ace0,
    0x00002000, 0x1a1a1a1a,
    0x00002004, 0x1a1a1a1a,
  ]

def read_miss_refill_WiEv_dmap( base_addr ):
   return [
     #    type  opq   addr      len  data               type  opq test len  data
     req( 'rd', 0x00, 0x00000000, 0, 0          ), resp('rd', 0x00, 0, 0, 0xdeadbeef ),
     req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
     req( 'wr', 0x02, 0x00001000, 0, 0x2b2b2b2b ), resp('wr', 0x02, 0, 0, 0			),
     req( 'wr', 0x03, 0x00001004, 0, 0x3c3c3c3c ), resp('wr', 0x03, 1, 0, 0			),
     req( 'rd', 0x00, 0x00001000, 0, 0          ), resp('rd', 0x00, 1, 0, 0x2b2b2b2b ),
     req( 'rd', 0x00, 0x00001004, 0, 0          ), resp('rd', 0x00, 1, 0, 0x3c3c3c3c ),
     req( 'rd', 0x00, 0x00000000, 0, 0          ), resp('rd', 0x00, 0, 0, 0xdeadbeef ),
     req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
     req( 'wr', 0x02, 0x00000000, 0, 0xf1f1f1f1 ), resp('wr', 0x02, 1, 0, 0			),
     req( 'wr', 0x03, 0x00000004, 0, 0xe3e3e3e3 ), resp('wr', 0x03, 1, 0, 0			),
     req( 'rd', 0x00, 0x00002000, 0, 0          ), resp('rd', 0x00, 0, 0, 0x1a1a1a1a ),
     req( 'rd', 0x01, 0x00002004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x1a1a1a1a ),
     req( 'wr', 0x02, 0x00002000, 0, 0x03050709 ), resp('wr', 0x02, 1, 0, 0			),
     req( 'wr', 0x03, 0x00002004, 0, 0x20406080 ), resp('wr', 0x03, 1, 0, 0			),
     req( 'rd', 0x00, 0x00001000, 0, 0          ), resp('rd', 0x00, 0, 0, 0x2b2b2b2b ),
     req( 'rd', 0x00, 0x00001004, 0, 0          ), resp('rd', 0x00, 1, 0, 0x3c3c3c3c ),
     req( 'rd', 0x00, 0x00001000, 0, 0          ), resp('rd', 0x00, 1, 0, 0x2b2b2b2b  ),
     req( 'rd', 0x00, 0x00001000, 0, 0          ), resp('rd', 0x00, 1, 0, 0x2b2b2b2b  ),
   ]

#fill the cache
def fill_cache_mem_dmap( base_addr ):
   return [
     # addr      data (in int)
     0x00020000, 0x00adbeef,
     0x00020010, 0x01adbeef,
     0x00020020, 0x02adbeef,
     0x00020030, 0x03adbeef,
     0x00020040, 0x04adbeef,
     0x00020050, 0x05adbeef,
     0x00020060, 0x06adbeef,
     0x00020070, 0x07adbeef,
     0x00020080, 0x08adbeef,
     0x00020090, 0x09adbeef,
     0x000200a0, 0x10adbeef,
     0x000200b0, 0x11adbeef,
     0x000200c0, 0x12adbeef,
     0x000200d0, 0x13adbeef,
     0x000200e0, 0x14adbeef,
     0x000200f0, 0x15adbeef,
   ]

def fill_cache_dmap( base_addr ):
    return [
      #    type  opq   addr      len  data               type  opq test len  data
      req( 'rd', 0x00, 0x00020000, 0, 0          ), resp('rd', 0x00, 0, 0, 0x00adbeef ),
      req( 'rd', 0x00, 0x00020010, 0, 0          ), resp('rd', 0x00, 0, 0, 0x01adbeef ),
      req( 'rd', 0x00, 0x00020020, 0, 0          ), resp('rd', 0x00, 0, 0, 0x02adbeef ),
      req( 'rd', 0x00, 0x00020030, 0, 0          ), resp('rd', 0x00, 0, 0, 0x03adbeef ),
      req( 'rd', 0x00, 0x00020040, 0, 0          ), resp('rd', 0x00, 0, 0, 0x04adbeef ),
      req( 'rd', 0x00, 0x00020050, 0, 0          ), resp('rd', 0x00, 0, 0, 0x05adbeef ),
      req( 'rd', 0x00, 0x00020060, 0, 0          ), resp('rd', 0x00, 0, 0, 0x06adbeef ),
      req( 'rd', 0x00, 0x00020070, 0, 0          ), resp('rd', 0x00, 0, 0, 0x07adbeef ),
      req( 'rd', 0x00, 0x00020080, 0, 0          ), resp('rd', 0x00, 0, 0, 0x08adbeef ),
      req( 'rd', 0x00, 0x00020090, 0, 0          ), resp('rd', 0x00, 0, 0, 0x09adbeef ),
      req( 'rd', 0x00, 0x000200a0, 0, 0          ), resp('rd', 0x00, 0, 0, 0x10adbeef ),
      req( 'rd', 0x00, 0x000200b0, 0, 0          ), resp('rd', 0x00, 0, 0, 0x11adbeef ),
      req( 'rd', 0x00, 0x000200c0, 0, 0          ), resp('rd', 0x00, 0, 0, 0x12adbeef ),
      req( 'rd', 0x00, 0x000200d0, 0, 0          ), resp('rd', 0x00, 0, 0, 0x13adbeef ),
      req( 'rd', 0x00, 0x000200e0, 0, 0          ), resp('rd', 0x00, 0, 0, 0x14adbeef ),
      req( 'rd', 0x00, 0x000200f0, 0, 0          ), resp('rd', 0x00, 0, 0, 0x15adbeef ),
      req( 'rd', 0x00, 0x00020000, 0, 0          ), resp('rd', 0x00, 1, 0, 0x00adbeef ),
      req( 'rd', 0x00, 0x00020010, 0, 0          ), resp('rd', 0x00, 1, 0, 0x01adbeef ),
      req( 'rd', 0x00, 0x00020020, 0, 0          ), resp('rd', 0x00, 1, 0, 0x02adbeef ),
      req( 'rd', 0x00, 0x00020030, 0, 0          ), resp('rd', 0x00, 1, 0, 0x03adbeef ),
      req( 'rd', 0x00, 0x00020040, 0, 0          ), resp('rd', 0x00, 1, 0, 0x04adbeef ),
      req( 'rd', 0x00, 0x00020050, 0, 0          ), resp('rd', 0x00, 1, 0, 0x05adbeef ),
      req( 'rd', 0x00, 0x00020060, 0, 0          ), resp('rd', 0x00, 1, 0, 0x06adbeef ),
      req( 'rd', 0x00, 0x00020070, 0, 0          ), resp('rd', 0x00, 1, 0, 0x07adbeef ),
      req( 'rd', 0x00, 0x00020080, 0, 0          ), resp('rd', 0x00, 1, 0, 0x08adbeef ),
      req( 'rd', 0x00, 0x00020090, 0, 0          ), resp('rd', 0x00, 1, 0, 0x09adbeef ),
      req( 'rd', 0x00, 0x000200a0, 0, 0          ), resp('rd', 0x00, 1, 0, 0x10adbeef ),
      req( 'rd', 0x00, 0x000200b0, 0, 0          ), resp('rd', 0x00, 1, 0, 0x11adbeef ),
      req( 'rd', 0x00, 0x000200c0, 0, 0          ), resp('rd', 0x00, 1, 0, 0x12adbeef ),
      req( 'rd', 0x00, 0x000200d0, 0, 0          ), resp('rd', 0x00, 1, 0, 0x13adbeef ),
      req( 'rd', 0x00, 0x000200e0, 0, 0          ), resp('rd', 0x00, 1, 0, 0x14adbeef ),
      req( 'rd', 0x00, 0x000200f0, 0, 0          ), resp('rd', 0x00, 1, 0, 0x15adbeef ),
	  ]

def conflict_misses_dmap( base_addr ):
    return [
      #    type  opq   addr      len  data               type  opq test len  data
      req( 'wr', 0x00, 0x00000000, 0, 0x1a1a1a1a ), resp('wr', 0x00, 0, 0, 0          ),
      req( 'wr', 0x00, 0x00001000, 0, 0x98765432 ), resp('wr', 0x00, 0, 0, 0          ),
      req( 'rd', 0x01, 0x00000000, 0, 0          ), resp('rd', 0x01, 0, 0, 0x1a1a1a1a ),
      req( 'rd', 0x01, 0x00001000, 0, 0          ), resp('rd', 0x01, 0, 0, 0x98765432 ),
      req( 'wr', 0x00, 0x00002000, 0, 0x00adbeef ), resp('wr', 0x00, 0, 0, 0          ),
      req( 'rd', 0x01, 0x00000000, 0, 0          ), resp('rd', 0x01, 0, 0, 0x1a1a1a1a ),
      req( 'rd', 0x01, 0x00001000, 0, 0          ), resp('rd', 0x01, 0, 0, 0x98765432 ),
      req( 'wr', 0x00, 0x00000000, 0, 0x1a1a1a1a ), resp('wr', 0x00, 0, 0, 0          ),
      req( 'wr', 0x00, 0x00000004, 0, 0x2b2b2b2b ), resp('wr', 0x00, 1, 0, 0          ),
      req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x2b2b2b2b ),
      req( 'rd', 0x01, 0x00000000, 0, 0          ), resp('rd', 0x01, 1, 0, 0x1a1a1a1a ),
      req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x2b2b2b2b ),
      req( 'wr', 0x00, 0x00001000, 0, 0x98765432 ), resp('wr', 0x00, 0, 0, 0          ),
      req( 'wr', 0x00, 0x00001004, 0, 0x1a1a1a1a ), resp('wr', 0x00, 1, 0, 0          ),
      req( 'rd', 0x01, 0x00001000, 0, 0          ), resp('rd', 0x01, 1, 0, 0x98765432 ),
      req( 'rd', 0x01, 0x00001004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x1a1a1a1a ),
      req( 'rd', 0x01, 0x00000000, 0, 0          ), resp('rd', 0x01, 0, 0, 0x1a1a1a1a ),
      req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x2b2b2b2b ),
      req( 'wr', 0x00, 0x00002000, 0, 0x11adbeef ), resp('wr', 0x00, 0, 0, 0          ),
      req( 'rd', 0x01, 0x00001000, 0, 0          ), resp('rd', 0x01, 0, 0, 0x98765432 ),
      req( 'rd', 0x01, 0x00000000, 0, 0          ), resp('rd', 0x01, 0, 0, 0x1a1a1a1a ),
      req( 'rd', 0x01, 0x00002000, 0, 0          ), resp('rd', 0x01, 0, 0, 0x11adbeef ),
    ]

def capacity_misses( base_addr ):
  return [
    #    type  opq   addr      len  data               type  opq test len  data
    req( 'wr', 0x00, 0x00000001, 0, 0x00c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x00000011, 0, 0x01c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x00000021, 0, 0x02c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x00000031, 0, 0x03c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x00000041, 0, 0x04c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x00000051, 0, 0x05c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x00000061, 0, 0x06c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x00000071, 0, 0x07c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x00000081, 0, 0x08c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x00000091, 0, 0x09c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x000000a1, 0, 0x10c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x000000b1, 0, 0x11c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x000000c1, 0, 0x12c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x000000d1, 0, 0x13c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x000000e1, 0, 0x14c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x000000f1, 0, 0x15c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x00000101, 0, 0x16c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x00000111, 0, 0x17c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x00000121, 0, 0x18c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x00000131, 0, 0x19c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
  ]

#----------------------------------------------------------------------
# Banked cache test
#----------------------------------------------------------------------
# The test field in the response message: 0 == MISS, 1 == HIT

# This test case is to test if the bank offset is implemented correctly.
#
# The idea behind this test case is to differentiate between a cache
# with no bank bits and a design has one/two bank bits by looking at cache
# request hit/miss status.

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# LAB TASK:
#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# [31 tag 		8|7  idx    4| 3 offset 0]
# [31 tag 10|9 idx 6|5 bank 4| 3 offset 0]
# x00000080 = 1 in 7th bit 
#	--> in original:	idx = 1000 --> 8th idx
#	--> in banked:		idx = 0010 --> 2nd  idx and bank = 00 --> 0th bank
# x00000280 = 1 in 9th and 7th bits
#	--> in original:	idx = 1000 --> 8th idx
#	--> in banked:		idx = 1010 --> 10th idx and bank = 00 --> 0th bank
# x000003F0 = 1 from [9:4]
#	--> in original:	idx = 1111 --> 16th idx
#	--> in banked:		idx = 1111 --> 16th idx and bank = 11 --> 3rd bank
# x000003E0 = 1 from [9:5]
#	--> in original:	idx = 1110 --> 15th idx
##	--> in banked:		idx = 1111 --> 16th idx and bank = 10 --> 2nd bank

def NoBank_4WM_2RM_2RH_dmap( base_addr):
	return[
	#    type  opq  addr       len data                type  opq  test len data
	req( 'wr', 0x0, 0x00000080, 0, 0xdeadbeef ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'wr', 0x1, 0x00000280, 0, 0x00c0ffee ), resp( 'wr', 0x1, 0,   0,  0          ),
	req( 'wr', 0x2, 0x000003F0, 0, 0x0a0b0c0d ), resp( 'wr', 0x2, 0,   0,  0          ),
	req( 'wr', 0x3, 0x000003E0, 0, 0x09876543 ), resp( 'wr', 0x3, 0,   0,  0          ),

    req( 'rd', 0x5, 0x000003F0, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x0a0b0c0d ),
	req( 'rd', 0x7, 0x000003E0, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x09876543 ),
	req( 'rd', 0x6, 0x00000080, 0, 0          ), resp( 'rd', 0x6, 0,   0,  0xdeadbeef ),
	req( 'rd', 0x4, 0x00000280, 0, 0          ), resp( 'rd', 0x4, 0,   0,  0x00c0ffee ),
	]

def W4Bank_4WM_4RM_dmap( base_addr):
	return[
	#    type  opq  addr       len data                type  opq  test len data
	req( 'wr', 0x0, 0x00000080, 0, 0xdeadbeef ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'wr', 0x1, 0x00000280, 0, 0x00c0ffee ), resp( 'wr', 0x1, 0,   0,  0          ),
	req( 'wr', 0x2, 0x000003F0, 0, 0x0a0b0c0d ), resp( 'wr', 0x2, 0,   0,  0          ),
	req( 'wr', 0x3, 0x000003E0, 0, 0x09876543 ), resp( 'wr', 0x3, 0,   0,  0          ),
	
	req( 'rd', 0x5, 0x000003F0, 0, 0          ), resp( 'rd', 0x5, 0,   0,  0x0a0b0c0d ),
	req( 'rd', 0x7, 0x000003E0, 0, 0          ), resp( 'rd', 0x7, 0,   0,  0x09876543 ),
	req( 'rd', 0x6, 0x00000080, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0xdeadbeef ),
	req( 'rd', 0x4, 0x00000280, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x00c0ffee ),
	]


#----------------------------------------
# Random Tests
#----------------------------------------
def mk_req( type_, addr, len_, data ):
  return req( type_, 0, addr, len_, data )

def mk_resp( type_, len_, data ):
  return resp( type_, 0, 0, len_, data )

Num_of_Rand_Tests = 100

#Simple address patterns, single request type, with random data
#Only Read - read_only
rand_msg_0  = []
mem_data_0  = []
addr_0 = 0
for i in xrange( Num_of_Rand_Tests ):
	addr_0 = i*16
	data_0 = random.randint(0,2147483647)
  	mem_data_0.append( addr_0 )
  	mem_data_0.append( data_0)
  	rand_msg_0.append( mk_req ( 'rd', addr_0, 0, 0 ) )
  	rand_msg_0.append( mk_resp( 'rd', 0, data_0    ) )

def rand0_read_only_msg(base_addr):
    return rand_msg_0

def rand0_read_only_mem(base_addr):
    return mem_data_0

#Only Write
rand_msg_1  = []
mem_data_1  = []
addr_1 = 0
for i in xrange( Num_of_Rand_Tests ):
	addr_1 = i*16
	data_1 = random.randint(0,2147483647)
  	mem_data_1.append( addr_1 )
  	mem_data_1.append( data_1)
  	rand_msg_1.append( mk_req ( 'wr', addr_1, 0, data_1 ) )
  	rand_msg_1.append( mk_resp( 'wr', 0, 0    ) )

def rand1_write_only_msg(base_addr):
    return rand_msg_1

def rand1_write_only_mem(base_addr):
    return mem_data_1

#Simple address patterns, with random request types and data
rand_msg_2  = []
mem_data_2  = []
addr_2 = 0
for i in xrange( Num_of_Rand_Tests ):
  addr_2 = i*16
  data_2 = random.randint(0,2147483647)
  mem_data_2.append( addr_2 )
  mem_data_2.append( data_2)
  if ( random.randint(1,2) == 1):
      rand_msg_2.append( mk_req ( 'rd', addr_2, 0, 0 ) )
      rand_msg_2.append( mk_resp( 'rd', 0, data_2    ) )
  else:
    rand_msg_2.append( mk_req ( 'wr', addr_2, 0, data_2 ) )
    rand_msg_2.append( mk_resp( 'wr', 0, 0 ) )

def rand2_RandReqData_msg(base_addr):
    return rand_msg_2

def rand2_RandReqData_mem(base_addr):
    return mem_data_2

#Random address patterns, request types, and data

rand_msg_3  = []
mem_data_3  = []
addr_3 = 0
data_3 = 0
for i in xrange( Num_of_Rand_Tests ):
  #while addr_3 in mem_data_3:
  j = random.randint(0,1)
  k = random.randint(0,7)
  addr_3 = j*256 + k*16
  data_3 = j*64 + k*4
  
  mem_data_3.append( addr_3 )
  mem_data_3.append( data_3)
  if ( random.randint(1,2) == 1):
      rand_msg_3.append( mk_req ( 'rd', addr_3, 0, 0 ) )
      rand_msg_3.append( mk_resp( 'rd', 0, data_3    ) )
  else:
    rand_msg_3.append( mk_req ( 'wr', addr_3, 0, data_3 ) )
    rand_msg_3.append( mk_resp( 'wr', 0, 0 ) )

def rand3_RandAddReqData_msg(base_addr):
    return rand_msg_3

def rand3_RandAddReqData_mem(base_addr):
    return mem_data_3


#Unit stride with random data
rand_msg_4  = []
mem_data_4  = []
addr_4 = 0
count = 0
for i in xrange( Num_of_Rand_Tests ):
  addr_4 = i*16
  data_4 = random.randint(0,2147483647)
  mem_data_4.append( addr_4 )
  mem_data_4.append( data_4 )

  if count == 0:
      temp_addr = addr_4
      temp_data = data_4
      rand_msg_4.append( mk_req ( 'rd', temp_addr, 0, 0 ) )
      rand_msg_4.append( mk_resp( 'rd', 0, temp_data    ) )
      count +=1
  elif count == 7:
      count = 0
  else:
      count += 1

def rand4_Stride_RandData_msg(base_addr):
    return rand_msg_4

def rand4_Stride_RandData_mem(base_addr):
    return mem_data_4

#Stride with random data
rand_msg_5  = []
mem_data_5  = []
addr_5 = 0
count = 0
for i in xrange( Num_of_Rand_Tests ):
  addr_5 = i*16
  data_5 = random.randint(0,2147483647)
  mem_data_5.append( addr_5 )
  mem_data_5.append( data_5 )

  if count == 0:
      temp_addr = addr_5
      temp_data = data_5
      rand_msg_5.append( mk_req ( 'rd', temp_addr, 0, 0 ) )
      rand_msg_5.append( mk_resp( 'rd', 0, temp_data    ) )
      count +=1
  elif count == 5:
      count = 0
  else:
      count += 1

def rand5_RandStrideData_msg(base_addr):
    return rand_msg_5

def rand5_RandStrideData_mem(base_addr):
    return mem_data_5

#Unit stride (high spatial locality) mixed with shared (high temporal locality)

rand_msg_6  = []
mem_data_6  = []
addr_6 = 0
count = 0
for i in xrange( Num_of_Rand_Tests ):
  addr_6 = i*16
  data_6 = random.randint(0,2147483647)
  mem_data_6.append( addr_6 )
  mem_data_6.append( data_6 )

  if count == 0:
      temp_addr = addr_6
      temp_data = data_6
      rand_msg_6.append( mk_req ( 'rd', temp_addr, 0, 0 ) )
      rand_msg_6.append( mk_resp( 'rd', 0, temp_data    ) )

      rand_msg_6.append( mk_req ( 'rd', temp_addr, 0, 0 ) )
      rand_msg_6.append( resp( 'rd', 0, 1, 0, temp_data ) )
      count +=1
  elif count == random.randint(0, 10):
      count = 0
  else:
      count += 1

def rand6_Loc_msg(base_addr):
    return rand_msg_6

def rand6_Loc_mem(base_addr):
    return mem_data_6



#-------------------------------------------------------------------------
# Test table for generic test
#-------------------------------------------------------------------------

test_case_table_generic = mk_test_case_table([
  (                         "msg_func               mem_data_func         nbank stall lat src sink"),
  [ "read_hit_1word_clean",  read_hit_1word_clean,  None,                 0,    0.0,  0,  0,  0    ],
  [ "read_miss_1word",       read_miss_1word_msg,   read_miss_1word_mem,  0,    0.0,  0,  0,  0    ],
  [ "read_hit_1word_4bank",  read_hit_1word_clean,  None,                 4,    0.0,  0,  0,  0    ],

  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # LAB TASK: Add test cases to this table
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  [ "write_hit_1word_clean",	write_hit_1word_clean, 	None,  			0,    0.0,  0,  0,  0    ],
  [ "write_miss_read_hit"  , 	write_miss_read_hit  , 	None,   		0,    0.0,  0,  0,  0    ],
  [ "read_hit_clean",    		read_hit_clean,    		None,   		0,    0.0,  0,  0,  0    ],
  [ "write_hit_clean", 			write_hit_clean, 		None, 			0,    0.0,  0,  0,  0    ],
  [ "read_hit_dirty", 			read_hit_dirty, 		None, 			0,    0.0,  0,  0,  0    ],
  [ "write_hit_dirty", 			write_hit_dirty, 		None, 			0,    0.0,  0,  0,  0    ],

  [ "read_miss_refill_NoEv",	read_miss_refill_NoEv, 	read_miss_mem, 	0,    0.0,  0,  0,  0    ],
  [ "write_miss_refill_NoEv",	write_miss_refill_NoEv, write_miss_mem, 0,    0.0,  0,  0,  0    ],
  [ "capacity_misses", 	  		capacity_misses, 		None,			0,    0.0,  0,  0,  0 	 ],

  [ "read_hit_clean_rand",    	read_hit_clean,    		None,           0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "write_hit_clean_rand",   	write_hit_clean,   		None,           0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "read_hit_dirty_rand",    	read_hit_dirty,    		None,           0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "write_hit_dirty_rand",   	write_hit_dirty,   		None,           0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "read_miss_refill__NoEv_rand",  read_miss_refill_NoEv,read_miss_mem,0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "write_miss_refill__NoEv_rand", write_miss_refill_NoEv,write_miss_mem,0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],

  [ "rand0_read_only",      rand0_read_only_msg,    	rand0_read_only_mem,		0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "rand1_write_only",     rand1_write_only_msg,   	rand1_write_only_mem,		0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "rand2_RandReqData",    rand2_RandReqData_msg,  	rand2_RandReqData_mem,		0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  #[ "rand3_RandAddReqData", rand3_RandAddReqData_msg,  	rand3_RandAddReqData_mem,		0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "rand4_Stride_RandData",rand4_Stride_RandData_msg,  rand4_Stride_RandData_mem,	0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "rand5_RandStrideData", rand5_RandStrideData_msg,   rand5_RandStrideData_mem,	0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "rand6_Loc", 			rand6_Loc_msg,   			rand6_Loc_mem,				0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],

])

@pytest.mark.parametrize( **test_case_table_generic )
def test_generic( test_params, dump_vcd ):
  msgs = test_params.msg_func( 0 )
  if test_params.mem_data_func != None:
    mem = test_params.mem_data_func( 0 )
  # Instantiate testharness
  harness = TestHarness( msgs[::2], msgs[1::2],
                         test_params.stall, test_params.lat,
                         test_params.src, test_params.sink,
                         BlockingCacheFL, test_params.nbank,
                         False, dump_vcd )
  # Load memory before the test
  if test_params.mem_data_func != None:
    harness.load( mem[::2], mem[1::2] )
  # Run the test
  run_sim( harness, dump_vcd )


#-------------------------------------------------------------------------
# Tests set-associative cache (alternative design)
#-------------------------------------------------------------------------

def G_read_hit_asso( base_addr ):
  return [
    #    type  opq  addr       len data                type  opq  test len data
    req( 'wr', 0x0, 0x00000000, 0, 0xdeadbeef ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'wr', 0x1, 0x00001000, 0, 0x00c0ffee ), resp( 'wr', 0x1, 0,   0,  0          ),
    req( 'rd', 0x2, 0x00000000, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0xdeadbeef ),
    req( 'rd', 0x3, 0x00001000, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x00c0ffee ),
    req( 'wr', 0x4, 0x00002000, 0, 0x0a0b0c0d ), resp( 'wr', 0x4, 0,   0,  0          ),
    req( 'wr', 0x5, 0x00003000, 0, 0x09876543 ), resp( 'wr', 0x5, 0,   0,  0          ),
    req( 'rd', 0x6, 0x00002000, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x0a0b0c0d ),
    req( 'rd', 0x7, 0x00003000, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x09876543 ),
    req( 'wr', 0x8, 0x00004000, 0, 0xdeadbeef ), resp( 'wr', 0x8, 0,   0,  0          ),
    req( 'wr', 0x9, 0x00005010, 0, 0x00c0ffee ), resp( 'wr', 0x9, 0,   0,  0          ),
    req( 'rd', 0xa, 0x00004000, 0, 0          ), resp( 'rd', 0xa, 1,   0,  0xdeadbeef ),
    req( 'rd', 0xb, 0x00005010, 0, 0          ), resp( 'rd', 0xb, 1,   0,  0x00c0ffee ),
  ]

def read_miss_refill_NoEv_asso( base_addr ):
  return [
    #    type  opq   addr      len  data               type  opq test len  data
    req( 'rd', 0x00, 0x00000000, 0, 0          ), resp('rd', 0x00, 0, 0, 0xdeadbeef ),
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
    req( 'rd', 0x00, 0x00021000, 0, 0          ), resp('rd', 0x00, 0, 0, 0xace0ace0 ),
    req( 'rd', 0x00, 0x00021004, 0, 0          ), resp('rd', 0x00, 1, 0, 0x1a1a1a1a ),
    req( 'rd', 0x00, 0x00000000, 0, 0          ), resp('rd', 0x00, 1, 0, 0xdeadbeef ),
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
  ]

def write_miss_refill_NoEv_asso( base_addr ):
  return [
    #    type  opq   addr      len  data               type  opq test len  data
    req( 'wr', 0x00, 0x00000000, 0, 0x00c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0xdeadbeef ),
    req( 'wr', 0x00, 0x00000004, 0, 0x00c0ffee ), resp('wr', 0x00, 1, 0, 0          ),
    req( 'rd', 0x01, 0x00000000, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
    req( 'wr', 0x00, 0x00021000, 0, 0x00c0ffee ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'rd', 0x01, 0x00021004, 0, 0          ), resp('rd', 0x01, 1, 0, 0xdeadbeef ),
    req( 'wr', 0x00, 0x00021004, 0, 0x00c0ffee ), resp('wr', 0x00, 1, 0, 0          ),
    req( 'rd', 0x01, 0x00021000, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
    req( 'rd', 0x01, 0x00021004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
    req( 'rd', 0x01, 0x00000000, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
  ]

#read_miss_mem_2
# addr      data (in int)
#    0x00000000, 0xdeadbeef,
#    0x00000004, 0x00c0ffee,
#    0x00001000, 0x98765432,
#    0x00001004, 0xace0ace0,
#    0x00002000, 0x1a1a1a1a,
#    0x00002004, 0x1a1a1a1a,

def read_miss_refill_WiEv_asso( base_addr ):
  return [
    #    type  opq   addr      len  data               type  opq test len  data
    req( 'rd', 0x00, 0x00000000, 0, 0          ), resp('rd', 0x00, 0, 0, 0xdeadbeef ),
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
    req( 'wr', 0x02, 0x00001000, 0, 0x2b2b2b2b ), resp('wr', 0x02, 0, 0, 0			),
    req( 'wr', 0x03, 0x00001004, 0, 0x3c3c3c3c ), resp('wr', 0x03, 1, 0, 0			),
    req( 'rd', 0x00, 0x00001000, 0, 0          ), resp('rd', 0x00, 1, 0, 0x2b2b2b2b ),
    req( 'rd', 0x00, 0x00001004, 0, 0          ), resp('rd', 0x00, 1, 0, 0x3c3c3c3c ),
    req( 'rd', 0x00, 0x00000000, 0, 0          ), resp('rd', 0x00, 1, 0, 0xdeadbeef ),
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
	req( 'rd', 0x00, 0x00002000, 0, 0          ), resp('rd', 0x00, 0, 0, 0x1a1a1a1a ),
    req( 'rd', 0x00, 0x00002004, 0, 0          ), resp('rd', 0x00, 1, 0, 0x1a1a1a1a ),
    req( 'wr', 0x04, 0x00002000, 0, 0x12345678 ), resp('wr', 0x04, 1, 0, 0			),
    req( 'wr', 0x05, 0x00002004, 0, 0x65656565 ), resp('wr', 0x05, 1, 0, 0			),
    req( 'rd', 0x00, 0x00002000, 0, 0          ), resp('rd', 0x00, 1, 0, 0x12345678 ),
    req( 'rd', 0x00, 0x00002004, 0, 0          ), resp('rd', 0x00, 1, 0, 0x65656565 ),
    req( 'rd', 0x00, 0x00000000, 0, 0          ), resp('rd', 0x00, 1, 0, 0xdeadbeef ),
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ),
    req( 'rd', 0x00, 0x00001000, 0, 0          ), resp('rd', 0x00, 0, 0, 0x2b2b2b2b ),
    req( 'rd', 0x00, 0x00001004, 0, 0          ), resp('rd', 0x00, 1, 0, 0x3c3c3c3c ),
    
  ]

def conflict_misses_asso( base_addr ):
  return [
    #    type  opq   addr      len  data               type  opq test len  data
    req( 'wr', 0x00, 0x00000000, 0, 0x1a1a1a1a ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'wr', 0x00, 0x00001000, 0, 0x2b2b2b2b ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'rd', 0x01, 0x00001000, 0, 0          ), resp('rd', 0x01, 1, 0, 0x2b2b2b2b ),
    req( 'rd', 0x01, 0x00000000, 0, 0          ), resp('rd', 0x01, 1, 0, 0x1a1a1a1a ),
    req( 'wr', 0x00, 0x00002000, 0, 0xf0cf0cff ), resp('wr', 0x00, 0, 0, 0          ),
    req( 'rd', 0x01, 0x00000000, 0, 0          ), resp('rd', 0x01, 1, 0, 0x1a1a1a1a ),	#also tests LRU
    req( 'rd', 0x01, 0x00001000, 0, 0          ), resp('rd', 0x01, 0, 0, 0x2b2b2b2b ),
  ]



#-------------------------------------------------------------------------
# Test table for set-associative cache (alternative design)
#-------------------------------------------------------------------------

test_case_table_set_assoc = mk_test_case_table([
  (                             "msg_func        					mem_data_func    nbank stall lat src sink"),
  [ "read_hit_asso",             	read_hit_asso,  				None,  				0,    0.0,  0,  0,  0 ],
  [ "G_read_hit_asso",           	G_read_hit_asso,  				None,  				0,    0.0,  0,  0,  0 ],
  [ "read_miss_refill__NoEv_asso", 	read_miss_refill_NoEv_asso, 	read_miss_mem, 		0,    0.0,  0,  0,  0 ],
  [ "write_miss_refill__NoEv_asso",	write_miss_refill_NoEv_asso,	write_miss_mem,		0,    0.0,  0,  0,  0 ],
  [ "read_miss_refill__WiEv_asso",	read_miss_refill_WiEv_asso,		read_miss_mem_2,	0,    0.0,  0,  0,  0 ],
  [ "conflict_misses_asso", 	  	conflict_misses_asso, 			None,				0,    0.0,  0,  0,  0 ],


  [ "read_hit_asso_bank",             	read_hit_asso,  				None,  			4,    0.0,  0,  0,  0 ],
  [ "G_read_hit_asso_bank",           	G_read_hit_asso,  				None,  			4,    0.0,  0,  0,  0 ],
  [ "read_miss_refill__NoEv_asso_bank", read_miss_refill_NoEv_asso, 	read_miss_mem, 	4,    0.0,  0,  0,  0 ],
  [ "write_miss_refill__NoEv_asso_bank",write_miss_refill_NoEv_asso,	write_miss_mem,	4,    0.0,  0,  0,  0 ],
  [ "read_miss_refill__WiEv_asso_bank",	read_miss_refill_WiEv_asso,		read_miss_mem_2,4,    0.0,  0,  0,  0 ],
  [ "conflict_misses_asso_bank", 	  	conflict_misses_asso, 			None,			4,    0.0,  0,  0,  0 ],

  [ "read_hit_asso_rand",       		read_hit_asso,  			None,           		0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "read_miss_refill_NoEv_asso_rand",  read_miss_refill_NoEv_asso, read_miss_mem,  		0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "write_miss_refill_NoEv_asso_rand", write_miss_refill_NoEv_asso,write_miss_mem, 		0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "read_miss_refill_WiEv_asso_rand",  read_miss_refill_WiEv_asso, read_miss_mem_2,		0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  #[ "entire_cache_asso_rand",      		entire_cache_asso_4,    	entire_cache_mem_asso_4,4, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "conflict_misses_asso_rand",   		conflict_misses_asso,   	None,                   4, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # LAB TASK: Add test cases to this table
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

])

@pytest.mark.parametrize( **test_case_table_set_assoc )
def test_set_assoc( test_params, dump_vcd ):
  msgs = test_params.msg_func( 0 )
  if test_params.mem_data_func != None:
    mem  = test_params.mem_data_func( 0 )
  # Instantiate testharness
  harness = TestHarness( msgs[::2], msgs[1::2],
                         test_params.stall, test_params.lat,
                         test_params.src, test_params.sink,
                         BlockingCacheFL, test_params.nbank,
                         False, dump_vcd )
  # Load memory before the test
  if test_params.mem_data_func != None:
    harness.load( mem[::2], mem[1::2] )
  # Run the test
  run_sim( harness, dump_vcd )


#-------------------------------------------------------------------------
# Test table for direct-mapped cache (baseline design)
#-------------------------------------------------------------------------

test_case_table_dir_mapped = mk_test_case_table([
  (                       			"msg_func              			mem_data_func      nbank 	stall lat src sink"),
  [ "read_hit_dmap",      			read_hit_dmap,        			None,   			0,		0.0,  0,  0,  0    ],
  [ "read_hit_dmap_G", 				read_hit_dmap_G, 				None, 				0,    	0.0,  0,  0,  0    ],
  [ "read_miss_refill_NoEv_dmap", 	read_miss_refill_NoEv_dmap, 	read_miss_mem,   	0,		0.0,  0,  0,  0    ],
  [ "write_miss_refill_NoEv_dmap",	write_miss_refill_NoEv_dmap,	write_miss_mem,  	0,		0.0,  0,  0,  0    ], 
  [ "read_miss_refill_WiEv_dmap", 	read_miss_refill_WiEv_dmap, 	read_miss_mem_2, 	0,		0.0,  0,  0,  0    ],
  [ "fill_cache_dmap", 				fill_cache_dmap, 				fill_cache_mem_dmap,0,		0.0,  0,  0,  0    ],
  [ "conflict_misses_dmap", 		conflict_misses_dmap, 			None, 				0,		0.0,  0,  0,  0    ],

  [ "read_hit_dmap_bank",      			read_hit_dmap,        		None,   			4,		0.0,  0,  0,  0    ],
  [ "read_hit_dmap_G_bank", 			read_hit_dmap, 				None, 				4,    	0.0,  0,  0,  0    ],
  [ "read_miss_refill_NoEv_dmap_bank",	read_miss_refill_NoEv_dmap, read_miss_mem,   	4,		0.0,  0,  0,  0    ],
  [ "write_miss_refill_NoEv_dmap_bank",	write_miss_refill_NoEv_dmap,write_miss_mem,  	4,		0.0,  0,  0,  0    ], 
  [ "read_miss_refill_WiEv_dmap_bank", 	read_miss_refill_WiEv_dmap, read_miss_mem_2, 	4,		0.0,  0,  0,  0    ],
  [ "conflict_misses_dmap_bank", 		conflict_misses_dmap, 		None, 				4,		0.0,  0,  0,  0    ],


  [ "NoBank_4WM_2RM_2RH_dmap", 			NoBank_4WM_2RM_2RH_dmap, 	None,  				0,    	0.0,  0,  0,  0    ],
  [ "W4Bank_4WM_4RM_dmap", 				W4Bank_4WM_4RM_dmap, 		None,   			4,    	0.0,  0,  0,  0    ],
  [ "WER_2wrM_2wrEv_2rdH_2rdM_dmap", 	WER_2wrM_2wrEv_2rdH_2rdM_dmap, None, 			0, 		0.0,  0,  0,  0    ],

  [ "read_hit_dmap_rand",            	read_hit_dmap_G,          	None,               0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "read_miss_refill_NoEv_dmap_rand",  read_miss_refill_NoEv_dmap, read_miss_mem,      0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "write_miss_refill_NoEv_dmap_rand", write_miss_refill_NoEv_dmap,write_miss_mem,     0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "read_miss_refill_WiEv_dmap_rand",  read_miss_refill_WiEv_dmap, read_miss_mem_2,    0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "fill_cache_dmap_rand",           	fill_cache_dmap,      		fill_cache_mem_dmap, 	0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  [ "conflict_misses_dmap_rand",        conflict_misses_dmap,   	None,               0, 0.75, random.randint(1,20), random.randint(1,20), random.randint(1,20)],
  

  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # LAB TASK: Add test cases to this table
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

])

@pytest.mark.parametrize( **test_case_table_dir_mapped )
def test_dir_mapped( test_params, dump_vcd ):
  msgs = test_params.msg_func( 0 )
  if test_params.mem_data_func != None:
    mem  = test_params.mem_data_func( 0 )
  # Instantiate testharness
  harness = TestHarness( msgs[::2], msgs[1::2],
                         test_params.stall, test_params.lat,
                         test_params.src, test_params.sink,
                         BlockingCacheFL, test_params.nbank,
                         False, dump_vcd )
  # Load memory before the test
  if test_params.mem_data_func != None:
    harness.load( mem[::2], mem[1::2] )
  # Run the test
  run_sim( harness, dump_vcd )

//=========================================================================
// Alternative Blocking Cache Datapath
//=========================================================================

`ifndef LAB3_MEM_BLOCKING_CACHE_ALT_DPATH_V
`define LAB3_MEM_BLOCKING_CACHE_ALT_DPATH_V

`include "vc/mem-msgs.v"
`include "vc/regs.v"
`include "vc/srams.v"
`include "vc/arithmetic.v"
`include "vc/muxes.v"

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Include necessary files
//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

module lab3_mem_BlockingCacheAltDpathVRTL
#(
  parameter p_idx_shamt    = 0
)
(
  input  logic                        clk,
  input  logic                        reset,

  // Cache Request

  input  mem_req_4B_t                 cachereq_msg,

  // Cache Response

  output mem_resp_4B_t                cacheresp_msg,

  // Memory Request

  output mem_req_16B_t                memreq_msg,

  // Memory Response

  input  mem_resp_16B_t               memresp_msg,

  // Cache Input Register Signals 
  output logic [2:0]                  cachereq_type,
  input  logic                        cachereq_en,
  output logic [31:0]                 cachereq_addr,

  // Tag Array Signals
  input  logic                         tag_array_ren,
  input  logic                         tag0_array_wen,
  input  logic                         tag1_array_wen,
  output logic                         tag0_match,
  output logic                         tag1_match,
  input  logic                         tag_check_en,

  input  logic [1:0]                   tag_check_hit,
  output logic [1:0]                   tag_check_out,
  input  logic                         hit_reg_en,

  // Data Array Signals
  input  logic                         victim,
  input  logic                         victim_sel,
  input  logic                         data_array_ren,
  input  logic                         data_array_wen,
  input  logic [15:0]                  data_array_wben,
  output logic                         idx_adj,
  
  // Write Data Mux Signal
  input  logic                         write_data_mux_sel,
  input  logic                         read_data_reg_en,
  input  logic [2:0]                   read_word_mux_sel,

  // refill request
  input  logic                         memreq_addr_mux_sel,
  input  logic [2:0]                   memreq_type,

  input  logic                         memresp_data_reg_en,
  input  logic                         evict_addr_reg_en,

  input  logic                         victim_reg_en
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Add dpath signals
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

);

  // local parameters not meant to be set from outside
  localparam size = 256;             // Cache size in bytes
  localparam dbw  = 32;              // Short name for data bitwidth
  localparam abw  = 32;              // Short name for addr bitwidth
  localparam o    = 8;               // Short name for opaque bitwidth
  localparam clw  = 128;             // Short name for cacheline bitwidth
  localparam nbl  = size*8/clw;      // Number of blocks in the cache
  localparam nby  = nbl/2;           // Number of blocks per way
  localparam idw  = $clog2(nby);     // Short name for index bitwidth
  localparam ofw  = $clog2(clw/8);   // Short name for the offset bitwidth
  // In this lab, to simplify things, we always use all bits except for the
  // offset in the tag, rather than storing the "normal" 24 bits. This way,
  // when implementing a multi-banked cache, we don't need to worry about
  // re-inserting the bank id into the address of a cacheline.
  localparam tgw  = abw - ofw;       // Short name for the tag bitwidth

  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Implement Dpath
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  logic [7:0]  in_opaque;
  logic [2:0]  in_type;
  logic [31:0] in_addr;
  logic [31:0] in_data;

  logic [7:0]  out_opaque;
  logic [2:0]  out_type;
  logic [31:0] out_addr;
  logic [31:0] out_data;

  assign in_opaque = cachereq_msg[73:66];
  assign in_type   = cachereq_msg[76:74];
  assign in_addr   = cachereq_msg[65:34];
  // There may be cases where only some bytes are valid
  assign in_data   = cachereq_msg[31:0];
 
  //********************************************
  //IDLE stage
  //********************************************

  vc_EnResetReg #(8, 0) cachereq_opaque_reg 
  (
    .clk(clk),
    .reset(reset),
    .en(cachereq_en),
    .d(in_opaque),
    .q(out_opaque)
  );

  assign cachereq_type = out_type;

  vc_EnResetReg #(3, 0) cachereq_type_reg 
  (
    .clk(clk),
    .reset(reset),
    .en(cachereq_en),
    .d(in_type),
    .q(out_type)
  );


  vc_EnResetReg #(32, 0) cachereq_addr_reg 
  (
    .clk(clk),
    .reset(reset),
    .en(cachereq_en),
    .d(in_addr),
    .q(out_addr)
  );


  vc_EnResetReg #(32, 0) cachereq_data_reg 
  (
    .clk(clk),
    .reset(reset),
    .en(cachereq_en),
    .d(in_data),
    .q(out_data)
  );

  assign cachereq_addr = out_addr;
  
  //****************************************
  //TAG_CHECK state
  //****************************************

  logic [2:0]  idx;
  logic [3:0]  byte_off;

  logic [27:0] tag0_read_data;
  logic [27:0] tag1_read_data;

  logic [27:0] tag_write_data;

  assign idx            = out_addr[6+p_idx_shamt:4+p_idx_shamt];
  assign tag_write_data = out_addr[31:4];

  vc_CombinationalBitSRAM_1rw #(28, 8) tag0_array
  (
    .clk(clk),
    .reset(reset),
    .read_en(tag_array_ren),
    .read_addr(idx),
    .read_data(tag0_read_data),
    .write_en(tag0_array_wen),
    .write_addr(idx),
    .write_data(tag_write_data)
  );

  vc_CombinationalBitSRAM_1rw #(28, 8) tag1_array
  (
    .clk(clk),
    .reset(reset),
    .read_en(tag_array_ren),
    .read_addr(idx),
    .read_data(tag1_read_data),
    .write_en(tag1_array_wen),
    .write_addr(idx),
    .write_data(tag_write_data)
  );

  logic [27:0] cmp_top_input;
  logic [27:0] cmp0_bottom_input;
  logic [27:0] cmp1_bottom_input;

  assign cmp_top_input    = out_addr[31:4];
  assign cmp0_bottom_input = tag0_read_data;
  assign cmp1_bottom_input = tag1_read_data;

  vc_EqComparator #(28) cmp0
  (
    .in0(cmp_top_input),
    .in1(cmp0_bottom_input),
    .out(tag0_match)
  );

  vc_EqComparator #(28) cmp1
  (
    .in0(cmp_top_input),
    .in1(cmp1_bottom_input),
    .out(tag1_match)
  );

  logic [1:0] hit_reg_in;
  logic [1:0] hit_reg_out;
  assign hit_reg_in = tag_check_hit;

  vc_EnResetReg #(2, 0) hit_reg
  (
    .clk(clk),
    .reset(reset),
    .en(hit_reg_en),
    .d(hit_reg_in),
    .q(hit_reg_out)
  );

  assign tag_check_out = hit_reg_out;

  logic tag_check_reg_out;

  vc_EnResetReg #(1, 0) tag_check_reg
  (
    .clk(clk),
    .reset(reset),
    .en(tag_check_en),
    .d(tag1_match),
    .q(tag_check_reg_out)
  );

 //logic idx_adj;
 logic victim_reg_out;

  vc_EnResetReg #(1, 0) victim_reg
  (
    .clk(clk),
    .reset(reset),
    .en(victim_reg_en),
    .d(victim),
    .q(victim_reg_out)
  );

  // 2 bit mux for the tag_match output and the victim select
  vc_Mux2 #(1) tag_match_victim_mux
  (
  .in0(tag_check_reg_out),
  .in1(victim_reg_out),
  .sel(victim_sel),
  .out(idx_adj)
  );



  //****************************************
  //STATE_INIT_DATA_ACCESS
  //****************************************

  logic [127:0]  write_data_mux_top;
  logic [127:0]  write_data_mux_bottom;
  logic [127:0]  write_data_mux_output;

  assign write_data_mux_top = {4{out_data}};

  vc_Mux2 #(128) write_data_mux
  (
    .in0(write_data_mux_bottom),
    .in1(write_data_mux_top),
    .sel(write_data_mux_sel),
    .out(write_data_mux_output)
  );

  logic [127:0]      data_arr_read_data;
  logic [127:0]      data_arr_write_data;

  assign data_arr_write_data = write_data_mux_output;
  
  logic [3:0] data_arr_idx; //need a different index for the data array since it is 16 bits.
  assign data_arr_idx = {idx_adj , idx};

  vc_CombinationalSRAM_1rw #(128, 16) data_array
  (
    .clk(clk),
    .reset(reset),
    .read_en(data_array_ren),
    .read_addr(data_arr_idx),
    .read_data(data_arr_read_data),
    .write_en(data_array_wen),
    .write_byte_en(data_array_wben),
    .write_addr(data_arr_idx),
    .write_data(data_arr_write_data)
  );

  logic [127:0]   in_read_data;
  logic [127:0]  out_read_data;
  logic [31:0]   out_read_word;

  assign in_read_data = data_arr_read_data;

  vc_EnResetReg #(128, 0) read_data_reg
  (
    .clk(clk),
    .reset(reset),
    .en(read_data_reg_en),
    .d(in_read_data),
    .q(out_read_data)
  );

  vc_Mux5 #(32) read_word_mux
  (
  .in0(32'b0),
  .in1(out_read_data[31:0]),
  .in2(out_read_data[63:32]),
  .in3(out_read_data[95:64]),
  .in4(out_read_data[127:96]),
  .sel(read_word_mux_sel),
  .out(out_read_word)
  );

  //------------------------------------------------------------------------
  // State Refill Request Parts for the datapath
  //------------------------------------------------------------------------

  logic [31:0] mkaddr;
  logic [31:0] memreq_addr_out;

  assign mkaddr = {cachereq_addr[31:4], 4'b0000};

  vc_Mux2 #(32) memreq_addr_mux
  (
  .in0(mkaddr),
  .in1(evict_addr_reg_out),
  .sel(memreq_addr_mux_sel),
  .out(memreq_addr_out)
  );

  assign memreq_msg[127:0] = out_read_data;
  assign memreq_msg[131:128] = 4'b0;
  assign memreq_msg[163:132] = memreq_addr_out;
  assign memreq_msg[171:164] = 8'b0;
  assign memreq_msg[174:172] = memreq_type;

  //-----------------------------------------------------------------------
  // STATE REFILL UPDATE
  //-----------------------------------------------------------------------

  logic [127:0] memresp_data_in;
  logic [127:0] memresp_data_out;

  assign memresp_data_in = memresp_msg[127:0];

  vc_EnResetReg #(128, 0) memresp_data_reg
  (
    .clk(clk),
    .reset(reset),
    .en(memresp_data_reg_en),
    .d(memresp_data_in),
    .q(memresp_data_out)
  );

  assign write_data_mux_bottom = memresp_data_out;


  //-------------------------------------------------------
  // WAIT STAGE
  //-------------------------------------------------------

   assign cacheresp_msg  = {cachereq_type, out_opaque, tag_check_out, 2'b0, out_read_word};

  //-------------------------------
  // Evict Stage
  // ------------------------------
  logic [31:0] mkaddr_evict;
  logic [31:0] evict_addr_reg_out;
  assign mkaddr_evict = {evict_addr_mux_out, 4'b0000};

  vc_EnResetReg #(32, 0) evict_addr_reg
  (
    .clk(clk),
    .reset(reset),
    .en(evict_addr_reg_en),
    .d(mkaddr_evict),
    .q(evict_addr_reg_out)
  );
  
  logic [27:0] evict_addr_mux_out;
  
  vc_Mux2 #(28) evict_addr_mux
  (
    .in0(tag0_read_data),
    .in1(tag1_read_data),
    .sel(victim),
    .out(evict_addr_mux_out)
  );

endmodule

`endif

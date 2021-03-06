//=========================================================================
// Alternative Blocking Cache
//=========================================================================

`ifndef LAB3_MEM_BLOCKING_CACHE_ALT_V
`define LAB3_MEM_BLOCKING_CACHE_ALT_V

`include "vc/mem-msgs.v"
`include "vc/trace.v"

`include "lab3_mem/BlockingCacheAltCtrlVRTL.v"
`include "lab3_mem/BlockingCacheAltDpathVRTL.v"

// Note on p_num_banks:
// In a multi-banked cache design, cache lines are interleaved to
// different cache banks, so that consecutive cache lines correspond to a
// different bank. The following is the addressing structure in our
// four-banked data caches:
//
// +--------------------------+--------------+--------+--------+--------+
// |        22b               |     4b       |   2b   |   2b   |   2b   |
// |        tag               |   index      |bank idx| offset | subwd  |
// +--------------------------+--------------+--------+--------+--------+
//
// We will compose a four-banked cache in lab5, the multi-core lab

module lab3_mem_BlockingCacheAltVRTL
#(
  parameter p_num_banks  = 0              // Total number of cache banks
)
(
  input  logic           clk,
  input  logic           reset,

  // Cache Request

  input  mem_req_4B_t    cachereq_msg,
  input  logic           cachereq_val,
  output logic           cachereq_rdy,

  // Cache Response

  output mem_resp_4B_t   cacheresp_msg,
  output logic           cacheresp_val,
  input  logic           cacheresp_rdy,

  // Memory Request

  output mem_req_16B_t   memreq_msg,
  output logic           memreq_val,
  input  logic           memreq_rdy,

  // Memory Response

  input  mem_resp_16B_t  memresp_msg,
  input  logic           memresp_val,
  output logic           memresp_rdy
);

  localparam size = 256; // Number of bytes in the cache
  localparam dbw  = 32;  // Short name for data bitwidth
  localparam abw  = 32;  // Short name for addr bitwidth
  localparam clw  = 128; // Short name for cacheline bitwidth

  // calculate the index shift amount based on number of banks

  localparam c_idx_shamt = $clog2( p_num_banks );

  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Define temporary wires
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  logic [2:0]  cachereq_type;
  logic        cachereq_en;
  logic [31:0] cachereq_addr;

  logic        tag_array_ren;
  logic        tag0_array_wen;
  logic        tag1_array_wen;
  logic        tag0_match;
  logic        tag1_match;
  logic        tag_check_en;

  logic [1:0]  tag_check_hit;
  logic [1:0]  tag_check_out;
  logic        hit_reg_en;

  logic        victim;
  logic        victim_sel;
  logic        data_array_ren;
  logic        data_array_wen;
  logic [15:0] data_array_wben;
  logic        write_data_mux_sel;
  logic        read_data_reg_en;
  logic [2:0]  read_word_mux_sel;
  logic        idx_adj;
  logic        memreq_addr_mux_sel;
  logic [2:0]  memreq_type;
  logic        memresp_data_reg_en;
  logic        evict_addr_reg_en;
  logic        victim_reg_en;
  //----------------------------------------------------------------------
  // Control
  //----------------------------------------------------------------------

  lab3_mem_BlockingCacheAltCtrlVRTL
  #(
    .p_idx_shamt            (c_idx_shamt)
  )
  ctrl
  (
   .clk               (clk),
   .reset             (reset),

   // Cache Request

   .cachereq_val      (cachereq_val),
   .cachereq_rdy      (cachereq_rdy),

   // Cache Response

   .cacheresp_val     (cacheresp_val),
   .cacheresp_rdy     (cacheresp_rdy),

   // Memory Request

   .memreq_val        (memreq_val),
   .memreq_rdy        (memreq_rdy),

   // Memory Response

   .memresp_val       (memresp_val),
   .memresp_rdy       (memresp_rdy),

   .cachereq_type     (cachereq_type), //added
   .cachereq_en       (cachereq_en),    //added
   .cachereq_addr     (cachereq_addr),

   .tag_array_ren     (tag_array_ren),
   .tag0_array_wen    (tag0_array_wen),
   .tag1_array_wen    (tag1_array_wen),
   .tag0_match        (tag0_match),
   .tag1_match        (tag1_match),
   .tag_check_en      (tag_check_en),

   .tag_check_hit     (tag_check_hit),
   .tag_check_out     (tag_check_out),
   .hit_reg_en        (hit_reg_en),
   //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
   // LAB TASK: Connect additional signals
   //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  .victim             (victim),
  .victim_sel         (victim_sel),
  .data_array_ren     (data_array_ren),
  .data_array_wen     (data_array_wen),
  .data_array_wben    (data_array_wben),
  .write_data_mux_sel (write_data_mux_sel),
  .read_data_reg_en   (read_data_reg_en),
  .read_word_mux_sel  (read_word_mux_sel),
  .idx_adj            (idx_adj),
  .memreq_addr_mux_sel(memreq_addr_mux_sel),
  .memreq_type        (memreq_type),
  .memresp_data_reg_en(memresp_data_reg_en),
  .evict_addr_reg_en  (evict_addr_reg_en),
  .victim_reg_en      (victim_reg_en)
  );

  //----------------------------------------------------------------------
  // Datapath
  //----------------------------------------------------------------------

  lab3_mem_BlockingCacheAltDpathVRTL
  #(
    .p_idx_shamt            (c_idx_shamt)
  )
  dpath
  (
   .clk               (clk),
   .reset             (reset),

   // Cache Request

   .cachereq_msg      (cachereq_msg),

   // Cache Response

   .cacheresp_msg     (cacheresp_msg),

   // Memory Request

   .memreq_msg        (memreq_msg),

   // Memory Response

   .memresp_msg       (memresp_msg),

   //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
   // LAB TASK: Connect additional ports
   //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
   .cachereq_type     (cachereq_type), //added
   .cachereq_en       (cachereq_en),    //added
   .cachereq_addr     (cachereq_addr),

   .tag_array_ren     (tag_array_ren),
   .tag0_array_wen    (tag0_array_wen),
   .tag1_array_wen    (tag1_array_wen),
   .tag0_match        (tag0_match),
   .tag1_match        (tag1_match),
   .tag_check_en      (tag_check_en),

   .tag_check_hit     (tag_check_hit),
   .tag_check_out     (tag_check_out),
   .hit_reg_en        (hit_reg_en),

   .victim             (victim),
   .victim_sel         (victim_sel),
   .data_array_ren     (data_array_ren),
   .data_array_wen     (data_array_wen),
   .data_array_wben    (data_array_wben),
   .write_data_mux_sel (write_data_mux_sel),
   .read_data_reg_en   (read_data_reg_en),
   .read_word_mux_sel  (read_word_mux_sel),
   .idx_adj            (idx_adj),
   .memreq_addr_mux_sel(memreq_addr_mux_sel),
   .memreq_type        (memreq_type),
   .memresp_data_reg_en(memresp_data_reg_en),
   .evict_addr_reg_en  (evict_addr_reg_en),
   .victim_reg_en      (victim_reg_en)
  );


  //----------------------------------------------------------------------
  // Line tracing
  //----------------------------------------------------------------------
  vc_MemReqMsg4BTrace cachereq_msg_trace
  (
    .clk   (clk),
    .reset (reset),
    .val   (cachereq_val),
    .rdy   (cachereq_rdy),
    .msg   (cachereq_msg)
  );

  vc_MemRespMsg4BTrace cacheresp_msg_trace
  (
    .clk   (clk),
    .reset (reset),
    .val   (cacheresp_val),
    .rdy   (cacheresp_rdy),
    .msg   (cacheresp_msg)
  );

  vc_MemReqMsg16BTrace memreq_msg_trace
  (
    .clk   (clk),
    .reset (reset),
    .val   (memreq_val),
    .rdy   (memreq_rdy),
    .msg   (memreq_msg)
  );

  vc_MemRespMsg16BTrace memresp_msg_trace
  (
    .clk   (clk),
    .reset (reset),
    .val   (memresp_val),
    .rdy   (memresp_rdy),
    .msg   (memresp_msg)
  );

  `VC_TRACE_BEGIN
  begin

    //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    // LAB TASK: Add line tracing
    //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  end
  `VC_TRACE_END

endmodule

`endif

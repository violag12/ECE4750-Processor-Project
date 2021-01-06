//=========================================================================
// Baseline Blocking Cache Control
//=========================================================================

`ifndef LAB3_MEM_BLOCKING_CACHE_BASE_CTRL_V
`define LAB3_MEM_BLOCKING_CACHE_BASE_CTRL_V

`include "vc/mem-msgs.v"
`include "vc/assert.v"

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Include necessary files
//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

module lab3_mem_BlockingCacheBaseCtrlVRTL
#(
  parameter p_idx_shamt    = 0
)
(
  input  logic                        clk,
  input  logic                        reset,

  // Cache Request

  input  logic                        cachereq_val,
  output logic                        cachereq_rdy,

  // Cache Response

  output logic                        cacheresp_val,
  input  logic                        cacheresp_rdy,

  // Memory Request

  output logic                        memreq_val,
  input  logic                        memreq_rdy,

  // Memory Response

  input  logic                        memresp_val,
  output logic                        memresp_rdy,
  
  // Cache Input Register Signals

  input  logic [2:0]                  cachereq_type,
  output logic                        cachereq_en ,
  input  logic [31:0]                 cachereq_addr,

  // Tag Check Signals
  
  output logic                        tag_array_ren,
  output logic                        tag_array_wen,
  input  logic                        tag_match,

  // Data Array Signals

  output logic                        data_array_ren,
  output logic                        data_array_wen,
  output logic [15:0]                 data_array_wben,
  
  // Write Data Mux Signal
  output logic                        write_data_mux_sel,

  output logic [1:0]                  hit,
  output logic [2:0]                  cacheresp_type,
  output logic                        read_data_reg_en,
  output logic [2:0]                  read_word_mux_sel,

  // refill request
  output logic                        memreq_addr_mux_sel,
  output logic [2:0]                  memreq_type,
  output logic                        memresp_data_write_en,                   
  output logic                        memresp_data_reg_en,
  output logic [1:0]                  tag_check_hit,
  input  logic [1:0]                  tag_check_out,
  output logic                        hit_reg_en,
  output logic                        cacheresp_mes_en,
  output logic						  evict_addr_reg_en       
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Define additional ports
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

 );

  // local parameters not meant to be set from outside
  localparam size = 256;             // Cache size in bytes
  localparam dbw  = 32;              // Short name for data bitwidth
  localparam abw  = 32;              // Short name for addr bitwidth
  localparam o    = 8;               // Short name for opaque bitwidth
  localparam clw  = 128;             // Short name for cacheline bitwidth
  localparam nbl  = size*8/clw;      // Number of blocks in the cache
  localparam nby  = nbl;             // Number of blocks per way
  localparam idw  = $clog2(nby);     // Short name for index bitwidth
  localparam ofw  = $clog2(clw/8);   // Short name for the offset bitwidth
  // In this lab, to simplify things, we always use all bits except for the
  // offset in the tag, rather than storing the "normal" 24 bits. This way,
  // when implementing a multi-banked cache, we don't need to worry about
  // re-inserting the bank id into the address of a cacheline.
  localparam tgw  = abw - ofw;       // Short name for the tag bitwidth

  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Implement control unit
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // State Definitions
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  localparam logic [3:0] STATE_IDLE               = 4'd0;
  localparam logic [3:0] STATE_TAG_CHECK          = 4'd1;
  localparam logic [3:0] STATE_READ_DATA_ACCESS   = 4'd2;
  localparam logic [3:0] STATE_WRITE_DATA_ACCESS  = 4'd3;
  localparam logic [3:0] STATE_INIT_DATA_ACCESS   = 4'd4;
  localparam logic [3:0] STATE_REFILL_REQUEST     = 4'd5;
  localparam logic [3:0] STATE_EVICT_PREPARE      = 4'd6;
  localparam logic [3:0] STATE_WAIT               = 4'd7;
  localparam logic [3:0] STATE_REFILL_WAIT        = 4'd8;
  localparam logic [3:0] STATE_REFILL_UPDATE      = 4'd9;
  localparam logic [3:0] STATE_EVICT_REQUEST      = 4'd10;
  localparam logic [3:0] STATE_EVICT_WAIT		  = 4'd11;
  
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // State
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  logic [3:0] CurrentState;
  logic [3:0] NextState;

  always_ff @(posedge clk) begin
    if(reset) CurrentState <= STATE_IDLE;
    else CurrentState <= NextState;
  end
  
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // State Transitions
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  
  logic dirty;
  assign dirty = dirty_bits[idx]; 
    
  always_comb begin 
    NextState = CurrentState;
    case(CurrentState)
      STATE_IDLE: if(cachereq_val) NextState = STATE_TAG_CHECK;
      STATE_TAG_CHECK: begin
             if (cachereq_type == 3'd2)             NextState = STATE_INIT_DATA_ACCESS;
             else if (!tag_check_hit[0] && dirty)                NextState = STATE_EVICT_PREPARE;
			 else if (!tag_check_hit[0] && !dirty)               NextState = STATE_REFILL_REQUEST;
			 else if (cachereq_type == 3'd0 && tag_check_hit[0]) NextState = STATE_READ_DATA_ACCESS;
			 else if (cachereq_type == 3'd1 && tag_check_hit[0]) NextState = STATE_WRITE_DATA_ACCESS;
			 else                                   NextState = 4'dx;
                       end
      STATE_INIT_DATA_ACCESS: NextState = STATE_WAIT;
      STATE_WAIT: begin
                    if(!cacheresp_rdy) NextState = STATE_WAIT;
		    else               NextState = STATE_IDLE;
                  end
      STATE_READ_DATA_ACCESS: NextState = STATE_WAIT;
      STATE_WRITE_DATA_ACCESS: NextState = STATE_WAIT;
      STATE_EVICT_PREPARE:    NextState = STATE_EVICT_REQUEST;
      STATE_REFILL_REQUEST: begin
                              if(!memreq_rdy) NextState = STATE_REFILL_REQUEST;
                              else NextState = STATE_REFILL_WAIT;
                            end
      STATE_REFILL_WAIT: begin
                           if(!memresp_val) NextState = STATE_REFILL_WAIT;
                           else NextState = STATE_REFILL_UPDATE;
                         end
      STATE_REFILL_UPDATE: begin
                             if(cachereq_type == 3'd0) NextState = STATE_READ_DATA_ACCESS;
                             if(cachereq_type == 3'd1) NextState = STATE_WRITE_DATA_ACCESS;
                           end
	  STATE_EVICT_REQUEST: begin
							if(!memreq_rdy) NextState = STATE_EVICT_REQUEST;
							else NextState = STATE_EVICT_WAIT;
							end
	  STATE_EVICT_WAIT: begin
							if(!memresp_val) NextState = STATE_EVICT_WAIT;
							else NextState = STATE_REFILL_REQUEST;						
						end
      default: NextState = 4'dx;
    endcase
  end
 
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // State Outputs
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  
  logic [15:0] valid_bits;
  logic [15:0] dirty_bits;
  logic [3:0]  idx;
  
  assign idx = cachereq_addr[7+p_idx_shamt:4+p_idx_shamt];
  assign cacheresp_type = cachereq_type;

  logic valid_bit;
  assign valid_bit = valid_bits[idx];
  
  logic [3:0] byte_off;
  assign byte_off = cachereq_addr[3:0];

//  if( CurrentState == STATE_INIT_DATA_ACCESS) assign tag_check_hit = 2'b0;
//  else assign tag_check_hit = {1'b0, tag_match && valid_bit}; 
/*  CTRL SIGNALS

		cachereq_rdy           = 1'b;
        cacheresp_val          = 1'b;
        cachereq_en            = 1'b;
        tag_array_ren          = 1'b;
        tag_array_wen          = 1'b;
        data_array_ren         = 1'b;
        data_array_wen         = 1'b;
        data_array_wben        = 16'b;
        write_data_mux_sel     = 1'b;
        valid_bits[idx]        = valid_bit;
		dirty_bits[idx]        = dirty;
		hit_reg_en             = 1'b;
        read_word_mux_sel      = 3'b;
        read_data_reg_en       = 1'b;
		memreq_val			   = 1'b;
		memresp_data_reg_en	   = 1'b;
		memresp_rdy			   = 1'b;
		memreq_addr_mux_sel	   = 1'b;
		memreq_type			   = 3'b;
		evict_addr_reg_en      = 1'b;
*/


  always_comb begin
 
   if( CurrentState == STATE_INIT_DATA_ACCESS) tag_check_hit = 2'b0;
   else tag_check_hit = {1'b0, tag_match && valid_bit};

    case (CurrentState)
      STATE_IDLE:              
        begin
        cachereq_rdy           = 1'b1;
        cacheresp_val          = 1'b0;
        cachereq_en            = 1'b1;
        tag_array_ren          = 1'b0;
        tag_array_wen          = 1'b0;
        data_array_ren         = 1'b0;
        data_array_wen         = 1'b0;
        data_array_wben        = 16'b0;
        write_data_mux_sel     = 1'bx;
        valid_bits[idx]        = valid_bit;
		dirty_bits[idx]        = dirty;
		hit_reg_en             = 1'b0;
        read_word_mux_sel      = 3'bx;
        read_data_reg_en       = 1'bx;
		memreq_val			   = 1'b0;
		memresp_data_reg_en	   = 1'b0;
		memresp_rdy			   = 1'b0;
		memreq_addr_mux_sel	   = 1'bx;
		memreq_type			   = 3'bx;
		evict_addr_reg_en      = 1'b0;
        end

      STATE_TAG_CHECK:        
        begin
        cachereq_rdy           = 1'b0;
        cacheresp_val          = 1'b0;
        cachereq_en            = 1'b0;
        tag_array_ren          = 1'b1;
        tag_array_wen          = 1'b0;
        data_array_ren         = 1'b0;
        data_array_wen         = 1'b0;
        data_array_wben        = 16'b0;
        write_data_mux_sel     = 1'bx;
		valid_bits[idx]        = valid_bit;
		dirty_bits[idx]        = dirty;
        hit_reg_en             = 1'b1;
        read_word_mux_sel      = 3'bx;
        read_data_reg_en       = 1'b1;
		memreq_val			   = 1'b0;
		memresp_data_reg_en	   = 1'b0;
		memresp_rdy			   = 1'b0;
		memreq_addr_mux_sel	   = 1'bx;
		memreq_type			   = 3'bx;
		evict_addr_reg_en      = 1'b0;
        end

      STATE_INIT_DATA_ACCESS:
      	begin  
	cachereq_rdy           = 1'b0;
        cacheresp_val          = 1'b0;
        cachereq_en            = 1'b0;
        tag_array_ren          = 1'b0;
        tag_array_wen          = 1'b1;
        data_array_ren         = 1'b0;
        data_array_wen         = 1'b1;
        if(byte_off == 4'b0000) data_array_wben  = 16'b0000000000001111;
        else if(byte_off == 4'b0100) data_array_wben = 16'b0000000011110000;
        else if(byte_off == 4'b1000) data_array_wben = 16'b0000111100000000;
        else if(byte_off == 4'b1100) data_array_wben = 16'b1111000000000000;
        write_data_mux_sel     = 1'b1;
		valid_bits[idx]        = 1'b1;
		dirty_bits[idx]        = 1'b0;
		hit_reg_en             = 1'b1;
        read_word_mux_sel      = 3'b0;
        read_data_reg_en       = 1'bx;
       	memreq_val			   = 1'b0;
		memresp_data_reg_en	   = 1'b0;
		memresp_rdy			   = 1'b0;
		memreq_addr_mux_sel	   = 1'bx;
		memreq_type			   = 3'bx;
		evict_addr_reg_en      = 1'b0;
        end

      STATE_READ_DATA_ACCESS:
        begin
        cachereq_rdy           = 1'b0;
        cacheresp_val          = 1'b0;
		cachereq_en            = 1'b0;
        tag_array_ren          = 1'b0;
        tag_array_wen          = 1'b0;
        data_array_ren         = 1'b1;
        data_array_wen         = 1'b0;
        data_array_wben        = 16'b0;
        write_data_mux_sel     = 1'bx;
        valid_bits[idx]        = valid_bit;
        dirty_bits[idx]        = dirty;
        hit_reg_en             = 1'b0;
        if(byte_off == 4'b0000) read_word_mux_sel  = 3'b001;
        else if(byte_off == 4'b0100) read_word_mux_sel  = 3'b010;
        else if(byte_off == 4'b1000) read_word_mux_sel  = 3'b011;
        else if(byte_off == 4'b1100) read_word_mux_sel  = 3'b100;
        read_data_reg_en       = 1'b1;
        memreq_val             = 1'b0;
        memresp_data_reg_en    = 1'b0;
        memresp_rdy            = 1'b0;
		memreq_addr_mux_sel	   = 1'bx;
		memreq_type			   = 3'bx;
		evict_addr_reg_en      = 1'b0;
        end

      STATE_WRITE_DATA_ACCESS:
        begin
		cachereq_rdy           = 1'b0;
        cacheresp_val          = 1'b0;
        cachereq_en            = 1'b0;
        tag_array_ren          = 1'b0;
        tag_array_wen          = 1'b0;
        data_array_ren         = 1'b0;
        data_array_wen         = 1'b1;
        if(byte_off == 4'b0000) data_array_wben  = 16'b0000000000001111;
        else if(byte_off == 4'b0100) data_array_wben = 16'b0000000011110000;
        else if(byte_off == 4'b1000) data_array_wben = 16'b0000111100000000;
        else if(byte_off == 4'b1100) data_array_wben = 16'b1111000000000000;
        write_data_mux_sel 		= 1'b1;
        dirty_bits[idx]    	= 1'b1;
        hit_reg_en             = 1'b0;
        valid_bits[idx]        = 1'b1;
        read_word_mux_sel      = 3'b0;
        read_data_reg_en       = 1'bx;
        memreq_val             = 1'b0;
        memresp_data_reg_en    = 1'b0;
        memresp_rdy            = 1'b0;
		memreq_addr_mux_sel	   = 1'bx;
		memreq_type			   = 3'bx;
		evict_addr_reg_en      = 1'b0;
        end

      STATE_REFILL_REQUEST:
        begin
        cachereq_rdy           = 1'b0;
        cacheresp_val          = 1'b0;
        cachereq_en            = 1'b0;
        tag_array_ren          = 1'b0;
        tag_array_wen          = 1'b0;
        data_array_ren         = 1'b0;
        data_array_wen         = 1'b0;
        data_array_wben        = 16'bx;
        write_data_mux_sel     = 1'b0;
        dirty_bits[idx]        = dirty;
        hit_reg_en             = 1'b0;
        valid_bits[idx]        = valid_bit;
        read_word_mux_sel      = 3'bx;
        read_data_reg_en       = 1'bx;
        memreq_val             = 1'b1;
        memresp_data_reg_en    = 1'b0;
        memresp_rdy            = 1'b0;
		memreq_addr_mux_sel    = 1'b0;
        memreq_type            = 3'b0;
		evict_addr_reg_en      = 1'b0;
        end

      STATE_REFILL_WAIT:
        begin
        cachereq_rdy           = 1'b0;
        cacheresp_val          = 1'b0;
        cachereq_en            = 1'b0;
        tag_array_ren          = 1'b0;
        tag_array_wen          = 1'b0;
        data_array_ren         = 1'b0;
        data_array_wen         = 1'b0;
        data_array_wben        = 16'bx;
        write_data_mux_sel     = 1'b0;
        dirty_bits[idx]        = dirty;
        hit_reg_en             = 1'b0;
        valid_bits[idx]        = valid_bit;
        read_word_mux_sel      = 3'bx;
        read_data_reg_en       = 1'bx;
        memreq_addr_mux_sel    = 1'b0;
        memreq_type            = 3'b0;
        memreq_val             = 1'b0;
        memresp_data_reg_en    = 1'b1;
        memresp_rdy            = 1'b0;
		evict_addr_reg_en      = 1'b0;
        end

      STATE_REFILL_UPDATE:
        begin
        cachereq_rdy           = 1'b0;
        cacheresp_val          = 1'b0;
        cachereq_en            = 1'b0;
        tag_array_ren          = 1'b0;
        tag_array_wen          = 1'b1;
        data_array_ren         = 1'b0;
        data_array_wen         = 1'b1;
        data_array_wben        = 16'b1111111111111111;
        write_data_mux_sel     = 1'b0;
        dirty_bits[idx]        = 1'b0;
        hit_reg_en             = 1'b0;
        valid_bits[idx]        = 1'b1;
        read_word_mux_sel      = 3'bx;
        read_data_reg_en       = 1'bx;
        memreq_addr_mux_sel    = 1'bx;
        memreq_type            = 3'bx;
        memreq_val             = 1'b0;
        memresp_data_reg_en    = 1'b1;
        memresp_rdy            = 1'b1;
		evict_addr_reg_en      = 1'b0;
        end

      STATE_WAIT:
        begin
        cachereq_rdy           = 1'b0;
        cacheresp_val          = 1'b1;
        cachereq_en            = 1'b0;
        tag_array_ren          = 1'b0;
        tag_array_wen          = 1'b0;
        data_array_ren         = 1'b0;
        data_array_wen         = 1'b0;
        data_array_wben        = 16'b0;
        write_data_mux_sel     = 1'bx;
        hit_reg_en             = 1'b0;
        valid_bits[idx]        = valid_bit;
        dirty_bits[idx]        = dirty;

        if(cacheresp_type == 3'd0) begin
          if(byte_off == 4'b0000) read_word_mux_sel  = 3'b001;
          else if(byte_off == 4'b0100) read_word_mux_sel  = 3'b010;
          else if(byte_off == 4'b1000) read_word_mux_sel  = 3'b011;
          else if(byte_off == 4'b1100) read_word_mux_sel  = 3'b100;
        end
        else read_word_mux_sel = 3'b0;

        read_data_reg_en       = 1'b0;
        memreq_val			   = 1'b0;
		memresp_data_reg_en	   = 1'b0;
		memresp_rdy			   = 1'b0;
		memreq_addr_mux_sel	   = 1'b0;
		memreq_type			   = 3'b0;
		evict_addr_reg_en      = 1'b0;
        end

	STATE_EVICT_PREPARE:
		begin
		cachereq_rdy           = 1'b0;
        cacheresp_val          = 1'b0;
        cachereq_en            = 1'b0;
        tag_array_ren          = 1'b1;
        tag_array_wen          = 1'b0;
        data_array_ren         = 1'b1;
        data_array_wen         = 1'b0;
        data_array_wben        = 16'b0;
        write_data_mux_sel     = 1'bx;
        valid_bits[idx]        = valid_bit;
		dirty_bits[idx]        = dirty;
		hit_reg_en             = 1'b0;
        read_word_mux_sel      = 3'bx;
        read_data_reg_en       = 1'b1;
		memreq_val			   = 1'b0;
		memresp_data_reg_en	   = 1'b0;
		memresp_rdy			   = 1'b0;
		memreq_addr_mux_sel	   = 1'b1;
		memreq_type			   = 3'b1;
		evict_addr_reg_en      = 1'b1;
		end

	STATE_EVICT_REQUEST:
		begin
		cachereq_rdy           = 1'b0;
        cacheresp_val          = 1'b0;
        cachereq_en            = 1'b0;
        tag_array_ren          = 1'b0;
        tag_array_wen          = 1'b0;
        data_array_ren         = 1'b0;
        data_array_wen         = 1'b0;
        data_array_wben        = 16'b0;
        write_data_mux_sel     = 1'bx;
        valid_bits[idx]        = valid_bit;
		dirty_bits[idx]        = dirty;
		hit_reg_en             = 1'b0;
        read_word_mux_sel      = 3'bx;
        read_data_reg_en       = 1'b0;
		memreq_val			   = 1'b1;
		memresp_data_reg_en	   = 1'b0;
		memresp_rdy			   = 1'b0;
		memreq_addr_mux_sel	   = 1'b1;
		memreq_type			   = 3'b1;
		evict_addr_reg_en      = 1'b0;
		end

	STATE_EVICT_WAIT:
		begin
		cachereq_rdy           = 1'b0;
        cacheresp_val          = 1'b0;
        cachereq_en            = 1'b0;
        tag_array_ren          = 1'b0;
        tag_array_wen          = 1'b0;
        data_array_ren         = 1'b0;
        data_array_wen         = 1'b0;
        data_array_wben        = 16'b0;
        write_data_mux_sel     = 1'bx;
        valid_bits[idx]        = valid_bit;
		dirty_bits[idx]        = dirty;
		hit_reg_en             = 1'b0;
        read_word_mux_sel      = 3'bx;
        read_data_reg_en       = 1'b0;
		memreq_val			   = 1'b0;
		memresp_data_reg_en	   = 1'b0;
		memresp_rdy			   = 1'b1;
		memreq_addr_mux_sel	   = 1'b1;
		memreq_type			   = 3'b1;
		evict_addr_reg_en      = 1'b0;
		end

      default:
        begin
        cachereq_rdy           = 1'bx;
        cacheresp_val          = 1'bx;
        cachereq_en            = 1'bx;
        tag_array_ren          = 1'bx;
        tag_array_wen          = 1'bx;
        data_array_ren         = 1'bx;
        data_array_wen         = 1'bx;
        data_array_wben        = 16'bx;
        write_data_mux_sel     = 1'bx;
        valid_bits[idx]        = 1'bx;
		dirty_bits[idx]        = 1'bx;
		hit_reg_en             = 1'bx;
        read_data_reg_en       = 1'bx;
        read_word_mux_sel      = 3'bx;
		evict_addr_reg_en      = 1'b0;
	end
    endcase
  end

endmodule

`endif

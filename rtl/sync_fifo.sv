// Synchronous FIFO
// - DEPTH must be a power of 2
// - Registered read: dout is valid one cycle after rd_en (when not empty)
// - Writes when full and reads when empty are ignored
module sync_fifo #(
    parameter int WIDTH = 8,
    parameter int DEPTH = 16
) (
    input  logic                   clk,
    input  logic                   rst_n,
    // write side
    input  logic                   wr_en,
    input  logic [WIDTH-1:0]       din,
    output logic                   full,
    // read side
    input  logic                   rd_en,
    output logic [WIDTH-1:0]       dout,
    output logic                   empty,
    // status
    output logic [$clog2(DEPTH):0] count
);
    localparam int AW = $clog2(DEPTH);

    logic [WIDTH-1:0] mem [DEPTH];
    // One extra bit tells full apart from empty
    logic [AW:0] wr_ptr, rd_ptr;

    logic do_write, do_read;
    assign do_write = wr_en && !full;
    assign do_read  = rd_en && !empty;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr <= '0;
        end else if (do_write) begin
            mem[wr_ptr[AW-1:0]] <= din;
            wr_ptr <= wr_ptr + 1'b1;
        end
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rd_ptr <= '0;
            dout   <= '0;
        end else if (do_read) begin
            dout   <= mem[rd_ptr[AW-1:0]];
            rd_ptr <= rd_ptr + 1'b1;
        end
    end

    assign count = wr_ptr - rd_ptr;
    assign empty = (wr_ptr == rd_ptr);
    assign full  = (wr_ptr[AW] != rd_ptr[AW]) && (wr_ptr[AW-1:0] == rd_ptr[AW-1:0]);

endmodule

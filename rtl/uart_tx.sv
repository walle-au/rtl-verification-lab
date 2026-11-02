// UART transmitter, 8N1 (1 start bit, 8 data bits LSB first, 1 stop bit)
// - tx_start is sampled only when busy is low
// - CLKS_PER_BIT = f_clk / baud  (e.g. 100 MHz / 115200 ≈ 868)
module uart_tx #(
    parameter int CLKS_PER_BIT = 868
) (
    input  logic       clk,
    input  logic       rst_n,
    input  logic       tx_start,
    input  logic [7:0] tx_data,
    output logic       tx,
    output logic       busy
);
    typedef enum logic [1:0] {IDLE, START, DATA, STOP} state_t;

    state_t state;
    logic [$clog2(CLKS_PER_BIT)-1:0] clk_cnt;
    logic [2:0] bit_idx;
    logic [7:0] shreg;

    logic bit_done;
    assign bit_done = (clk_cnt == CLKS_PER_BIT - 1);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state   <= IDLE;
            clk_cnt <= '0;
            bit_idx <= '0;
            shreg   <= '0;
            tx      <= 1'b1;  // line idles high
        end else begin
            case (state)
                IDLE: begin
                    tx      <= 1'b1;
                    clk_cnt <= '0;
                    if (tx_start) begin
                        shreg <= tx_data;
                        tx    <= 1'b0;  // start bit
                        state <= START;
                    end
                end

                START: begin
                    if (bit_done) begin
                        clk_cnt <= '0;
                        bit_idx <= '0;
                        tx      <= shreg[0];
                        state   <= DATA;
                    end else begin
                        clk_cnt <= clk_cnt + 1'b1;
                    end
                end

                DATA: begin
                    if (bit_done) begin
                        clk_cnt <= '0;
                        if (bit_idx == 3'd7) begin
                            tx    <= 1'b1;  // stop bit
                            state <= STOP;
                        end else begin
                            bit_idx <= bit_idx + 1'b1;
                            tx      <= shreg[bit_idx + 1'b1];
                        end
                    end else begin
                        clk_cnt <= clk_cnt + 1'b1;
                    end
                end

                STOP: begin
                    if (bit_done) begin
                        clk_cnt <= '0;
                        state   <= IDLE;
                    end else begin
                        clk_cnt <= clk_cnt + 1'b1;
                    end
                end

                default: state <= IDLE;
            endcase
        end
    end

    assign busy = (state != IDLE);

endmodule

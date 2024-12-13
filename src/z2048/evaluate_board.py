    # def evaluate_board(self, board, value, visit):
    #     # Weights for each component (adjust as needed)
    #     WEIGHT_MONOTONICITY = 2.0
    #     WEIGHT_SMOOTHNESS   = 2.5
    #     WEIGHT_EMPTY        = 1.5
    #     WEIGHT_MAX_CORNER   = 0.5
    #     WEIGHT_MAX_TILE     = 0.5
    #     WEIGHT_NODE_AVERAGE = 1.5 

    #     rows = board
    #     cols = list(zip(*board))
        
    #     # Calculate number of empty cells
    #     empty_count = sum(row.count(0) for row in rows)
        
    #     # Identify the maximum tile
    #     max_tile = max(max(row) for row in rows)
        
    #     # Check if max tile is in a corner
    #     corners = [rows[0][0], rows[0][-1], rows[-1][0], rows[-1][-1]]
    #     max_in_corner = 1 if max_tile in corners else 0

    #     # Define a snake pattern function for rows
    #     def snake_pattern_horizontal(board):
    #         """
    #         Returns a list of tile values in a snake-like traversal horizontally:
    #         first row left-to-right, second row right-to-left, etc.
    #         """
    #         sequence = []
    #         for i, row in enumerate(board):
    #             if i % 2 == 0:
    #                 # Even row index: left-to-right
    #                 sequence.extend(row)
    #             else:
    #                 # Odd row index: right-to-left
    #                 sequence.extend(row[::-1])
    #         return sequence

    #     # Define a snake pattern for columns as well
    #     def snake_pattern_vertical(board):
    #         """
    #         Snake-like traversal vertically:
    #         first column top-to-bottom, second column bottom-to-top, etc.
    #         """
    #         transposed = list(zip(*board))
    #         sequence = []
    #         for j, col in enumerate(transposed):
    #             col = list(col)
    #             if j % 2 == 0:
    #                 sequence.extend(col)       # top-to-bottom
    #             else:
    #                 sequence.extend(col[::-1]) # bottom-to-top
    #         return sequence

    #     def monotonicity_score_for_sequence(seq):
    #         """
    #         Compute monotonicity for a given sequence.
    #         We use the same method as row_monotonicity:
    #         lower inc_cost or dec_cost means more monotonic.
    #         """
    #         inc_cost = 0
    #         dec_cost = 0
    #         for i in range(len(seq)-1):
    #             if seq[i] > seq[i+1]:
    #                 inc_cost += abs(seq[i] - seq[i+1])
    #             else:
    #                 dec_cost += abs(seq[i] - seq[i+1])
    #         # Negative of min cost to reward more monotonic sequences
    #         return -min(inc_cost, dec_cost)

    #     # Compute horizontal snake monotonicity
    #     horizontal_snake_seq = snake_pattern_horizontal(board)
    #     horizontal_monotonicity = monotonicity_score_for_sequence(horizontal_snake_seq)

    #     # Compute vertical snake monotonicity
    #     vertical_snake_seq = snake_pattern_vertical(board)
    #     vertical_monotonicity = monotonicity_score_for_sequence(vertical_snake_seq)

    #     # Combine horizontal and vertical monotonicity
    #     monotonicity_score = horizontal_monotonicity + vertical_monotonicity

    #     # Smoothness calculation (remain the same)
    #     def smoothness_score_for_line(line):
    #         score_line = 0
    #         for i in range(len(line)-1):
    #             if line[i] != 0 and line[i+1] != 0:
    #                 score_line -= abs(line[i] - line[i+1])
    #         return score_line

    #     smoothness_score = 0
    #     for r in rows:
    #         smoothness_score += smoothness_score_for_line(r)
    #     for c in cols:
    #         c = list(c)
    #         smoothness_score += smoothness_score_for_line(c)
        
    #     # Empty cells score
    #     empty_score = empty_count
        
    #     # Max tile score: Using log2 for scaling
    #     max_tile_score = math.log2(max_tile) if max_tile > 0 else 0

    #     # Average node value (score/visit), safe division
    #     avg_node_value = value / visit if visit > 0 else 0

    #     # Combine the scores
    #     total_score = (WEIGHT_MONOTONICITY * monotonicity_score
    #                 + WEIGHT_SMOOTHNESS * smoothness_score
    #                 + WEIGHT_EMPTY * empty_score
    #                 + WEIGHT_MAX_CORNER * max_in_corner
    #                 + WEIGHT_MAX_TILE * max_tile_score
    #                 + WEIGHT_NODE_AVERAGE * avg_node_value)

    #     return total_score
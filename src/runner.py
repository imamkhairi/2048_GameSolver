from main import Game2048, AIPlayer
from z2048.controller import MCTS

def run_multiple_games(num_games: int, weights: dict, steps: int = 50):
    """
    Runs the 2048 game multiple times with specified MCTS weights and collects results.
    """
    results = []

    # Modify the weights in the MCTS.evaluate_board function
    def modify_weights():
        MCTS.WEIGHT_MONOTONICITY = weights.get('monotonicity', 2.0)
        MCTS.WEIGHT_SMOOTHNESS   = weights.get('smoothness', 2.0)
        MCTS.WEIGHT_EMPTY        = weights.get('empty', 1.5)
        MCTS.WEIGHT_MAX_CORNER   = weights.get('max_corner', 0.8)
        MCTS.WEIGHT_MAX_TILE     = weights.get('max_tile', 0.5)
        MCTS.WEIGHT_NODE_AVERAGE = weights.get('node_average', 1.3)

    for i in range(num_games):
        print(f"Running game {i+1}/{num_games} with weights: {weights}")
        modify_weights()  # Apply the weights before each game
        player = AIPlayer(weight=weights)
        game = Game2048(player)
        
        try:
            game.run()
        except SystemExit:
            results.append({
                "score": game.score,
                "max_tile": max(max(row) for row in game.board),
                "final_board": game.board
            })
            print(f"Game {i+1} finished with score {game.score}")
    
    return results

def adjust_weight_and_run(weight_name: str, original_value: float, delta: float, num_steps: int, num_games: int):
    """
    Adjusts a specific weight (e.g., 'monotonicity') by delta increments, plays multiple games,
    and collects results.
    """
    results_summary = []

    for step in range(-num_steps, num_steps + 1):
        adjusted_value = round(original_value + step * delta, 2)
        weights = {
            "monotonicity": 2.0,  # Original default values
            "smoothness": 2.0,
            "empty": 1.5,
            "max_corner": 0.8,
            "max_tile": 0.5,
            "node_average": 1.3,
        }
        weights[weight_name] = adjusted_value  # Modify the target weight

        print(f"\nTesting {weight_name} = {adjusted_value}")
        results = run_multiple_games(num_games, weights)
        results_summary.append({
            "adjusted_value": adjusted_value,
            "games": results
        })

    return results_summary

def main():
    # Configuration
    original_monotonicity = 2.0  # Starting value for monotonicity
    delta = 0.1                  # Increment value
    num_steps = 1                # Steps: -0.5 to +0.5 (0.1 * 5 = 0.5)
    num_games = 1                # Number of games per weight value

    # Run experiments for monotonicity weight
    monotonicity_results = adjust_weight_and_run(
        weight_name="monotonicity",
        original_value=original_monotonicity,
        delta=delta,
        num_steps=num_steps,
        num_games=num_games
    )

    # Print summary of results
    for result in monotonicity_results:
        print(f"\nMonotonicity Weight: {result['adjusted_value']}")
        for game_idx, game_result in enumerate(result['games']):
            print(f"{result['adjusted_value']}, {game_result['score']}, {game_result['max_tile']}")


if __name__ == "__main__":
    main()

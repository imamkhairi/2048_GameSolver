import random
from concurrent.futures import ProcessPoolExecutor, as_completed
from main import Game2048, AIPlayer
import math

def run_single_game(weights: dict) -> dict:
    """
    Runs a single 2048 game with the given weights and returns the score and highest tile.
    """
    player = AIPlayer(weight=weights)
    game = Game2048(player)
    try:
        game.run()
    except SystemExit:
        # Extract score and highest tile from the finished game
        score = game.score
        max_tile = max(max(row) for row in game.board)
        return {"score": score, "max_tile": max_tile}
    return {"score": 0, "max_tile": 0}

def run_games_for_weights(weights: dict, num_games: int):
    """
    Runs multiple games in smaller parallel batches for a single weight combination.
    For example, if num_games=10 and we choose batch_size=5, it will run two batches of 5 games each.
    """
    results = []
    batch_size = 5  # Adjust as needed
    num_batches = math.ceil(num_games / batch_size)

    for _ in range(num_batches):
        # Determine how many games to run in this batch (for cases where num_games is not a multiple of batch_size)
        current_batch_size = min(batch_size, num_games - len(results))
        
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(run_single_game, weights) for _ in range(current_batch_size)]
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
    
    return results

def random_search(num_trials: int, num_games_per_trial: int):
    """
    Performs random search by generating random weight combinations, running multiple games per combination
    in parallel (in smaller batches), and printing the results for each individual run.
    """
    # Define ranges for each weight
    weight_ranges = {
        "monotonicity": (1.0, 3.0),
        "smoothness": (0.5, 3.0),
        "empty": (0.5, 2.0),
        "max_corner": (0.5, 2.0),
        "max_tile": (0.5, 2.0),
        "node_average": (0.5, 2.5),
        "node_access": (0.05, 0.4)
    }

    print("weight_monotonicity, weight_smoothness, weight_empty, weight_max_corner, weight_max_tile, weight_node_average, weight_node_access, score, max_tile")

    for trial in range(num_trials):
        # Generate a random weight combination
        weights = {key: round(random.uniform(*value), 2) for key, value in weight_ranges.items()}

        # Run games for this weight combination in smaller parallel batches
        results = run_games_for_weights(weights, num_games_per_trial)

        # Print results for each game
        for result in results:
            print(f"{weights['monotonicity']}, {weights['smoothness']}, {weights['empty']}, "
                  f"{weights['max_corner']}, {weights['max_tile']}, {weights['node_average']}, {weights['node_access']}, "
                  f"{result['score']}, {result['max_tile']}")

def main():
    # Configuration
    num_trials = 10  # Number of random weight combinations to test
    num_games_per_trial = 10  # Number of games to run per weight combination (will be done in two batches of 5)

    print("Starting Random Search for MCTS Weights Optimization...\n")
    random_search(num_trials, num_games_per_trial)

if __name__ == "__main__":
    main()

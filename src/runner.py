import random
from main import Game2048, AIPlayer
# from z2048.controller import MCTS

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

def random_search(num_trials: int, num_games_per_trial: int):
    """
    Performs random search by generating random weight combinations, running multiple games per combination,
    and printing the results for each individual run.
    """
    # Define ranges for each weight
    weight_ranges = {
        "monotonicity": (1.0, 3.0),
        "smoothness": (0.5, 3.0),
        "empty": (0.5, 2.0),
        "max_corner": (0.1, 1.5),
        "max_tile": (0.1, 1.5),
        "node_average": (0.1, 2.0),
        "node_access": (0.05, 0.4)
    }

    print("weight_monotonicity, weight_smoothness, weight_empty, weight_max_corner, weight_max_tile, weight_node_average, weight_node_access, score, max_tile")

    for trial in range(num_trials):
        # Randomly generate a weight combination
        weights = {key: round(random.uniform(*value), 2) for key, value in weight_ranges.items()}

        for game_idx in range(num_games_per_trial):
            # Run a single game
            result = run_single_game(weights)

            # Print the weights and results for this run
            print(f"{weights['monotonicity']}, {weights['smoothness']}, {weights['empty']}, "
                  f"{weights['max_corner']}, {weights['max_tile']}, {weights['node_average']}, {weights['node_access']}, "
                  f"{result['score']}, {result['max_tile']}")

def main():
    # Configuration
    num_trials = 2  # Number of random weight combinations to test
    num_games_per_trial = 1  # Number of games to run per weight combination

    print("Starting Random Search for MCTS Weights Optimization...\n")
    random_search(num_trials, num_games_per_trial)

if __name__ == "__main__":
    main()

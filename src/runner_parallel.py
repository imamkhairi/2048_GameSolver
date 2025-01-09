# import random
# from concurrent.futures import ProcessPoolExecutor, as_completed
# from main import Game2048, AIPlayer
# import math

# def run_single_game(alpha: float, beta: float) -> dict:
#     """
#     Runs a single 2048 game with the given alpha and beta values and returns the score and highest tile.
#     """
#     player = AIPlayer(alpha=alpha, beta=beta)  # Pass alpha and beta directly
#     game = Game2048(player)
#     try:
#         game.run()
#     except SystemExit:
#         # Extract score and highest tile from the finished game
#         score = game.score
#         max_tile = max(max(row) for row in game.board)
#         return {"score": score, "max_tile": max_tile}
#     return {"score": 0, "max_tile": 0}

# def run_games_for_alpha_beta(alpha: float, beta: float, num_games: int):
#     """
#     Runs multiple games in smaller parallel batches for a single alpha-beta combination.
#     """
#     results = []
#     batch_size = 5  # Adjust as needed
#     num_batches = math.ceil(num_games / batch_size)

#     for _ in range(num_batches):
#         # Determine how many games to run in this batch (for cases where num_games is not a multiple of batch_size)
#         current_batch_size = min(batch_size, num_games - len(results))
        
#         with ProcessPoolExecutor() as executor:
#             futures = [executor.submit(run_single_game, alpha, beta) for _ in range(current_batch_size)]
#             for future in as_completed(futures):
#                 result = future.result()
#                 results.append(result)
    
#     return results

# def incremental_search_alpha_beta(start: float, stop: float, step: float, num_games_per_trial: int):
#     """
#     Performs search by incrementing alpha from start to stop with a fixed step, 
#     running multiple games per combination, and printing the results.
#     """
#     beta = 1.0  # Keep beta fixed
#     print("alpha, beta, score, max_tile")

#     current_alpha = start
#     while current_alpha <= stop:
#         # Run games for this alpha-beta combination
#         results = run_games_for_alpha_beta(current_alpha, beta, num_games_per_trial)

#         # Print results for each game
#         for result in results:
#             print(f"{current_alpha}, {beta}, {result['score']}, {result['max_tile']}")

#         # Increment alpha
#         current_alpha = round(current_alpha + step, 2)

# def main():
#     # Configuration
#     start_alpha = 0.05  # Starting value of alpha
#     stop_alpha = 1.0    # Ending value of alpha
#     step_alpha = 0.05   # Increment step for alpha
#     num_games_per_trial = 10  # Number of games to run per alpha-beta combination

#     print("Starting Incremental Search for Alpha-Beta Optimization...\n")
#     incremental_search_alpha_beta(start_alpha, stop_alpha, step_alpha, num_games_per_trial)

# if __name__ == "__main__":
#     main()


import random
from concurrent.futures import ProcessPoolExecutor, as_completed
from main import Game2048, AIPlayer
import math

def run_single_game(alpha: float, beta: float) -> dict:
    """
    Runs a single 2048 game with the given alpha and beta values and returns the score and highest tile.
    """
    player = AIPlayer(alpha=alpha, beta=beta)  # Pass alpha and beta directly
    game = Game2048(player)
    try:
        game.run()
    except SystemExit:
        # Extract score and highest tile from the finished game
        score = game.score
        max_tile = max(max(row) for row in game.board)
        return {"score": score, "max_tile": max_tile}
    return {"score": 0, "max_tile": 0}

def run_games_for_alpha_beta(alpha: float, beta: float, num_games: int):
    """
    Runs multiple games in smaller parallel batches for a single alpha-beta combination.
    """
    results = []
    batch_size = 5  # Adjust as needed
    num_batches = math.ceil(num_games / batch_size)

    for _ in range(num_batches):
        # Determine how many games to run in this batch (for cases where num_games is not a multiple of batch_size)
        current_batch_size = min(batch_size, num_games - len(results))
        
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(run_single_game, alpha, beta) for _ in range(current_batch_size)]
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
    
    return results

def incremental_search_alpha_fixed(start: float, stop: float, step: float, alpha: float, num_games_per_trial: int):
    """
    Performs search by incrementing beta from start to stop with a fixed step, 
    running multiple games per combination, and printing the results.
    """
    print("alpha, beta, score, max_tile")

    current_beta = start
    while current_beta <= stop:
        # Run games for this alpha-beta combination
        results = run_games_for_alpha_beta(alpha, current_beta, num_games_per_trial)

        # Print results for each game
        for result in results:
            print(f"{alpha}, {current_beta}, {result['score']}, {result['max_tile']}")

        # Increment beta
        current_beta = round(current_beta + step, 2)

def main():
    # Configuration
    alpha = 0.3          # Fixed value of alpha
    start_beta = 1.05    # Starting value of beta
    stop_beta = 2.0      # Ending value of beta
    step_beta = 0.05     # Increment step for beta
    num_games_per_trial = 10  # Number of games to run per alpha-beta combination

    print("Starting Incremental Search for Alpha-Beta Optimization...\n")
    incremental_search_alpha_fixed(start_beta, stop_beta, step_beta, alpha, num_games_per_trial)

if __name__ == "__main__":
    main()


# import random
# from concurrent.futures import ProcessPoolExecutor, as_completed
# from main import Game2048, AIPlayer
# import math

# def run_single_game(alpha: float, beta: float) -> dict:
#     """
#     Runs a single 2048 game with the given alpha and beta values and returns the score and highest tile.
#     """
#     player = AIPlayer(alpha=alpha, beta=beta)  # Pass alpha and beta directly
#     game = Game2048(player)
#     try:
#         game.run()
#     except SystemExit:
#         # Extract score and highest tile from the finished game
#         score = game.score
#         max_tile = max(max(row) for row in game.board)
#         return {"score": score, "max_tile": max_tile}
#     return {"score": 0, "max_tile": 0}

# def run_games_with_fixed_alpha_beta(alpha: float, beta: float, num_games: int):
#     """
#     Runs multiple games with fixed alpha and beta values and prints the results.
#     """
#     results = []
#     batch_size = 5  # Adjust as needed
#     num_batches = math.ceil(num_games / batch_size)

#     for _ in range(num_batches):
#         # Determine how many games to run in this batch (for cases where num_games is not a multiple of batch_size)
#         current_batch_size = min(batch_size, num_games - len(results))
        
#         with ProcessPoolExecutor() as executor:
#             futures = [executor.submit(run_single_game, alpha, beta) for _ in range(current_batch_size)]
#             for future in as_completed(futures):
#                 result = future.result()
#                 results.append(result)
    
#     # Print results
#     print("alpha, beta, score, max_tile")
#     for result in results:
#         print(f"{alpha}, {beta}, {result['score']}, {result['max_tile']}")
    
#     return results

# def main():
#     # Configuration
#     alpha = 0.3          # Fixed value of alpha
#     beta  = 0.6          # Fixed value of beta
#     num_games_per_trial = 5  # Number of games to run with fixed alpha-beta

#     print("Running Games with Fixed Alpha-Beta Values...\n")
#     run_games_with_fixed_alpha_beta(alpha, beta, num_games_per_trial)

# if __name__ == "__main__":
#     main()

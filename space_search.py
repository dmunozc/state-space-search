"""Demonstration of complete state-space search using the A* method.

This demo uses a toy problem. The objective of the game is to sit aliens
that like each other in a dinner situation.
It outputs the maximum score achieved and the seating for each alien.
"""

from dinner import Dinner
import random
import argparse
import numpy as np
from datetime import datetime
from itertools import permutations


def best_for_location(party, location, noise):
    """
    Calculates which alien gets the maximum score when seating at
    location
    """
    aliens_not_seated = party.aliens_not_seated.copy()
    scores_per_alien = {}
    original_score = party.bar_score()
    # For each alien that is not seated find its a-star score.
    for alien_not_seated in aliens_not_seated:
        party.seat_alien_at(alien_not_seated, location)
        # g is the score of the table before they were seated + the
        # score of the table once they seat.
        # g + h is the a-start heuristic.
        g = party.location_score(location) + original_score
        h = float("-inf")
        adjacent_locations = party.get_empty_adjacent_locations(location)
        # Get all pairs that can seat in the adjacent empty location to the
        # current alien.
        # Will calculate maximum score possible by seating aliens adjacent
        # and across.
        remaining_pairs = permutations(
            party.aliens_not_seated, len(adjacent_locations)
        )
        for pair in remaining_pairs:
            temp_score = g
            # Seat each alien and calculate its immediate impact on the table.
            for i in range(len(adjacent_locations)):
                party.seat_alien_at(pair[i], adjacent_locations[i])
                temp_score += party.location_score(adjacent_locations[i])
            if temp_score > h:
                h = temp_score
            # Undo the seating for trying next pair.
            for i in range(len(adjacent_locations)):
                party.unseat_location(adjacent_locations[i])
        scores_per_alien[alien_not_seated] = g + h
        # Undo and try next alien.
        party.unseat_location(location)
    # return sorted aliens by score, want to sometimes explore a random path
    # by using swap_random.
    return swap_random(
        sorted(scores_per_alien.items(), key=lambda x: x[1], reverse=True),
        noise,
    )


def swap_random(seq, noise=0.25, max_nodes=12):
    """Swaps two locations randomly in a list.
     modified code from
     stackoverflow.com/questions/47724017/swap-two-values-randomly-in-list
    """
    # Swap makes no sense if less than 3 items.
    if len(seq) <= 3:
        return seq
    # Sometimes we dont want to randomly swap.
    if random.random() > noise:
        return seq[:max_nodes]
    idx = range(len(seq))
    i1, i2 = random.sample(idx, 2)
    seq[i1], seq[i2] = seq[i2], seq[i1]
    return seq[:max_nodes]


def seat_next_alien(
    party, locations, time_start, max_seconds, solution, noise
):
    """Tries to find the best alien to set at the needed location."""
    if not locations:
        return solution
    # Make sure to stop if time runs out.
    if (datetime.now() - time_start).total_seconds() < max_seconds:
        for loc in locations:
            # Get sorted list of aliens that would give the best score at loc
            scores_per_alien = best_for_location(
                party=party, location=loc, noise=noise
            )
            for pair in scores_per_alien:
                # for each of those aliens, seat them and find the next best
                # alien for empty locations
                party.seat_alien_at(pair[0], loc)
                adj_locations = party.get_empty_adjacent_locations(loc)
                # Make sure to stop if time runs out.
                if (datetime.now() - time_start).total_seconds() < max_seconds:
                    solution = seat_next_alien(
                        party,
                        adj_locations,
                        time_start,
                        max_seconds,
                        solution,
                        noise,
                    )
                # Once the bar is full, get the scores and if it is
                # better, record it.
                if party.bar_full():
                    current_score = party.bar_score()
                    if current_score > solution["max_score"]:
                        solution = party.seating_dict()
                        solution["max_score"] = current_score
                # Unseat the last alien seated and continue looking.
                party.unseat_location(loc)
                # Make sure to stop if time runs out.
                if (datetime.now() - time_start).total_seconds() > max_seconds:
                    break
    return solution


def solve_astar(
    n_aliens, preference_matrix, time_start, max_seconds=60, noise=0.2
):
    """Solves the problem using complete state space search."""
    # Sum rows and columns for each alien. Aliens with lowest scores
    # must be seated at corner since it is not liked and does not like
    # others.
    row = np.sum(preference_matrix, axis=1)
    col = np.sum(preference_matrix, axis=0)
    scores = []
    for i in range(len(row)):
        scores.append(row[i] + col[i])
    worst_aliens = np.argsort(scores)
    party = Dinner(n_aliens, preference_matrix)
    # Start the candidate solutions.
    solution = {"max_score": -500}
    # Starting with the lowest score alien, sit them at a corner and try
    # seating the remaining aliens.
    for bad_alien in worst_aliens:
        party.seat_alien_at(bad_alien, 0)
        adj_locations = party.get_empty_adjacent_locations(0)
        solution = seat_next_alien(
            party=party,
            locations=adj_locations,
            time_start=time_start,
            max_seconds=max_seconds,
            solution=solution,
            noise=noise,
        )
        party.unseat_location(0)
        # Make sure to stop if time runs out.
        if (datetime.now() - time_start).total_seconds() >= max_seconds:
            break
    max_score = solution.pop("max_score")
    return (
        max_score,
        sorted(solution.items(), key=lambda x: x[1], reverse=False),
    )


def main(preference_file_loc, max_seconds=60):
    file = open(preference_file_loc, "r")
    lines = file.readlines()
    n_aliens = int(lines[0].rstrip())
    preference_matrix = []
    # Build preference matrix from file.
    for line in lines[1:]:
        preference_matrix.append([int(x) for x in line.rstrip().split(" ")])
    # Get score and solution.
    score, couch = solve_astar(
        n_aliens,
        preference_matrix,
        time_start=datetime.now(),
        max_seconds=max_seconds,
        noise=0.2,
    )
    print("Maximum score", score)
    print("Seating arrangement")
    for location, alien in couch:
        print("Alien", alien, "at location", location)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-pref",
        dest="preference_file",
        help="seating preference file",
        default="pref1.txt",
    )
    parser.add_argument(
        "-mt",
        dest="max_time",
        help="maximum running time, in seconds",
        default=60,
    )
    args = parser.parse_args()
    main(args.preference_file, int(args.max_time))

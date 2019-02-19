import itertools
import datetime
from collections import Counter

import numpy as np
import pandas as pd
from tqdm import tqdm

import src.metrics as metrics
from src.utils import get_closest_power

DEBUG = False

def log(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


# Randomly select players from different teams until no teams are left
# Unfortunately ends up with the last team producing many collisions
def generate_greedy_solution(students, previous_teaming, precision):
    n_students = len(students)
    n_teams = get_closest_power(len(students) // 5)

    grouped = previous_teaming.groupby('Team').groups
    previous_teams = [grouped[g] for g in grouped]
    teams = []
    counts = [len(x) for x in previous_teams]
    used_counts = [0] * n_teams
    for t in range(n_teams):
        not_used_teams = [x for x in range(n_teams) if used_counts[x] < counts[x]]
        team = []
        while len(team) < counts[t] and len(not_used_teams):
            choice = np.random.choice(not_used_teams)
            team.append(previous_teams[choice][used_counts[choice]])
            used_counts[choice] += 1
            not_used_teams.remove(choice)
        not_used_teams = [x for x in range(n_teams) if used_counts[x] < counts[x]]
        while len(team) < counts[t]:
            choice = np.random.choice(not_used_teams)
            team.append(previous_teams[choice][used_counts[choice]])
            used_counts[choice] += 1
            if used_counts[choice] == counts[choice]:
                not_used_teams.remove(choice)
        teams.append(team)
    teaming = pd.concat([students.loc[idxs].assign(Team=i+1) for i, idxs in enumerate(teams)])
    metric_values = metrics.sem_multi_objective(teaming, previous_teaming)
    return teaming, round(metric_values, precision)

def generate_random_solution(students, previous_teaming, precision):
    # Often worse than random permutation
    # if previous_teaming is not None:
    #     return generate_greedy_solution(students, previous_teaming, precision)
    n_students = len(students)
    n_teams = get_closest_power(len(students) // 5)
    shuffled = np.random.permutation(n_students)
    teams = np.array_split(shuffled, n_teams)
    teaming = pd.concat([students.iloc[idxs].assign(Team=i+1) for i, idxs in enumerate(teams)])
    metric_values = metrics.sem_multi_objective(teaming, previous_teaming)
    return teaming, round(metric_values, precision)

def get_collisions(teaming, previous_teaming, pairs):
    collisions = []
    is_involved = dict(zip(teaming.index, np.zeros_like(teaming.index, dtype=bool)))
    if previous_teaming is None:
        return collisions, is_involved
    if not isinstance(previous_teaming, tuple):
        previous_teaming = (previous_teaming,)
    for entry, (s1, s2) in enumerate(pairs):
        if teaming['Team'][s1] != teaming['Team'][s2]:
            continue
        for i, pteaming in enumerate(previous_teaming):
            if pteaming['Team'][s1] == pteaming['Team'][s2]:
                collisions.append(entry)
                is_involved[s1] = True
                is_involved[s2] = True
                break
    return collisions, is_involved

# Mac (20 steps) run time: 0.13s, with pteaming (40 students): 0.07s
def mutate(teaming, steps, previous_teaming, precision, pairs):
    mutation = pd.DataFrame(teaming.copy())
    # for _ in range(steps):
    p = np.ones(len(pairs), dtype=float)
    if previous_teaming is None:
        for i, (s1, s2) in enumerate(pairs):
            # Don't switch partners from the same team
            if mutation['Team'][s1] == mutation['Team'][s2]:
                p[i] = 0
            else:
                p[i] += 6 - 2 * sum(mutation.loc[s1] == mutation.loc[s2])
    else:
        collisions, is_involved = get_collisions(mutation, previous_teaming, pairs)
        for i, (s1, s2) in enumerate(pairs):
            if mutation['Team'][s1] == mutation['Team'][s2]:
                p[i] = 0
            else:
                # Partner collisions should be more likely switched
                if is_involved[s1] or is_involved[s2]:
                    p[i] = 10
                p[i] += 6 - 2 * sum(mutation.loc[s1] == mutation.loc[s2])
    for choice in np.random.choice(len(pairs), steps, replace=False, p=p/sum(p)):
        i1, i2 = pairs[choice]
        temp = mutation['Team'][i1]
        mutation.loc[i1, 'Team'] = mutation['Team'][i2]
        mutation.loc[i2, 'Team'] = temp
    metric_values = metrics.sem_multi_objective(mutation, previous_teaming)
    return mutation, round(metric_values, precision)

def check_domination(P, new_x):
    # 1: p dominates new_x;  -1: new_x dominates p;  0: no domination
    relation = np.zeros(len(P))
    found_equal = False
    for i, p in enumerate(P):
        any_greater_than_new_x = any(p[1] > new_x[1])
        any_lower_than_new_x = any(p[1] < new_x[1])
        # if new_x[1]['Collision'] < p[1]['Collision'] and (any_lower_than_new_x or not any_greater_than_new_x):
        #     # Manual tweak: new_x partly dominates p regarding collisions (so it won't kick out p but wil be kept in P)
        #     relation[i] = -0.5
        # elif not any_lower_than_new_x and any_greater_than_new_x:
        if not any_lower_than_new_x and any_greater_than_new_x:
            # new_x dominates p
            relation[i] = -1
        elif not any_greater_than_new_x and any_lower_than_new_x:
            # p dominates new_x
            relation[i] = 1
        elif not any_greater_than_new_x and not any_lower_than_new_x:
            found_equal = True
    log('Removing {} out of {} elements'.format(sum(relation == - 1), len(P)))
    P = list(np.array(P)[relation > -1])
    if all(relation < 1) and not found_equal:
        # No element dominates new_x
        log("Not dominated!")
        P.append(new_x)
        log('P scoring:', sorted([round(overall_score(p[1]), 3) for p in P]))
    return P

def overall_score(scores):
    return np.sqrt((scores**2).sum())

def best_element(P):
    distances = np.array([overall_score(p[1]) for p in P])
    # Select the nearest element for zero
    return P[distances.argmin()]

def semo(students, semester=None, debug=False, init_P=None, epochs=5,
         mutation_intensity=3, previous_teaming=None, precision=2, progressbar=None):
    # Give the ability to run the function multiple times on the same collection
    # of Pareto elements. Each element consists of a tuple (solution, metrics)
    if init_P is None:
        P = [generate_random_solution(students, previous_teaming, precision)]
    else:
        P = init_P
    log('Init:', ' | '.join([f'{x:.4f}' for x in P[0][1]]))
    pairs = list(itertools.combinations(sorted(P[0][0].index), 2))
    bar = (progressbar or tqdm)(range(epochs))
    for i in bar:
        try:
            x = P[np.random.choice(range(len(P)), 1)[0]]
            # metrics.print_metric(metrics.sem_multi_objective(x[0], previous_teaming), 'debug #1')
            x2 = mutate(x[0], mutation_intensity, previous_teaming, precision, pairs)
            log('- From', ' | '.join([f'{x:.4f}' for x in x[1]]))
            log('--> To', ' | '.join([f'{x:.4f}' for x in x2[1]]))
            # metrics.print_metric(metrics.sem_multi_objective(x[0], previous_teaming), 'debug #2')
            P = check_domination(P, x2)
            if i % np.ceil(epochs / 100) == 0:
                solution, scores = best_element(P)
                score_str = ' | '.join([f'{x:.4f}' for x in scores])
                bar.set_description(f"Errors: {score_str} => {overall_score(scores):.3f}")
                bar.refresh()  # to show immediately the update
                # metric_values = metrics.sem_multi_objective(x2[0], previous_teaming)
        except KeyboardInterrupt:
            print(f'User Interaction: Stopped earlier at epoch {i} !')
            break
    best = best_element(P)
    print('\nBest solution out of {} elements:'.format(len(P)))
    output_metrics = metrics.print_metric(best[1], 'semester {semester}' if semester else 'given semester')
    if hasattr(bar, 'set_final_desc'):
        bar.set_final_desc(output_metrics)
    if debug:
        return P
    return best[0]

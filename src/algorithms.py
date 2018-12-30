import numpy as np
import pandas as pd
from tqdm import tqdm

import src.metrics as metrics

def arbitrary_teaming(students):
    n_teams = len(students) // 5
    groups = []
    for i in range(n_teams - 1):
        team = students[i*5:(i+1)*5]
        groups.extend((x['hash'], i+1, x['Sex'], x['Discipline'], x['Nationality'])
                      for _, x in team.iterrows())
    last_team_idx = len(students) - 5
    groups.extend((x['hash'], n_teams, x['Sex'], x['Discipline'], x['Nationality'])
                  for _, x  in students[last_team_idx:].iterrows())
    grouped = pd.DataFrame(groups, columns=['hash', 'Team', 'Sex', 'Discipline', 'Nationality'])
    return grouped

def generate_random_solution(students, previous_teaming, precision):
    n_students = len(students)
    n_teams = len(students) // 5
    shuffled = np.random.permutation(n_students)
    teams = np.split(shuffled[:n_students], n_teams)
    teams[-1] = np.append(teams[-1], shuffled[n_students:])
    teaming = pd.concat([students.iloc[idx].assign(Team=i+1) for i, idx in enumerate(teams)])
    metric_values = metrics.sem_multi_objective(teaming, previous_teaming)
    return teaming, round(metric_values, precision)

def mutate(teaming, steps, previous_teaming, precision):
    mutation = pd.DataFrame(teaming.copy())
    for _ in range(steps):
        i1, i2 = np.random.choice(mutation.index, 2, replace=False)
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
        if not any_lower_than_new_x and any_greater_than_new_x:
            # new_x dominates p
            relation[i] = -1
        elif not any_greater_than_new_x and any_lower_than_new_x:
            # p dominates new_x
            relation[i] = 1
        elif not any_greater_than_new_x and not any_lower_than_new_x:
            found_equal = True
    # print('Removing {} out of {} elements'.format(sum(relation == - 1), len(P)))
    P = list(np.array(P)[relation > -1])
    if all(relation < 1) and not found_equal:
        # print('Adding dominating element')
        # No element dominates new_x
        P.append(new_x)
    return P

def best_element(P):
    distances = np.array([np.sqrt((p[1]**2).sum()) for p in P])
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
    bar = (progressbar or tqdm)(range(epochs))
    for i in bar:
        try:
            x = P[np.random.choice(range(len(P)), 1)[0]]
            # metrics.print_metric(metrics.sem_multi_objective(x[0], previous_teaming), 'debug #1')
            x2 = mutate(x[0], mutation_intensity, previous_teaming, precision)
            # metrics.print_metric(metrics.sem_multi_objective(x[0], previous_teaming), 'debug #2')
            P = check_domination(P, x2)
            if i % 10 == 0:
                scores = metrics.sem_multi_objective(x2[0])
                score_str = ' | '.join([f'{x:.2f}' for x in scores])
                bar.set_description(f"Errors: {score_str} => {scores.mean():.3f}")
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

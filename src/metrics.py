import numpy as np
import pandas as pd
import itertools as it

#------------------------------------------------------------------------------#
# Multi-objective definition
#------------------------------------------------------------------------------#

COLLISIONS_PUNISHMENT = 1
MIN_STUDENTS = 75
MAX_STUDENTS = 85

def metric_gender_balance(team):
    k = len(team)
    assert k in (4,5,6), team
    men_share = sum(team['Sex'].str.lower() == 'm') / k
    women_share = 1 - men_share
    opt_balance = np.ceil(k/2) * np.trunc(k/2) / k**2
    return 1 - men_share * women_share / opt_balance

def metric_discipline(team):
    k = len(team)
    occurences = team['Discipline'].value_counts()
    l2norm = np.sqrt((occurences**2).sum())
    return (l2norm - np.sqrt(k))/(k-np.sqrt(k))

def metric_nationality(team):
    k = len(team)
    occurences = team['Nationality'].value_counts()
    l2norm = np.sqrt((occurences**2).sum())
    return (l2norm - np.sqrt(k))/(k-np.sqrt(k))


"""
# Update: The below described case won't happen so just compare both rows through a hashmap -> O(1)

Regarding the case of students occuring multiple times over all semesters
multiple_occurences = dict((x, y > 1) for (x, y) in students['hash'].value_counts().iteritems())

[...] -> When calculating collisions:

# If students occure multiple times we have to check all students -> O(n)
if multiple_occurences[team['hash'][s1]] or multiple_occurences[team['hash'][s2]]:
     occ = previous_teaming['hash'].isin([team['hash'][s1], team['hash'][s2]])
     entries = previous_teaming[occ]
     # If there is a team within a semester in which both members are (a group has size 2) there is a collision
     if entries.groupby(['Semester', 'Team']).size().max() == 2:
         collisions += 1
"""
def metric_collision(team, previous_teaming=None):
    if previous_teaming is None:
        return 0
    k = len(team)
    if isinstance(previous_teaming, tuple):
        previous_teaming1, previous_teaming2 = previous_teaming
        collisions = sum((previous_teaming1['Team'][s1] == previous_teaming1['Team'][s2]) + \
                         (previous_teaming2['Team'][s1] == previous_teaming2['Team'][s2])
                         for s1, s2 in it.combinations(team.index, 2))
        possible_collisions = 20 if k == 5 else 30  # 2 * (k * (k - 1) / 2)
        return collisions / possible_collisions
    collisions = sum(previous_teaming['Team'][s1] == previous_teaming['Team'][s2]
                     for s1, s2 in it.combinations(team.index, 2))
    # Normalize using the gaussian summation formula
    possible_collisions = 10 if k == 5 else 15  # k * (k - 1) / 2
    return (collisions / possible_collisions) ** (1/COLLISIONS_PUNISHMENT)

def multi_objective(team, previous_teaming=None):
    metric = pd.Series(index=['Gender', 'Discipline', 'Nationality', 'Collision'])
    metric['Gender'] = metric_gender_balance(team)
    metric['Discipline'] = metric_discipline(team)
    metric['Nationality'] = metric_nationality(team)
    metric['Collision'] = metric_collision(team, previous_teaming)
    # print('{:.2f},{:.2f},{:.2f},{:.2f}'.format(
    #    metric['Gender'], metric['Discipline'], metric['Nationality'], metric['Collision']))
    # print(team.head())
    return metric

def sem_multi_objective(teaming, previous_teaming=None):
    results = []
    g = teaming.groupby('Team')
    for team_number, team_idx in g.groups.items():
        team = teaming.loc[team_idx]
        results.append(multi_objective(team, previous_teaming))
    results = pd.DataFrame(results)
    reported = np.mean(results, axis=0)
    # Collision metric is always more important than the others
    reported['Collision'] = 10 * np.mean(results['Collision'])
    # Take the average for each objective
    return reported

def overall_multi_objective(teaming, previous_teaming=None):
    results = []
    for semester in ('WT-15', 'ST-16', 'WT-16', 'ST-17'):
        sem_teaming = teaming[teaming['Semester'] == semester]
        assert MIN_STUDENTS <= len(sem_teaming) <= MAX_STUDENTS,\
            'Expected between 75 and 85 students but got {}'.format(len(sem_teaming))
        results.append(round(sem_multi_objective(sem_teaming, previous_teaming), 2))
    return np.mean(results, axis=0)

def print_metric(metric_output, teaming_name):
    output = ('Multi-objective metric:\n' +
              'GenderBalance={:.2f}, Disciplines={:.2f}'.format(*metric_output[:2]) +
              ', Nationalities={:.2f}, Collision={:.2f}'.format(*metric_output[2:]))
    print(output)
    return output

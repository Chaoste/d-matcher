import os

import pandas as pd

import algorithms as algo
import utils
import metrics

METRICS = ('Gender', 'Discipline', 'Nationality', 'Collision')
SEMESTER = ('WT-15', 'ST-16', 'WT-16', 'ST-17')

# Input file should be a csv file
def read_input(path):
    students = pd.read_csv(path)
    return students

def find_teaming(students):
    teaming = utils.process_semesters(
        students, algo.semo, epochs=6000,
        previous_teaming=teaming2, mutation_intensity=20,
        precision=4
    )
    metric_values = metrics.overall_multi_objective(teaming)
    metrics.print_metric(metric_values, 'Teaming')
    return (teaming, metric_values)

def store_output(teaming):
    dir, filename = os.path.split(path)
    output_path = os.path.join(dir, 'output_{}'.format(filename))
    utils.store_teaming(teaming, output_path)
    print('Saved results to {}.'.format(output_path))

def execute(path):
    students = read_input(path)
    teaming, metric_values = find_teaming(students)
    store_output(teaming)


### Snippets from notebook ###


def metric_collision(team, previous_teaming=None):
    if previous_teaming is None:
        return 0
    k = len(team)
    if isinstance(previous_teaming, tuple):
        previous_teaming1, previous_teaming2 = previous_teaming
        collisions = sum((previous_teaming1['Team'][s1] == previous_teaming1['Team'][s2]) +
                         (previous_teaming2['Team'][s1] == previous_teaming2['Team'][s2])
                         for s1, s2 in it.combinations(team.index, 2))
        return collisions
    collisions = sum(previous_teaming['Team'][s1] == previous_teaming['Team'][s2]
                     for s1, s2 in it.combinations(team.index, 2))
    return collisions

def sem_multi_objective(teaming, previous_teaming=None):
    results = 0
    for i in range(16):
        team = teaming[teaming['Team'] == i+1]
        results += metric_collision(team, previous_teaming)
    # Take the average for each objective
    return results

def overall_multi_objective(teaming, previous_teaming=None):
    results = 0
    for semester in ('WT-15', 'ST-16', 'WT-16', 'ST-17'):
        sem_teaming = teaming[teaming['Semester'] == semester]
        results += sem_multi_objective(sem_teaming, previous_teaming)
    return results

def print_conclusion():
    teaming1 = pd.read_csv('output/teaming1.out')
    teaming2 = pd.read_csv('output/teaming2.out')
    teaming3 = pd.read_csv('output/teaming3.out')
    teaming4 = pd.read_csv('output/teaming4.out')
    print(overall_multi_objective(teaming3, teaming2))
    print(overall_multi_objective(teaming4, (teaming2, teaming3)))

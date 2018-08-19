import os
from typing import Optional, Tuple

import pandas as pd
import numpy as np

import algorithms as algo
import utils
import metrics

METRICS = ('Gender', 'Discipline', 'Nationality', 'Collision')
SEMESTER = ('WT-15', 'ST-16', 'WT-16', 'ST-17')

Students = pd.DataFrame
PreviousTeaming = Optional[pd.DataFrame, Tuple[pd.DataFrame]]
Teaming = pd.DataFrame
TeamingResult = Tuple[pd.DataFrame, np.ndarray]


# Input file should be a csv file
def read_input(path: str) -> pd.DataFrame:
    students = pd.read_csv(path)
    return students


def find_teaming(students: pd.DataFrame,
                 previous_teaming: PreviousTeaming = None) -> TeamingResult:
    teaming = utils.process_semesters(
        students, algo.semo, epochs=6000,
        previous_teaming=previous_teaming, mutation_intensity=20,
        precision=4
    )
    metric_values = metrics.overall_multi_objective(teaming)
    metrics.print_metric(metric_values, 'Teaming')
    return (teaming, metric_values)


def store_output(teaming: Teaming, path: str):
    dir, filename = os.path.split(path)
    output_path = os.path.join(dir, 'output_{}'.format(filename))
    utils.store_teaming(teaming, output_path)
    print('Saved results to {}.'.format(output_path))


def execute(path: str):
    students = read_input(path)
    teaming, metric_values = find_teaming(students)
    store_output(teaming, path)


if __name__ == '__main__':
    execute('input/students.csv')

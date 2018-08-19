import os
from typing import Optional, Tuple, Union
from time import gmtime, strftime

import pandas as pd
import numpy as np

import algorithms as algo
import utils
# import metrics

METRICS = ('Gender', 'Discipline', 'Nationality', 'Collision')
SEMESTER = ('WT-15', 'ST-16', 'WT-16', 'ST-17')

Students = pd.DataFrame
PreviousTeaming = Optional[Union[pd.DataFrame, Tuple[pd.DataFrame]]]
Teaming = pd.DataFrame
TeamingResult = Tuple[pd.DataFrame, np.ndarray]


# Input file should be a csv file
def read_input(path: str) -> pd.DataFrame:
    students = pd.read_csv(os.path.join('input', path))
    return students[['hash', 'Sex', 'Discipline', 'Nationality']]


def find_teaming(students: pd.DataFrame,
                 previous_teaming: PreviousTeaming = None) -> TeamingResult:
    teaming = algo.semo(
        students, epochs=6000, precision=4,
        previous_teaming=previous_teaming, mutation_intensity=20) \
        .reset_index()
    return teaming


def store_output(teaming: Teaming, path: str):
    _, filename = os.path.split(path)
    filename, ext = os.path.splitext(filename)
    timestamp = strftime("%Y_%m_%d_%H_%M_%S", gmtime())
    output_path = os.path.join('output', f'teamings_{timestamp}{ext}')
    utils.store_teaming(teaming, output_path)
    print('Saved results to {}.'.format(output_path))


def execute(path: str):
    students = read_input(path)
    teaming = find_teaming(students)
    store_output(teaming, path)


if __name__ == '__main__':
    execute('students_wt_15.csv')

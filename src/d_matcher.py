import os
from typing import Optional, Tuple, Union
from time import gmtime, strftime

import pandas as pd
import numpy as np

import src.algorithms as algo
import src.utils as utils
# import metrics

METRICS = ('Gender', 'Discipline', 'Nationality', 'Collision')
SEMESTER = ('WT-15', 'ST-16', 'WT-16', 'ST-17')

Students = pd.DataFrame
PreviousTeaming = Optional[Union[pd.DataFrame, Tuple[pd.DataFrame]]]
Teaming = pd.DataFrame
TeamingResult = Tuple[pd.DataFrame, np.ndarray]


# Input file should be a csv file
def read_input(path: str) -> pd.DataFrame:
    students = pd.read_csv(path)
    return students[['hash', 'Sex', 'Discipline', 'Nationality']]


def find_teaming(students: pd.DataFrame,
                 previous_teaming: PreviousTeaming = None,
                 epochs: int = 6000,
                 progressbar=None) -> TeamingResult:
    teaming = algo.semo(
        students, epochs=epochs, precision=4,
        previous_teaming=previous_teaming, mutation_intensity=20,
        progressbar=progressbar) \
        .reset_index()
    return teaming


def store_output(teaming: Teaming, path: str, no: int):
    directory, filename = os.path.split(path)
    filename, ext = os.path.splitext(filename)
    timestamp = strftime("%Y_%m_%d_%H_%M_%S", gmtime())
    output_path = os.path.join(directory, f'teamings_{no}__{timestamp}{ext}')
    utils.store_teaming(teaming, output_path)
    print('Saved results to {}.'.format(output_path))


def execute(path: str, epochs: int = 6000, progressbar = None, amount_teamings = 1):
    assert path is not None, 'Path of input file may not be None'
    assert 0 < amount_teamings < 4, 'Only 1, 2 or 3 teamings are possible'
    print(f'Execute D-Matcher with {epochs} epochs for input file {path}')
    students = read_input(path)
    teaming1 = find_teaming(students, epochs=epochs, progressbar=progressbar)
    store_output(teaming1, path, no=1)
    if amount_teamings > 1:
        teaming2 = find_teaming(students, epochs=epochs, progressbar=progressbar, previous_teaming=teaming1)
        store_output(teaming2, path, no=2)
        if amount_teamings > 2:
            teaming3 = find_teaming(students, epochs=epochs, progressbar=progressbar, previous_teaming=(teaming1, teaming2))
            store_output(teaming3, path, no=3)
            return [teaming1, teaming2, teaming3]
        return [teaming1, teaming2]
    return [teaming1]


if __name__ == '__main__':
    execute('input/students_wt_15.csv', epochs=300, amount_teamings=3)

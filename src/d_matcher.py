import os
from typing import Optional, Tuple, Union, List
from time import gmtime, strftime

import pandas as pd
import numpy as np

import src.algorithms as algo
import src.utils as utils
# import metrics

METRICS = ('Gender', 'Discipline', 'Nationality', 'Collision')
SEMESTER = ('WT-15', 'ST-16', 'WT-16', 'ST-17')

Students = pd.DataFrame
PreviousTeaming = Optional[Union[pd.DataFrame, Tuple[pd.DataFrame], List[pd.DataFrame]]]
Teaming = pd.DataFrame
TeamingResult = Tuple[pd.DataFrame, np.ndarray]


# Input file should be a csv file
def read_input(path: str) -> pd.DataFrame:
    if path[-5:] == '.xlsx':
        students = pd.read_excel(path)
    else:
        students = pd.read_csv(path, index_col=0)
    return students


def read_and_transform_input(path: str) -> pd.DataFrame:
    students = read_input(path)
    students = utils.transform_to_old_format(students)
    return students[['hash', 'Sex', 'Discipline', 'Nationality']]


def find_teaming(students: pd.DataFrame,
                 previous_teaming: PreviousTeaming = None,
                 epochs: int = 6000,
                 progressbar=None) -> TeamingResult:
    if type(previous_teaming) == list:
        previous_teaming = tuple(previous_teaming)
    teaming = algo.semo(
        students, epochs=epochs, precision=4,
        previous_teaming=previous_teaming, mutation_intensity=20,
        progressbar=progressbar) \
        .reset_index()
    return teaming


def store_output(teamings: List[Teaming], path: str):
    teaming_columns = ['1st', '2nd', '3rd']
    enriched_students = read_input(path)
    if 'hash' not in enriched_students.columns:
        enriched_students = utils.enhance_with_hash(enriched_students)
    for i, teaming in enumerate(teamings):
        t = teaming[['hash', 'Team']].rename(
            {'Team': teaming_columns[i]}, axis=1)
        enriched_students = enriched_students.merge(t)
    directory, filename = os.path.split(path)
    filename, _ = os.path.splitext(filename)
    timestamp = strftime("%Y_%m_%d_%H_%M_%S", gmtime())
    output_path = os.path.join(directory, f'Teamings__{timestamp}')
    enriched_students.drop(columns="hash", inplace=True)
    utils.store_teaming(enriched_students, output_path)
    print('Saved results to {}.'.format(output_path))


def execute(path: str, epochs: int = 6000, progressbar = None,
            amount_teamings = 1, split_after_first_teamings=True):
    assert path is not None, 'Path of input file may not be None'
    assert 0 < amount_teamings < 4, 'Only 1, 2 or 3 teamings are possible'
    print(f'Execute D-Matcher with {epochs} epochs for input file {path}')
    students = read_and_transform_input(path)
    teamings = []
    teamings.append(find_teaming(students, epochs=epochs, progressbar=progressbar))
    if not split_after_first_teamings:
        if amount_teamings > 1:
            teamings.append(find_teaming(students, epochs=epochs, progressbar=progressbar, previous_teaming=teamings[0]))
        if amount_teamings > 2:
            teamings.append(find_teaming(students, epochs=epochs, progressbar=progressbar, previous_teaming=teamings))
    else:
        assert amount_teamings == 3, 'Splitting into orange and yellow track'\
            'are only supported for creating three teamings'
        teamings1, teamings2, students1, students2 = utils.split_tracks(teamings[0], students)
        assert False, 'Currently not supported'
        # TODO: SEMO only supprots 80 students
        teamings1.append(find_teaming(students1, epochs=epochs, progressbar=progressbar, previous_teaming=teamings1))
        teamings1.append(find_teaming(students1, epochs=epochs, progressbar=progressbar, previous_teaming=teamings1))
        teamings2.append(find_teaming(students2, epochs=epochs, progressbar=progressbar, previous_teaming=teamings2))
        teamings2.append(find_teaming(students2, epochs=epochs, progressbar=progressbar, previous_teaming=teamings2))
        teamings = utils.merge_tracks(teamings1, teamings2)
    store_output(teamings, path)
    return teamings


if __name__ == '__main__':
    execute('input/students_wt_15.csv', epochs=300, amount_teamings=3)

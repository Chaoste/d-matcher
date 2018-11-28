import pandas as pd
import itertools as it
import csv

import src.metrics as metrics
import src.xlsx_utils as xlsx_utils

# --------------------------------------------------------------------------- #
# Helper
# --------------------------------------------------------------------------- #


def process_semesters(students, target_func, *args, **kwargs):
    result = []  # pd.DataFrame(columns=['hash', 'Team', 'Semester', 'Sex', 'Discipline', 'Nationality'])
    for semester in ('WT-15', 'ST-16', 'WT-16', 'ST-17'):
        sem_students = students[students['Semester'] == semester]
        assert len(sem_students) in (80, 81),\
            'Expected 80 or 81 students but got {}'.format(len(students))
        partial_result = target_func(sem_students, semester, *args, **kwargs)
        result.append(partial_result)
    return pd.DataFrame(pd.concat(result).copy(), index=range(321))


def store_teaming(teaming, filename=None, show_all=True):
    assert all(teaming.columns[-3:] == ['1st', '2nd', '3rd']), \
        'Only 3 teamings are supported for xlsx export'
    xlsx_utils.export(teaming, filename)

    # Use the same format as used for the input data
    # Generates FutureWarning: Passing list-likes to .loc or [] with missing label
    # return teaming.to_csv(f'{filename}.csv', quoting=csv.QUOTE_MINIMAL, index=False,
    #                       columns=None if show_all else ['hash', 'Team'],
    #                       sep=',')

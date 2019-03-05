import pandas as pd
import itertools as it
import csv
import math
import hashlib

import src.metrics as metrics
import src.xlsx_utils as xlsx_utils

# --------------------------------------------------------------------------- #
# Helper
# --------------------------------------------------------------------------- #

def hash(student):
    s = f"{student['First Name']} {student['Name']} {student['Nationality']} {student['M/F']}"
    hash_object = hashlib.md5(str.encode(s))
    return hash_object.hexdigest()


def enhance_with_hash(students):
    students['hash'] = [hash(x) for _, x in students.iterrows()]
    return students


def transform_to_old_format(students):
    if 'hash' in students.columns:
        return students
    students = enhance_with_hash(students)
    students.rename({
        'M/F': 'Sex',
        'Field of Study': 'Discipline'
    }, axis='columns', inplace=True)
    return students


def split_tracks(teaming, students):
    enhanced_students = students.merge(teaming[['hash', 'Team']])
    teaming1 = teaming[teaming['Team'] <= 8]
    teaming2 = teaming[teaming['Team'] > 8]
    students1 = students[enhanced_students['Team'] <= 8]
    students2 = students[enhanced_students['Team'] > 8]
    return [teaming1], [teaming2], students1, students2


def merge_tracks(teamings1, teamings2):
    teamings = []
    for teaming1, teaming2 in zip(teamings1, teamings2):
        teamings.append(pd.concat([teaming1, teaming2]))
    return teamings


def process_semesters(students, target_func, *args, **kwargs):
    result = []
    for semester in ('WT-15', 'ST-16', 'WT-16', 'ST-17'):
        sem_students = students[students['Semester'] == semester]
        assert metrics.MIN_STUDENTS <= len(sem_teaming) <= metrics.MAX_STUDENTS,\
            'Expected between 75 and 85 students but got {}'.format(len(sem_teaming))
        partial_result = target_func(sem_students, semester, *args, **kwargs)
        result.append(partial_result)
    return pd.DataFrame(pd.concat(result).copy(), index=range(321))


def store_teaming(teaming, filename=None, show_all=True, xlsx=True):
    if xlsx:
        print(teaming.columns)
        assert all(teaming.columns[-3:] == ['1st', '2nd', '3rd']), \
            'Only 3 teamings are supported for xlsx export'
        xlsx_utils.export(teaming, filename)
    else:
        # Use the same format as used for the input data
        # Generates FutureWarning: Passing list-likes to .loc or [] with missing label
        return teaming.to_csv(f'{filename}.csv', quoting=csv.QUOTE_MINIMAL, index=False,
                              columns=None if show_all else ['hash', 'Team'],
                              sep=',')

# Get power of 2 which is closest to num
def get_closest_power(num):
    return 2 ** round(math.log(num, 2))

from src.d_matcher import execute, get_collisions

# execute('input/students_wt_15.csv', epochs=3, amount_teamings=3)
# execute('input/new_students_wt_15.csv', epochs=3, amount_teamings=3)
# teaming = execute('input/new_students_wt_15.xlsx', epochs=3, amount_teamings=3)
# teaming = execute('input/students_corrupted_wt_15.csv', epochs=epochs, amount_teamings=3)
# teaming = execute('input/students_corrupted_wt_15_2.csv', epochs=epochs, amount_teamings=3)
collisions = []
# 4, 8, 12, 16, 20, 20, 50, 100, 200
# [44, 45, 34, 31, 36, 38, 40, 40, 35]
# After semo optimizations: [37, 32, 23, 31, 27, 27, 25, 25, 27]
# mutation_intensity = 20 -> 2: [43, 39, 41, 26, 32, 36, 25, 23, 22]
# mutation_intensity = 2 -> 40:
for epochs in [4, 8, 12, 16, 20, 20, 50, 100, 200]:
    teaming = execute('input/new_students_wt_15.xlsx', epochs=epochs,
                      mutation_intensity=40, amount_teamings=3)
    collisions.append(len(list(get_collisions(teaming))))
    # print("Merged:")
    # coll2 = list(get_collisions(teamings))
    # print(len(coll2), '\n'.join(coll2))
print(collisions)

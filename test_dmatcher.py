from src.d_matcher import execute, get_collisions

# execute('input/students_wt_15.csv', epochs=3, amount_teamings=3)
# execute('input/new_students_wt_15.csv', epochs=3, amount_teamings=3)
# teaming = execute('input/new_students_wt_15.xlsx', epochs=3, amount_teamings=3)
# teaming = execute('input/students_corrupted_wt_15.csv', epochs=epochs, amount_teamings=3)
# teaming = execute('input/students_corrupted_wt_15_2.csv', epochs=epochs, amount_teamings=3)
collisions = []
# 4, 8, 12, 16, 20, 20, 50, 100, 200, *500, *1000
# [44, 45, 34, 31, 36, 38, 40, 40, 35]
# After semo optimizations: [37, 32, 23, 31, 27, 27, 25, 25, 27]
# mutation_intensity = 20 -> 2: [43, 39, 41, 26, 32, 36, 25, 23, 22]
# mutation_intensity = 2 -> 40: [26, 31, 25, 29, 24, 17, 25, 20, 17]
# mutation_intensity = 40 -> 60: [26, 27, 26, 19, 29, 26, 16, 27, 24]
# mutation_intensity = 60 -> 2, p = int->float: [40, 32, 33, 36, 33, 38, 34, 16, 23]
# mutation_intensity = 2 -> 20: [32, 27, 20, 28, 30, 25, 24, 20, 21]
# mutation_intensity = choose steps at once: [38, 39, 37, 34, 35, 34, 29, 30, 42, 32, 26]
# mutation_intensity = 20 -> 60: [35, 39, 44, 36, 33, 38, 34, 31, 26, 34, 39]
# mutation_intensity = 60 -> 100: [36, 35, 32, 37, 38, 40, 41, 28, 24, 32, 34]
# [1, 2, 4, 8, 16, 32, 64, 128, 256, 256, 512] -> [27, 21, 29, 25, 34, 31, 33, 31, 36, 30, 32]
# epochs=200 -> [22, 21, 16, 27, 33, 31, 27, 36, 32, 33, 36]
# for mutation_intensity in [1, 2, 4, 8, 16, 32, 64, 128, 256, 256, 512]:
for mutation_intensity in [100, 100, 100, 100, 100, 200, 200, 200, 200, 200]:
    epochs = mutation_intensity
    mutation_intensity = mutation_intensity
    teaming = execute('input/new_students_wt_15.xlsx', epochs=epochs,
                      mutation_intensity=mutation_intensity, amount_teamings=3)
    collisions.append(len(list(get_collisions(teaming))))
    # print("Merged:")
    # coll2 = list(get_collisions(teamings))
    # print(len(coll2), '\n'.join(coll2))
print(collisions)

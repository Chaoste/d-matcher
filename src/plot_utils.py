from matplotlib import pyplot as plt

# --------------------------------------------------------------------------- #
# Visualization
# --------------------------------------------------------------------------- #

def plot_pareto_front_3d(P, filename=None):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(*zip(*[x[1]['Gender':'Nationality'].values for x in P]))
    ax.set_xlabel('Gender')
    ax.set_ylabel('Discipline')
    ax.set_zlabel('Nationality')
    ax.set_title('Found elements of the 3-dimensional Pareto Front')
    fig.tight_layout()
    if filename:
        fig.savefig(filename)

def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)

def plot_pareto_front_2d(P, filename=None):
    cmap = get_cmap(len(P))
    fig, axes = plt.subplots(1, 3, figsize=(12, 3))
    submetrics = P[0][1].index[:-1]
    for i, (x, y) in enumerate(it.combinations(submetrics, 2)):
        axes[i].scatter([p[1][x] for p in P], [p[1][y] for p in P], c=[cmap(j) for j in range(len(P))])
        # axes[i].set_xlim([0, 1])
        # axes[i].set_ylim([0, 1])
        axes[i].set_xlabel(x)
        axes[i].set_ylabel(y)
        axes[i].set_title('Pareto Front: {} vs {}'.format(x, y))
    fig.tight_layout()
    if filename:
        fig.savefig(filename)

def plot_comparison(teaming_metrics, filename=None):
    fig, ax = plt.subplots(1, 1, figsize=(11, 4))
    for i, teaming_metric in enumerate(teaming_metrics):
        if i in (0, 1):
            ax.plot(teaming_metric[:-1], label='teaming{}'.format(i+1))
        else:
            ax.plot(teaming_metric, label='teaming{}'.format(i+1))
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(['Gender', 'Discipline', 'Nationality', 'Collision'])
    ax.legend()
    ax.set_title('The submetrics of all teamings')
    fig.tight_layout()
    if filename:
        fig.savefig(filename)

def comparison_table(teaming1, teaming2, teaming3, teaming4, METRICS, SEMESTER, verbose=False):
    comparison = pd.Panel(items=('teaming1', 'teaming2', 'teaming3', 'teaming4'),
                      major_axis=METRICS, minor_axis=SEMESTER)
    teamings = (teaming1, teaming2, teaming3, teaming4)
    previous = (None, None, teaming2, (teaming2, teaming3))
    for i, (teaming, previous_teamings) in enumerate(zip(teamings, previous)):
        for semester in SEMESTER:
            name = 'teaming{}'.format(i+1)
            sem_teaming = teaming[teaming['Semester'] == semester]
            result = metrics.sem_multi_objective(sem_teaming, previous_teamings)
            if previous_teamings is None:
                result[-1] = None
            if verbose:
                metrics.print_metric(result, '{} - semester {}'.format(name, semester))
            comparison.loc[name, :, semester] = result
    return comparison

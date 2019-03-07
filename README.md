# D Matcher

Grouping students with a high diversity regarding gender, profession and nationality.

### Install & Build

```
brew install pkg-config sdl2 sdl2_image sdl2_ttf sdl2_mixer gstreamer
pip install Cython==0.26.1
pip install git+https://github.com/matham/kivy.git@async-loop
pip install -r requirements/extended.mac.build.txt
```

Make sure pyinstaller is installed. Furthermore see the kivy docs on installings kivy dependencies.

```
  pyinstaller dmatcher.spec
  # From kivy docs
  pushd dist
  hdiutil create ./Touchtracer.dmg -srcfolder touchtracer.app -ov
  popd
```

### Troubleshooting

If matplotlib or pygame is installed, pyinstaller will take the "libpng16.16.dylib" form those modules which currently appear to be deprecated. Since at least version 52 is required, you need to make sure that the lib ist loaded form the PIL module. To check the current used version run `otool -V my/path/libpng16.16.dylib`.

### Input

The data for this project is real data provided to us by the HPI School of Design Thinking. You are given as input a table stored in CSV format. This table has 80/81 rows and five columns. Each row corresponds
to a student and the columns are as follows:

< hash > < Sex > < Discipline > < Nationality > < Semester >

- The < hash > field contains a cryptographic hash of the student’s name (for privacy reasons).
- The sex field contains ‘m’ for male and ‘f’ for female.
- The Discipline field contains one of the following seven entries:
  ‘Business’, ‘Creative Disciplines’, ‘Engineering’, ‘Humanities’, ‘Life Sciences’, ‘Media’ or ‘Social Sciences’.
- The Nationality field contains one of 37 nationalities, depending on the selfreported nationality of the student.
- The Semester field contains the semester in which that student was enrolled. This is stored as a code that indicates the semester and year. For example, the students in Winter 2015 semester have WT-15 (for Winter Term), and the students enrolled in this semester have the code ST-17.

### Output

Three diverse teamings (16 Teams) regarding the three aspects of a student.

### Method

We decided to implement the Simple Evolutionary Multi-objective Optimization (SEMO) algorithm proposed by [Laumanns et al.][0]. It collects all non-dominated solutions defining a Pareto front. Note that those might be far away from the optimal Pareto front depending on the difficulty of the given problem

[0]: http://repository.ias.ac.in/83516/1/20-a.pdf

### Evaluation

For comparing results we defined metrics for each dimension which gives a rating for one team (as a part of a semesters teaming). To give a conclusion by one number we combined all four metrics (dimensions+collisions) using the L2-Norm. For more information see our paper.

The results of the algorithm between teaming2 and teaming3 get worse because we consider the fourth metric in the second one. With an additional submetric the problem become's more difficult and the search space greater. Therefore the algorithm takes longer to find a good local minimum regarding all four submetrics.
For the fourth teaming the search space doesn't become greater but there are less good solution because of the aggravated metric

### Release

For a description of the data see the DATA_FORMAT.md

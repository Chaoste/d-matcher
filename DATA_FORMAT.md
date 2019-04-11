# Data Format

The application accepts files with the csv or xlsx extension. It might be possible to drop files somewhere in the window instead of using the file dialog.

#### Required columns

- 'First Name'
- 'Name'
- 'M/F' (or 'Sex')
  - 'm'/'M' is interpreted as male while everything else is internally treated as female
- 'Discipline' (or 'Field of Study')
  - Generally any string is excepted but for the color mapping it is mandatory that they be one of the following ones: ['Business', 'Creative Disciplines', 'Engineering', 'Humanities', 'Life Sciences', 'Media', 'Social Sciences']
- 'Nationality'
  - Any string is excepted

Every additional column will be ignored for the matching algorithm but will be readded to the output file which contains the team assignments. The students are splitted into orange and yellow track after the first assignments.

#### Further Informations:

- Between 75 and 85 students are required (there will be always 4 or 5 students per team)
- A notification is generated when the application is finished
- There will be still collisions in the final teaming
- If the application throws an error this is most likely due to invalid input data. The application will show a popup dialog before it breaks and generate an error.txt which you can send to the owner of the project.

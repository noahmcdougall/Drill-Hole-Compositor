import csv
import os.path

## Listing variables up here that would later be user input ##
cutoffgrade = 3

## Initial loading of data from csv ##
with open('C:/Users/noahm/Desktop/compositorinputdata3.csv', 'rt') as datalist:
    reader = csv.reader(datalist, delimiter=",")
    holes = []
    datatable = []
    next(reader)
    for row in reader:
        if row[0] not in holes:
            holes.append(row[0])
        datatable.append([row[0],float(row[1]),float(row[2]),float(row[3])])

## Sorts the data by hole and sets the initial parameters#
results = []
for i in holes:
    inorout = "out"
    grade = 0
    gradeton = 0
    length = 0
    runlength = 0
    beginning = 0
    end = 0
    iteratornum = 0

    ## Iterates through the rows only where the hole ID matches ##
    for j in range(0, len(datatable)):
        if datatable[j][0] == i:
            length = datatable[j][2]-datatable[j][1]
            gobacklength = datatable[iteratornum][2]-datatable[iteratornum][1]

            ## Condition where we start into the first run ##
            if ((datatable[j][3]*length)+gradeton)/(runlength + length)>=cutoffgrade:
                grade = ((datatable[j][3]*length)+gradeton)/(runlength + length)
                runlength = runlength + length
                gradeton = grade * runlength
                if inorout == "out":
                    beginning = datatable[j][1]
                    iteratornum = j-1
                end = datatable[j][2]
                inorout = "in"

            ## Condition where we get to the end of the first run and commit the results ##
            if ((datatable[j][3]*length)+gradeton)/(runlength + length)<cutoffgrade and inorout == "in":
                ## Once at the end of the run, it goes back to check if adding the row prior to the run (as long as it's greater than 0%) keeps the entire run above grade) ##
                if iteratornum >= 0 and datatable[iteratornum][3] > 0 and ((datatable[iteratornum][3]*gobacklength)+gradeton)/(runlength + gobacklength)>=cutoffgrade:
                    grade = ((datatable[iteratornum][3]*gobacklength)+gradeton)/(runlength + gobacklength)
                    runlength = runlength + gobacklength
                results.append((i, beginning, end, runlength, round(grade,2)))
                runlength = 0
                grade = 0
                gradeton = 0
                inorout = "out"

print(results)

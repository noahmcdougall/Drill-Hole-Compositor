#!/usr/bin/env python
import sys
sys.stdout = sys.stderr
import csv
import os.path
import cherrypy
import jinja2
import io
import atexit

## Sessions enabled ##
wsgi_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
conf = {
         '/': {
             'tools.sessions.on': True
         },
         '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(wsgi_dir, 'assets'),
        }
    }

## Setting up jinja2's web template stuff ##
env = jinja2.Environment(loader=jinja2.FileSystemLoader('/home/noahmcdougall/OreGrader/wsgi/static'))

if cherrypy.__version__.startswith('3.') and cherrypy.engine.state == 0:
    cherrypy.engine.start(blocking=False)
    atexit.register(cherrypy.engine.stop)

## Listing variables up here that would later be user input ##
global cutoffgrade
cutoffgrade = 3

global results

class calculate:
    @cherrypy.expose
    def index(self):
        tmpl = env.get_template('index.html')
        return tmpl.render()

    ## Initial loading of data from csv ##
    @cherrypy.expose
    def processdata(self, myFile):
        holes = []
        datatable = []
        reader = csv.reader(myFile.file)
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
                        else:
                            end = datatable[j][2]
                        inorout = "in"

                    ## Condition where we get to the end of the first run and commit the results ##
                    if ((datatable[j][3]*length)+gradeton)/(runlength + length)<cutoffgrade and inorout == "in":
                        ## Once at the end of the run, it goes back to check if adding the row prior to the run (as long as it's greater than 0%) keeps the entire run above grade) ##
                        if iteratornum >= 0 and datatable[iteratornum][3] > 0 and ((datatable[iteratornum][3]*gobacklength)+gradeton)/(runlength + gobacklength)>=cutoffgrade:
                            grade = ((datatable[iteratornum][3]*gobacklength)+gradeton)/(runlength + gobacklength)
                            runlength = runlength + gobacklength
                        results.append({'Holeid' : i, 'From' : beginning, 'To' : end, 'RunLength' : runlength, 'Grade' : round(grade,2)})
                        runlength = 0
                        grade = 0
                        gradeton = 0
                        inorout = "out"

        raise cherrypy.HTTPRedirect("/displayprocesseddata")

    ## Displays table of data ##
    @cherrypy.expose
    def displayprocesseddata(self):
        tmpl = env.get_template('exportdata.html')
        return tmpl.render(results = results)

application = cherrypy.Application(calculate(), '/', conf)

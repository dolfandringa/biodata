import odf.opendocument
from odf.table import *
from odf.text import P
from collections import OrderedDict

class ODSReader:

    # loads the file
    def __init__(self, file):
        self.doc = odf.opendocument.load(file)
        self.SHEETS = OrderedDict()
        for sheet in self.doc.spreadsheet.getElementsByType(Table):
            self.readSheet(sheet)


    # reads a sheet in the sheet dictionary, storing each sheet as an array (rows) of arrays (columns)
    def readSheet(self, sheet):
        name = sheet.getAttribute("name")
        rows = sheet.getElementsByType(TableRow)
        arrRows = []

        # for each row
        for row in rows:
            row_comment = ""
            arrCells = []
            cells = row.getElementsByType(TableCell)

            # for each cell
            for cell in cells:
                # repeated value?
                repeat = cell.getAttribute("numbercolumnsrepeated")
                if(not repeat):
                    repeat = 1

                ps = cell.getElementsByType(P)
                textContent = ""

                # for each text node
                for p in ps:
                    for n in p.childNodes:
                        if (n.nodeType == 3):
                            textContent = textContent + unicode(n.data)

                if(textContent):
                    if(textContent[0] != "#"): # ignore comments cells
                        for rr in range(int(repeat)): # repeated?
                            arrCells.append(textContent)

                    else:
                        row_comment = row_comment + textContent + " ";
                else:
                    for rr in range(int(repeat)): # repeated?
                        arrCells.append(u'')

            # if row contained something
            if len(arrCells):
                arrRows.append(arrCells)

            #else:
            #   print "Empty or commented row (", row_comment, ")"
        while arrRows[-1]==len(arrRows[-1])*[u'']:
            #delete empty rows at the end
            del(arrRows[-1])
        self.SHEETS[name] = arrRows

    # returns a sheet as an array (rows) of arrays (columns)
    def getSheet(self, name):
        return self.SHEETS[name]

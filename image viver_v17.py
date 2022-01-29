from PyQt5.QtCore import QDir, Qt, QRect, QPoint
from PyQt5.QtGui import QImage, QPainter, QPalette, \
    QPixmap, QPen, QPolygon, QIntValidator, QDoubleValidator, QColor, QKeyEvent
from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QPushButton, QLabel, QComboBox, QListWidget, QAbstractScrollArea, \
    QLineEdit, QMessageBox, QInputDialog, QFileDialog, QAction, QMenu, QApplication, QTableWidget, QTableWidgetItem, QHeaderView
import cv2, os, ctypes, pyabf, csv, random
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

###
# Global variables
filename: str = ""
scrollvalueint: int
image: QImage
listofcordes = []
cord = []
tool = "Rectangle"
count = 0
scalecof : float = 0
abf: pyabf.ABF
abfflag = False
roidataarr = []
###


class ImageViewer(QMainWindow):

    global scrollvalueint, listofcordes, cord, abf
    
    def __init__(self):
        super(ImageViewer, self).__init__()
        ### Creating form
        self.setWindowTitle("Neuron")
        self.resize(ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
        self.approxarr = []
        self.pixmap = QPixmap()

        ## Widgets to work with ROI's
        # Label to work with rectangle and ellipse
        self.imageLabel = MyLabel(self)
        self.imageLabel.move(5, 20)
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.imageLabel.hide()

        #Label to work with polygon
        self.polygonlabel = PolygonLabel(self)
        self.polygonlabel.setGeometry(5, 20, 412, 397)
        self.polygonlabel.setBackgroundRole(QPalette.Base)
        self.polygonlabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.polygonlabel.setScaledContents(True)
        self.polygonlabel.hide()

        #Label to work with Autoselect
        self.autolabel = PolygonLabel(self)
        self.autolabel.move(5, 20)
        self.autolabel.setBackgroundRole(QPalette.Base)
        self.autolabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.autolabel.setScaledContents(True)
        self.autolabel.hide()

        #Save ROI button
        self.savebtn = QPushButton(self)
        self.savebtn.setText("Save ROI")
        self.savebtn.setGeometry(560, 310, 100, 25)
        self.savebtn.clicked.connect(self.saveROI)
        self.savebtn.hide()

        #Delete ROI button
        self.delbtn = QPushButton(self)
        self.delbtn.setText("Delete ROI")
        self.delbtn.setGeometry(450, 310, 100, 25)
        self.delbtn.clicked.connect(self.delROI)
        self.delbtn.hide()
        #Label to show all ROI's
        self.allLabel = Showall(self)
        self.allLabel.move(5, 20)
        self.allLabel.setBackgroundRole(QPalette.Base)
        self.allLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.allLabel.setScaledContents(True)
        self.allLabel.hide()

        #Button to show all ROI's
        self.showallbtn = QPushButton(self)
        self.showallbtn.setText("Show all items")
        self.showallbtn.setGeometry(480, 380, 150, 30)
        self.showallbtn.clicked.connect(self.showall)
        self.showallbtn.hide()

        self.toollabel = QLabel(self)
        self.toollabel.setText("Tool Selection")
        self.toollabel.hide()

        #Tool selection combo box
        self.toolbox = QComboBox(self)
        self.toolbox.setGeometry(480, 30, 150, 20)
        self.toolbox.addItem("Rectangle")
        self.toolbox.addItem("Ellipse")
        self.toolbox.addItem("Polygon")
        self.toolbox.addItem("Autoselect")
        self.toolbox.currentIndexChanged.connect(self.toolchange)
        self.toolbox.hide()

        self.modelabel = QLabel(self)
        self.modelabel.setFixedSize(150, 30)
        self.modelabel.setText("Change compute mode")
        self.modelabel.hide()

        #Compute mode selection
        self.modebox = QComboBox(self)
        self.modebox.setGeometry(480, 415, 150, 20)
        self.modebox.addItem("Mean")
        self.modebox.addItem("Median")
        #self.modebox.currentIndexChanged.connect(self.modechange)
        self.modebox.hide()

        self.roilabel = QLabel(self)
        self.roilabel.setText("ROI's list")
        self.roilabel.hide()

        #ROI's list list widget
        self.ROIbox = QListWidget(self)
        self.ROIbox.setSelectionMode(3)
        self.ROIbox.setGeometry(480, 60, 150, 200)
        self.ROIbox.currentItemChanged.connect(self.selectROI)
        self.ROIbox.itemDoubleClicked.connect(self.rename)
        self.ROIbox.hide()

        # self.backlabel = QLabel(self)
        # self.backlabel.setText("Background selection")
        # self.backlabel.hide()

        # #Bacground selection
        # self.backgroundroi = QComboBox(self)
        # self.backgroundroi.setGeometry(480, 270, 150, 20)
        # self.backgroundroi.hide()

        self.timelabel = QLabel(self)
        self.timelabel.setText("Frame time")
        self.timelabel.hide()
        #Time interval text box
        self.timetextbox = QLineEdit(self)
        self.timetextbox.setGeometry(480, 470, 150, 20)
        self.timetextbox.setPlaceholderText("Step")
        self.timetextbox.setValidator(QDoubleValidator(0.0, 100.0, 6))
        self.timetextbox.setText("250")
        self.timetextbox.hide()

        self.totaltimelabel = QLabel(self)
        self.totaltimelabel.setText("Total time")
        self.totaltimelabel.hide()
        # Roral time text box
        self.totaltimebox = QLineEdit(self)
        self.totaltimebox.setGeometry(480, 470, 150, 20)
        self.totaltimebox.setPlaceholderText("Time")
        self.totaltimebox.setValidator(QDoubleValidator(0.0, 10000.0, 6))
        self.totaltimebox.setText(str(int(self.timetextbox.text())*12))
        self.totaltimebox.hide()

        self.valslabel = QLabel(self)
        self.valslabel.setText("Frames")
        self.valslabel.hide()

        #Mode 2 text boxes
        self.minvaltextbox = valtextbox(self)
        self.minvaltextbox.setGeometry(480, 445, 70, 20)
        self.minvaltextbox.setPlaceholderText("Start index")
        self.minvaltextbox.hide()

        self.maxvaltextbox = valtextbox(self)
        self.maxvaltextbox.setGeometry(560, 445, 70, 20)
        self.maxvaltextbox.setPlaceholderText("End index")
        self.maxvaltextbox.hide()

        #Compute button
        self.computebtn = QPushButton(self)
        self.computebtn.setGeometry(480, 500, 150, 30)
        self.computebtn.setText("Compute")
        self.computebtn.clicked.connect(self.compute)
        self.computebtn.hide()

        self.thresholdlabel = QLabel(self)
        self.thresholdlabel.setText("Threshold")
        self.thresholdlabel.hide()
        #threshold text box for autoselect
        self.threshtextbox = QLineEdit(self)
        self.threshtextbox.setGeometry(30, 550, 70, 20)
        self.threshtextbox.setPlaceholderText("Start")
        self.threshtextbox.setText("200")
        self.thresh = 200
        self.threshtextbox.setValidator(QIntValidator(0, 255, self))
        self.threshtextbox.hide()
        #Refresh button for autoselect
        self.refreshbtn = QPushButton(self)
        self.refreshbtn.setText("Refresh")
        self.refreshbtn.setGeometry(30, 30, 100, 25)
        self.refreshbtn.hide()
        self.refreshbtn.clicked.connect(self.refreshautolabel)
        #Clear button for autoselect
        self.clearbtn = QPushButton(self)
        self.clearbtn.setText("Clear")
        self.clearbtn.setGeometry(480, 340, 100, 25)
        self.clearbtn.hide()
        self.clearbtn.clicked.connect(self.autoselect)

        ## Widgets to work with *.abf files
        # Label for filename
        self.abffilename = QLabel(self)
        self.abffilename.setFixedSize(200, 30)
        self.abffilename.hide()
        # Label for protocol
        self.abfprotocol = QLabel(self)
        self.abfprotocol.setFixedSize(200, 30)
        self.abfprotocol.hide()
        # Label for SweepLenght
        self.abflength = QLabel(self)
        self.abflength.setFixedSize(200, 30)
        self.abflength.hide()
        # Table for *.abf file data
        self.abftable = QTableWidget(self)
        self.abftable.horizontalHeader().hide()
        self.abftable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.abftable.setRowCount(7)
        self.abftable.setVerticalHeaderLabels(['Epoch', 'Level', 'Start', 'Length', 'Digital out(3-0)', 'Camera', 'Light'])
        self.abftable.setGeometry(30, 30, 600, 300)
        self.abftable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.abftable.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.abftable.hide()
        self.abftable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.abftable.cellClicked.connect(self.cellclick)
        ##
        self.createActions()
        self.createMenus()
        self.showMaximized()



    ## ABF table cell click procedure
    def cellclick(self, row, column):
        # Coloring camera selection
        if self.abftable.item(row, column) == None:
            self.abftable.setItem(row, column, QTableWidgetItem())
            self.abftable.item(row, column).setBackground(QColor(255, 255, 255))
        if row == 5:
            self.abftable.selectRow(row)
            if self.abftable.item(row, column).background().color() == QColor(0, 255, 0):
                self.abftable.item(row, column).setBackground(QColor(255, 255, 255))
                self.abftable.clearSelection()
            else:
                for item in self.abftable.selectedItems():
                    item.setBackground(QColor(255, 255, 255))
                self.abftable.clearSelection()
                self.abftable.item(row, column).setBackground(QColor(0, 255, 0))
        # Coloring light selection
        elif row == 6:
            if self.abftable.item(row, column).background().color() == QColor(255, 255, 255):
                self.abftable.item(row, column).setBackground(QColor(0, 0, 255))
                self.abftable.clearSelection()
            else:
                self.abftable.item(row, column).setBackground(QColor(255, 255, 255))
                self.abftable.clearSelection()

    ##Autolabel redresh procedure
    def refreshautolabel(self):
        # Set new limit of threshold
        self.thresh = int(self.threshtextbox.text().title())
        #Clear selected region
        self.approxarr = []
        self.autolabel.poslist = QPolygon()
        self.autolabel.poslistimg = QPolygon()

        self.autoselect()

    ##Compute mode change procedure
    # def modechange(self):
    #     #if Mode 1 was selected shows Mode 1 widgets and hide Mode 2
    #     if self.modebox.currentIndex() == 0:
    #         self.backgroundroi.show()
    #         self.backlabel.show()
    #         self.minvaltextbox.hide()
    #         self.minvaltextbox.clear()
    #         self.maxvaltextbox.hide()
    #         self.maxvaltextbox.clear()
    #         self.valslabel.hide()
    #     else:
    #         self.backgroundroi.hide()
    #         self.backlabel.hide()
    #         self.minvaltextbox.show()
    #         self.maxvaltextbox.show()
    #         self.valslabel.show()

    ## Procedure to compute ROI mean
    def computeroidata(self, fname, index):
        global scalecof, roidataarr
        # Compute Ellipse or Rectangle
        if (listofcordes[index][1] == "Ellipse"
                or listofcordes[index][1] == "Rectangle"):
            roix0 = int(listofcordes[index][2] / scalecof)
            roiy0 = int(listofcordes[index][3] / scalecof)
            roix1 = int(listofcordes[index][4] / scalecof)
            roiy1 = int(listofcordes[index][5] / scalecof)
            # Create arrea variable
            roiarea = (roix0, roiy0, roix1, roiy1)
            # Get image
            img = Image.open(fname)
            # Crop image
            croproi = img.crop(roiarea)
            # If tool is Ellipse clear around Ellipse
            if (listofcordes[index][1] == "Ellipse"):
                h, w = croproi.size
                imArray = np.array(croproi)
                maskIm = Image.new('L', (h, w), 0)
                ImageDraw.Draw(maskIm).pieslice([(0, 0), (h, w)], 0, 360, outline=1, fill=1)
                mask = np.array(maskIm)
                mask_flattened = mask.flatten()
                imArray_flattend = imArray.flatten()
                roidata = imArray_flattend[mask_flattened == 1]
            else:
                roidata = np.asarray(croproi)
            roidataarr.append(roidata)

        # Compute Polygon
        elif (listofcordes[index][1] == "Polygon"):
            # Create cariable to contains polygon points list
            pointlist = []
            for point in self.polygonlabel.poslistimg:
                pointlist.append((point.x(), point.y()))
            # Get image
            img = Image.open(fname)
            imArray = np.array(img)
            # Create mask
            maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
            ImageDraw.Draw(maskIm).polygon(pointlist, outline=1, fill=1)
            mask = np.array(maskIm)
            # Flatten mask and image
            mask_flattened = mask.flatten()
            imArray_flattend = imArray.flatten()
            # Filter image by mask
            roidata = imArray_flattend[mask_flattened == 1]
            roidataarr.append(roidata)
        # Compute Autoselect
        elif (listofcordes[index][1] == "Autoselect"):
            # Create cariable to contains polygon points list
            pointlist = []
            for approx in listofcordes[index][2]:
                for array in approx:
                    pointlist.append((array[0][0], array[0][1]))
            # Get image
            img = Image.open(fname)
            imArray = np.array(img)
            # Create mask
            maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
            ImageDraw.Draw(maskIm).polygon(pointlist, outline=1, fill=1)
            mask = np.array(maskIm)
            # Flatten mask and image
            mask_flattened = mask.flatten()
            imArray_flattend = imArray.flatten()
            # Filter image by mask
            roidata = imArray_flattend[mask_flattened == 1]
            roidataarr.append(roidata)


    ## Procedure to compute ROI mean (almost everything is the same as computeroidata,
    #                                               but ROI takes from background ROI combo box)
    # def computebackmean(self, fname):
    #     if (listofcordes[self.backgroundroi.currentIndex()][1] == "Ellipse"
    #             or listofcordes[self.backgroundroi.currentIndex()][1] == "Rectangle"):
    #         backx0 = int(listofcordes[self.backgroundroi.currentIndex()][2] / scalecof)
    #         backy0 = int(listofcordes[self.backgroundroi.currentIndex()][3] / scalecof)
    #         backx1 = int(listofcordes[self.backgroundroi.currentIndex()][4] / scalecof)
    #         backy1 = int(listofcordes[self.backgroundroi.currentIndex()][5] / scalecof)
    #         backarea = (backx0, backy0, backx1, backy1)
    #         img = Image.open(fname)
    #         cropback = img.crop(backarea)
    #         if (listofcordes[self.backgroundroi.currentIndex()][1] == "Ellipse"):
    #             h, w = cropback.size
    #             alpha = Image.new('L', [h, w], 0)
    #             draw = ImageDraw.Draw(alpha)
    #             draw.pieslice([(0, 0), (h, w)], 0, 360, fill=255)
    #             npImage = np.array(cropback)
    #             npAlpha = np.array(alpha)
    #             backdata = np.dstack((npImage, npAlpha))
    #         else:
    #             backdata = np.asarray(cropback)
    #         backmean = np.mean(backdata)
    #     elif (listofcordes[self.backgroundroi.currentIndex()][1] == "Polygon"):
    #         pointlist = []
    #         for point in listofcordes[self.backgroundroi.currentIndex()][3]:
    #             pointlist.append((point.x(), point.y()))
    #         img = Image.open(fname)
    #         imArray = np.array(img)
    #         maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
    #         ImageDraw.Draw(maskIm).polygon(pointlist, outline=1, fill=1)
    #         mask = np.array(maskIm)
    #         mask_flattened = mask.flatten()
    #         imArray_flattend = imArray.flatten()
    #         back_pix_final = imArray_flattend[mask_flattened == 1]
    #         backmean = back_pix_final.mean()
    #     elif (listofcordes[self.backgroundroi.currentIndex()][1] == "Autoselect"):
    #         pointlist = []
    #         for approx in listofcordes[self.backgroundroi.currentIndex()][2]:
    #             for array in approx:
    #                 pointlist.append((array[0][0], array[0][1]))
    #         img = Image.open(fname)
    #         imArray = np.array(img)
    #         maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
    #         ImageDraw.Draw(maskIm).polygon(pointlist, outline=1, fill=1)
    #         mask = np.array(maskIm)
    #         mask_flattened = mask.flatten()
    #         imArray_flattend = imArray.flatten()
    #         back_pix_final = imArray_flattend[mask_flattened == 1]
    #         backmean = back_pix_final.mean()
    #     return backmean

    ## Procedure to compute graph data, show it and create *.csv files
    def compute(self):
        global filename, abf, abfflag, roidataarr
        cameraon = 0
        lighton = []
        pixsnp = np.array([])
        # If *.abf flie exist take selected camera and light
        if abfflag:
            for i in range(len(abf.sweepX)):
                lighton.append('0')
            self.abftable.selectRow(5)
            for item in self.abftable.selectedItems():
                if item.background().color() == QColor(0, 255, 0):
                    cameraon = float(self.abftable.item(2, item.column()).text())
            self.abftable.selectRow(6)
            for item in self.abftable.selectedItems():
                if item.background().color() == QColor(0, 0, 255):
                    for i in range(len(abf.sweepX)):
                        if float(self.abftable.item(2, item.column()).text()) <= abf.sweepX[i] \
                                <= float(self.abftable.item(2, item.column()).text()) + \
                                float(self.abftable.item(3, item.column()).text()) or lighton[i] == '1':
                            lighton[i] = '1'
                        else:
                            lighton[i] = '0'
            self.abftable.clearSelection()
            if (cameraon == None):
                QMessageBox.information(QMessageBox(), "Image Viewer",
                                        "Incorrect camera selection!")
                return
        # Verification of the possibility of performing the procedure
        if (self.timetextbox.text().title() == "") or (self.totaltimebox.text().title() == ""):
            QMessageBox.information(QMessageBox(), "Image Viewer",
                                    "Incorrect time interval")
            return

        if (self.modebox.currentIndex() == 1 and
            ((self.minvaltextbox.text().title() == "" or self.maxvaltextbox.text().title() == "") or
           (int(self.minvaltextbox.text().title()) > int(self.maxvaltextbox.text().title())))):
            QMessageBox.information(QMessageBox(), "Image Viewer",
                                            "Incorrect interval")
            return

        if len(self.ROIbox.selectedItems()) == 0:
            QMessageBox.information(QMessageBox(), "Image Viewer",
                                    "Select ROI's to compute")
            return

        # Get files list
        dir = os.path.dirname(filename)
        filelist = [f for f in os.listdir(os.path.dirname(filename))
                    if os.path.isfile(os.path.join(os.path.dirname(filename), f))]
        # Filter files list
        unwantedfiles = []
        for file in filelist:
            if not (file.endswith(".tif")):
                unwantedfiles.append(file)
        filelist = [ele for ele in filelist if ele not in unwantedfiles]
        # loop for all selected ROI's to compute
        for j in range(len(self.ROIbox.selectedItems())):
            # Reference variable before assignment
            graphdata = []
            selecteditems = []
            roidataarr = []
            pixsnp = np.array([])
            cnt = 0
            x = []
            xabc: float = 0
            graphsel = []
            #If selected ROI is the same as background ROI at mode 1 skip it
            # if (self.ROIbox.row(self.ROIbox.selectedItems()[i]).__index__() ==
            #                                         self.backgroundroi.currentIndex()    median(mean(ROI Frame 1) mean(ROI Frame 2) ...)   [pixs F1 ].apped(F2...)
            #                                         and self.modebox.currentIndex() == 0):
            #     continue
            # Loop for all *.tif files in folder
            for file in filelist:
                # Get full file name
                fname = dir[:3] + '/' + dir[3:] + '/' + file
                # Get ROI mean of file
                self.computeroidata(fname, self.ROIbox.row(self.ROIbox.selectedItems()[j]))
                for item in roidataarr:
                    if (cnt >= int(self.minvaltextbox.text().title())
                    and cnt <= int(self.maxvaltextbox.text().title())):
                        selecteditems.append(item)
                    cnt += 1
                # If mode 1 selected compute background ROI mean
                # if self.modebox.currentIndex() == 0:
                #     backmean = self.computebackmean(fname)  
                #     # Compute mode 1 formula and append graph data array
                #     graphdata.append(round(((roimean - backmean) / backmean), 5))
            for item in selecteditems:
                pixsnp = np.append(pixsnp, item)
            if self.modebox.currentIndex() == 0:
                f1 = round(np.mean(pixsnp), 5)
            else:
                f1 = round(np.median(pixsnp), 5)
            # Compute formula and append graph data array
            for item in roidataarr:
                if self.modebox.currentIndex == 0:
                    graphdata.append(round(((np.mean(item) - f1) / f1), 5))
                else:
                    graphdata.append(round(((np.median(item) - f1) / f1), 5))
            print(f1)
            selecteditems = []
            randvalues = []
            totalcount = int(float(self.totaltimebox.text()) / float(self.timetextbox.text()))
            diff = totalcount - len(graphdata)
            if diff > 0:
                for i in range(diff):
                    rand = random.randint(1, len(graphdata) - 2)
                    graphdata.insert(rand, float((float(graphdata[rand - 1]) + float(graphdata[rand + 1])) / 2))
                    randvalues.append(rand)
                randvalues.sort()
                legend = 'Random values: '
                legend = legend + ", ".join(map(str, randvalues))
            if cameraon > 0:
                xabc = cameraon
            # Create graph abscissa
            for cnt in range(len(graphdata)):
                x.append(xabc)
                if (cnt >= int(self.minvaltextbox.text().title())
                    and cnt <= int(self.maxvaltextbox.text().title())):
                    graphsel.append(xabc)
                    selecteditems.append(graphdata[cnt])
                # Set next abscissa point on graph
                xabc += round(float(self.timetextbox.text().title().replace(",", "."))/1000, 3)
            # If *.abf file exist create 2 plots
            if abfflag:
                fig, axs = plt.subplots(2)
                if diff > 0:
                    fig.text(0.5, 0.05, legend, horizontalalignment='center', verticalalignment='center', wrap=True)
                fig.suptitle(listofcordes[self.ROIbox.row(self.ROIbox.selectedItems()[j])][0] + ' (' + self.modebox.currentText() +')')
                axs[0].plot(x, graphdata)
                axs[1].plot(abf.sweepX, abf.sweepY)
                axs[0].plot(graphsel, selecteditems)
                axs[0].set_ylabel('df / F', fontsize = 16)
                axs[0].grid()
                axs[1].grid()
                axs[0].set_xlim(left=0)
                axs[1].set_xlim(left=0)
                # Call message box to save *.csv file
                buttonReply = QMessageBox.question(self, 'Image Viewer',
                                                   "Create a csv file?",
                                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    # Call save file dialog
                    csvfilename, check = QFileDialog.getSaveFileName(None, "Save csv",
                                                                     os.path.dirname(filename) + "/" + listofcordes[
                                                                         self.ROIbox.row(
                                                                             self.ROIbox.selectedItems()[j])][
                                                                         0] + ".csv",
                                                                     "All files (*);;CSV files (*.csv);")
                    # Create 2 *.csv files
                    if check:
                        # *.csv file for compute graph
                        with open(csvfilename, 'w', newline='') as csvfile:
                            writer = csv.DictWriter(csvfile,
                                                    fieldnames=['Compute_time', 'Compute_data'])
                            writer.writeheader()
                            for i in range(len(x)):
                                writer.writerow({'Compute_time': x[i], 'Compute_data': graphdata[i]})

                        # *.csv file for *.abf file graph
                        with open(csvfilename[:-4] + '_Sweep' + csvfilename[-4:], 'w', newline='') as csvfile:
                            writer = csv.DictWriter(csvfile,
                                                    fieldnames=['SweepX', 'SweepY', 'Camera', 'Light'])
                            writer.writeheader()
                            for i in range(len(abf.sweepX)):
                                writer.writerow({'SweepX': abf.sweepX[i], 'SweepY': abf.sweepY[i], 'Camera': 0 if cameraon >= abf.sweepX[i] else 1, 'Light': lighton[i]})

            # If *.abf file doesn't exist create 1 plot
            else:
                fig, axs = plt.subplots(1)
                if diff > 0:
                    fig.text(0.5, 0.05, legend, horizontalalignment='center', verticalalignment='center', wrap=True)
                axs.plot(x, graphdata)
                axs.plot(graphsel, selecteditems)
                axs.set_ylabel('df / F', fontsize = 16)
                axs.grid()
                fig.suptitle(listofcordes[self.ROIbox.row(self.ROIbox.selectedItems()[j])][0] + ' (' + self.modebox.currentText() +')')
                # Call message box to save *.csv file
                buttonReply = QMessageBox.question(self, 'Image Viewer',
                                                   "Create a csv file?",
                                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    # *.csv file for compute graph
                    csvfilename, check = QFileDialog.getSaveFileName(None, "Save csv",
                                                              os.path.dirname(filename) + "/" + listofcordes[
                                                                  self.ROIbox.row(self.ROIbox.selectedItems()[j])][
                                                                  0] + ".csv",
                                                              "All files (*);;CSV files (*.csv);")
                    # Create *.csv file
                    if check:
                        with open(csvfilename, 'w', newline='') as csvfile:
                            writer = csv.DictWriter(csvfile,
                                                    fieldnames=['Compute_time', 'Compute_data'])
                            writer.writeheader()
                            for i in range(len(x)):
                                writer.writerow({'Compute_time': x[i], 'Compute_data': graphdata[i]})
            # Show plot
            plt.show()

    ## Check ROI's list for show all button
    def checkshowall(self):
        flag = False
        for i in range(len(listofcordes)):
            if not(listofcordes[i][1] == "Autoselect"):
                flag = True
        if flag:
            self.showallbtn.show()
        else:
            self.showallbtn.hide()
    
    
    ## Show all ROI's except Autoselected
    def showall(self):
        self.imageLabel.hide()
        self.polygonlabel.hide()
        self.autolabel.hide()
        self.allLabel.show()
        self.allLabel.update()

    ## Rename ROI by double click on it
    def rename(self, item):
        global listofcordes
        text, okPressed = QInputDialog.getText(self, "New name", "New name:", text=item.text())

        if okPressed and text != '':
            item.setText(text)
            num = self.ROIbox.currentRow().__index__()
            listofcordes[num][0] = text
            # self.backgroundroi.setItemText(num, text)
    
    
    # Show selecte ROI
    def selectROI(self):
        global listofcordes
        num = self.ROIbox.currentRow()
        if (listofcordes[num][1] == "Rectangle"
            or listofcordes[num][1] == "Ellipse"):
            self.toolbox.setCurrentText(listofcordes[num][1])
            self.imageLabel.x0 = listofcordes[num][2]
            self.imageLabel.y0 = listofcordes[num][3]
            self.imageLabel.x1 = listofcordes[num][4]
            self.imageLabel.y1 = listofcordes[num][5]
            self.imageLabel.update()
        elif listofcordes[num][1] == "Polygon":
            self.toolbox.setCurrentText(listofcordes[num][1])
            self.polygonlabel.poslist = listofcordes[num][2]
            self.polygonlabel.poslistimg = listofcordes[num][3]
            self.polygonlabel.update()
        else:
            self.toolbox.setCurrentText(listofcordes[num][1])
            self.approxarr = listofcordes[num][2]
            self.autolabel.poslist = QPolygon()
            self.autolabel.poslistimg = QPolygon()
            self.autoselect()
        self.toolchange()


    ## Delete selected ROI
    def delROI(self):
        global listofcordes, cord
        num = self.ROIbox.currentRow().__index__()
        if num == -1:
            QMessageBox.information(QMessageBox(), "Image Viewer",
                                    "Select ROI please")
            return
        self.ROIbox.takeItem(num)
        # self.backgroundroi.removeItem(num)
        listofcordes.pop(num)
        if (self.toolbox.currentText() == "Rectangle"
            or self.toolbox.currentText() == "Ellipse"):
            self.imageLabel.x0 = 0
            self.imageLabel.y0 = 0
            self.imageLabel.x1 = 0
            self.imageLabel.y1 = 0
            self.imageLabel.update()
        elif self.toolbox.currentText() == "Polygon":
            self.polygonlabel.poslist = QPolygon()
            self.polygonlabel.poslistimg = QPolygon()
            self.polygonlabel.update()
        else:
            self.autolabel.poslist = QPolygon()
            self.autolabel.poslistimg = QPolygon()
            self.autolabel.update()
            self.autoselect()
        self.checkshowall()


    ## Save dedicated ROI
    def saveROI(self):
        global listofcordes, cord, count, tool
        if (tool == "Rectangle"
            or tool == "Ellipse"):
            if ((self.imageLabel.x0==0) and (self.imageLabel.y0==0) and
                (self.imageLabel.x1==0) and (self.imageLabel.y1==0)):
                return
            cord.append('ROI'+str(count))
            cord.append(tool)
            if self.imageLabel.x0 <= self.imageLabel.x1 and self.imageLabel.y0 <= self.imageLabel.y1:
                cord.append(self.imageLabel.x0)
                cord.append(self.imageLabel.y0)
                cord.append(self.imageLabel.x1)
                cord.append(self.imageLabel.y1)
            elif self.imageLabel.x0 >= self.imageLabel.x1 and self.imageLabel.y0 <= self.imageLabel.y1:
                cord.append(self.imageLabel.x1)
                cord.append(self.imageLabel.y0)
                cord.append(self.imageLabel.x0)
                cord.append(self.imageLabel.y1)
            elif self.imageLabel.x0 <= self.imageLabel.x1 and self.imageLabel.y0 >= self.imageLabel.y1:
                cord.append(self.imageLabel.x0)
                cord.append(self.imageLabel.y1)
                cord.append(self.imageLabel.x1)
                cord.append(self.imageLabel.y0)
            elif self.imageLabel.x0 >= self.imageLabel.x1 and self.imageLabel.y0 >= self.imageLabel.y1:
                cord.append(self.imageLabel.x1)
                cord.append(self.imageLabel.y1)
                cord.append(self.imageLabel.x0)
                cord.append(self.imageLabel.y0)
            self.imageLabel.x0 = 0
            self.imageLabel.y0 = 0
            self.imageLabel.x1 = 0
            self.imageLabel.y1 = 0
            self.imageLabel.update()
        elif tool == "Polygon":
            cord.append('ROI' + str(count))
            cord.append(tool)
            cord.append(self.polygonlabel.poslist)
            cord.append(self.polygonlabel.poslistimg)
            self.polygonlabel.poslist = QPolygon()
            self.polygonlabel.poslistimg = QPolygon()
            self.polygonlabel.update()
        else:
            cord.append('ROI' + str(count))
            cord.append(tool)
            cord.append(self.approxarr)
            self.autolabel.poslist = QPolygon()
            self.autolabel.poslistimg = QPolygon()
            self.approxarr = []
            self.autolabel.update()
            self.autoselect()
        self.ROIbox.addItem('ROI' + str(count))
        # self.backgroundroi.addItem('ROI' + str(count))
        listofcordes.append(list(cord))
        cord.clear()
        count += 1
        self.checkshowall()

    ## Tool change procedure
    def toolchange(self):
        global tool, filename
        self.allLabel.hide()
        if self.toolbox.currentText() == "Polygon":
            self.imageLabel.hide()
            self.autolabel.hide()
            self.polygonlabel.show()
            self.polygonlabel.update()
            self.thresholdlabel.hide()
            self.threshtextbox.hide()
            self.refreshbtn.hide()
            self.clearbtn.hide()
        elif self.toolbox.currentText() == "Autoselect":
            if filename == "":
                QMessageBox.information(QMessageBox(), "Image Viewer",
                                        "File not opened")
                self.toolbox.setCurrentIndex(0)
            else:
                self.imageLabel.hide()
                self.polygonlabel.hide()
                self.autolabel.show()
                self.thresholdlabel.show()
                self.clearbtn.show()
                self.threshtextbox.show()
                self.refreshbtn.show()
                self.autoselect()
        else:
            self.imageLabel.show()
            self.polygonlabel.hide()
            self.autolabel.hide()
            self.thresholdlabel.hide()
            self.threshtextbox.hide()
            self.refreshbtn.hide()
            self.clearbtn.hide()
            self.imageLabel.update()
        tool = self.toolbox.currentText()

    ## File open
    def open(self):
        global filename, listofcordes, count, scalecof, abf, abfflag
        # Set default values
        self.abffilename.hide()
        self.abflength.hide()
        self.abfprotocol.hide()
        self.abftable.hide()
        abfflag = False
        self.imageLabel.x0 = 0
        self.imageLabel.y0 = 0
        self.imageLabel.x1 = 0
        self.imageLabel.y1 = 0
        self.imageLabel.update()
        self.polygonlabel.poslist = QPolygon()
        self.polygonlabel.poslistimg = QPolygon()
        self.polygonlabel.update()
        self.autolabel.poslist = QPolygon()
        self.autolabel.poslistimg = QPolygon()
        self.autolabel.update()
        self.approxarr = []
        self.ROIbox.clear()
        #self.backgroundroi.clear()
        self.modebox.setCurrentIndex(0)
        # self.valslabel.hide()
        # self.minvaltextbox.clear()
        # self.minvaltextbox.hide()
        # self.maxvaltextbox.clear()
        # self.maxvaltextbox.hide()
        listofcordes = []
        count = 0
        # Open dialog
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())
        if filename == "":
            QMessageBox.information(QMessageBox(), "Image Viewer",
                                    "File not opened")
            return
        else:
            QImg = QImage(filename)
            if QImg.isNull():
                QMessageBox.information(self, "Image Viewer",
                        "Cannot load %s." % filename)
                return
        # Create pixmap and set it in show Widgets
        self.pixmap = QPixmap.fromImage(QImg)
        self.imageLabel.setPixmap(self.pixmap)
        self.polygonlabel.setPixmap(self.pixmap)
        self.allLabel.setPixmap(self.pixmap)
        # Compute approximation factor
        scalecof = (ctypes.windll.user32.GetSystemMetrics(1) - 300) / self.pixmap.height()
        # Set image size by approximation factor
        self.imageLabel.setFixedSize(int(self.pixmap.width() * scalecof), int(self.pixmap.height() * scalecof))
        self.polygonlabel.setFixedSize(int(self.pixmap.width() * scalecof), int(self.pixmap.height() * scalecof))
        self.allLabel.setFixedSize(int(self.pixmap.width() * scalecof), int(self.pixmap.height() * scalecof))
        self.minvaltextbox.setText('0')
        self.timetextbox.setText('10')
        unwantedfiles = []
        filelist = os.listdir(os.path.dirname(filename))
        for file in filelist:
            if not (file.endswith(".tif")):
                unwantedfiles.append(file)
        filecount = len([ele for ele in filelist if ele not in unwantedfiles])
        self.maxvaltextbox.setText(str(filecount))
        self.totaltimebox.setText(str(int(self.timetextbox.text())*filecount))
        self.moveitems()
        # If the folder contains *.abf file open it and take data
        for fname in os.listdir(os.path.dirname(filename)):
            if fname.endswith('.abf'):
                abfflag = True
                abf = pyabf.ABF(os.path.dirname(filename) + "/" + fname)
                self.abffilename.setText("File name: " + fname)
                self.abfprotocol.setText("Protocol: " + str(abf.protocol))
                self.abflength.setText("Length: " + str(abf.sweepLengthSec))
                string = str(abf.headerHTML)
                res = ''
                for idx in range(string.index("<pre>") + len("<pre>") + 1, string.index("</pre>")):
                    res = res + string[idx]
                rows = res.split("\n")
                for words in rows:
                    wordslist = words.split()
                    if wordslist == []:
                        continue
                    if wordslist[0] == 'EPOCH':
                        wordslist.pop(0)
                        self.abftable.setColumnCount(len(wordslist))
                        i = 0
                        for item in wordslist:
                            self.abftable.setItem(0, i, QTableWidgetItem(str(item)))
                            self.abftable.item(0, i).setTextAlignment(Qt.AlignCenter)
                            i += 1
                    if wordslist[0] == 'First' and wordslist[1] == 'Level':
                        del wordslist[:2]
                        i = 0
                        for item in wordslist:
                            self.abftable.setItem(1, i, QTableWidgetItem(str(item)))
                            self.abftable.item(1, i).setTextAlignment(Qt.AlignCenter)
                            i += 1
                    if wordslist[0] == 'First' and wordslist[1] == 'Duration':
                        del wordslist[:3]
                        i = 0
                        pointduration: float = float(abf.sweepLengthSec) / float(abf.sweepPointCount)
                        for item in wordslist:
                            self.abftable.setItem(3, i, QTableWidgetItem(str(round(float(item) * float(pointduration), 5))))
                            self.abftable.item(3, i).setTextAlignment(Qt.AlignCenter)
                            if i == 0:
                                self.abftable.setItem(2, i, QTableWidgetItem(str('0')))
                            else:
                                self.abftable.setItem(2, i, QTableWidgetItem(str(round(float(self.abftable.item(3, i - 1).text()) + float(self.abftable.item(2, i - 1).text()), 5))))
                            self.abftable.item(2, i).setTextAlignment(Qt.AlignCenter)
                            i += 1
                    if wordslist[0] == 'Digital' and wordslist[1] == 'Pattern' and wordslist[2] == '#3-0':
                        del wordslist[:3]
                        i = 0
                        for item in wordslist:
                            self.abftable.setItem(4, i, QTableWidgetItem(item))
                            self.abftable.item(4, i).setTextAlignment(Qt.AlignCenter)
                            i += 1
                self.abffilename.show()
                self.abflength.show()
                self.abfprotocol.show()
                self.abftable.resizeColumnsToContents()
                self.abftable.show()
                break
        
        if self.toolbox.currentText() == "Autoselect":
            self.autoselect()
        self.toolchange()
    
    # Move widgets relative to the size of approximated image
    def moveitems(self):
        global scalecof
        self.toollabel.move(int(self.pixmap.width() * scalecof) + 45, 30)
        self.toollabel.show()
        self.toolbox.move(int(self.pixmap.width() * scalecof) + 45, self.toollabel.y() + self.toollabel.height())
        self.toolbox.show()
        self.roilabel.move(int(self.pixmap.width() * scalecof) + 45, self.toolbox.y() + self.toolbox.height())
        self.roilabel.show()
        self.ROIbox.move(int(self.pixmap.width() * scalecof) + 45, self.roilabel.y() + self.roilabel.height())
        self.ROIbox.show()
        self.savebtn.move(int(self.pixmap.width() * scalecof) + 20, self.ROIbox.y() + self.ROIbox.height() + 5)
        self.savebtn.show()
        self.delbtn.move(int(self.pixmap.width() * scalecof) + 120, self.ROIbox.y() + self.ROIbox.height() + 5)
        self.delbtn.show()
        self.timelabel.move(int(self.pixmap.width() * scalecof) + 45, self.delbtn.y() + self.delbtn.height())
        self.timelabel.show()
        self.timetextbox.move(int(self.pixmap.width() * scalecof) + 45, self.timelabel.y() + self.timelabel.height())
        self.timetextbox.show()
        self.totaltimelabel.move(int(self.pixmap.width() * scalecof) + 45, self.timetextbox.y() + self.timetextbox.height())
        self.totaltimelabel.show()
        self.totaltimebox.move(int(self.pixmap.width() * scalecof) + 45, self.totaltimelabel.y() + self.totaltimelabel.height())
        self.totaltimebox.show()
        self.modelabel.move(int(self.pixmap.width() * scalecof) + 45, self.totaltimebox.y() + self.totaltimebox.height())
        self.modelabel.show()
        self.modebox.move(int(self.pixmap.width() * scalecof) + 45, self.modelabel.y() + self.modelabel.height())
        self.modebox.show()
        # self.backlabel.move(int(self.pixmap.width() * scalecof) + 45, self.modebox.y() + self.modebox.height())
        # self.backlabel.show()
        # self.backgroundroi.move(int(self.pixmap.width() * scalecof) + 45, self.backlabel.y() + self.backlabel.height())
        # self.backgroundroi.show()
        self.valslabel.move(int(self.pixmap.width() * scalecof) + 45, self.modebox.y() + self.modebox.height())
        
        self.valslabel.show()

        self.minvaltextbox.move(int(self.pixmap.width() * scalecof) + 45, self.valslabel.y() + self.valslabel.height())
        
        self.minvaltextbox.show()
        
        self.maxvaltextbox.move(int(self.pixmap.width() * scalecof) + 125, self.valslabel.y() + self.valslabel.height())
        
        self.maxvaltextbox.show()

        self.computebtn.move(int(self.pixmap.width() * scalecof) + 45, self.minvaltextbox.y() + self.minvaltextbox.height() + 5)
        self.computebtn.show()
        self.showallbtn.move(int(self.pixmap.width() * scalecof) + 45, self.computebtn.y() + self.computebtn.height() + 5)
        self.thresholdlabel.move(30, int(self.pixmap.height() * scalecof) + 20)
        self.threshtextbox.move(self.thresholdlabel.x() + 50, int(self.pixmap.height() * scalecof) + 25)
        self.refreshbtn.move(self.threshtextbox.x() + int(self.threshtextbox.width()) + 5, int(self.pixmap.height() * scalecof) + 25)
        self.clearbtn.move(self.refreshbtn.x() + int(self.refreshbtn.width()) + 5, int(self.pixmap.height() * scalecof) + 25)
        self.abffilename.move(self.toolbox.x() + self.toolbox.width() + 60, 30)
        self.abfprotocol.move(self.toolbox.x() + self.toolbox.width() + 60, self.abffilename.y() +self.abffilename.height() + 5)
        self.abflength.move(self.toolbox.x() + self.toolbox.width() + 60, self.abfprotocol.y() +self.abfprotocol.height() + 5)
        self.abftable.move(self.toolbox.x() + self.toolbox.width() + 60, self.abflength.y() +self.abflength.height() + 5)
    
    
    ## Create shortcuts
    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O",
                triggered=self.open)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)
    
    
    ## Create file menu
    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.menuBar().addMenu(self.fileMenu)


    ## Autoselect procedure
    def autoselect(self):
        global filename
        # Reading image
        img1 = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        # Reading same image in another
        # variable and converting to gray scale.
        img2 = cv2.imread(filename, cv2.IMREAD_COLOR)

        # Converting image to a binary image
        # ( black and white only image).
        _, threshold = cv2.threshold(img1, self.thresh, 255, cv2.THRESH_BINARY)
        # Detecting contours in image.
        pointcount = 0
        if self.approxarr == []:
            contours, _ = cv2.findContours(threshold, cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)
            # Going through every contours found in the image.
            for cnt in contours:
                approx = cv2.approxPolyDP(cnt, 0.009 * cv2.arcLength(cnt, True), True)
                for apr in approx:
                    point = QPoint()
                    point.setX(apr[0][0])
                    point.setY(apr[0][1])
                    pointcount += 1
                    if self.autolabel.poslistimg.containsPoint(point, 0):
                        approx = np.delete(approx, 0, axis=0)
                if pointcount >= 50000:
                    self.threshtextbox.setText("240")
                    self.refreshautolabel()
                    QMessageBox.information(QMessageBox(), "Image Viewer",
                                            "Set higher threshold")
                    return
                # draws boundary of contours.
                if len(approx) != 0:
                    cv2.drawContours(img2, [approx], 0, (0, 0, 255), 2)
                    self.approxarr.append(approx)
        else:
            contours = self.approxarr
            self.approxarr = []
            for cnt in contours:
                approx = cnt
                for apr in approx:
                    point = QPoint()
                    point.setX(apr[0][0])
                    point.setY(apr[0][1])
                    if self.autolabel.poslistimg.containsPoint(point, 0):
                        approx = np.delete(approx, 0, axis=0)
                # draws boundary of contours.
                if len(approx) != 0:
                    cv2.drawContours(img2, [approx], 0, (0, 0, 255), 2)
                    self.approxarr.append(approx)

        # Showing the final image.
        print(pointcount)
        cvRGBImg = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
        qimg = QImage(cvRGBImg.data, cvRGBImg.shape[1], cvRGBImg.shape[0], cvRGBImg.shape[1] * 3, QImage.Format_RGB888)
        self.autolabel.setPixmap(QPixmap.fromImage(qimg))
        self.autolabel.setFixedSize(int(self.pixmap.width() * scalecof), int(self.pixmap.height() * scalecof))
        self.autolabel.poslist = QPolygon()
        self.autolabel.poslistimg = QPolygon()
        self.update()





### Widget class to create and show Rectangles and Ellipses ROI's
class MyLabel(QLabel):
    global tool, scalecof
    x0 = 0
    y0 = 0
    x1 = 0
    y1 = 0
    flag = False

    def mousePressEvent(self,event):
        self.flag = True
        self.x0 = event.x()
        self.y0 = event.y()

    def mouseReleaseEvent(self,event):
        self.flag = False

    def mouseMoveEvent(self,event):
        if self.flag:
            self.x1 = event.x()
            self.y1 = event.y()
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        rect = QRect()
        if self.x0 <= self.x1 and self.y0 <= self.y1:
            rect = QRect(self.x0, self.y0, abs(self.x1-self.x0), abs(self.y1-self.y0))
        elif self.x0 > self.x1 and self.y0 < self.y1:
            rect = QRect(self.x1, self.y0, abs(self.x0-self.x1), abs(self.y1-self.y0))
        elif self.x0 < self.x1 and self.y0 > self.y1:
            rect = QRect(self.x0, self.y1, abs(self.x1-self.x0), abs(self.y0-self.y1))
        elif self.x0 > self.x1 and self.y0 > self.y1:
            rect = QRect(self.x1, self.y1, abs(self.x0-self.x1), abs(self.y0-self.y1))
        painter = QPainter(self)
        print(self.x0, self.y0, self.x1, self.y1)
        print((int(self.x0/scalecof), int(self.y0/scalecof), int(self.x1/scalecof), int(self.y1/scalecof)))
        painter.setPen(QPen(Qt.red, 1, Qt.SolidLine))
        if tool == "Rectangle":
            painter.drawRect(rect)
        elif tool == "Ellipse":
            painter.drawEllipse(rect)
        else:
            return


### Class to create and show Polygons and Autoselected ROI's
class PolygonLabel(QLabel):
    point = QPoint()
    poslist = QPolygon()
    poslistimg = QPolygon()

    def mousePressEvent(self, event):
        if event.button() == 1:
            self.point.setX(event.x())
            self.point.setY(event.y())
            self.poslist.append(self.point)
            print((int(self.point.x() / scalecof), int(self.point.y() / scalecof)))
            self.poslistimg.append(QPoint(int(self.point.x() / scalecof), int(self.point.y() / scalecof)))
        elif event.button() == 2:
            self.poslist = QPolygon()
            self.poslistimg = QPolygon()
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 1, Qt.SolidLine))
        painter.drawPolygon(self.poslist)


#Class to show all ROI's except Autoselected
class Showall(QLabel):
    global tool, listofcordes, filename
    colours = [Qt.red, Qt.blue, Qt.green, Qt.white, Qt.cyan, Qt.magenta, Qt.yellow]
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        index = 0
        for obj in listofcordes:
            painter.setPen(QPen(self.colours[index], 1, Qt.SolidLine))
            index += 1
            if index > 6:
                index = 0
            if obj[1] == "Polygon":
                rect = obj[2].boundingRect().getRect()
                painter.drawText(QPoint(rect[0], rect[1]-5), obj[0])
                painter.drawPolygon(obj[2])
            elif obj[1] == "Rectangle":
                painter.drawText(QPoint(obj[2], obj[3]-5), obj[0])
                painter.drawRect(obj[2], obj[3], abs(obj[4]-obj[2]), abs(obj[5]-obj[3]))
            elif obj[1] == "Ellipse":
                painter.drawText(QPoint(obj[2], obj[3]-5), obj[0])
                painter.drawEllipse(obj[2], obj[3], abs(obj[4]-obj[2]), abs(obj[5]-obj[3]))
            else:
                continue

class valtextbox(QLineEdit):
    global filename
    def keyPressEvent(self, event: QKeyEvent):
        try:
            unwantedfiles = []
            filelist = os.listdir(os.path.dirname(filename))
            for file in filelist:
                if not (file.endswith(".tif")):
                    unwantedfiles.append(file)
            filelist = [ele for ele in filelist if ele not in unwantedfiles]
            if event.key() == Qt.Key_Backspace:
                super(valtextbox, self).keyPressEvent(event)
            if int(self.text() + event.text()) <= int(len(filelist)):
                super(valtextbox, self).keyPressEvent(event)
        except ValueError:
            return



if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    imageViewer = ImageViewer()
    imageViewer.show()
    sys.exit(app.exec_())
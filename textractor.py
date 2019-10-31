#!/Users/f/PythonApps/Textractor/bin/python3

from PyQt5.QtWidgets import QPushButton, QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QPlainTextEdit, qApp, QMainWindow, QTabWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore

import sys
import os

from pdf2image import convert_from_path
import pytesseract
import cv2


class ChildWidget(QWidget):

    def __init__(self, parent):
        super ().__init__ ()
        #QMainWindow.__init__ (self, None, QtCore.Qt.WindowStaysOnTopHint)
        QMainWindow.__init__ (self, None)

        # set position
        self.setGeometry (parent.screenW * 0.9, parent.screenH*0.248, parent.screenW * 0.1, parent.screenH * 0.4)
        self.setWindowTitle ('Text output ('+os.path.basename(parent.fname)+')')

        self.layout = QVBoxLayout (self)
        self.layout.setContentsMargins (0, 10, 0, 0)

        # Initialize tab screen
        self.tabs = QTabWidget ()
        #self.tabs.resize (300, 200)

        # Add tabs
        for p in range(parent.page_num):
            tab = QWidget ()
            self.tabs.addTab (tab, "Page " + str(p+1))

            # add content to the tab
            tab.layout = QVBoxLayout (tab)
            tab.layout.setContentsMargins (0, 0, 0, 0)
            # Text preview area
            self.out_txt = QPlainTextEdit (self)
            self.out_txt.insertPlainText (parent.text_allpages[p])

            tab.layout.addWidget (self.out_txt)
            tab.setLayout (tab.layout)

        # Add tabs to widget
        self.layout.addWidget (self.tabs)
        self.setLayout (self.layout)



class MainWindowWidget (QWidget):

    def __init__ (self):
        super ().__init__ ()
        QMainWindow.__init__ (self, None, QtCore.Qt.WindowStaysOnTopHint)

        # get screen size and set app size
        screen_resolution = app.desktop ().screenGeometry ()
        self.screenW, self.screenH = screen_resolution.width (), screen_resolution.height ()

        # set position
        self.setGeometry (self.screenW * 0.9, 0, self.screenW * 0.1, self.screenH * 0.2)
        self.setWindowTitle ('Textractor')

        # background
        self.icon = QLabel (self)
        self.icon.setAlignment (Qt.AlignCenter)
        self.icon.setPixmap (QPixmap ('/Users/f/PycharmProjects/Textractor/icon.png'))

        self.message = QLabel (self)
        self.message.setMinimumWidth (200)
        self.message.setAlignment (Qt.AlignCenter)
        self.message.setText ("<b>Drop</b> your files <b>here</b>")

        # A Vertical layout to include the button layout and then the image
        layout = QVBoxLayout ()
        layout.addWidget (self.icon)
        layout.addWidget (self.message)
        self.setLayout (layout)

        # Enable dragging and dropping onto the GUI
        self.setAcceptDrops (True)

        self.childWindows = []

        self.show ()

    def save_txt (self):
        fileName, _ = QFileDialog.getSaveFileName (self, "QFileDialog.getSaveFileName()", "",
                                                   "All Files (*);;Text Files (*.txt)")
        if fileName:
            text_file = open (fileName, "w")
            text_file.write (self.text)
            text_file.close ()

    def load_file_dialog (self):

        # Get the file location
        self.fname, _ = QFileDialog.getOpenFileName (self, 'Open file')
        # Load the image from the location
        self.load_doc ()

    def load_doc (self):
        is_image = True
        supported = True

        self.filename, f_extension = os.path.splitext (self.fname)
        if f_extension.lower() in ['.jpg', '.jpeg', '.png']:
            pages = [0]
        elif f_extension == ".pdf":
            is_image = False
            pages = convert_from_path (self.fname)
        else:
            supported = False

        text = ""
        self.text_allpages = []
        self.page_num = 0

        if supported:
            for page in pages:
                self.page_num += 1
                if is_image:
                    image = cv2.imread (self.fname)
                else:
                    # temp save pages as images
                    page.save ('temp.jpg', 'JPEG')
                    image = cv2.imread ('temp.jpg')
                    os.remove ('temp.jpg')

                # convert to grayscale and extract text with tesseract
                gray = cv2.cvtColor (image, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string (gray, lang="deu")
                text += "\n"
                self.text_allpages.append(text)
                #print (self.text)

            window_to_open = ChildWidget (self)
            window_to_open.show ()
            self.childWindows.append(window_to_open)

        else:
            print ('sorry, unsupported file!')

    # The following three methods set up dragging and dropping for the app
    def dragEnterEvent (self, e):
        if e.mimeData ().hasUrls:
            e.accept ()
        else:
            e.ignore ()

    def dragMoveEvent (self, e):
        if e.mimeData ().hasUrls:
            e.accept ()
        else:
            e.ignore ()

    def dropEvent (self, e):
        # Drop files directly onto the widget
        if e.mimeData ().hasUrls:
            e.setDropAction (Qt.CopyAction)
            e.accept ()
            for url in e.mimeData ().urls ():
                fname = str (url.toLocalFile ())
            self.fname = fname
            self.load_doc ()
        else:
            e.ignore ()


# Run if called directly
if __name__ == '__main__':
    # Initialise the application
    app = QApplication (sys.argv)
    # Call the widget
    ex = MainWindowWidget ()
    sys.exit (app.exec_ ())

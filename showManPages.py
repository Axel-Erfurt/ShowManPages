
from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QApplication, QMessageBox, \
                             QFrame, QComboBox, QAction, QLineEdit,\
                             QMainWindow
from PyQt5.QtGui import QIcon, QTextCursor, QFont
from PyQt5.QtCore import Qt, QDir, QFile, QTextStream, QProcess, QSize
import sys, os
quote = str(chr(34))
class myEditor(QMainWindow):
    def __init__(self, parent = None):
        super(myEditor, self).__init__(parent)
        ### editor
        self.editor = QPlainTextEdit()
        try:
            root = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            import sys
            root = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.appfolder = root + "/"
        self.editor.setFrameStyle(QFrame.NoFrame)
        self.editor.setTabStopWidth(20)
        myfont = QFont()
        myfont.setFamily("Droid Sans")
        myfont.setPointSize(8)
        self.editor.setFont(myfont)
        self.editor.setReadOnly(True)

        ### shell settings
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyRead.connect(self.readData)
        self.process.started.connect(lambda: self.statusBar().showMessage("starting shell"))
        self.process.finished.connect(lambda: self.statusBar().showMessage("shell ended"))

        ### toolbar
        bar=self.addToolBar("File")
        bar.setMovable(False)
        bar.setIconSize(QSize(16, 16))
        bar.addAction(QAction(QIcon.fromTheme('document-save'), "Save", self, triggered = self.saveFile, shortcut = "Ctrl+s"))
        bar.addSeparator()

        self.mycombo = QComboBox()
        self.mycombo.setFont(myfont)
        self.mycombo.setFixedWidth(200)
        self.mycombo.setToolTip("insert template")
        self.mycombo.activated[str].connect(self.loadFile)
        bar.addWidget(self.mycombo)

        bar.addSeparator()

        self.findfield = QLineEdit()
        self.findfield.setFont(myfont)
        self.findfield.addAction(QIcon.fromTheme("edit-find"), QLineEdit.LeadingPosition)
        self.findfield.setClearButtonEnabled(True)
        self.findfield.setFixedWidth(200)
        self.findfield.setPlaceholderText("find")
        self.findfield.setToolTip("press RETURN to find")
        self.findfield.setText("")
        self.findfield.returnPressed.connect(self.findText)
        bar.addWidget(self.findfield)
        bar.addSeparator()

        self.commandfield = QLineEdit()
        self.commandfield.setFont(myfont)
        self.commandfield.addAction(QIcon.fromTheme("edit-find"), QLineEdit.LeadingPosition)
        self.commandfield.setClearButtonEnabled(True)
        self.commandfield.setFixedWidth(200)
        self.commandfield.setPlaceholderText("enter command")
        self.commandfield.setToolTip("press RETURN to show help")
        self.commandfield.setText("")
        self.commandfield.returnPressed.connect(self.run)
        bar.addWidget(self.commandfield)

        ### layout
        layoutV = QVBoxLayout()
        layoutV.addWidget(self.editor)
        mq = QWidget(self)
        mq.setLayout(layoutV)
        self.setCentralWidget(mq)

        self.commandfield.setFocus()
        self.fillCombo()
        self.statusBar().showMessage("Welcome")
        self.statusBar().setFont(QFont("Droid Sans", 7))
        self.mycombo.setCurrentIndex(0)
        self.loadFile()

    def loadFile(self):
        path = self.appfolder + "Pages/" + self.mycombo.itemText(self.mycombo.currentIndex()) + ".txt"
        self.statusBar().showMessage(path)
        if path:
            self.editor.clear()
            inFile = QFile(path)
            if inFile.open(QFile.ReadOnly | QFile.Text):
                text = inFile.readAll()
                self.editor.setFocus()
                try: ### python 3
                    self.editor.textCursor().insertText(str(text, encoding = 'utf8'))
                except TypeError:  ### python 2
                    self.editor.textCursor().insertText(str(text))
                self.statusBar().showMessage("'" + self.mycombo.itemText(self.mycombo.currentIndex()) + "' loaded")
                self.editor.moveCursor(self.editor.textCursor().Start)
                inFile.close()
                self.commandfield.setFocus()
            else:
                self.statusBar().showMessage("error loading File")

    def loadFile2(self):
        path = "/tmp/temp.txt"
        self.statusBar().showMessage(path)
        if path:
            self.editor.clear()
            inFile = QFile(path)
            if inFile.open(QFile.ReadOnly | QFile.Text):
                text = inFile.readAll()
                self.editor.setFocus()
                try: ### python 3
                    self.editor.textCursor().insertText(str(text, encoding = 'utf8'))
                except TypeError:  ### python 2
                    self.editor.textCursor().insertText(str(text))
                self.statusBar().showMessage("'" + self.commandfield.text() + "' loaded")
                self.editor.moveCursor(self.editor.textCursor().Start)
                inFile.close()
                self.commandfield.setFocus()
            else:
                self.statusBar().showMessage("error loading File")

    def saveFile(self):
        file = QFile(self.appfolder + "Pages/" + self.commandfield.text() + ".txt")
        if not file.open(QFile.WriteOnly | QFile.Text):
            QMessageBox.warning(self, "Message",
                    "Cannot write file")
            return False

        outfile = QTextStream(file)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        outfile << self.editor.toPlainText()
        QApplication.restoreOverrideCursor()
        self.statusBar().showMessage("File saved", 3000)
        self.mycombo.clear()
        self.fillCombo()
        return True

    def fillCombo(self):
        folder = self.appfolder + "Pages"
        if QDir().exists(folder):
            self.currentDir = QDir(folder)
            count = self.currentDir.count()
            fileName = "*"
            files = self.currentDir.entryList([fileName],
                    QDir.Files | QDir.NoSymLinks)
#            self.statusBar().showMessage(','.join(files))   
            for i in range(count - 2):
                file = (files[i])
                if file.endswith(".txt"):
                    self.mycombo.addItem(file.replace(self.appfolder + "/Pages", "").replace(".txt", ""))

    def exitAct(self):
        print("Goodbye ...")
        app.quit()

    def findText(self):
        word = self.findfield.text()
        if self.editor.find(word):
            linenumber = self.editor.textCursor().blockNumber() + 1
            self.statusBar().showMessage("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
            self.editor.centerCursor()
        else:
            self.statusBar().showMessage("<b>'" + self.findfield.text() + "'</b> not found")
            self.editor.moveCursor(QTextCursor.Start)            
            if self.editor.find(word):
                linenumber = self.editor.textCursor().blockNumber() + 1
                self.statusBar().showMessage("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
                self.editor.centerCursor()

    def run(self):
        if not self.commandfield.text() == "":
            self.readData()
        else:
            self.statusBar().showMessage("no code to run")

    def readData(self):
        os.system(self.commandfield.text() + " --help > /tmp/temp.txt")
        self.loadFile2()

    def msgbox(self, message):
        QMessageBox.warning(self, "Message", message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = myEditor()
    win.setWindowIcon(QIcon.fromTheme("gnome-mime-text-x-python"))
    win.setWindowTitle("showManPages")
    win.setGeometry(0, 0, 710,700)
    win.setMinimumSize(710,250)
    win.show()
    app.exec_()
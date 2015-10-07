
try:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
except:
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *    
    from PyQt5.QtWidgets import * 

import zipfile
import uncompyle2
import re
import py_compile
import shutil
import os
import platform

class MainWin(QWidget):
    #----------------------------------------------------------------------
    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        
        paths = self.findWingIDEPath()
    
        self.cbxPath = QComboBox()
        self.cbxPath.setEditable(True)
        self.cbxPath.addItems(paths)
        
        lay = QVBoxLayout()
        lay.addWidget(QLabel('Path'))
        
        button = QPushButton('Browse...')
        button.clicked.connect(self.onBrowseClick)
        
        slay = QHBoxLayout() 
        slay.addWidget(self.cbxPath)
        slay.addWidget(button)
        lay.addLayout(slay)
        
        button2 = QPushButton('Process')
        button2.clicked.connect(self.onProcess)
        lay.addWidget(button2)
        
        self.setLayout(lay)
    
    #----------------------------------------------------------------------
    def findWingIDEPath(self):
        paths = []
        if platform.system() == 'Windows':
            settings = QSettings('HKEY_LOCAL_MACHINE\\SOFTWARE\\ARCHAEOPTERYX\\WINGIDE',QSettings.NativeFormat)
            for version in settings.childGroups():
                settings.beginGroup(version)
                settings.beginGroup('INSTALL')
                paths.append(QDir(settings.value('WINGHOME','').toString()).absolutePath() + '/bin/2.7/src.zip')
                settings.endGroup()
                settings.endGroup()
        if platform.system() == 'Darwin':
            paths.append('/Applications/WingIDE.app/Contents/Resources/bin/2.7/src.zip')
        return paths
    
    #----------------------------------------------------------------------
    def onBrowseClick(self):
        path = QFileDialog.getOpenFileName(self,'Get src.zip',QDesktopServices.storageLocation(QDesktopServices.ApplicationsLocation),'src.zip')
        if path:
            self.cbxPath.setEditText(path)
        
    #----------------------------------------------------------------------
    def onProcess(self):
        src_zip = self.cbxPath.currentText()
        if not QDir().exists(src_zip):
            QMessageBox.critical(self,'Error',"Cannot find file %s" % src_zip)
            return
        src_zip = src_zip
        work_dir = QDir.currentPath()

        SRC_PYO = 'process/wingctl.pyo'
        UNCOMP_PY = 'u_wingctl.py'
        HACK_PY = 'wingctl.py'
        COMP_PYO = 'wingctl.pyo'
        TGT_ZIP = 'src.zip'
        
        fh_zip_w = zipfile.ZipFile(TGT_ZIP,'w')
        fh_zip = zipfile.ZipFile(str(src_zip),'r')
        fh_zip.extract(SRC_PYO,str(work_dir))
        for f in fh_zip.namelist():
            if f != SRC_PYO:
                fh_zip_w.writestr(f,fh_zip.read(f))
            
        fh_zip.close()
        uncompyle2.main(str(work_dir),str(work_dir),[SRC_PYO],[],outfile=UNCOMP_PY)
        
        fh_pyr = open(UNCOMP_PY,'r')
        fh_pyd = open(HACK_PY,'w')
        
        for line in fh_pyr:
            fh_pyd.write(line.replace('self.LicenseOK()','1'))
        fh_pyr.close()
        fh_pyd.close()
    
        py_compile.compile(HACK_PY,COMP_PYO)
        
        fh_zip_w.write(COMP_PYO,SRC_PYO)
        fh_zip_w.close()
        shutil.move(TGT_ZIP,str(src_zip))
        os.remove(SRC_PYO)
        os.remove(UNCOMP_PY)
        os.remove(HACK_PY)
        os.remove(COMP_PYO)
        
if __name__ == '__main__':
    app = QApplication([])
    w = MainWin()
    w.show()
    app.exec_()
        
        

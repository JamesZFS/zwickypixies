from PyQt5 import QtWidgets
import config
class BottomBar:

    def __init__(self, parent):
        self.parent = parent
        self.bottombar = None
        self.bottomBarFileLabel = None
        self.bottomBarProgressLabel = None
        self.bottomBarThresholdLabel = None
        self.bottomBarFilterLabel = None
        self.initBottomBar()

    def initBottomBar(self):
        self.bottombar = QtWidgets.QFrame(self.parent.frame)
        self.bottombar.setFixedHeight(20)
        self.bottombar.setStyleSheet("background-color: rgba(255, 255, 255, 0.2);")
        bottomBarLayout = QtWidgets.QHBoxLayout(self.bottombar)
        bottomBarLayout.setSpacing(0)
        bottomBarLayout.setContentsMargins(0, 0, 0, 0)
        self.bottombar.setLayout(bottomBarLayout)

        self.bottomBarFileLabel = QtWidgets.QLabel(self.bottombar)
        self.bottomBarFileLabel.setContentsMargins(0, 0, 0, 0)
        self.bottomBarFileLabel.setMinimumSize(self.bottomBarFileLabel.sizeHint())
        bottomBarLayout.addWidget(self.bottomBarFileLabel)

        self.bottomBarProgressLabel = QtWidgets.QLabel(self.bottombar)
        self.bottomBarProgressLabel.setContentsMargins(0, 0, 0, 0)
        self.bottomBarProgressLabel.setMinimumSize(self.bottomBarProgressLabel.sizeHint())
        bottomBarLayout.addWidget(self.bottomBarProgressLabel)

        self.bottomBarThresholdLabel = QtWidgets.QLabel(self.bottombar)
        self.bottomBarThresholdLabel.setContentsMargins(0, 0, 0, 0)
        self.bottomBarThresholdLabel.setMinimumSize(self.bottomBarThresholdLabel.sizeHint())
        bottomBarLayout.addWidget(self.bottomBarThresholdLabel)

        self.bottomBarFilterLabel = QtWidgets.QLabel(self.bottombar)
        self.bottomBarFilterLabel.setContentsMargins(0, 0, 0, 0)
        self.bottomBarFilterLabel.setMinimumSize(self.bottomBarFilterLabel.sizeHint())
        bottomBarLayout.addWidget(self.bottomBarFilterLabel)

        self.parent.vl.addWidget(self.bottombar)
        self.parent.vl.setSpacing(0)

    def updateBottomBarText(self):
        self.bottomBarFileLabel.setText(" File: " + config.File)

    def updateBottomBarProgress(self, current):
        percent = 100/624*current
        self.bottomBarProgressLabel.setText("Rendering: [{}] {}%".format(self.getloadingbar(percent), int(percent)))

    def clearBottomBarProgress(self):
        self.bottomBarProgressLabel.setText("")

    def getloadingbar(self, percent):
        barlen = 40
        num = int(barlen / 100 * percent)
        arr = []
        for i in range(num):
            arr.append("#")
        for i in range(num, barlen):
            arr.append(" ")
        return ''.join(arr)



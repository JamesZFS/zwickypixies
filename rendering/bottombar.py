from PyQt5 import QtWidgets
import config
class BottomBar:

    def __init__(self, parent):
        self.parent = parent
        self.bottombar = None
        self.bottomBarFileLabel = None
        self.bottomBarArrayNameLabel = None
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

        self.bottomBarArrayNameLabel = QtWidgets.QLabel(self.bottombar)
        self.bottomBarArrayNameLabel.setContentsMargins(0, 0, 0, 0)
        self.bottomBarArrayNameLabel.setMinimumSize(self.bottomBarArrayNameLabel.sizeHint())
        bottomBarLayout.addWidget(self.bottomBarArrayNameLabel)

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


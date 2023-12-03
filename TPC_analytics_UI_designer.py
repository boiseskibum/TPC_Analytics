# Form implementation generated from reading ui file 'TPC_analytics_UI_designer.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainAnalyticsWindow(object):
    def setupUi(self, MainAnalyticsWindow):
        MainAnalyticsWindow.setObjectName("MainAnalyticsWindow")
        MainAnalyticsWindow.resize(1561, 978)
        self.centralwidget = QtWidgets.QWidget(parent=MainAnalyticsWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.tabWidget = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_trial_browser = QtWidgets.QWidget()
        self.tab_trial_browser.setObjectName("tab_trial_browser")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.tab_trial_browser)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.splitter = QtWidgets.QSplitter(parent=self.tab_trial_browser)
        self.splitter.setEnabled(True)
        self.splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.splitter.setObjectName("splitter")
        self.splitter_3 = QtWidgets.QSplitter(parent=self.splitter)
        self.splitter_3.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.splitter_3.setObjectName("splitter_3")
        self.treeWidget = QtWidgets.QTreeWidget(parent=self.splitter_3)
        self.treeWidget.setMinimumSize(QtCore.QSize(175, 0))
        self.treeWidget.setColumnCount(1)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.treeWidget.header().setVisible(False)
        self.layoutWidget_3 = QtWidgets.QWidget(parent=self.splitter_3)
        self.layoutWidget_3.setObjectName("layoutWidget_3")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget_3)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_protocol = QtWidgets.QLabel(parent=self.layoutWidget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_protocol.sizePolicy().hasHeightForWidth())
        self.label_protocol.setSizePolicy(sizePolicy)
        self.label_protocol.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.label_protocol.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.label_protocol.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_protocol.setObjectName("label_protocol")
        self.gridLayout.addWidget(self.label_protocol, 1, 0, 1, 1)
        self.label_athlete = QtWidgets.QLabel(parent=self.layoutWidget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_athlete.sizePolicy().hasHeightForWidth())
        self.label_athlete.setSizePolicy(sizePolicy)
        self.label_athlete.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_athlete.setObjectName("label_athlete")
        self.gridLayout.addWidget(self.label_athlete, 0, 0, 1, 1)
        self.label_athlete_value = QtWidgets.QLabel(parent=self.layoutWidget_3)
        self.label_athlete_value.setObjectName("label_athlete_value")
        self.gridLayout.addWidget(self.label_athlete_value, 0, 1, 1, 1)
        self.label_date = QtWidgets.QLabel(parent=self.layoutWidget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_date.sizePolicy().hasHeightForWidth())
        self.label_date.setSizePolicy(sizePolicy)
        self.label_date.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_date.setObjectName("label_date")
        self.gridLayout.addWidget(self.label_date, 2, 0, 1, 1)
        self.label_date_value = QtWidgets.QLabel(parent=self.layoutWidget_3)
        self.label_date_value.setObjectName("label_date_value")
        self.gridLayout.addWidget(self.label_date_value, 2, 1, 1, 1)
        self.label_protocol_value = QtWidgets.QLabel(parent=self.layoutWidget_3)
        self.label_protocol_value.setObjectName("label_protocol_value")
        self.gridLayout.addWidget(self.label_protocol_value, 1, 1, 1, 1)
        self.label_trial_value = QtWidgets.QLabel(parent=self.layoutWidget_3)
        self.label_trial_value.setObjectName("label_trial_value")
        self.gridLayout.addWidget(self.label_trial_value, 3, 1, 1, 1)
        self.label_trial = QtWidgets.QLabel(parent=self.layoutWidget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_trial.sizePolicy().hasHeightForWidth())
        self.label_trial.setSizePolicy(sizePolicy)
        self.label_trial.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_trial.setObjectName("label_trial")
        self.gridLayout.addWidget(self.label_trial, 3, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout_graph = QtWidgets.QVBoxLayout()
        self.verticalLayout_graph.setObjectName("verticalLayout_graph")
        self.label_graphic = QtWidgets.QLabel(parent=self.layoutWidget_3)
        self.label_graphic.setObjectName("label_graphic")
        self.verticalLayout_graph.addWidget(self.label_graphic)
        self.videoSlider = QtWidgets.QSlider(parent=self.layoutWidget_3)
        self.videoSlider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.videoSlider.setObjectName("videoSlider")
        self.verticalLayout_graph.addWidget(self.videoSlider)
        self.verticalLayout.addLayout(self.verticalLayout_graph)
        self.horizontalLayout_play = QtWidgets.QHBoxLayout()
        self.horizontalLayout_play.setObjectName("horizontalLayout_play")
        self.pushButton_rewind_to_start = QtWidgets.QPushButton(parent=self.layoutWidget_3)
        self.pushButton_rewind_to_start.setObjectName("pushButton_rewind_to_start")
        self.horizontalLayout_play.addWidget(self.pushButton_rewind_to_start)
        self.pushButton_rewind_chunk = QtWidgets.QPushButton(parent=self.layoutWidget_3)
        self.pushButton_rewind_chunk.setObjectName("pushButton_rewind_chunk")
        self.horizontalLayout_play.addWidget(self.pushButton_rewind_chunk)
        self.pushButton_rewind = QtWidgets.QPushButton(parent=self.layoutWidget_3)
        self.pushButton_rewind.setObjectName("pushButton_rewind")
        self.horizontalLayout_play.addWidget(self.pushButton_rewind)
        self.pushButton_stop = QtWidgets.QPushButton(parent=self.layoutWidget_3)
        self.pushButton_stop.setObjectName("pushButton_stop")
        self.horizontalLayout_play.addWidget(self.pushButton_stop)
        self.pushButton_play = QtWidgets.QPushButton(parent=self.layoutWidget_3)
        self.pushButton_play.setObjectName("pushButton_play")
        self.horizontalLayout_play.addWidget(self.pushButton_play)
        self.pushButton_forward = QtWidgets.QPushButton(parent=self.layoutWidget_3)
        self.pushButton_forward.setObjectName("pushButton_forward")
        self.horizontalLayout_play.addWidget(self.pushButton_forward)
        self.pushButton_forward_chunk = QtWidgets.QPushButton(parent=self.layoutWidget_3)
        self.pushButton_forward_chunk.setObjectName("pushButton_forward_chunk")
        self.horizontalLayout_play.addWidget(self.pushButton_forward_chunk)
        self.verticalLayout.addLayout(self.horizontalLayout_play)
        self.horizontalLayout_play_options = QtWidgets.QHBoxLayout()
        self.horizontalLayout_play_options.setObjectName("horizontalLayout_play_options")
        self.verticalLayout_speed = QtWidgets.QVBoxLayout()
        self.verticalLayout_speed.setObjectName("verticalLayout_speed")
        self.radioButton_full = QtWidgets.QRadioButton(parent=self.layoutWidget_3)
        self.radioButton_full.setObjectName("radioButton_full")
        self.verticalLayout_speed.addWidget(self.radioButton_full)
        self.radioButton_slow = QtWidgets.QRadioButton(parent=self.layoutWidget_3)
        self.radioButton_slow.setObjectName("radioButton_slow")
        self.verticalLayout_speed.addWidget(self.radioButton_slow)
        self.radioButton_super_slow = QtWidgets.QRadioButton(parent=self.layoutWidget_3)
        self.radioButton_super_slow.setObjectName("radioButton_super_slow")
        self.verticalLayout_speed.addWidget(self.radioButton_super_slow)
        self.horizontalLayout_play_options.addLayout(self.verticalLayout_speed)
        self.verticalLayout_labels = QtWidgets.QVBoxLayout()
        self.verticalLayout_labels.setObjectName("verticalLayout_labels")
        self.checkBox_short_video = QtWidgets.QCheckBox(parent=self.layoutWidget_3)
        self.checkBox_short_video.setObjectName("checkBox_short_video")
        self.verticalLayout_labels.addWidget(self.checkBox_short_video)
        self.checkBox_freeze_y_axis = QtWidgets.QCheckBox(parent=self.layoutWidget_3)
        self.checkBox_freeze_y_axis.setObjectName("checkBox_freeze_y_axis")
        self.verticalLayout_labels.addWidget(self.checkBox_freeze_y_axis)
        self.qlabel_time = QtWidgets.QLabel(parent=self.layoutWidget_3)
        self.qlabel_time.setObjectName("qlabel_time")
        self.verticalLayout_labels.addWidget(self.qlabel_time)
        self.label_align_video = QtWidgets.QLabel(parent=self.layoutWidget_3)
        self.label_align_video.setObjectName("label_align_video")
        self.verticalLayout_labels.addWidget(self.label_align_video)
        self.videoAlignmentSlider = QtWidgets.QSlider(parent=self.layoutWidget_3)
        self.videoAlignmentSlider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.videoAlignmentSlider.setObjectName("videoAlignmentSlider")
        self.verticalLayout_labels.addWidget(self.videoAlignmentSlider)
        self.horizontalLayout_play_options.addLayout(self.verticalLayout_labels)
        self.verticalLayout.addLayout(self.horizontalLayout_play_options)
        self.verticalLayout.setStretch(1, 1)
        self.layoutWidget_4 = QtWidgets.QWidget(parent=self.splitter)
        self.layoutWidget_4.setObjectName("layoutWidget_4")
        self.horizontalLayout_video_panels = QtWidgets.QHBoxLayout(self.layoutWidget_4)
        self.horizontalLayout_video_panels.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_video_panels.setObjectName("horizontalLayout_video_panels")
        self.verticalLayout_Lvideo = QtWidgets.QVBoxLayout()
        self.verticalLayout_Lvideo.setObjectName("verticalLayout_Lvideo")
        self.label_video1 = QtWidgets.QLabel(parent=self.layoutWidget_4)
        self.label_video1.setMinimumSize(QtCore.QSize(350, 0))
        self.label_video1.setObjectName("label_video1")
        self.verticalLayout_Lvideo.addWidget(self.label_video1)
        self.checkBox_video1_enable = QtWidgets.QCheckBox(parent=self.layoutWidget_4)
        self.checkBox_video1_enable.setChecked(True)
        self.checkBox_video1_enable.setObjectName("checkBox_video1_enable")
        self.verticalLayout_Lvideo.addWidget(self.checkBox_video1_enable)
        self.checkBox_video1_overlay = QtWidgets.QCheckBox(parent=self.layoutWidget_4)
        self.checkBox_video1_overlay.setChecked(True)
        self.checkBox_video1_overlay.setObjectName("checkBox_video1_overlay")
        self.verticalLayout_Lvideo.addWidget(self.checkBox_video1_overlay)
        self.horizontalLayout_video_panels.addLayout(self.verticalLayout_Lvideo)
        self.verticalLayout_Rvideo = QtWidgets.QVBoxLayout()
        self.verticalLayout_Rvideo.setObjectName("verticalLayout_Rvideo")
        self.label_video2 = QtWidgets.QLabel(parent=self.layoutWidget_4)
        self.label_video2.setMinimumSize(QtCore.QSize(350, 0))
        self.label_video2.setObjectName("label_video2")
        self.verticalLayout_Rvideo.addWidget(self.label_video2)
        self.checkBox_video2_enable = QtWidgets.QCheckBox(parent=self.layoutWidget_4)
        self.checkBox_video2_enable.setChecked(True)
        self.checkBox_video2_enable.setObjectName("checkBox_video2_enable")
        self.verticalLayout_Rvideo.addWidget(self.checkBox_video2_enable)
        self.checkBox_video2_overlay = QtWidgets.QCheckBox(parent=self.layoutWidget_4)
        self.checkBox_video2_overlay.setChecked(True)
        self.checkBox_video2_overlay.setObjectName("checkBox_video2_overlay")
        self.verticalLayout_Rvideo.addWidget(self.checkBox_video2_overlay)
        self.horizontalLayout_video_panels.addLayout(self.verticalLayout_Rvideo)
        self.horizontalLayout.addWidget(self.splitter)
        self.tabWidget.addTab(self.tab_trial_browser, "")
        self.tab_report = QtWidgets.QWidget()
        self.tab_report.setObjectName("tab_report")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.tab_report)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.treeWidget_reports = QtWidgets.QTreeWidget(parent=self.tab_report)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeWidget_reports.sizePolicy().hasHeightForWidth())
        self.treeWidget_reports.setSizePolicy(sizePolicy)
        self.treeWidget_reports.setMinimumSize(QtCore.QSize(175, 0))
        self.treeWidget_reports.setObjectName("treeWidget_reports")
        self.treeWidget_reports.headerItem().setText(0, "1")
        self.treeWidget_reports.header().setVisible(False)
        self.horizontalLayout_7.addWidget(self.treeWidget_reports)
        self.verticalLayout_10 = QtWidgets.QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.gridLayout_plots = QtWidgets.QGridLayout()
        self.gridLayout_plots.setContentsMargins(5, 5, 5, 5)
        self.gridLayout_plots.setHorizontalSpacing(6)
        self.gridLayout_plots.setObjectName("gridLayout_plots")
        self.label_plot3 = QtWidgets.QLabel(parent=self.tab_report)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_plot3.sizePolicy().hasHeightForWidth())
        self.label_plot3.setSizePolicy(sizePolicy)
        self.label_plot3.setObjectName("label_plot3")
        self.gridLayout_plots.addWidget(self.label_plot3, 1, 0, 1, 1)
        self.label_plot2 = QtWidgets.QLabel(parent=self.tab_report)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_plot2.sizePolicy().hasHeightForWidth())
        self.label_plot2.setSizePolicy(sizePolicy)
        self.label_plot2.setObjectName("label_plot2")
        self.gridLayout_plots.addWidget(self.label_plot2, 0, 1, 1, 1)
        self.label_plot1 = QtWidgets.QLabel(parent=self.tab_report)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_plot1.sizePolicy().hasHeightForWidth())
        self.label_plot1.setSizePolicy(sizePolicy)
        self.label_plot1.setObjectName("label_plot1")
        self.gridLayout_plots.addWidget(self.label_plot1, 0, 0, 1, 1)
        self.label_plot4 = QtWidgets.QLabel(parent=self.tab_report)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_plot4.sizePolicy().hasHeightForWidth())
        self.label_plot4.setSizePolicy(sizePolicy)
        self.label_plot4.setObjectName("label_plot4")
        self.gridLayout_plots.addWidget(self.label_plot4, 1, 1, 1, 1)
        self.verticalLayout_10.addLayout(self.gridLayout_plots)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem)
        self.pushButton_page_back = QtWidgets.QPushButton(parent=self.tab_report)
        self.pushButton_page_back.setObjectName("pushButton_page_back")
        self.horizontalLayout_6.addWidget(self.pushButton_page_back)
        self.page_of_page = QtWidgets.QLabel(parent=self.tab_report)
        self.page_of_page.setObjectName("page_of_page")
        self.horizontalLayout_6.addWidget(self.page_of_page)
        self.pushButton_page_forward = QtWidgets.QPushButton(parent=self.tab_report)
        self.pushButton_page_forward.setObjectName("pushButton_page_forward")
        self.horizontalLayout_6.addWidget(self.pushButton_page_forward)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem1)
        self.pushButton_create_pdf = QtWidgets.QPushButton(parent=self.tab_report)
        self.pushButton_create_pdf.setObjectName("pushButton_create_pdf")
        self.horizontalLayout_6.addWidget(self.pushButton_create_pdf)
        self.pushbutton_results_directory = QtWidgets.QPushButton(parent=self.tab_report)
        self.pushbutton_results_directory.setObjectName("pushbutton_results_directory")
        self.horizontalLayout_6.addWidget(self.pushbutton_results_directory)
        self.horizontalLayout_6.setStretch(0, 12)
        self.horizontalLayout_6.setStretch(4, 2)
        self.verticalLayout_10.addLayout(self.horizontalLayout_6)
        self.verticalLayout_10.setStretch(0, 1)
        self.horizontalLayout_7.addLayout(self.verticalLayout_10)
        self.horizontalLayout_2.addLayout(self.horizontalLayout_7)
        self.tabWidget.addTab(self.tab_report, "")
        self.horizontalLayout_3.addWidget(self.tabWidget)
        MainAnalyticsWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainAnalyticsWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1561, 22))
        self.menubar.setObjectName("menubar")
        MainAnalyticsWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainAnalyticsWindow)
        self.statusbar.setObjectName("statusbar")
        MainAnalyticsWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainAnalyticsWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainAnalyticsWindow)

    def retranslateUi(self, MainAnalyticsWindow):
        _translate = QtCore.QCoreApplication.translate
        MainAnalyticsWindow.setWindowTitle(_translate("MainAnalyticsWindow", "MainWindow"))
        self.label_protocol.setText(_translate("MainAnalyticsWindow", "Protocol:"))
        self.label_athlete.setText(_translate("MainAnalyticsWindow", "Athlete:"))
        self.label_athlete_value.setText(_translate("MainAnalyticsWindow", "TextLabel"))
        self.label_date.setText(_translate("MainAnalyticsWindow", "Date:"))
        self.label_date_value.setText(_translate("MainAnalyticsWindow", "TextLabel"))
        self.label_protocol_value.setText(_translate("MainAnalyticsWindow", "TextLabel"))
        self.label_trial_value.setText(_translate("MainAnalyticsWindow", "TextLabel"))
        self.label_trial.setText(_translate("MainAnalyticsWindow", "Trial:"))
        self.label_graphic.setText(_translate("MainAnalyticsWindow", "TextLabel"))
        self.pushButton_rewind_to_start.setText(_translate("MainAnalyticsWindow", "Rewind to start"))
        self.pushButton_rewind_chunk.setText(_translate("MainAnalyticsWindow", "Rewind chunk"))
        self.pushButton_rewind.setText(_translate("MainAnalyticsWindow", "Rewind 1"))
        self.pushButton_stop.setText(_translate("MainAnalyticsWindow", "Stop"))
        self.pushButton_play.setText(_translate("MainAnalyticsWindow", "Play"))
        self.pushButton_forward.setText(_translate("MainAnalyticsWindow", "Forward 1"))
        self.pushButton_forward_chunk.setText(_translate("MainAnalyticsWindow", "Forward chunk"))
        self.radioButton_full.setText(_translate("MainAnalyticsWindow", "Full Speed"))
        self.radioButton_slow.setText(_translate("MainAnalyticsWindow", "Slow Motion"))
        self.radioButton_super_slow.setText(_translate("MainAnalyticsWindow", "Super Slow Motion"))
        self.checkBox_short_video.setText(_translate("MainAnalyticsWindow", "Jump only"))
        self.checkBox_freeze_y_axis.setText(_translate("MainAnalyticsWindow", "Freeze Y axis"))
        self.qlabel_time.setText(_translate("MainAnalyticsWindow", "time"))
        self.label_align_video.setText(_translate("MainAnalyticsWindow", "Align video with \"feet off\" in CMJ"))
        self.label_video1.setText(_translate("MainAnalyticsWindow", "video 1"))
        self.checkBox_video1_enable.setText(_translate("MainAnalyticsWindow", "enable"))
        self.checkBox_video1_overlay.setText(_translate("MainAnalyticsWindow", "overlay"))
        self.label_video2.setText(_translate("MainAnalyticsWindow", "video 2"))
        self.checkBox_video2_enable.setText(_translate("MainAnalyticsWindow", "enable"))
        self.checkBox_video2_overlay.setText(_translate("MainAnalyticsWindow", "overlay"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_trial_browser), _translate("MainAnalyticsWindow", "Trial Browser"))
        self.label_plot3.setText(_translate("MainAnalyticsWindow", "TextLabel"))
        self.label_plot2.setText(_translate("MainAnalyticsWindow", "TextLabel"))
        self.label_plot1.setText(_translate("MainAnalyticsWindow", "TextLabel"))
        self.label_plot4.setText(_translate("MainAnalyticsWindow", "TextLabel"))
        self.pushButton_page_back.setText(_translate("MainAnalyticsWindow", "  Page Back  "))
        self.page_of_page.setText(_translate("MainAnalyticsWindow", "TextLabel"))
        self.pushButton_page_forward.setText(_translate("MainAnalyticsWindow", "  Page Forward  "))
        self.pushButton_create_pdf.setText(_translate("MainAnalyticsWindow", "  Create PDF Report  "))
        self.pushbutton_results_directory.setText(_translate("MainAnalyticsWindow", "  Results Directory  "))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_report), _translate("MainAnalyticsWindow", "Trial Reports"))

# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QAbstractSpinBox, QApplication, QCheckBox,
    QComboBox, QDateTimeEdit, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QSizePolicy, QTabWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_MyMainWindow(object):
    def setupUi(self, MyMainWindow):
        if not MyMainWindow.objectName():
            MyMainWindow.setObjectName(u"MyMainWindow")
        MyMainWindow.resize(1240, 800)
        MyMainWindow.setMinimumSize(QSize(1240, 700))
        MyMainWindow.setMaximumSize(QSize(1240, 800))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        MyMainWindow.setFont(font)
        MyMainWindow.setDocumentMode(False)
        MyMainWindow.setTabShape(QTabWidget.Triangular)
        MyMainWindow.setDockNestingEnabled(False)
        self.centralwidget = QWidget(MyMainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setMinimumSize(QSize(1240, 700))
        self.centralwidget.setMaximumSize(QSize(1240, 800))
        self.centralwidget.setFocusPolicy(Qt.TabFocus)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setAutoFillBackground(True)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.tab.setAutoFillBackground(True)
        self.widget_6 = QWidget(self.tab)
        self.widget_6.setObjectName(u"widget_6")
        self.widget_6.setGeometry(QRect(5, 270, 1200, 481))
        self.widget_6.setMaximumSize(QSize(1200, 16777215))
        self.widget_6.setAutoFillBackground(True)
        self.verticalLayout_3 = QVBoxLayout(self.widget_6)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(6, 6, 6, 6)
        self.widget_20 = QWidget(self.widget_6)
        self.widget_20.setObjectName(u"widget_20")
        self.widget_20.setMaximumSize(QSize(700, 40))
        self.horizontalLayout_17 = QHBoxLayout(self.widget_20)
        self.horizontalLayout_17.setSpacing(6)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.horizontalLayout_17.setContentsMargins(6, 6, 0, 0)
        self.btn_select_all_profiles = QPushButton(self.widget_20)
        self.btn_select_all_profiles.setObjectName(u"btn_select_all_profiles")
        self.btn_select_all_profiles.setMinimumSize(QSize(100, 25))
        self.btn_select_all_profiles.setMaximumSize(QSize(100, 16777215))
        self.btn_select_all_profiles.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_17.addWidget(self.btn_select_all_profiles)

        self.in_api_url = QLineEdit(self.widget_20)
        self.in_api_url.setObjectName(u"in_api_url")
        self.in_api_url.setEnabled(True)
        self.in_api_url.setMinimumSize(QSize(0, 25))
        self.in_api_url.setMaximumSize(QSize(160, 16777215))
        font1 = QFont()
        font1.setPointSize(10)
        self.in_api_url.setFont(font1)

        self.horizontalLayout_17.addWidget(self.in_api_url)

        self.btn_reload_profiles = QPushButton(self.widget_20)
        self.btn_reload_profiles.setObjectName(u"btn_reload_profiles")
        self.btn_reload_profiles.setMinimumSize(QSize(120, 25))
        self.btn_reload_profiles.setMaximumSize(QSize(120, 16777215))
        self.btn_reload_profiles.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_17.addWidget(self.btn_reload_profiles)

        self.in_search_profiles = QLineEdit(self.widget_20)
        self.in_search_profiles.setObjectName(u"in_search_profiles")
        self.in_search_profiles.setEnabled(True)
        self.in_search_profiles.setMinimumSize(QSize(0, 25))
        self.in_search_profiles.setMaximumSize(QSize(140, 16777215))
        self.in_search_profiles.setFont(font1)

        self.horizontalLayout_17.addWidget(self.in_search_profiles)

        self.cb_groups_profile = QComboBox(self.widget_20)
        self.cb_groups_profile.setObjectName(u"cb_groups_profile")
        self.cb_groups_profile.setMinimumSize(QSize(0, 25))
        self.cb_groups_profile.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_17.addWidget(self.cb_groups_profile)


        self.verticalLayout_3.addWidget(self.widget_20)

        self.table_list_profiles = QTableWidget(self.widget_6)
        if (self.table_list_profiles.columnCount() < 7):
            self.table_list_profiles.setColumnCount(7)
        __qtablewidgetitem = QTableWidgetItem()
        self.table_list_profiles.setHorizontalHeaderItem(0, __qtablewidgetitem)
        font2 = QFont()
        font2.setFamilies([u"Arial"])
        font2.setPointSize(10)
        font2.setBold(True)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setFont(font2);
        self.table_list_profiles.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setFont(font2);
        self.table_list_profiles.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        __qtablewidgetitem3.setFont(font2);
        self.table_list_profiles.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setFont(font2);
        self.table_list_profiles.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        __qtablewidgetitem5.setFont(font2);
        self.table_list_profiles.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        __qtablewidgetitem6.setFont(font2);
        self.table_list_profiles.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        self.table_list_profiles.setObjectName(u"table_list_profiles")
        self.table_list_profiles.setMinimumSize(QSize(0, 0))
        self.table_list_profiles.setMaximumSize(QSize(1230, 16777215))
        self.table_list_profiles.viewport().setProperty("cursor", QCursor(Qt.CursorShape.ArrowCursor))
        self.table_list_profiles.setAutoFillBackground(True)
        self.table_list_profiles.setStyleSheet(u"#QHeaderView::section {\n"
"	border-bottom: 1px solid #D8D8D8;\n"
"}\n"
" ")
        self.table_list_profiles.setInputMethodHints(Qt.ImhNone)
        self.table_list_profiles.setLineWidth(1)
        self.table_list_profiles.setMidLineWidth(0)
        self.table_list_profiles.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_list_profiles.setProperty("showDropIndicator", False)
        self.table_list_profiles.setDragDropOverwriteMode(False)
        self.table_list_profiles.setAlternatingRowColors(True)
        self.table_list_profiles.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_list_profiles.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_list_profiles.setShowGrid(True)
        self.table_list_profiles.setGridStyle(Qt.SolidLine)
        self.table_list_profiles.setSortingEnabled(True)
        self.table_list_profiles.setWordWrap(False)
        self.table_list_profiles.setCornerButtonEnabled(False)
        self.table_list_profiles.horizontalHeader().setVisible(True)
        self.table_list_profiles.horizontalHeader().setCascadingSectionResizes(False)
        self.table_list_profiles.horizontalHeader().setMinimumSectionSize(0)
        self.table_list_profiles.horizontalHeader().setDefaultSectionSize(170)
        self.table_list_profiles.horizontalHeader().setHighlightSections(False)
        self.table_list_profiles.horizontalHeader().setProperty("showSortIndicator", True)
        self.table_list_profiles.horizontalHeader().setStretchLastSection(False)
        self.table_list_profiles.verticalHeader().setVisible(False)
        self.table_list_profiles.verticalHeader().setMinimumSectionSize(28)
        self.table_list_profiles.verticalHeader().setDefaultSectionSize(40)
        self.table_list_profiles.verticalHeader().setHighlightSections(False)
        self.table_list_profiles.verticalHeader().setProperty("showSortIndicator", False)
        self.table_list_profiles.verticalHeader().setStretchLastSection(False)

        self.verticalLayout_3.addWidget(self.table_list_profiles)

        self.widget = QWidget(self.tab)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(0, 0, 1211, 271))
        self.widget_2 = QWidget(self.widget)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setGeometry(QRect(0, 0, 731, 261))
        self.widget_2.setAutoFillBackground(True)
        self.table_list_auto = QTableWidget(self.widget_2)
        if (self.table_list_auto.columnCount() < 6):
            self.table_list_auto.setColumnCount(6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.table_list_auto.setHorizontalHeaderItem(0, __qtablewidgetitem7)
        font3 = QFont()
        font3.setFamilies([u"Arial"])
        font3.setBold(True)
        __qtablewidgetitem8 = QTableWidgetItem()
        __qtablewidgetitem8.setFont(font3);
        self.table_list_auto.setHorizontalHeaderItem(1, __qtablewidgetitem8)
        font4 = QFont()
        font4.setFamilies([u"Arial"])
        font4.setPointSize(8)
        font4.setBold(True)
        __qtablewidgetitem9 = QTableWidgetItem()
        __qtablewidgetitem9.setFont(font4);
        self.table_list_auto.setHorizontalHeaderItem(2, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        __qtablewidgetitem10.setFont(font3);
        self.table_list_auto.setHorizontalHeaderItem(3, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        __qtablewidgetitem11.setFont(font3);
        self.table_list_auto.setHorizontalHeaderItem(4, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        __qtablewidgetitem12.setFont(font4);
        self.table_list_auto.setHorizontalHeaderItem(5, __qtablewidgetitem12)
        self.table_list_auto.setObjectName(u"table_list_auto")
        self.table_list_auto.setGeometry(QRect(9, 39, 711, 221))
        self.table_list_auto.setMinimumSize(QSize(0, 0))
        self.table_list_auto.setMaximumSize(QSize(1230, 16777215))
        self.table_list_auto.viewport().setProperty("cursor", QCursor(Qt.CursorShape.ArrowCursor))
        self.table_list_auto.setFocusPolicy(Qt.StrongFocus)
        self.table_list_auto.setAutoFillBackground(True)
        self.table_list_auto.setStyleSheet(u"#QHeaderView::section {\n"
"	border-bottom: 1px solid #D8D8D8;\n"
"}\n"
" ")
        self.table_list_auto.setInputMethodHints(Qt.ImhNone)
        self.table_list_auto.setLineWidth(1)
        self.table_list_auto.setMidLineWidth(0)
        self.table_list_auto.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_list_auto.setProperty("showDropIndicator", False)
        self.table_list_auto.setDragDropOverwriteMode(False)
        self.table_list_auto.setAlternatingRowColors(True)
        self.table_list_auto.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_list_auto.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_list_auto.setShowGrid(True)
        self.table_list_auto.setGridStyle(Qt.SolidLine)
        self.table_list_auto.setSortingEnabled(True)
        self.table_list_auto.setWordWrap(False)
        self.table_list_auto.setCornerButtonEnabled(False)
        self.table_list_auto.horizontalHeader().setVisible(True)
        self.table_list_auto.horizontalHeader().setCascadingSectionResizes(False)
        self.table_list_auto.horizontalHeader().setMinimumSectionSize(0)
        self.table_list_auto.horizontalHeader().setDefaultSectionSize(170)
        self.table_list_auto.horizontalHeader().setHighlightSections(False)
        self.table_list_auto.horizontalHeader().setProperty("showSortIndicator", True)
        self.table_list_auto.horizontalHeader().setStretchLastSection(False)
        self.table_list_auto.verticalHeader().setVisible(False)
        self.table_list_auto.verticalHeader().setMinimumSectionSize(28)
        self.table_list_auto.verticalHeader().setDefaultSectionSize(40)
        self.table_list_auto.verticalHeader().setHighlightSections(False)
        self.table_list_auto.verticalHeader().setProperty("showSortIndicator", False)
        self.table_list_auto.verticalHeader().setStretchLastSection(False)
        self.label = QLabel(self.widget_2)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 12, 91, 16))
        self.widget_8 = QWidget(self.widget_2)
        self.widget_8.setObjectName(u"widget_8")
        self.widget_8.setGeometry(QRect(390, 4, 335, 31))
        self.horizontalLayout_4 = QHBoxLayout(self.widget_8)
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.btn_reload_auto = QPushButton(self.widget_8)
        self.btn_reload_auto.setObjectName(u"btn_reload_auto")
        self.btn_reload_auto.setMinimumSize(QSize(65, 25))
        self.btn_reload_auto.setMaximumSize(QSize(65, 25))
        self.btn_reload_auto.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_4.addWidget(self.btn_reload_auto)

        self.in_search_auto = QLineEdit(self.widget_8)
        self.in_search_auto.setObjectName(u"in_search_auto")
        self.in_search_auto.setEnabled(True)
        self.in_search_auto.setMinimumSize(QSize(0, 25))
        self.in_search_auto.setMaximumSize(QSize(140, 16777215))
        self.in_search_auto.setFont(font1)

        self.horizontalLayout_4.addWidget(self.in_search_auto)

        self.btn_select_all_auto = QPushButton(self.widget_8)
        self.btn_select_all_auto.setObjectName(u"btn_select_all_auto")
        self.btn_select_all_auto.setMinimumSize(QSize(100, 25))
        self.btn_select_all_auto.setMaximumSize(QSize(100, 25))
        self.btn_select_all_auto.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_4.addWidget(self.btn_select_all_auto)

        self.widget_4 = QWidget(self.widget)
        self.widget_4.setObjectName(u"widget_4")
        self.widget_4.setGeometry(QRect(730, 0, 481, 271))
        self.widget_4.setAutoFillBackground(True)
        self.widget_5 = QWidget(self.widget_4)
        self.widget_5.setObjectName(u"widget_5")
        self.widget_5.setGeometry(QRect(40, 150, 301, 53))
        self.horizontalLayout_2 = QHBoxLayout(self.widget_5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.in_date_time_run = QDateTimeEdit(self.widget_5)
        self.in_date_time_run.setObjectName(u"in_date_time_run")
        self.in_date_time_run.setMinimumSize(QSize(150, 25))
        self.in_date_time_run.setButtonSymbols(QAbstractSpinBox.NoButtons)

        self.horizontalLayout_2.addWidget(self.in_date_time_run)

        self.in_max_threads = QLineEdit(self.widget_5)
        self.in_max_threads.setObjectName(u"in_max_threads")
        self.in_max_threads.setMinimumSize(QSize(0, 25))

        self.horizontalLayout_2.addWidget(self.in_max_threads)

        self.lb_lien_he_ho_tro_2 = QLabel(self.widget_4)
        self.lb_lien_he_ho_tro_2.setObjectName(u"lb_lien_he_ho_tro_2")
        self.lb_lien_he_ho_tro_2.setGeometry(QRect(120, 50, 271, 41))
        font5 = QFont()
        font5.setPointSize(20)
        font5.setBold(True)
        self.lb_lien_he_ho_tro_2.setFont(font5)
        self.widget_7 = QWidget(self.widget_4)
        self.widget_7.setObjectName(u"widget_7")
        self.widget_7.setGeometry(QRect(40, 200, 301, 53))
        self.horizontalLayout_3 = QHBoxLayout(self.widget_7)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.btn_run_auto = QPushButton(self.widget_7)
        self.btn_run_auto.setObjectName(u"btn_run_auto")
        self.btn_run_auto.setMinimumSize(QSize(80, 35))
        self.btn_run_auto.setMaximumSize(QSize(50, 40))
        self.btn_run_auto.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_3.addWidget(self.btn_run_auto)

        self.btn_stop_auto = QPushButton(self.widget_7)
        self.btn_stop_auto.setObjectName(u"btn_stop_auto")
        self.btn_stop_auto.setMinimumSize(QSize(80, 35))
        self.btn_stop_auto.setMaximumSize(QSize(50, 40))
        self.btn_stop_auto.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_3.addWidget(self.btn_stop_auto)

        self.btn_file_data_out = QPushButton(self.widget_7)
        self.btn_file_data_out.setObjectName(u"btn_file_data_out")
        self.btn_file_data_out.setMinimumSize(QSize(110, 30))
        self.btn_file_data_out.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_3.addWidget(self.btn_file_data_out)

        self.widget_3 = QWidget(self.widget_4)
        self.widget_3.setObjectName(u"widget_3")
        self.widget_3.setGeometry(QRect(340, 150, 151, 62))
        self.verticalLayout_2 = QVBoxLayout(self.widget_3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.cb_export_query_id = QCheckBox(self.widget_3)
        self.cb_export_query_id.setObjectName(u"cb_export_query_id")
        self.cb_export_query_id.setChecked(True)

        self.verticalLayout_2.addWidget(self.cb_export_query_id)

        self.cb_hidden_browser = QCheckBox(self.widget_3)
        self.cb_hidden_browser.setObjectName(u"cb_hidden_browser")
        self.cb_hidden_browser.setChecked(False)

        self.verticalLayout_2.addWidget(self.cb_hidden_browser)

        self.lb_lien_he_ho_tro = QLabel(self.widget)
        self.lb_lien_he_ho_tro.setObjectName(u"lb_lien_he_ho_tro")
        self.lb_lien_he_ho_tro.setGeometry(QRect(1100, 0, 111, 20))
        font6 = QFont()
        font6.setBold(True)
        self.lb_lien_he_ho_tro.setFont(font6)
        self.lb_lien_he_ho_tro.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.tab_2.setAutoFillBackground(True)
        self.widget_68 = QWidget(self.tab_2)
        self.widget_68.setObjectName(u"widget_68")
        self.widget_68.setGeometry(QRect(0, 0, 501, 201))
        self.widget_68.setAutoFillBackground(True)
        self.label_50 = QLabel(self.widget_68)
        self.label_50.setObjectName(u"label_50")
        self.label_50.setGeometry(QRect(20, 10, 131, 16))
        self.widget_69 = QWidget(self.widget_68)
        self.widget_69.setObjectName(u"widget_69")
        self.widget_69.setGeometry(QRect(10, 73, 481, 41))
        self.horizontalLayout_56 = QHBoxLayout(self.widget_69)
        self.horizontalLayout_56.setObjectName(u"horizontalLayout_56")
        self.label_51 = QLabel(self.widget_69)
        self.label_51.setObjectName(u"label_51")
        self.label_51.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_56.addWidget(self.label_51)

        self.in_mail_generated = QLineEdit(self.widget_69)
        self.in_mail_generated.setObjectName(u"in_mail_generated")
        self.in_mail_generated.setMinimumSize(QSize(0, 25))

        self.horizontalLayout_56.addWidget(self.in_mail_generated)

        self.cbb_in_host_mail = QComboBox(self.widget_69)
        self.cbb_in_host_mail.addItem("")
        self.cbb_in_host_mail.addItem("")
        self.cbb_in_host_mail.addItem("")
        self.cbb_in_host_mail.addItem("")
        self.cbb_in_host_mail.addItem("")
        self.cbb_in_host_mail.addItem("")
        self.cbb_in_host_mail.addItem("")
        self.cbb_in_host_mail.setObjectName(u"cbb_in_host_mail")
        self.cbb_in_host_mail.setMinimumSize(QSize(120, 25))
        self.cbb_in_host_mail.setMaximumSize(QSize(120, 16777215))
        self.cbb_in_host_mail.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_56.addWidget(self.cbb_in_host_mail)

        self.label_57 = QLabel(self.widget_69)
        self.label_57.setObjectName(u"label_57")

        self.horizontalLayout_56.addWidget(self.label_57)

        self.in_length_mail = QLineEdit(self.widget_69)
        self.in_length_mail.setObjectName(u"in_length_mail")
        self.in_length_mail.setMinimumSize(QSize(40, 25))
        self.in_length_mail.setMaximumSize(QSize(40, 16777215))
        self.in_length_mail.setMaxLength(2)

        self.horizontalLayout_56.addWidget(self.in_length_mail)

        self.btn_generate_mail = QPushButton(self.widget_69)
        self.btn_generate_mail.setObjectName(u"btn_generate_mail")
        self.btn_generate_mail.setMinimumSize(QSize(0, 25))
        self.btn_generate_mail.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_56.addWidget(self.btn_generate_mail)

        self.widget_70 = QWidget(self.widget_68)
        self.widget_70.setObjectName(u"widget_70")
        self.widget_70.setGeometry(QRect(10, 117, 481, 41))
        self.horizontalLayout_57 = QHBoxLayout(self.widget_70)
        self.horizontalLayout_57.setObjectName(u"horizontalLayout_57")
        self.label_52 = QLabel(self.widget_70)
        self.label_52.setObjectName(u"label_52")
        self.label_52.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_57.addWidget(self.label_52)

        self.in_pass_generated = QLineEdit(self.widget_70)
        self.in_pass_generated.setObjectName(u"in_pass_generated")
        self.in_pass_generated.setMinimumSize(QSize(0, 25))
        self.in_pass_generated.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_57.addWidget(self.in_pass_generated)

        self.label_58 = QLabel(self.widget_70)
        self.label_58.setObjectName(u"label_58")

        self.horizontalLayout_57.addWidget(self.label_58)

        self.in_length_password = QLineEdit(self.widget_70)
        self.in_length_password.setObjectName(u"in_length_password")
        self.in_length_password.setMinimumSize(QSize(40, 25))
        self.in_length_password.setMaximumSize(QSize(40, 16777215))
        self.in_length_password.setMaxLength(2)

        self.horizontalLayout_57.addWidget(self.in_length_password)

        self.cb_has_symbols = QCheckBox(self.widget_70)
        self.cb_has_symbols.setObjectName(u"cb_has_symbols")
        self.cb_has_symbols.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_57.addWidget(self.cb_has_symbols)

        self.btn_generate_pass = QPushButton(self.widget_70)
        self.btn_generate_pass.setObjectName(u"btn_generate_pass")
        self.btn_generate_pass.setMinimumSize(QSize(0, 25))
        self.btn_generate_pass.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_57.addWidget(self.btn_generate_pass)

        self.widget_77 = QWidget(self.widget_68)
        self.widget_77.setObjectName(u"widget_77")
        self.widget_77.setGeometry(QRect(10, 30, 481, 41))
        self.horizontalLayout_64 = QHBoxLayout(self.widget_77)
        self.horizontalLayout_64.setObjectName(u"horizontalLayout_64")
        self.label_64 = QLabel(self.widget_77)
        self.label_64.setObjectName(u"label_64")
        self.label_64.setMinimumSize(QSize(50, 0))
        self.label_64.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_64.addWidget(self.label_64)

        self.in_name_generated = QLineEdit(self.widget_77)
        self.in_name_generated.setObjectName(u"in_name_generated")
        self.in_name_generated.setMinimumSize(QSize(0, 25))
        self.in_name_generated.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_64.addWidget(self.in_name_generated)

        self.btn_generate_name = QPushButton(self.widget_77)
        self.btn_generate_name.setObjectName(u"btn_generate_name")
        self.btn_generate_name.setMinimumSize(QSize(0, 25))
        self.btn_generate_name.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_64.addWidget(self.btn_generate_name)

        self.widget_78 = QWidget(self.widget_68)
        self.widget_78.setObjectName(u"widget_78")
        self.widget_78.setGeometry(QRect(160, 0, 141, 38))
        self.horizontalLayout_65 = QHBoxLayout(self.widget_78)
        self.horizontalLayout_65.setObjectName(u"horizontalLayout_65")
        self.label_65 = QLabel(self.widget_78)
        self.label_65.setObjectName(u"label_65")

        self.horizontalLayout_65.addWidget(self.label_65)

        self.cbb_in_generate_country = QComboBox(self.widget_78)
        self.cbb_in_generate_country.addItem("")
        self.cbb_in_generate_country.addItem("")
        self.cbb_in_generate_country.addItem("")
        self.cbb_in_generate_country.addItem("")
        self.cbb_in_generate_country.addItem("")
        self.cbb_in_generate_country.addItem("")
        self.cbb_in_generate_country.setObjectName(u"cbb_in_generate_country")
        self.cbb_in_generate_country.setMinimumSize(QSize(80, 25))
        self.cbb_in_generate_country.setMaximumSize(QSize(80, 16777215))
        self.cbb_in_generate_country.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_65.addWidget(self.cbb_in_generate_country)

        self.widget_79 = QWidget(self.widget_68)
        self.widget_79.setObjectName(u"widget_79")
        self.widget_79.setGeometry(QRect(10, 160, 481, 41))
        self.horizontalLayout_66 = QHBoxLayout(self.widget_79)
        self.horizontalLayout_66.setObjectName(u"horizontalLayout_66")
        self.label_66 = QLabel(self.widget_79)
        self.label_66.setObjectName(u"label_66")
        self.label_66.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_66.addWidget(self.label_66)

        self.in_address_generated = QLineEdit(self.widget_79)
        self.in_address_generated.setObjectName(u"in_address_generated")
        self.in_address_generated.setMinimumSize(QSize(0, 25))
        self.in_address_generated.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_66.addWidget(self.in_address_generated)

        self.btn_generate_address = QPushButton(self.widget_79)
        self.btn_generate_address.setObjectName(u"btn_generate_address")
        self.btn_generate_address.setMinimumSize(QSize(0, 25))
        self.btn_generate_address.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_66.addWidget(self.btn_generate_address)

        self.tabWidget.addTab(self.tab_2, "")

        self.verticalLayout.addWidget(self.tabWidget)

        MyMainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MyMainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MyMainWindow)
    # setupUi

    def retranslateUi(self, MyMainWindow):
        MyMainWindow.setWindowTitle(QCoreApplication.translate("MyMainWindow", u"NextGen Automation", None))
        self.btn_select_all_profiles.setText(QCoreApplication.translate("MyMainWindow", u"Select All", None))
        self.in_api_url.setPlaceholderText(QCoreApplication.translate("MyMainWindow", u"http://127.0.0.1:19995", None))
        self.btn_reload_profiles.setText(QCoreApplication.translate("MyMainWindow", u"Reload Profiles", None))
        self.in_search_profiles.setPlaceholderText(QCoreApplication.translate("MyMainWindow", u"Search profile name", None))
        ___qtablewidgetitem = self.table_list_profiles.horizontalHeaderItem(1)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MyMainWindow", u"Profile Name", None));
        ___qtablewidgetitem1 = self.table_list_profiles.horizontalHeaderItem(2)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MyMainWindow", u"Status", None));
        ___qtablewidgetitem2 = self.table_list_profiles.horizontalHeaderItem(3)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MyMainWindow", u"Running", None));
        ___qtablewidgetitem3 = self.table_list_profiles.horizontalHeaderItem(4)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MyMainWindow", u"Auto Last Run", None));
        ___qtablewidgetitem4 = self.table_list_profiles.horizontalHeaderItem(5)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MyMainWindow", u"Auto Next Run", None));
        ___qtablewidgetitem5 = self.table_list_profiles.horizontalHeaderItem(6)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MyMainWindow", u"DONE", None));
        ___qtablewidgetitem6 = self.table_list_auto.horizontalHeaderItem(1)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MyMainWindow", u"Name Auto", None));
        ___qtablewidgetitem7 = self.table_list_auto.horizontalHeaderItem(2)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MyMainWindow", u"File Data In", None));
        ___qtablewidgetitem8 = self.table_list_auto.horizontalHeaderItem(3)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MyMainWindow", u"Last Run", None));
        ___qtablewidgetitem9 = self.table_list_auto.horizontalHeaderItem(4)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MyMainWindow", u"Next Run", None));
        ___qtablewidgetitem10 = self.table_list_auto.horizontalHeaderItem(5)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MyMainWindow", u"Last Updated", None));
        self.label.setText(QCoreApplication.translate("MyMainWindow", u"List Bot Auto", None))
        self.btn_reload_auto.setText(QCoreApplication.translate("MyMainWindow", u"Reload", None))
        self.in_search_auto.setPlaceholderText(QCoreApplication.translate("MyMainWindow", u"Search auto name", None))
        self.btn_select_all_auto.setText(QCoreApplication.translate("MyMainWindow", u"Select All", None))
        self.in_max_threads.setPlaceholderText(QCoreApplication.translate("MyMainWindow", u"Max Threads(5)", None))
        self.lb_lien_he_ho_tro_2.setText(QCoreApplication.translate("MyMainWindow", u"NextGen Automation", None))
        self.btn_run_auto.setText(QCoreApplication.translate("MyMainWindow", u"Run Auto", None))
        self.btn_stop_auto.setText(QCoreApplication.translate("MyMainWindow", u"Stop Auto", None))
        self.btn_file_data_out.setText(QCoreApplication.translate("MyMainWindow", u"File Data Out", None))
        self.cb_export_query_id.setText(QCoreApplication.translate("MyMainWindow", u"Export QueryID", None))
        self.cb_hidden_browser.setText(QCoreApplication.translate("MyMainWindow", u"Hidden Browser", None))
        self.lb_lien_he_ho_tro.setText(QCoreApplication.translate("MyMainWindow", u"Contact Support", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MyMainWindow", u"Manager", None))
        self.label_50.setText(QCoreApplication.translate("MyMainWindow", u"Generate Data temp", None))
        self.label_51.setText(QCoreApplication.translate("MyMainWindow", u"Mail", None))
        self.cbb_in_host_mail.setItemText(0, QCoreApplication.translate("MyMainWindow", u"@hotmail.com", None))
        self.cbb_in_host_mail.setItemText(1, QCoreApplication.translate("MyMainWindow", u"@outlook.com", None))
        self.cbb_in_host_mail.setItemText(2, QCoreApplication.translate("MyMainWindow", u"@gmail.com", None))
        self.cbb_in_host_mail.setItemText(3, QCoreApplication.translate("MyMainWindow", u"@inboxbear.com", None))
        self.cbb_in_host_mail.setItemText(4, QCoreApplication.translate("MyMainWindow", u"@blondmail.com", None))
        self.cbb_in_host_mail.setItemText(5, QCoreApplication.translate("MyMainWindow", u"@guysmail.com", None))
        self.cbb_in_host_mail.setItemText(6, QCoreApplication.translate("MyMainWindow", u"Custom", None))

        self.label_57.setText(QCoreApplication.translate("MyMainWindow", u"Length", None))
        self.in_length_mail.setText(QCoreApplication.translate("MyMainWindow", u"17", None))
        self.btn_generate_mail.setText(QCoreApplication.translate("MyMainWindow", u"Generate", None))
        self.label_52.setText(QCoreApplication.translate("MyMainWindow", u"Pass", None))
        self.label_58.setText(QCoreApplication.translate("MyMainWindow", u"Length", None))
        self.in_length_password.setText(QCoreApplication.translate("MyMainWindow", u"15", None))
        self.cb_has_symbols.setText(QCoreApplication.translate("MyMainWindow", u"Symbols", None))
        self.btn_generate_pass.setText(QCoreApplication.translate("MyMainWindow", u"Generate", None))
        self.label_64.setText(QCoreApplication.translate("MyMainWindow", u"Name", None))
        self.btn_generate_name.setText(QCoreApplication.translate("MyMainWindow", u"Generate", None))
        self.label_65.setText(QCoreApplication.translate("MyMainWindow", u"Country", None))
        self.cbb_in_generate_country.setItemText(0, QCoreApplication.translate("MyMainWindow", u"US", None))
        self.cbb_in_generate_country.setItemText(1, QCoreApplication.translate("MyMainWindow", u"China", None))
        self.cbb_in_generate_country.setItemText(2, QCoreApplication.translate("MyMainWindow", u"Germany", None))
        self.cbb_in_generate_country.setItemText(3, QCoreApplication.translate("MyMainWindow", u"Korea", None))
        self.cbb_in_generate_country.setItemText(4, QCoreApplication.translate("MyMainWindow", u"Japan", None))
        self.cbb_in_generate_country.setItemText(5, QCoreApplication.translate("MyMainWindow", u"French", None))

        self.label_66.setText(QCoreApplication.translate("MyMainWindow", u"Address", None))
        self.btn_generate_address.setText(QCoreApplication.translate("MyMainWindow", u"Generate", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MyMainWindow", u"Generate Info", None))
    # retranslateUi


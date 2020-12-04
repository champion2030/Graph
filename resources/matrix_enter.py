from PyQt5.QtWidgets import QFileDialog, QMessageBox

from resources.User import User_Class
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(570, 374)
        self.verticalLayoutWidget = QtWidgets.QWidget(Form)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 561, 51))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 551, 41))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.neog_matrix_enter = QtWidgets.QTextEdit(Form)
        self.neog_matrix_enter.setGeometry(QtCore.QRect(10, 100, 551, 221))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        self.neog_matrix_enter.setFont(font)
        self.neog_matrix_enter.setObjectName("neog_matrix_enter")
        self.layoutWidget = QtWidgets.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(310, 330, 251, 41))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.save_matrix_neog = QtWidgets.QPushButton(self.layoutWidget)
        self.save_matrix_neog.setObjectName("save_matrix_neog")
        self.horizontalLayout.addWidget(self.save_matrix_neog)
        self.cancel_matrix_neog = QtWidgets.QPushButton(self.layoutWidget)
        self.cancel_matrix_neog.setObjectName("cancel_matrix_neog")
        self.horizontalLayout.addWidget(self.cancel_matrix_neog)
        self.take_file_matrix = QtWidgets.QPushButton(Form)
        self.take_file_matrix.setGeometry(QtCore.QRect(420, 70, 141, 23))
        self.take_file_matrix.setObjectName("take_file_matrix")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Матрица смежности"))
        self.label_2.setText(
            _translate("Form", "Задайте матрицу смежности. Используйте запятую пробел в качестве разделителя"))
        self.save_matrix_neog.setText(_translate("Form", "Сохранить"))
        self.cancel_matrix_neog.setText(_translate("Form", "Отмена"))
        self.take_file_matrix.setText(_translate("Form", "Считать с файла"))


class First_Widget(QtWidgets.QWidget):
    numbers = list()

    def __init__(self):
        super(First_Widget, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.show_matrix()
        self.ui.cancel_matrix_neog.clicked.connect(self.close_window)
        self.ui.save_matrix_neog.clicked.connect(self.save_matrix)
        self.ui.take_file_matrix.clicked.connect(self.read_from_file)

    def show_matrix(self):
        user = User_Class()
        matrix = np.array(user.give_matrix())
        result = ""
        for i in range(len(matrix)):
            temp = ""
            for j in range(len(matrix[i])):
                temp += str(matrix[i][j]) + " "
            if i == len(matrix) - 1:
                result += temp.strip()
            else:
                result += temp.strip() + "\n"
        self.ui.neog_matrix_enter.setText(result)

    def close_window(self):
        self.numbers.clear()
        self.hide()

    def read_from_file(self):
        file_name = QFileDialog.getOpenFileName()
        if file_name != ('', ''):
            path = file_name[0]
            temp = ""
            with open(path, "r") as file:
                line = file.readline()
                while line:
                    temp += line
                    line = file.readline()
            self.ui.neog_matrix_enter.setText(temp)

    def isSquare(self, m):
        return all(len(row) == len(m) for row in m)

    def check_ravnobok_matrix(self):
        if self.isSquare(self.numbers):
            return True
        else:
            error = QMessageBox()
            error.setWindowTitle("Matrix error")
            error.setText("Матрица должна быть квадратная!")
            error.setIcon(QMessageBox.Critical)
            error.exec_()
            return False

    def check_isNumeric_matrix(self):
        k = False
        for i in range(len(self.numbers)):
            for j in range(len(self.numbers[i])):
                if self.numbers[i][j].isnumeric():
                    if self.numbers[i][j] == '1' or self.numbers[i][j] == '0':
                        g = int(self.numbers[i][j])
                        self.numbers[i][j] = g
                        k = True
                    else:
                        error = QMessageBox()
                        error.setWindowTitle("Matrix error")
                        error.setText("В матрице могут быть только числа 0 или 1")
                        error.setIcon(QMessageBox.Critical)
                        error.exec_()
                        return False
                else:
                    error = QMessageBox()
                    error.setWindowTitle("Matrix error")
                    error.setText("В матрице должны быть только числа")
                    error.setIcon(QMessageBox.Critical)
                    error.exec_()
                    return False
        return k

    def check_main_diagonal(self):
        d = [self.numbers[i][i] for i in range(len(self.numbers))]
        count_zero = np.count_nonzero(d)
        if count_zero == 0:
            return True
        else:
            error = QMessageBox()
            error.setWindowTitle("Matrix error")
            error.setText("В главной диагонали должны быть только нули")
            error.setIcon(QMessageBox.Critical)
            error.exec_()
            return False

    def check_symmetric(self):
        for k in range(len(self.numbers)):
            for l in range(len(self.numbers[k])):
                if self.numbers[k][l] != self.numbers[l][k]:
                    return "No"
        return "Yes"

    def check_symmetric_org(self):
        count = 0
        for k in range(len(self.numbers)):
            for l in range(len(self.numbers[k])):
                if self.numbers[k][l] == 1 and self.numbers[l][k] == 1:
                    count += 1
        if count == 0:
            return True
        else:
            error = QMessageBox()
            error.setWindowTitle("Matrix error")
            error.setText("В ориентированной матрице нет симметричных элементов")
            error.setIcon(QMessageBox.Critical)
            error.exec_()
            return False

    def save_matrix(self):
        self.numbers.clear()
        myText = self.ui.neog_matrix_enter.toPlainText()
        words = myText.split("\n")
        for line in words:
            self.numbers.append(list(line.split()))
        if self.check_ravnobok_matrix():
            if self.check_isNumeric_matrix():
                if self.check_main_diagonal():
                    if self.check_symmetric() == "Yes":
                        temp = User_Class()
                        temp.take_matrix(self.numbers)
                        temp.setIdentificator(1)
                        self.close()
                    elif self.check_symmetric_org():
                        temp = User_Class()
                        temp.take_matrix(self.numbers)
                        temp.setIdentificator(2)
                        self.close()
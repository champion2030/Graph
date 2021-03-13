import sys
import cv2
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QSizePolicy, \
    QPushButton, QGridLayout, QInputDialog, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matrix_enter import First_Widget
from User import User_Class
import os
from collections import defaultdict
from itertools import *


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.title = 'Graph'
        self.left = 200
        self.top = 200
        self.width = 1350
        self.height = 800
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        widget = QWidget(self)
        self.setCentralWidget(widget)
        vlay = QVBoxLayout(widget)
        hlay = QHBoxLayout()
        vlay.addLayout(hlay)
        self.setGeometry(self.left, self.top, self.width - 100, self.height)

        m = WidgetPlot(self)
        vlay.addWidget(m)


class WidgetPlot(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.grid = QGridLayout()
        self.canvas = PlotCanvas()
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.do_matrix = QPushButton('Задать матрицу смежности', self)
        self.do_matrix.setFixedHeight(50)

        self.draw_graph = QPushButton('Построить граф', self)
        self.draw_graph.setFixedHeight(50)

        self.add_top = QPushButton('Добавить вершину', self)
        self.add_top.setFixedHeight(50)

        self.clear_all = QPushButton('Соединить вершины', self)
        self.clear_all.setFixedHeight(50)

        self.task = QPushButton('Построить все каркасы', self)
        self.task.setFixedHeight(50)

        self.show_trees = QPushButton('Показать остовные деревья', self)
        self.show_trees.setFixedHeight(50)

        self.grid.setSpacing(20)
        self.grid.setColumnMinimumWidth(0, 200)
        self.grid.addWidget(self.do_matrix, 1, 0)
        self.grid.addWidget(self.add_top, 2, 0)
        self.grid.addWidget(self.draw_graph, 3, 0)
        self.grid.addWidget(self.task, 4, 0)
        self.grid.addWidget(self.clear_all, 5, 0)
        self.grid.addWidget(self.show_trees, 6, 0)
        self.grid.addWidget(self.toolbar, 1, 1)
        self.grid.addWidget(self.canvas, 2, 1, 6, 1)
        self.setLayout(self.grid)

        self.do_matrix.clicked.connect(self.canvas.open_matrix_enter)
        self.draw_graph.clicked.connect(self.canvas.read_graph_from_file)
        self.task.clicked.connect(self.canvas.task)
        self.add_top.clicked.connect(self.canvas.add_nodes)
        self.clear_all.clicked.connect(self.show_nodes_dialog)
        self.show_trees.clicked.connect(self.canvas.playVideo)

    def get_int(self):
        i, okPressed = QInputDialog.getInt(self, "Get integer", "Введите вершину", 0, 0,
                                           self.canvas.graph.number_of_nodes() - 1, 1)
        if okPressed:
            return i

    def show_nodes_dialog(self):
        if self.canvas.graph is None:
            error_dialog = QMessageBox()
            error_dialog.setWindowTitle("Graph error")
            error_dialog.setText("Сначала нужно задать граф")
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.exec_()
        else:
            first_node = self.get_int()
            second_node = self.get_int()
            self.canvas.link_nodes(first_node, second_node)


class PlotCanvas(FigureCanvas):
    matrix = None
    graph = None
    l = []
    changed = []

    def __init__(self):
        figure = plt.figure()
        FigureCanvas.__init__(self, figure)
        self.setParent(None)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def read_graph_from_file(self):
        self.user = User_Class()
        self.matrix = np.array(self.user.give_matrix())
        if self.user.get_identificator() == 1:
            self.graph = nx.Graph(self.matrix)
            self.plot()
        elif self.user.get_identificator() == 2:
            self.graph = nx.DiGraph(self.matrix)
            self.plot()
        else:
            error = QMessageBox()
            error.setWindowTitle("Matrix error")
            error.setText("Вы не ввели граф")
            error.setIcon(QMessageBox.Critical)
            error.exec_()

    def plot(self):
        self.figure.clear()
        nx.draw_circular(self.graph, with_labels=True, node_size=850)
        self.draw_idle()

    def add_matrix_row_column(self):
        user = User_Class()
        self.matrix = np.array(user.give_matrix())
        column_to_be_added = np.zeros(len(self.matrix), dtype=int)
        result = np.hstack((self.matrix, np.atleast_2d(column_to_be_added).T))
        row_add = column_to_be_added.transpose()
        row_add = np.append(row_add, 0)
        result = np.insert(result, [len(self.matrix)], row_add, axis=0)
        user.take_matrix(result)

    def add_nodes(self):
        user = User_Class()
        if self.graph is None:
            error_dialog = QMessageBox()
            error_dialog.setWindowTitle("Graph error")
            error_dialog.setText("Сначала нужно задать и построить граф")
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.exec_()
        elif user.get_identificator() == 1:
            self.graph = nx.Graph(np.array(user.give_matrix()))
            nodes = self.graph.number_of_nodes()
            self.add_matrix_row_column()
            self.graph.add_node(nodes)
            self.plot()
        else:
            self.graph = nx.DiGraph(np.array(user.give_matrix()))
            nodes = self.graph.number_of_nodes()
            self.add_matrix_row_column()
            self.graph.add_node(nodes)
            self.plot()

    def link_nodes(self, number1, number2):
        if number1 is not None and number2 is not None:
            user = User_Class()
            change_matrix = np.array(user.give_matrix())
            if user.get_identificator() == 1:
                change_matrix[number1][number2] = 1
                change_matrix[number2][number1] = 1
                user.take_matrix(change_matrix)
                self.graph.add_edge(number1, number2)
                self.plot()
            if user.get_identificator() == 2:
                if change_matrix[number1][number2] == 1 or change_matrix[number2][number1] == 1:
                    error_dialog = QMessageBox()
                    error_dialog.setWindowTitle("Graph error")
                    error_dialog.setText("Между этими вершинами уже есть дуга")
                    error_dialog.setIcon(QMessageBox.Critical)
                    error_dialog.exec_()
                else:
                    change_matrix[number1][number2] = 1
                    user.take_matrix(change_matrix)
                    self.graph.add_edge(number1, number2)
                    self.plot()

    def open_matrix_enter(self):
        self.second = First_Widget()
        self.second.show()

    def DFS(self, v):
        visited[v] = 1
        for i in range(len(self.matrix)):
            if self.matrix[v][i] == 1 and not visited[i]:
                self.DFS(i)

    def check_components(self):
        user = User_Class()
        self.matrix = np.array(user.give_matrix())
        global visited
        visited = [False] * len(self.matrix)
        Ans = 0
        for i in range(len(self.matrix)):
            if not visited[i]:
                Ans += 1
                self.DFS(i)
        return Ans

    def create_directory(self):
        path = os.getcwd()
        try:
            os.makedirs(path[0:2] + "/graph_photos")
            return path[0:2] + "/graph_photos"
        except OSError:
            return path[0:2] + "/graph_photos"

    def find(self, key):
        for j in range(len(self.changed[key])):
            for i in range(len(self.l)):
                if self.changed[key][j][0] == self.l[i][0] or self.changed[key][j][1] == self.l[i][0] or \
                        self.changed[key][j][0] == self.l[i][1] or \
                        self.changed[key][j][1] == self.l[i][1]:
                    self.changed[key].append(self.l[i])
                    self.l.pop(i)
                    if j == len(self.changed[key]):
                        return
                    else:
                        return self.find(key)

    def clear_directory(self):
        import os, shutil
        folder = self.create_directory()
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

    def task(self):
        self.check_components()
        path = self.create_directory()
        self.clear_directory()
        someFile = open(path[0:2] + "/results.txt", "w")
        user = User_Class()
        if user.get_identificator() == 3:
            error = QMessageBox()
            error.setWindowTitle("Matrix error")
            error.setText("Сначало нунжно ввести граф")
            error.setIcon(QMessageBox.Critical)
            error.exec_()
        elif len(self.graph.edges()) == 0:
            error = QMessageBox()
            error.setWindowTitle("Matrix error")
            error.setText("В графе нет рёбер")
            error.setIcon(QMessageBox.Critical)
            error.exec_()
        elif self.check_components() != 1:
            self.figure.clear()
            k = self.graph.edges()
            self.changed = [[] for k in range(self.check_components())]
            for j in k:
                self.l.append(list(j))
            for n in range(self.check_components()):
                if len(self.l) != 0:
                    self.changed[n].append(self.l[n])
                    self.l.pop(n)
                    self.find(n)
            while [] in self.changed:
                self.changed.remove([])
            m = 0
            z = ""
            for i in range(len(self.changed)):
                for j in range(len(self.changed[i])):
                    self.changed[i][j] = tuple(self.changed[i][j])
            for i in range(len(self.changed)):
                v = 0
                m = m + 1
                tempGraph = nx.Graph()
                tempGraph.add_edges_from(self.changed[i])
                num = []
                k = []
                for i in combinations(self.changed[i], tempGraph.number_of_nodes() - 1):
                    num.append(i)
                for i in range(len(num)):
                    k.append(list(num[i]))
                for i in range(len(k)):
                    if user.get_identificator() == 1:
                        graph1 = nx.Graph()
                        graph1.add_edges_from(k[i])
                    else:
                        graph1 = nx.DiGraph()
                        graph1.add_edges_from(k[i])
                    someFile.write("На рассмотрении граф с \nвершинами - " + str(graph1.nodes()) + "\n")
                    someFile.write("рёбрами - " + str(graph1.edges()) + "\n")
                    g = Graph(graph1.number_of_nodes())
                    for j in range(len(k[i])):
                        g.addEdge(k[i][j][0], k[i][j][1])
                    if len(graph1.edges()) == graph1.number_of_nodes():
                        someFile.write("Количество рёбер меньше или равно количеству вершин - не остов\n\n")
                        pass
                    elif g.isCyclic():
                        someFile.write("Есть цикл - не остов\n\n")
                        pass
                    elif graph1.number_of_nodes() < tempGraph.number_of_nodes():
                        pass
                    else:
                        someFile.write("Граф: \n")
                        someFile.write("Вершины - " + str(graph1.nodes()) + "\n")
                        someFile.write("Рёбра - " + str(graph1.edges()) + "\n")
                        someFile.write("ОСТОВ\n\n")
                        v += 1
                        nx.draw_circular(graph1, with_labels=True, node_size=850)
                        plt.savefig(path + '/Graph' + str(v) + '.jpg')
                        self.figure.clear()
                z = z + " \n" + "Подграф " + str(m) + " имеет: " + str(v) + " остовов"
            someFile.close()
            self.plot()
            self.create_video()
            error = QMessageBox()
            error.setWindowTitle("Trees information")
            error.setText("Все остовные деревья построены и лежат в " + path + "\n" + z)
            error.setIcon(QMessageBox.Information)
            error.exec_()
        else:
            self.figure.clear()
            num = list()
            k = []
            if user.get_identificator() == 1:
                l = self.graph.edges()
                for i in combinations(l, self.graph.number_of_nodes() - 1):
                    num.append(i)
                for i in range(len(num)):
                    k.append(list(num[i]))
                v = 0
                for i in range(len(k)):
                    graph1 = nx.Graph()
                    graph1.add_edges_from(k[i])
                    someFile.write("На рассмотрении граф с \nвершинами - " + str(graph1.nodes()) + "\n")
                    someFile.write("рёбрами - " + str(graph1.edges()) + "\n")
                    g = Graph(graph1.number_of_nodes())
                    for j in range(len(k[i])):
                        g.addEdge(k[i][j][0], k[i][j][1])
                    if len(graph1.edges()) == graph1.number_of_nodes():
                        someFile.write("Количество рёбер меньше или равно количеству вершин - не остов\n\n")
                        pass
                    elif g.isCyclic():
                        someFile.write("Есть цикл - не остов\n\n")
                        pass
                    elif graph1.number_of_nodes() < self.graph.number_of_nodes():
                        pass
                    else:
                        someFile.write("Граф: \n")
                        someFile.write("Вершины - " + str(graph1.nodes()) + "\n")
                        someFile.write("Рёбра - " + str(graph1.edges()) + "\n")
                        someFile.write("ОСТОВ\n\n")
                        v += 1
                        nx.draw_circular(graph1, with_labels=True, node_size=850)
                        plt.savefig(path + '/Graph' + str(v) + '.jpg')
                        self.figure.clear()
                someFile.close()
                self.plot()
                self.create_video()
                error = QMessageBox()
                error.setWindowTitle("Trees information")
                error.setText("Все остовные деревья построены и лежат в " + path + "\nКол-во остовов: " + str(v))
                error.setIcon(QMessageBox.Information)
                error.exec_()
            else:
                l = self.graph.in_edges()
                for i in combinations(l, self.graph.number_of_nodes() - 1):
                    num.append(i)
                for i in range(len(num)):
                    k.append(list(num[i]))
                v = 0
                for i in range(len(k)):
                    graph1 = nx.DiGraph()
                    graph1.add_edges_from(k[i])
                    someFile.write("На рассмотрении граф с \nвершинами - " + str(graph1.nodes()) + "\n")
                    someFile.write("рёбрами - " + str(graph1.edges()) + "\n")
                    g = Graph(graph1.number_of_nodes())
                    for j in range(len(k[i])):
                        g.addEdge(k[i][j][0], k[i][j][1])
                    if len(graph1.edges()) == graph1.number_of_nodes():
                        someFile.write("Количество рёбер меньше или равно количеству вершин - не остов\n\n")
                        pass
                    elif g.isCyclic():
                        someFile.write("Есть цикл - не остов\n\n")
                        pass
                    elif graph1.number_of_nodes() < self.graph.number_of_nodes():
                        pass
                    else:
                        someFile.write("Граф: \n")
                        someFile.write("Вершины - " + str(graph1.nodes()) + "\n")
                        someFile.write("Рёбра - " + str(graph1.edges()) + "\n")
                        someFile.write("ОСТОВ\n\n")
                        v += 1
                        nx.draw_circular(graph1, with_labels=True, node_size=850)
                        plt.savefig(path + '/Graph' + str(v) + '.jpg')
                        self.figure.clear()
                someFile.close()
                self.plot()
                self.create_video()
                error = QMessageBox()
                error.setWindowTitle("Trees information")
                error.setText("Все остовные деревья построены и лежат в " + path + "\nКол-во остовов: " + str(v))
                error.setIcon(QMessageBox.Information)
                error.exec_()


    def create_video(self):
        image_folder = self.create_directory()
        video_name = image_folder + '/video.avi'
        images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
        frame = cv2.imread(os.path.join(image_folder, images[0]))
        height, width, layers = frame.shape

        video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 1.0, (width, height))

        for image in images:
            video.write(cv2.imread(os.path.join(image_folder, image)))

        cv2.destroyAllWindows()
        video.release()

    def playVideo(self):
        if os.path.isfile(self.create_directory() + "\\video.avi"):
            os.startfile(self.create_directory() + "\\video.avi")
        else:
            error = QMessageBox()
            error.setWindowTitle("Video error")
            error.setText("Вы ещё не построили деревьев")
            error.setIcon(QMessageBox.Information)
            error.exec_()

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = defaultdict(list)

    def addEdge(self, v, w):
        self.graph[v].append(w)
        self.graph[w].append(v)

    def isCyclicUtil(self, v, visited, parent):
        visited[v] = True
        for i in self.graph[v]:
            if i > len(visited) - 1:
                return False
            if visited[i] == False:
                if (self.isCyclicUtil(i, visited, v)):
                    return True
            elif parent != i:
                return True
        return False

    def isCyclic(self):
        visited = [False] * (self.V)
        for i in range(self.V):
            if visited[i] == False:
                if (self.isCyclicUtil(i, visited, -1)) == True:
                    return True
        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

# PyQt6 is the only library you need
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *
from PyQt6.QtTest import QTest

# the RGBA of each color that will be used
RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)
DARK_GREEN = (0, 100, 0, 255)
BLUE = (0, 0, 255, 255)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

wait = 100  # this variable is global so both `Grid` and `MainWindow` can access it
            # see pause() below to see the use of the `wait` variable


def pause():
    """Pauses the program for `wait` milliseconds."""
    QTest.qWait(wait)


class Grid(QTableWidget):
    """This class will represent my actual grid.
    It has three types of cells: The starting cell, the ending cell, and obstacle cells.
    Internally, it is represented as a QTableWidget, or a table of cells.
    """

    # fields:
    # - self.n: number of rows
    # - self.m: number of columns
    # - self.ran: did the bfs function run without being cleared?
    # - self.stop: a flag that is set by MainWindow to stop self.bfs()
    #   (used when the user presses the "stop" button when running)
    # - self.start: the starting cell's location
    # - self.end: the ending cell's location
    def __init__(self, n, m):
        super().__init__()
        self.n = n
        self.m = m
        self.reset()
        self.stop = False  # should I stop?

        # create the actual board
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # block editing the table

        # no need to show horizontal nor vertical headers
        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        # stretch to fit into window
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # remove all highlights when a cell is clicked
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

    def reset(self):
        self.resize_(self.n, self.m)

    def resize_(self, n, m):
        # resize
        self.n = n
        self.m = m
        self.setRowCount(self.n)
        self.setColumnCount(self.m)

        # clear the board
        for i in range(self.n):
            for j in range(self.m):
                self.setItem(i, j, QTableWidgetItem())  # create the cell
                self.item(i, j).setBackground(QtGui.QColor(*WHITE))  # set the colour
        self.ran = False  # it doesn't matter whether we've run the code or not,
                          # as long as we've cleared the board, self.ran is false.

        self.start = (0, 0)  # start cell
        self.item(0, 0).setBackground(QtGui.QColor(*GREEN))  # set cell (0, 0) to green
        self.end = (self.n - 1, self.m - 1)  # ending cell
        self.item(self.n - 1, self.m - 1).setBackground(QtGui.QColor(*RED))  # set cell (n-1, m-1) to red

    def color(self, r, c):
        # return the color of the cell (r, c)
        return self.item(r, c).background().color().getRgb()

    def bfs(self) -> bool:  # returns whether a path was found
        """Perform a breadth-first search (BFS) from the starting cell.
        The program stops only when all reachable cells have been considered,
        or when the ending cell has been reached. If the ending cell is
        reached, it traces the shortest path from the starting to the ending
        cell.
        All visited cells (including the starting cell) will have an integer
        written on it, specifying the distance from the starting cell."""

        # prev is a 2D array where prev[r][c] is the previous cell
        # on the path from the starting cell to cell (r, c).
        # prev is needed to retrace the previous path.
        # Also, we will maintain that a cell (r, c)
        # is visited iff prev[r][c] != (-1, -1)
        prev = []
        for _ in range(self.n):
            prev.append([])
            for _ in range(self.m):
                prev[-1].append((-1, -1))
        prev[self.start[0]][self.start[1]] = self.start

        q = [(*self.start, 0)]
        self.item(*self.start).setText("0")
        cur = 0
        # Usually, we would have the variable q as a queue,
        # but there is no direct queue implementation in Python,
        # so we use a list with `cur` as the index of the first
        # element in the queue.
        # Obviously, we could just remove the first element in q,
        # but that's wayyy too slow in a list.
        # "But what if q takes up too much memory?"
        # The size of q is at most self.n * self.m.
        # We already have a table with self.n * self.m cells.
        # The memory complexity is thus O(self.n * self.m).
        # If we can store the table, then we can also store q.
        # (search up big-O notation to understand)
        while cur < len(q):
            r, c, dis = q[cur]
            cur += 1  # "popping" the queue

            # dr, dc are the difference in row and column, respectively.
            # This is used to search all neighbors of cell (r, c).
            for (dr, dc) in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                # the flag self.stop stops this function immediately.
                if self.stop:
                    self.stop = False
                    return False  # no path found

                # cell (r2, c2) is a neighbor of (r, c)
                r2, c2 = r + dr, c + dc

                # we cannot go to a cell out of bounds
                # or into a visited cell
                # or into an obstacle
                if r2 < 0 or r2 >= self.n or c2 < 0 or c2 >= self.m \
                        or prev[r2][c2] != (-1, -1) \
                        or self.color(r2, c2) == BLACK:
                    continue

                prev[r2][c2] = (r, c)
                self.item(r2, c2).setText(str(dis + 1))
                if (r2, c2) == self.end:
                    # found the path!
                    # we will now trace the path back to the start.
                    # we will color the shortest path DARK_GREEN
                    r2, c2 = prev[r2][c2]  # don't want to color the ending cell
                    while (r2, c2) != self.start:  # while we're not at the starting cell
                        # set color to dark green
                        self.item(r2, c2).setBackground(QtGui.QColor(*DARK_GREEN))
                        # go to the previous cell in the shortest path
                        r2, c2 = prev[r2][c2]
                    return True
                q.append((r2, c2, dis + 1))
                self.item(r2, c2).setBackground(QtGui.QColor(*BLUE))  # visited is blue
                pause()
        return False  # no path found


class MainWindow(QWidget):
    """The main window that will contain the control panel of buttons
    and input boxes, and the grid to visual breadth-first search."""

    # fields:
    # - n: number of rows
    # - m: number of columns
    # - grid: the grid of which we will visualize BFS
    # - state: the state of the grid
    #   (0 = unrun, 1 = running, 2 = ran BUT not cleared)
    # - reset_button: the button for restoring the board back to
    #   its default state
    # - cell_type: the "mode" when clicking a cell in the grid
    # - delay: a slider determining how "slow" the visualization is
    # - speed_indicator: a label showing the current value in self.delay
    # - multi_button: a button that changes text and purpose.
    #   When self.state == 0, multi_button is "Run" (runs the BFS).
    #   When self.state == 1, multi_button is "Stop" (stops the BFS).
    #   When self.state == 2, multi_button is "Clear" (clears the board).
    # - rows: an input box specifying the number of rows in the grid
    # - cols: an input box specifying the number of columns in the grid
    # - resize_button: resizes the grid based on self.rows and self.cols
    def __init__(self, window_title: str, n: int, m: int):
        super().__init__()
        self.setWindowTitle(window_title)
        self.n = n
        self.m = m
        self.state = 0  # 0 = unrun, 1 = running, 2 = ran (but not cleared)

        # top bar of buttons and other widgets
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_clicked)
        self.cell_type = QComboBox()
        self.cell_type.addItems(("Start", "Wall", "End"))
        self.cell_type.setCurrentIndex(1)

        self.delay = QSlider(Qt.Orientation.Horizontal)
        self.delay.setRange(50, 500)  # set the left and right endpoints to be 50 & 500
        # self.delay.setSingleStep(50)   didn't want to include these lines cuz I want to give
        # self.delay.setTickInterval(50) the user more freedom to choose the delay
        self.delay.setValue(wait)  # default value
        self.delay.valueChanged.connect(self.delay_changed)
        self.speed_indicator = QLabel(f'Delay: {wait}')
        self.multi_button = QPushButton("Run")
        self.multi_button.clicked.connect(self.multi_button_clicked)

        self.rows = QSpinBox()
        self.rows.setValue(n)
        self.rows.setMinimum(2)
        self.rows.setMaximum(50)
        self.cols = QSpinBox()
        self.cols.setValue(m)
        self.cols.setMinimum(2)
        self.cols.setMaximum(50)
        self.resize_button = QPushButton("Resize")
        self.resize_button.clicked.connect(self.resize_clicked)

        top = QHBoxLayout()  # top layout
        top.addWidget(self.reset_button)
        top.addWidget(self.cell_type)
        top.addWidget(self.multi_button)
        top.addWidget(self.delay)
        top.addWidget(self.speed_indicator)
        top.addWidget(self.rows)
        top.addWidget(QLabel("rows by"))
        top.addWidget(self.cols)
        top.addWidget(QLabel("columns"))
        top.addWidget(self.resize_button)

        # the grid
        self.grid = Grid(n, m)
        self.grid.clicked.connect(self.cell_clicked)

        ent = QVBoxLayout()  # entire layout
        ent.addLayout(top)
        ent.addWidget(self.grid)
        self.setLayout(ent)

    def delay_changed(self):
        global wait  # don't want to create a local variable
        wait = self.delay.value()
        self.speed_indicator.setText(f'Delay: {wait}')

    def reset_clicked(self):
        if QMessageBox.question(self, "Confirmation", "Do you want to reset?") \
                == QMessageBox.StandardButton.No:
            return
        self.grid.resize_(self.n, self.m)
        self.multi_button.setText('Run')
        self.state = 0

    def resize_clicked(self):
        if QMessageBox.question(self, "Confirmation", "If you resize, the board will be reset.") \
                == QMessageBox.StandardButton.No:
            return
        self.n = self.rows.value()
        self.m = self.cols.value()
        self.grid.resize_(self.n, self.m)
        self.multi_button.setText('Run')
        self.state = 0

    def cell_clicked(self, cell):
        if self.state != 0:
            return  # need to clear first!

        r, c = cell.row(), cell.column()  # row, column of the clicked cell
        if self.cell_type.currentIndex() == 0:  # starting cell mode
            if self.grid.color(r, c) == WHITE:
                # relocate the starting cell
                self.grid.item(*self.grid.start).setBackground(QtGui.QColor(*WHITE))
                self.grid.start = (r, c)
                self.grid.item(*self.grid.start).setBackground(QtGui.QColor(*GREEN))
        elif self.cell_type.currentIndex() == 1:  # wall mode
            # toggle wall cell
            if self.grid.color(r, c) == WHITE:
                self.grid.item(r, c).setBackground(QtGui.QColor(*BLACK))
            elif self.grid.color(r, c) == BLACK:
                self.grid.item(r, c).setBackground(QtGui.QColor(*WHITE))
        else:  # ending cell mode
            if self.grid.color(r, c) == WHITE:
                # move the ending cell
                self.grid.item(*self.grid.end).setBackground(QtGui.QColor(*WHITE))
                self.grid.end = (r, c)
                self.grid.item(*self.grid.end).setBackground(QtGui.QColor(*RED))

    def multi_button_clicked(self):
        if self.state == 2:
            # the text on self.run should be "clear"
            # set all dark green and blue cells back to white
            for i in range(self.grid.n):
                for j in range(self.grid.m):
                    if self.grid.color(i, j) in (DARK_GREEN, BLUE):
                        # clear cell (i, j) to white
                        self.grid.setItem(i, j, QTableWidgetItem())
                        self.grid.item(i, j).setBackground(QtGui.QColor(*WHITE))
                    # no matter what, the cell should not have any text in it
                    self.grid.item(i, j).setText('')
            self.multi_button.setText("Run")
            self.state = 0
        elif self.state == 0:
            # the text on self.run should be "run"
            self.state = 1
            self.multi_button.setText("Stop")
            # don't want the user to resize/reset the grid while running!
            self.resize_button.setDisabled(True)
            self.reset_button.setDisabled(True)
            if self.grid.bfs():  # successfully found a path
                QMessageBox.information(self, "Success", "Shortest path found (dark green).")
            else:  # successfully failed lol
                QMessageBox.information(self, "Fail", "No path found.")
            self.multi_button.setText("Clear")
            self.state = 2
            # re-enable
            self.resize_button.setDisabled(False)
            self.reset_button.setDisabled(False)
        else:  # self.state == 1
            self.grid.stop = True
            self.state = 2


app = QApplication([])  # needed, but I don't know why

main_window = MainWindow("Breadth-first search on a grid visualization", 10, 10)  # default grid size is 10, 10
main_window.show()

app.exec()  # run the program!

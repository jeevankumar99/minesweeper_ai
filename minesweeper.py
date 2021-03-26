import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count
        self.mines_known = set()
        self.safes_known = set()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        temp_set = set()
        for cell in self.cells:
            if cell in self.mines_known:
                temp_set.add(cell)
        return temp_set

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        temp_set = set()
        for cell in self.cells:
            if cell in self.safes_known:
                temp_set.add(cell)
        return temp_set

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell not in self.cells:
            return
        self.cells.remove(cell)
        self.mines_known.add(cell)
        self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell not in self.cells:
            return
        self.cells.remove(cell)
        self.safes_known.add(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # current move is safe, so add it to moves_made and mark it safe
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # find out the neighbor cells around the current cell
        neighbors = neighbor_cells(cell, self.height, self.width)

        # remove neighbor cells if they are safe or mines
        remove_cells = []
        for cell in neighbors:
            if cell in self.safes:
                remove_cells.append(cell)
            elif cell in self.mines:
                remove_cells.append(cell)
                count -= 1
        for cell in remove_cells:
            neighbors.remove(cell)

        # if count is zero, then all cells are safe and exit function
        if count == 0:
            for cell in neighbors:
                self.mark_safe(cell)
            return

        # if cells is equal to count, each cell is a mine and exit function
        if len(neighbors) == count:
            for cell in neighbors:
                self.mark_mine(cell)
            return

        # add the new sentence to knowledge
        new_sentence = Sentence(neighbors, count)
        self.knowledge.append(new_sentence)

        # check if any sentence in knowledge infers cells as mines or safe
        remove_sentence = []
        mark_mines = []
        mark_safes = []
        for sentence in self.knowledge:
            if len(sentence.cells) == sentence.count:
                for cell in sentence.cells:
                    mark_mines.append(cell)
                remove_sentence.append(sentence)
                continue
            if sentence.count == 0:
                for cell in sentence.cells:
                    mark_safes.append(cell)
                remove_sentence.append(sentence)
        # remove sentences from knowledge as they are safe or mines
        for sentence in remove_sentence:
            self.knowledge.remove(sentence)
        # mark the cells mines
        for cell in mark_mines:
            self.mark_mine(cell)
        # marks the cells safes
        for cell in mark_safes:
            self.mark_safe(cell)


        # iterate through each sentence in knowlege and use intersection of sets to create new sentences.
        for sentence in self.knowledge:
            # comp_sentence is just every other sentence in knowledge used for comparing.
            for comp_sentence in self.knowledge:
                if sentence == comp_sentence:
                    continue
                # check if comparing sentence is a subset of the other
                if comp_sentence.cells.issubset(sentence.cells):
                    sentence.cells = sentence.cells.difference(comp_sentence.cells)
                    sentence.count = sentence.count - comp_sentence.count
                # check if current sentence is a subset of the other
                elif sentence.cells.issubset(comp_sentence.cells):
                    comp_sentence.cells = comp_sentence.cells.difference(sentence.cells)
                    comp_sentence.count = comp_sentence.count - sentence.count
        return

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_moves = self.safes.difference(self.moves_made)
        # no safe moves available
        if not len(safe_moves):
            return None
        else:
            for moves in safe_moves:
                return moves

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.mines and (i, j) not in self.moves_made:
                    self.moves_made.add((i, j))
                    return (i, j)
        return None

def neighbor_cells(current_cell, height, width):
    """
    Returns the {(i, j)} of all the neighboring cell_size
    """
    neighbors = set()

    for i in range(current_cell[0] - 1, current_cell[0] + 2):
        for j in range(current_cell[1] - 1, current_cell[1] + 2):
            # skip current cell
            if (i, j) == current_cell:
                continue
            # to keep index in bound
            if 0 <= i < height and 0 <= j < width:
                    neighbors.add((i, j))
    return neighbors

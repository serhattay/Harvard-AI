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

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells):
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


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
        # marking the cell as a move that has been made
        self.moves_made.add(cell)

        # mark the cell as safe
        self.mark_safe(cell)
        self.safes.add(cell)

        # add a new sentence to the AI's knowledge
        # base based on the value of 'cell' and 'count'
        adjacents = self.get_adjacent_cells(cell)
        for adjacent in set(adjacents):
            if adjacent in self.mines:
                count -= 1
                adjacents.remove(adjacent)

            elif adjacent in self.safes:
                adjacents.remove(adjacent)

        new_sentence = Sentence(adjacents, count)
        self.knowledge.append(new_sentence)

        if possible_mines := new_sentence.known_mines():
            for mine in set(possible_mines):
                if mine not in self.mines:
                    self.mines.add(mine)
                    self.mark_mine(mine)

        if possible_safes := new_sentence.known_safes():
            for safe in set(possible_safes):
                if safe not in self.safes:
                    self.safes.add(safe)
                    self.mark_safe(safe)

        # mark any additional cells as safe or as mines if it can
        # be concluded based on the AI's knowledge base
        self.process_knowledge()

        # add any new sentences to the AI's knowledge base if
        # they can be inferred from existing knowledge
        is_inferred = self.check_for_inferring()
        while is_inferred:
            self.process_knowledge()
            is_inferred = self.check_for_inferring()

    def process_knowledge(self):
        is_processed = False
        for current_sentence in self.knowledge:
            if possible_mines := current_sentence.known_mines():
                for mine in set(possible_mines):
                    if mine not in self.mines:
                        self.mines.add(mine)
                        self.mark_mine(mine)
                        is_processed = True

            if possible_safes := current_sentence.known_safes():
                for safe in set(possible_safes):
                    if safe not in self.safes:
                        self.safes.add(safe)
                        self.mark_safe(safe)
                        is_processed = True

        if is_processed:
            self.process_knowledge()

    def check_for_inferring(self):
        is_inferred = False
        for first_sentence in self.knowledge:
            for second_sentence in self.knowledge:
                if first_sentence != second_sentence and (
                        first_sentence.cells.issubset(second_sentence.cells)):
                    generated_knowledge = Sentence(second_sentence.cells - first_sentence.cells,
                                                   second_sentence.count - first_sentence.count)
                    if generated_knowledge not in self.knowledge:
                        self.knowledge.append(generated_knowledge)
                        is_inferred = True
        return is_inferred

    def get_adjacent_cells(self, cell):
        adjacent_cells = set()
        for rc in [-1, 0, 1]:
            for cc in [-1, 0, 1]:
                if rc == 0 and cc == 0:
                    continue

                new_row, new_col = cell[0] + rc, cell[1] + cc

                if 0 <= new_row < self.height and 0 <= new_col < self.width:
                    adjacent_cells.add((new_row, new_col))
        return adjacent_cells

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        if len(self.moves_made) + len(self.mines) == self.height * self.width:
            return None

        i = random.randint(0, self.height - 1)
        j = random.randint(0, self.width - 1)

        while (i, j) in self.mines | self.moves_made:
            i = random.randint(0, self.height - 1)
            j = random.randint(0, self.width - 1)

        return (i, j)

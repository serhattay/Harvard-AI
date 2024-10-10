import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains:
            for word in self.domains[variable].copy():
                if len(word) != variable.length:
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlaps = self.crossword.overlaps[x, y]
        if overlaps is None:
            return False

        letter_of_x, letter_of_y = overlaps[0], overlaps[1]

        is_revised = False

        for potential_word_x in self.domains[x].copy():
            is_okay = False
            for potential_word_y in self.domains[y]:
                if potential_word_x[letter_of_x] == potential_word_y[letter_of_y]:
                    is_okay = True
                    break

            if not is_okay:
                is_revised = True
                self.domains[x].remove(potential_word_x)

        return is_revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            queue = [(x, y) for x in self.domains for y in self.domains if x != y]
        else:
            queue = arcs

        while queue:
            current = queue.pop(0)
            is_revised = self.revise(current[0], current[1])
            if len(self.domains[current[0]]) == 0:
                return False
            if is_revised:
                neighbors = [(x, current[0]) for x in self.crossword.neighbors(current[0])]
                for neighbor in neighbors:
                    queue.append(neighbor)

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return assignment.keys() == self.domains.keys()

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        value_set = set()
        for variable in assignment:
            word = assignment[variable]
            if word not in value_set:
                value_set.add(word)
            else:
                return False

            neighbors = self.crossword.neighbors(variable)

            for neighbor in neighbors:
                if neighbor in assignment:
                    intersection_var, intersection_neighbor = self.crossword.overlaps[variable, neighbor]
                    if assignment[variable][intersection_var] != assignment[neighbor][intersection_neighbor]:
                        return False

            if len(assignment[variable]) != variable.length:
                return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        word_list = self.domains[var]
        conflict_dict = dict()

        for word in word_list:
            conflict_counter = 0
            for neighbor in self.crossword.neighbors(var):
                letter_x_index, letter_y_index = self.crossword.overlaps[var, neighbor]
                letter_x = word[letter_x_index]

                for neighbor_word in self.domains[neighbor]:
                    letter_y = neighbor_word[letter_y_index]
                    if letter_x != letter_y:
                        conflict_counter += 1

            conflict_dict[word] = conflict_counter

        return sorted(conflict_dict.keys(), key=lambda x: conflict_dict[x])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        lowest_number_of_values = float("inf")
        lowest_variable = None

        for variable in self.domains:
            if variable not in assignment:
                number_of_values = len(self.domains[variable])
                if number_of_values < lowest_number_of_values:
                    lowest_number_of_values = number_of_values
                    lowest_variable = variable

        return lowest_variable

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for val in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = val
            result = self.backtrack(new_assignment)
            if result is not None:
                return result
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

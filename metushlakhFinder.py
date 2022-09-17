import random

# list of chromosomes (the population)
POPULATION = []
# the two board we will be switching between
BOARD1 = []
BOARD2 = []
# a random initialized compact board (the starting configuration of a chromosome
RANDOM_CONFIGURATION = []
# array that saves all the fitnesses of the current generation
FITNESS_ARRAY = []
# the start and the end configuration of a successful metushlakh
START_CONF = []
END_CONF = []
# number of iteration it took a successful metushlakh to get stable
M_ITERATION = 0

# boolean vars to know which board we are using
B1 = B2 = None
# number of alive cells of the chromosome at the begining, and on its peak
START_LIVE_CELLS = MAX_LIVE_CELLS = 1

CROSSOVER_CHANCE = 0.95
MUTATION_CHANCE = 0.05

# sizes #
BOARD_SIZE = 32
START_CONF_SIZE = 8
POPULATION_SIZE = 20
# the size of generations the genetic algorithm is gonna run
GENETIC_ALG_GEN_SIZE = 20
GAME_OF_LIFE_ITERATIONS_SIZE = 100
# a min limit for iterations.
# (if the iterations exceeded it, it means the configuration has a potential to metushlakh)
ENOUGH_ITERATIONS = GAME_OF_LIFE_ITERATIONS_SIZE / 2
# a min limit for a configuration size
# (if the iterations exceeded it, it means the configuration has a potential to metushlakh)
ENOUGH_BIG = BOARD_SIZE * 2


def init_0_or_random(board, size, rand=False):
    """
    initializes a chromosome to all 0, or to random values (1 or 0) if rand is True.
    """
    for i in range(size):
        temp = [0] * size
        board.append(temp)
    if rand:
        for i in range(size):
            for j in range(size):
                board[i][j] = random.choice([0, 1])


def set_up(place):
    """
    generates a new chromosome in the population which is randomly initialized at the center (10*10)
    """
    global RANDOM_CONFIGURATION, BOARD_SIZE, START_CONF_SIZE

    # new temp board
    board = []
    # new configuration board
    RANDOM_CONFIGURATION = []
    # initializing the temp board with 0
    init_0_or_random(board, BOARD_SIZE)
    # inserting the temp board into the population in 'place'
    POPULATION.insert(place, board)

    # initializing the new configuration randomly (with 0 and 1)
    init_0_or_random(RANDOM_CONFIGURATION, START_CONF_SIZE, True)

    # calculation the center of a board
    spot = int((BOARD_SIZE / 2) - 4)

    # copying the new random configuration into the new chromosome in the population
    for i in range(spot, spot + START_CONF_SIZE):
        for j in range(spot, spot + START_CONF_SIZE):
            (POPULATION[place])[i][j] = RANDOM_CONFIGURATION[i - spot][j - spot]


def run(iterations, starting_board, print_conf=False):
    """
    runs game of life while checking if the starting chromosome is a successful metushlakh or not
    :param iterations: number of generations we want to run game of life
    :param starting_board: the starting random configuration
    :param print_conf: if we already know its a successful metushlakh and we want
    to run it for the second time to print it
    :return: if its a successful metushlakh or not
    """
    global START_LIVE_CELLS, MAX_LIVE_CELLS, B1, B2, BOARD1, BOARD2, ENOUGH_ITERATIONS, \
        ENOUGH_BIG, START_CONF, END_CONF, M_ITERATION

    # helps to know which board we are using. (BOARD1 or BOARD2)
    B1 = True
    B2 = False

    pre = []
    BOARD1 = []
    BOARD2 = []

    # initializing the three boards with 0 (the one before, the current one and the next one)
    init_0_or_random(current_board(), BOARD_SIZE)
    init_0_or_random(next_board(), BOARD_SIZE)
    init_0_or_random(pre, BOARD_SIZE)

    # initializing the boards in case we get successful metushlakh
    init_0_or_random(START_CONF, BOARD_SIZE)
    init_0_or_random(END_CONF, BOARD_SIZE)

    # the current generation in game of life
    generations = 0

    # copying to START_CONF in case this chromosome is a successful metushlakh
    copy_chromosome(starting_board, START_CONF)

    copy_chromosome(starting_board, current_board())

    # initializing to the number of alive cells in the starting chromosome
    START_LIVE_CELLS = MAX_LIVE_CELLS = count_live_cells(current_board())

    # running game of live for 'iterations' times
    while generations < iterations:

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                # if the gene is at the boarder then put 0
                if at_boarder(i, j):
                    next_board()[i][j] = 0
                # else update the gene by the rules of game of life
                else:
                    if alive(current_board(), i, j):
                        if check_neighbors(current_board(), i, j) < 2:
                            next_board()[i][j] = 0
                        elif check_neighbors(current_board(), i, j) > 3:
                            next_board()[i][j] = 0
                        else:
                            next_board()[i][j] = 1
                    else:
                        if check_neighbors(current_board(), i, j) == 3:
                            next_board()[i][j] = 1
                        else:
                            next_board()[i][j] = 0

        # if its a successful metushlakh print the stages
        if print_conf:
            print("After ", generations + 1, "iterations:")
            print_stage(next_board())

        # if stable from the get go it is not metushlakh
        if generations == 0 and compare_chromosomes(current_board(), next_board()):
            return False
        if generations == 1 and compare_chromosomes(pre, next_board()):
            return False

        # if all cells died before the iterations ended, there is no use to continue (it cant be a metushlakh)
        if is_all_zeros(current_board(), BOARD_SIZE):
            break

        # if it took it enough time to get stable and its max alive cells is bigger
        # enough than its starting alive cells then its a successful metushlakh
        if generations > ENOUGH_ITERATIONS and MAX_LIVE_CELLS - START_LIVE_CELLS > ENOUGH_BIG \
                and (compare_chromosomes(pre, current_board()) or compare_chromosomes(pre, next_board())):
            M_ITERATION = generations
            copy_chromosome(current_board(), END_CONF)
            return True

        a = count_live_cells(current_board())
        # updating the maximum live cell a configuration can get to
        if count_live_cells(current_board()) > MAX_LIVE_CELLS:
            MAX_LIVE_CELLS = count_live_cells(current_board())

        # updating the pre board
        copy_chromosome(current_board(), pre)

        # switching the two boards
        if B1:
            B1 = False
            B2 = True

        elif B2:
            B1 = True
            B2 = False

        # updating the generation
        generations += 1

    return False


def cross_over(parent1, parent2, p=0.5):
    """
    The Two-Dimensional Substring Crossover.
    """
    child1 = []
    child2 = []
    # initializing the two children
    init_0_or_random(child1, BOARD_SIZE)
    init_0_or_random(child2, BOARD_SIZE)

    spot = int((BOARD_SIZE / 2) - 4)

    # generation to random integers
    rr = random.randint(spot, spot + START_CONF_SIZE - 1)
    rc = random.randint(spot, spot + START_CONF_SIZE - 1)
    r = random.random()
    if r > 0.5:
        # performing horizontal cross over
        for row in range(spot, spot + START_CONF_SIZE):
            if row < rr:
                for col in range(spot, spot + START_CONF_SIZE):
                    child1[row][col] = parent1[row][col]
                    child2[row][col] = parent2[row][col]
            elif row == rr:
                for col in range(spot, spot + START_CONF_SIZE):
                    child1[row][col] = parent1[row][col]
                    child2[row][col] = parent2[row][col]
                for col in range(rc + 1, spot + START_CONF_SIZE):
                    child1[row][col] = parent2[row][col]
                    child2[row][col] = parent1[row][col]
            else:
                for col in range(spot, spot + START_CONF_SIZE):
                    child1[row][col] = parent2[row][col]
                    child2[row][col] = parent1[row][col]
        # performing vertical cross over
    else:
        for col in range(spot, spot + START_CONF_SIZE):
            if col < rc:
                for row in range(spot, spot + START_CONF_SIZE):
                    child1[row][col] = parent1[row][col]
                    child2[row][col] = parent2[row][col]
            elif col == rc:
                for row in range(spot, spot + START_CONF_SIZE):
                    child1[row][col] = parent1[row][col]
                    child2[row][col] = parent2[row][col]
                for row in range(rr + 1, spot + START_CONF_SIZE):
                    child1[row][col] = parent2[row][col]
                    child2[row][col] = parent1[row][col]
            else:
                for row in range(spot, spot + START_CONF_SIZE):
                    child1[row][col] = parent2[row][col]
                    child2[row][col] = parent1[row][col]
    return child1, child2


def mutate(original):
    """
    The mutation function. there is a MUTATION_CHANCE that two genes where
    their places were randomly generated will get swapped.
    """
    global MUTATION_CHANCE, BOARD_SIZE

    mutated_board = []
    # initializing the new chromosome
    init_0_or_random(mutated_board, BOARD_SIZE)

    # calculating the center of the chromosome
    spot = int((BOARD_SIZE / 2) - 4)

    # copying the original chromosome to the muted chromosome as it is
    copy_chromosome(original, mutated_board)

    # swiping between two genes by a chance of MUTATION_CHANCE
    if random.random() < MUTATION_CHANCE:

        # generation 4 random numbers between 'spot' and 'spot' + the size of a compact board
        rr1 = random.randint(spot, spot + START_CONF_SIZE - 1)
        rc1 = random.randint(spot, spot + START_CONF_SIZE - 1)
        rr2 = random.randint(spot, spot + START_CONF_SIZE - 1)
        rc2 = random.randint(spot, spot + START_CONF_SIZE - 1)
        # making sure they are not equal
        while rr1 == rr2:
            rr2 = random.randint(spot, spot + START_CONF_SIZE - 1)
        while rc1 == rc2:
            rc2 = random.randint(spot, spot + START_CONF_SIZE - 1)

        mutated_board[rr1][rc1] = original[rr2][rc2]
        mutated_board[rr2][rc2] = original[rr1][rc1]

    return mutated_board


def genetic_algorithm():
    """
    genetic algorithm.
    """
    global POPULATION, POPULATION_SIZE, FITNESS_ARRAY

    # if a chromosome is a successful metushlakh
    is_success_m = False

    # index to the population's chromosomes
    index = 0

    # the biggest fitness in the current generation
    max_fitness = 0

    # creating population (with random values (0/1))
    while index < POPULATION_SIZE:
        set_up(index)
        index += 1

    index = 0
    # running the generations of the genetic algorithm
    while index < GENETIC_ALG_GEN_SIZE:

        # initializing the fitness array of this generation
        FITNESS_ARRAY = [0.0] * POPULATION_SIZE

        for i in range(POPULATION_SIZE):
            is_success_m = run(GAME_OF_LIFE_ITERATIONS_SIZE, POPULATION[i])
            if is_success_m:
               print_m(i, index)
            fitness(FITNESS_ARRAY, i)

        # updating the biggest fitness
        max_fitness = max(FITNESS_ARRAY)
        print("The biggest fitness for generation:", index + 1, "is:", max_fitness)

        temp_population = []
        for _ in range(int(POPULATION_SIZE / 2)):
            # selection
            child1 = weighted_random_choice()
            child2 = weighted_random_choice()
            # make sure its not the same parent
            while compare_chromosomes(child1, child2):
                child2 = weighted_random_choice()

            # crossover
            if random.random() < CROSSOVER_CHANCE:
                child1, child2 = cross_over(child1, child2)

            # mutation
            child1 = mutate(child1)
            child2 = mutate(child2)

            temp_population.append(child1)
            temp_population.append(child2)

        POPULATION = temp_population
        index += 1


def copy_chromosome(a1, a2):
    """
    copies the first chromosome to the second one
    """
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            a2[i][j] = a1[i][j]


def compare_chromosomes(a1, a2):
    """
    compares two given chromosomes
    """
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if a2[i][j] != a1[i][j]:
                return False
    return True


def fitness(array, place):
    """
    Computes the fitness of a specific chromosome that found by the place.
    """
    f = MAX_LIVE_CELLS / START_LIVE_CELLS
    array[place] = f


def weighted_random_choice():
    """
    chooses a random member from the population by the fitnesses,
    the weight determines the probability of choosing its respective member
    """
    f_total = sum(f for f in FITNESS_ARRAY)
    pick = random.uniform(0, f_total)
    weight = 0
    for i in range(BOARD_SIZE):
        weight += FITNESS_ARRAY[i]
        if weight > pick:
            return POPULATION[i]


def current_board():
    """
    :return: the board that has the configuration in the current generation
    """
    global B1, BOARD1, BOARD2
    if B1:
        return BOARD1
    else:
        return BOARD2


def next_board():
    """
    :return: the board that we wand to draw on the next generation
    """
    global B1, BOARD1, BOARD2
    if B1:
        return BOARD2
    else:
        return BOARD1


def check_neighbors(array, i, j):
    """
    checks how many alive neighbors the gene in the place i j has
    :return: number of alive neighbors
    """
    num_alive = 0

    num_alive += array[i - 1][j - 1]
    num_alive += array[i - 1][j]
    num_alive += array[i - 1][j + 1]
    num_alive += array[i][j - 1]
    num_alive += array[i][j + 1]
    num_alive += array[i + 1][j - 1]
    num_alive += array[i + 1][j]
    num_alive += array[i + 1][j + 1]

    return num_alive


def is_all_zeros(board, size):
    """
    checks if all the genes in the chromosome are zeros
    """
    for i in range(size):
        for j in range(size):
            if board[i][j] == 1:
                return False
    return True


def at_boarder(i, j):
    """
    checks if a given place i j is at the boarder or not
    """
    if i == (BOARD_SIZE - 1) or i == 0 or j == 0 or j == (BOARD_SIZE - 1):
        return True
    else:
        return False


def alive(array, i, j):
    """
    checks if a the gene in the place i j is alive or not (1 or not)
    """
    if array[i][j] == 0:
        return False
    else:
        return True


def count_live_cells(board):
    """
    :return: number of alive genes in the given chromosome
    """
    num_alive = 0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == 1:
                num_alive += 1

    return num_alive


def print_m(place, gen, evolving=False):
    """
    printing the successful metushlakh's starting form, ending form, number of iteration
    it took it to get stable, number of start alive cells, max alive cells it got, and the its
    generation in the genetic algorithm. if 'evolving' is True it prints all the stages of the metushlakh evolving
    """
    print("Successful Metushlakh was found in generation:", gen + 1)
    print("its starting live cells is:", START_LIVE_CELLS)
    print("its max live cells is:", MAX_LIVE_CELLS)
    print("its starting form:")
    print_stage(START_CONF)
    print("its ending form:")
    print_stage(END_CONF)
    print("it took it", M_ITERATION, "iterations to get to its ending form")

    if evolving:
        print("it's starting configuration is:\n")
        print_stage(POPULATION[place])
        print("\nIt's evolving stages:\n")
        run(GAME_OF_LIFE_ITERATIONS_SIZE, POPULATION[place], print_conf=True)


def print_stage(board):
    """
    printing the stages of how the configuration evolved
    """
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == 0:
                print('.', end=' ')
            else:
                print('*', end=' ')
        print('\n')


def main():
    genetic_algorithm()
    a = input()
    if a == '\n':
        exit()


if __name__ == "__main__":
    main()

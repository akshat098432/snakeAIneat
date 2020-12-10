import os
import sys
import math
import numpy as np
import neat
import pygame
from matplotlib import pyplot as plt
# local imports
import game_utils as gu
from model.field import Field
from model.snake import Snake
from model.food import Food

# ===============================================================================================
# Global variable(s)
# ===============================================================================================
best_fitness = 0

# ===============================================================================================
# Method declaration
# ===============================================================================================
def play_game(genomes, config):
    global screen
    global best_fitness
    global pop

    dx = 1
    dy = 0
    best_foods = 0
    generation_number = 0
    best_instance = None
    genome_number = 0

    # Create the field, the snake and a bit of food
    theField = Field(screen, gu.field_width, gu.field_height, gu.blockSize, gu.field_color)

    # Outer loop is for all the genomes
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        dx = 1
        dy = 0
        score = 0.0
        calories = 100

        # create food at random position
        theFood = Food(theField)

        # Snake starts from a fixed location
        theSnake = Snake(theField, gu.snake_color, 5, x = int(gu.field_width/2), y=int(gu.field_height/2))

        # initialize an empty set for loop detection
        loopPoints = set()
        food_count = 0   # keep counting of food

        while True:
            event = pygame.event.wait()

            # Window is going to be closed
            if event.type == pygame.QUIT:
                print("Quitting the game now ...")

                ## save the population
                gu.save_object(pop, gu.pop_data_file)
                pygame.quit()
                sys.exit()

            # Every TIME_DURATION there will be a SNAKE_EVENT to move the snake
            if event.type == SNAKE_EVENT:
                # initially dx = 1 and dy = 0 i.e. moving to the right on X axis

                # current distance from the food
                hx, hy = theSnake.position()
                fx, fy = theFood.position()
                dist_before_move = math.sqrt((hx - fx) ** 2 + (hy - fy) ** 2)

                # find out current input points (total 9 for now)
                inputs = gu.get_inputs(theSnake.body[0], theFood.position(), (gu.field_width, gu.field_height), (dx, dy))

                # it will generate 3 outputs (continue straight, left or right)
                outputs = net.activate(inputs)

                # find index of maximum value and determine the direction (0 - straight, 1 - left or 2 - right)
                direction = outputs.index(max(outputs))

                # decide the movement direction based on the outcome
                if direction == 1:  # turn left
                    (dx, dy) = gu.left((dx, dy))
                elif direction == 2:  # turn right
                    (dx, dy) = gu.right((dx, dy))
                else:  # keep going straight (direction = 0)
                    # dx and dy values will remain same
                    pass

                # because of movement calories will burn
                calories -= 1

                # move the snake now, also check if move is invalid or calories are exausted
                # if not theSnake.move(dx, dy) or calories <= 0:
                if (theSnake.move(dx, dy) == False) or (theSnake.body[0] in loopPoints):
                    # too bad snake died
                    # genome.fitness = 0
                    loopPoints = set()
                    break

                # Reward the snake for being alive
                score += gu.ALIVE_SCORE

                # punish for the loop
                # if theSnake.body[0] in loopPoints:
                #    score -= gu.LOOP_SCORE

                # keep tracking head positon till next food grab
                loopPoints.add(theSnake.body[0])

                # distance from the food after the move
                hx, hy = theSnake.position()
                dist_after_move = math.sqrt((hx - fx) ** 2 + (hy - fy) ** 2)

                # adjust the score
                if (hx, hy) == (fx, fy):
                    # if snake grabs the food
                    food_count += 1
                    score += gu.FOOD_SCORE
                    calories += gu.FOOD_CALORIES     # found food, got calories
                    theSnake.grow()                  # grow by one length

                    # Make new food now
                    theFood = Food(theField)

                    # Also reset loopPoints
                    loopPoints = set()
                elif dist_after_move > dist_before_move:
                    score -= gu.FAR_SCORE
                elif dist_after_move < dist_before_move:
                    score += gu.NEAR_SCORE
                else:
                    # place holder for something else
                    score += 0
            # end of SNAKE_EVENT

            # Render snake and food
            theField.draw()
            theFood.draw()
            theSnake.draw()
            pygame.display.update()
            pygame.time.wait(gu.renderdelay)
        # end of while loop

        # while loop is done for the current genome
        for i in range(0, 2):
            theField.draw()
            theFood.draw()
            theSnake.draw(damage=(i % 2 == 0))
            pygame.display.update()

        # Tell about the fitness
        genome.fitness = score / 100

        # Keep saving best instance
        if not best_instance or genome.fitness > best_fitness:
            best_instance = {
                'num_generation': generation_number,
                'fitness': genome.fitness,
                'score': score,
                'genome': genome,
                'net': net,
            }

        best_foods = max(best_foods, food_count)
        best_fitness = max(best_fitness, genome.fitness)
        # if gu.debug_on:
        print(f"Generation {generation_number} \tGenome {genome_number} \tFoods {food_count} \tBF {best_foods} \tFitness {genome.fitness} \tBest fitness {best_fitness} \tScore {score}")
        genome_number += 1
    # end of for loop, all genomes are done

    # Save end results
    gu.save_best_generation_instance(best_instance)
    generation_number += 1
    if generation_number % 20 == 0:
        gu.save_object(pop, gu.pop_data_file)
        print("Exporting population")
        # export population
        # gu.save_object(pop,gu.pop_data_file)
        # export population

    global list_best_fitness
    global fig
    list_best_fitness.append(best_fitness)
    line_best_fitness.set_ydata(np.array(list_best_fitness))
    line_best_fitness.set_xdata(list(range(len(list_best_fitness))))
    plt.xlim(0, len(list_best_fitness)-1)
    plt.ylim(0, max(list_best_fitness)+0.5)
    fig.canvas.draw()
    fig.canvas.flush_events()

# ===============================================================================================
# Execution of code starts
# ===============================================================================================
# Initialize pygame and open a window
pygame.init()
screen = pygame.display.set_mode(gu.screenSize)

SNAKE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SNAKE_EVENT, gu.EVENT_DURATION)

clock = pygame.time.Clock()
screenSurface = pygame.surfarray.pixels2d(screen)

list_best_fitness = []
plt.ion()
fig = plt.figure()
plt.title('Best fitness')
ax = fig.add_subplot(111)
line_best_fitness, = ax.plot(list_best_fitness, 'r-')  # Returns a tuple of line objects, thus the comma

# Load the configuration
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                     neat.DefaultStagnation, gu.config_file)

# Create the population
pop = neat.Population(config)

# Run until a solution is found.
winner = pop.run(play_game, 50)   # 50 generations

# if len(sys.argv) > 1:
#    pop = gu.load_object(sys.argv[1])
#    print("Reading popolation from " + sys.argv[1])
# pop.run(eval_fitness)

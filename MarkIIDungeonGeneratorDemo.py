'''

This version of the terrain generator library interpreter is set up to produce branching tree-like dungeons.


Note that the dependencies do NOT include math, even though the generator library does.

'''

import NoiseMapGenerators_14 as NoiseMapGenerators
import pygame
import sys
import random




#### Constants ####


WINDOW_CAPTION = "NoiseMapGenerator Library Demonstration"



#WHICH_COLOR_SCHEME = 'terrain'
#WHICH_COLOR_SCHEME = 'grayscale'
## Starfield will require extensive parameters testing with each generator.
#WHICH_COLOR_SCHEME = 'starfield'
WHICH_COLOR_SCHEME = 'dungeon'


## For display purposes.
MAPTILE_SIZE_IN_PIXELS = MAPTILE_WIDTH_IN_PIXELS, MAPTILE_HEIGHT_IN_PIXELS = 4, 4

print("MAPTILE_SIZE_IN_PIXELS == %s" % str(MAPTILE_SIZE_IN_PIXELS))



## The NOISE_WIDTH (and NOISE_HEIGHT) options adjust the size of the map that is created. Or at least I'd be awfully surprised to learn that isn't what they do.
NOISE_WIDTH = 120

## Adjusted this to make it a perfect square for testing purposes.
NOISE_HEIGHT = NOISE_WIDTH
#NOISE_HEIGHT = 16



#### Dungeon map testing observations ####

ROOM_MAX_SIZE = 18
ROOM_MIN_SIZE = 6


## Note: Room max count and room min count are not currently used by the RoomFilledMapGenerator.
ROOM_MAX_COUNT = 14444
ROOM_MIN_COUNT = 12







#### Simplex noise testing observations ####

#NOISE_FREQUENCY = 0.01
#NOISE_OCTAVES = 32
#NOISE_PERSISTENCE = 0.5


## IMPORTANT!!! Frequency MUST BE VERY LOW! Beneath 1.0 and above 0.0, possibly always beneath 0.1
## Otherwise the "width of tiles on the planet's surface" is going to be SMALLER THAN A MAPTILE.
## This makes it seem hugely spikey, when simplex noise should be smooth and cloudlike.
## I got decent results at 0.01 frequency with all sorts of octaves and 0.5 persistence.
## 0.01f 32o 0.5p looks fairly zoomed in, though.

## Below data is from before I discovered the above.
## octaves seems to smoothen it out as it increases, as with before

## f2 o2 p2-4-8-16 seemed to create more land area with more p, though p0 created plenty of land and was extremely spikey
## no visible difference between f2o2p64 and f2o2p512, but f2o2p2 had more water and seemed less spikey

## f32o2p2 made visible lleft-->uright diagonal repetition
## f256o2p2 made a series of lleft-->uright streaks.
## I think scaling up frequency too far makes it more obviously repeat itself.

## f1o2p1 had visible lleft-->uright diagonal repetition

## ...
## heh oops. Persistence should be between 0 and 1.




#### Perlin noise testing observations ####

# width of the tiles on the planet's surface??
#NOISE_FREQUENCY = 64
# how close we are to the tiles?? <-- this seems to be a decent interpretation of its effects
#NOISE_OCTAVES = 1024

#NOISE_FREQUENCY = 32
#NOISE_OCTAVES = 512

#NOISE_FREQUENCY = 8
#NOISE_OCTAVES = 128



## Discovery: Maintaining the ratios of frequency and octaves maintains the appearance of the results.
## Due to how the octaves are used I think this means octaves should be kept small to speed runtime.
## ...
## Could this algorithm be used to zoom in to a specific map by creating one particular randseed and using it for every pass of the algorithm?







MAP_SIZE_IN_TILES = MAP_WIDTH_IN_TILES, MAP_HEIGHT_IN_TILES = NOISE_WIDTH, NOISE_HEIGHT

print("MAP_SIZE_IN_TILES == %s" % str(MAP_SIZE_IN_TILES))

## Size the screen so the maptiles fit in it neatly.
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = (MAP_WIDTH_IN_TILES * MAPTILE_WIDTH_IN_PIXELS), (MAP_HEIGHT_IN_TILES * MAPTILE_HEIGHT_IN_PIXELS)    

print("SCREEN_SIZE == %s" % str(SCREEN_SIZE))


print("\n")


## In this program, BLACK is used to clean the screen when redrawing.
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]

LIGHT_GRAY = [120, 120, 120]
DARK_GRAY = [50, 50, 50]

RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]

DARK_BLUE = [0, 0, 150]
DEEP_BLUE = [0, 0, 75]

BRAUN = [95, 45, 0]
LIGHT_BRAUN = [115, 65, 20]
SANDY_TAN = [245, 165, 95]

DARK_GREEN = [0, 155, 0]
LIGHT_GREEN = [50, 255, 50]

DEBUG_PINK = [224, 176, 255]



#### Classes ####




class MapTile:


    def __init__(self, supplied_x_in_maptiles, supplied_y_in_maptiles, supplied_z):

        ''' Make a MapTile object with coordinates on the screen and in the map (meansured in pixels and tiles, respectively). Each MapTile has a magnitude, called: z '''
    
    
        self.x = supplied_x_in_maptiles
        self.pixel_x = self.x * MAPTILE_WIDTH_IN_PIXELS
        
        self.y = supplied_y_in_maptiles
        self.pixel_y = self.y * MAPTILE_HEIGHT_IN_PIXELS
        
        self.z = supplied_z
        
        if self.z != None:
            if self.z > 255:
                self.z = 255
            elif self.z < 0:
                self.z = 0
        elif self.z == None:
            #print("NONE DETECTED in self.z!! " + str(self.z))
            pass
            
            

    def draw_maptile(self):
        
        
        ## Regardless of the color scheme, pixels with value of None type will be set to DEBUG_PINK.

        if type(self.z) == None:
            _color_of_this_pixel = DEBUG_PINK
            pygame.draw.rect(screen, _color_of_this_pixel, [self.pixel_x, self.pixel_y, MAPTILE_WIDTH_IN_PIXELS, MAPTILE_HEIGHT_IN_PIXELS])
                    
            return
        
        
        
        if WHICH_COLOR_SCHEME == 'terrain':
        
            if self.z < 90:
                _color_of_this_pixel = DEEP_BLUE
        
            elif self.z < 120:
                _color_of_this_pixel = DARK_BLUE
            
            elif self.z < 160:
                _color_of_this_pixel = BLUE
                
            elif self.z < 170:
                _color_of_this_pixel = GREEN
                
            elif self.z < 180:
                _color_of_this_pixel = DARK_GREEN
                
            elif self.z < 190:
                _color_of_this_pixel = GREEN
                
            elif self.z < 200:
                _color_of_this_pixel = BRAUN
                
            elif self.z < 210:
                _color_of_this_pixel = LIGHT_BRAUN
                
            else:
                _color_of_this_pixel = WHITE
        
        
        
        elif WHICH_COLOR_SCHEME == 'starfield':
            
            if self.z == 1:
                _color_of_this_pixel = WHITE
            
            elif self.z == 2:
                _color_of_this_pixel = LIGHT_GRAY
                
            elif self.z == 3:
                _color_of_this_pixel = DARK_GRAY
            
            else:
                _color_of_this_pixel = BLACK
        
        
        
        elif WHICH_COLOR_SCHEME == 'dungeon':
            
            if self.z == 0:
                _color_of_this_pixel = BLACK
            
            elif self.z == 1:
                _color_of_this_pixel = LIGHT_GRAY
                
            else:
                _color_of_this_pixel = DEBUG_PINK
                
                #print("\n  OMG DEBUG PINK OMG OMG\n    x: %d y: %d" % (self.x, self.y))



        
        elif WHICH_COLOR_SCHEME == 'grayscale':
            _color_of_this_pixel = [self.z, self.z, self.z] # I summon thee

            

        pygame.draw.rect(screen, _color_of_this_pixel, [self.pixel_x, self.pixel_y, MAPTILE_WIDTH_IN_PIXELS, MAPTILE_HEIGHT_IN_PIXELS])






#### Functions ####


def convert_noise_map_to_maptile_map(supplied_map):
    
    ''' Return a list full of MapTiles with x, y and z values corresponding to the output of a TerrainGenerator. '''
    
    ## Note: This whole script is an example of how to interpret the more "pure" results of a noise generator as something useful to another program.
    ## This program interprets the noise as "terrain maps" and therefore reads the x, y and z values as a map. This function handles that conversion and could conceivably be expanded to stack multiple supplied_maps of noise, or stitch maps together or something. Or even do something rather unmaplike with the x/y/z coordinates, if desired.
    
    new_maptile_map = []
    
    for each_y_index in range(0, len(supplied_map)):
    
        for each_x_index in range(0, len(supplied_map[each_y_index])):

            new_maptile = MapTile(each_x_index, each_y_index, supplied_map[each_y_index][each_x_index])

            new_maptile_map.append(new_maptile)
            
    return new_maptile_map


    
    
def handle_keys(should_we_keep_the_window_open):

    ''' Interpret pressed keys as input commands. '''
    
    for event in pygame.event.get():   # NOTE: This does not seem to allow for continuously-held-down keys being re-read if another key is pressed and released during the first key's held period.
        if event.type == pygame.QUIT:
            sys.exit
        elif event.type == pygame.KEYDOWN:
            ## events and KEYDOWN prevent multiple firings from holding down buttan.
            
            if event.key == pygame.K_ESCAPE:
                sys.exit
                pygame.quit
                should_we_keep_the_window_open = False ## NOTE: Only this line ACTUALLY works! How humorous.
    
    
    return should_we_keep_the_window_open
    

    
    
def render_all(array_of_all_maptiles):

    ''' Draw ALL THE PIXELS! '''

    screen.fill(BLACK)
    

    for _each_nook in array_of_all_maptiles:
        _each_nook.draw_maptile()

        
    ## Don't forget this line. It uses pygame to put the things you want to see on the thing you can see.
    pygame.display.flip()
    
        
    
    


#### Inits ####


## The type of generator you want to use can be changed here for now.
## Options currently include:
##    PlasmaFractalGenerator()
##    PerlinNoiseGenerator()
##    SimplexNoiseGenerator()
##    DungeonMapGenerator()
##    RoomFilledMapGenerator()
##    MarkIIDungeonMapGenerator()
##
## Of these, the Simplex generator is the most technically complex but is theoretically faster at creating a noise map than the Plasma and Perlin generators.
## It's not clear whether my implementation is even close to optimized for speed, though. I don't yet know enough about python/C integration to try speeding it up.
## The Perlin generator return the best-looking terrain maps, possibly tied with the Simplex generator. They both require some fiddling with generator input parameters to get better-looking results.
## The plasma generator has some gridwards bias, but it too produces decent noise clouds, as long as you don't look too closely or get too unlucky.
## TerrainMapGenerators contains noise generators and "dungeon map generators," which are more like signal than noise, as they return maps full of rooms and corridors illustrated using two Z values (0 and 1).
## The DungeonMapGenerator produces randomly placed rectangular rooms that all connect to each other using L-shaped corridors daisy chained from one room's centerpoint to the next, in the order of room placement. This algorithm was inspired by/copied from the libtcod roguelike tutorial at < http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python%2Blibtcod,_part_1 >.
## The RoomFilledMapGenerator creates maps packed full of rectangular rooms. Has significant bias and no connecting corridors. I didn't really like the direction it was going in, but it can probably be turned into something decent with some upgrading and tweaking. 
## The MarkIIDungeonMapGenerator is my favorite one so far. It produces maps wherein the rooms are connected in a branching pattern such that dungeons have "wings" which can be quite lengthy and significantly subdivided.




#### MK II DUNGEON MAP GENERATOR DEMONSTRATION ####

the_mk_ii_dungeon_map_generator = NoiseMapGenerators.MarkIIDungeonMapGenerator()





#### ROOM-FILLED MAP DEMONSTRATION ####

#the_room_filled_map_generator = NoiseMapGenerators.RoomFilledMapGenerator()



#### DUNGEON MAP DEMONSTRATION ####

#the_dungeon_generator = NoiseMapGenerators.DungeonMapGenerator()





#### SIMPLEX NOISE DEMONSTRATION ####

#the_simplex_generator = NoiseMapGenerators.SimplexNoiseGenerator()





#### PERLIN NOISE DEMONSTRATION ####

#the_perlin_generator = NoiseMapGenerators.PerlinNoiseGenerator()






#### PLASMA FRACTAL DEMONSTRATION ####

#the_plasma_generator = NoiseMapGenerators.PlasmaFractalGenerator()

## I think I wrote this before I realized I wanted to provide sensible silent defaults for all the little options.
## It may or may not work with the 3 following lines commented.
#the_plasma_generator.displacement_min = (-40)
#the_plasma_generator.displacement_max = 40

#the_plasma_generator.reinitialize_corners(uleft_corner=135, uright_corner=245, lleft_corner=135, lright_corner=135)



#### Execution ####



## Initialize the screen
screen = pygame.display.set_mode(SCREEN_SIZE)
    

## Window title            
pygame.display.set_caption(WINDOW_CAPTION)        
        
        
    
## Create a clock object to make the game run at a specified speed in the main loop
clock = pygame.time.Clock()

## To keep the game running
keep_window_open = True
    
    
    

## DEBUG: Leaving these lines in will cause the generator to make one pass before the main loop. Combine this with commenting the regeneration of the map in the main loop to get a single map displayed for the duration of the program.  cfref:one-pass
#the_map_of_noise = []
#the_grand_map = []


#the_map_of_noise = the_simplex_generator.generate_noise(128, 128)

#the_grand_test_map = convert_noise_map_to_maptile_map(the_map_of_noise)
    
#print(str(the_map_of_noise))    

## The hash iterator moves the hash value inside the simplex noise generator through all 256 points in its range.
## IMPORTANT! This makes it NOT produce terrain-like noise. What it produces is more predictable.
## The place to put in unpredictability is in the NUMBER SHEET the simplex generator is seeded with, NOT the hash value.
## De-comment this to see it slide through the increasingly predictable patterns of the shifted hash sheet.  cfref:hash-iterator
#debugging_hash_iterator = 0    
    
    
    
#### Main Loop ####



while keep_window_open == True:
        
    ## DEBUG COMMENT TO SEE ONLY ONE PASS cfref:one-pass
    the_map_of_noise = []
    the_grand_test_map = []
    
    

    ## The hash iterator moves the hash value inside the simplex noise generator through all 256 points in its range.
    ## IMPORTANT! This makes it NOT produce terrain-like noise. What it produces is more predictable.
    ## The place to put in unpredictability is in the NUMBER SHEET the simplex generator is seeded with, NOT the hash value.
    ## De-comment these lines to see it slide through the increasingly predictable patterns of the shifted hash sheet.  cfref:hash-iterator
    #the_simplex_generator.hash_number = debugging_hash_iterator
    
    #if debugging_hash_iterator < 255:
    #    debugging_hash_iterator += 1
    #else:
    #    debugging_hash_iterator = 0
    
    
    
    #### Regenerating the noise ####
    
    ## If using the Mk II dungeon map generator:
    the_map_of_noise = the_mk_ii_dungeon_map_generator.generate_noise(supplied_map_width=NOISE_WIDTH, supplied_map_height=NOISE_HEIGHT, room_max_size=ROOM_MAX_SIZE, room_min_size=ROOM_MIN_SIZE, room_max_count=ROOM_MAX_COUNT, room_min_count=ROOM_MIN_COUNT)
    
    ## If using a room-filled map generator:
    #the_map_of_noise = the_room_filled_map_generator.generate_noise(supplied_map_width=NOISE_WIDTH, supplied_map_height=NOISE_HEIGHT, room_max_size=ROOM_MAX_SIZE, room_min_size=ROOM_MIN_SIZE)
    
    ## If using a dungeon map generator:
    #the_map_of_noise = the_dungeon_generator.generate_noise(supplied_map_width=NOISE_WIDTH, supplied_map_height=NOISE_HEIGHT, room_max_size=ROOM_MAX_SIZE, room_min_size=ROOM_MIN_SIZE, room_max_count=ROOM_MAX_COUNT, room_min_count=ROOM_MIN_COUNT)

    ## If using a simplex noise generator:
    #the_map_of_noise = the_simplex_generator.generate_noise(NOISE_WIDTH, NOISE_HEIGHT, NOISE_FREQUENCY, NOISE_OCTAVES, NOISE_PERSISTENCE)

    ## If using a Perlin noise generator:
    #the_map_of_noise = the_perlin_generator.generate_noise(NOISE_WIDTH, NOISE_HEIGHT, NOISE_FREQUENCY, NOISE_OCTAVES)

    ## If using a plasma fractal generator:
    #the_map_of_noise = the_plasma_generator.generate_noise(x=0, y=0, supplied_width=NOISE_WIDTH, supplied_height=NOISE_HEIGHT)
    

    
    
    
    
    ## DEBUG COMMENT TO SEE ONLY ONE PASS cfref:one-pass
    the_grand_test_map = convert_noise_map_to_maptile_map(the_map_of_noise)
    

    
    
    
    ## Process keyboard input
    keep_window_open = handle_keys(keep_window_open)
    
    
    ## Game speed and event progression metering. Measured in maximum permissible frames per second.
    clock.tick(30)
    #clock.tick(1)    
        
    
    
    ## Graphical display for much human friendly.
    render_all(the_grand_test_map)    
    
    
    ## DEBUG COMMENT TO SEE ONLY ONE PASS cfref:one-pass
    del the_map_of_noise
    del the_grand_test_map

    

    

# "Be IDLE friendly," they said.    
pygame.quit    
        
        

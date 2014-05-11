'''

Fractal noise map generator library.
Also includes additional non-"noise" map generators for dungeon generation purposes.
The reason for putting them in is because I want the games I make to be able to use very similar code for all the different types of maps I need. Ensuring a high level of cross-compatibility at the generator level may enhance creativity later on.

Each generator is an object built by a class specific to that type of generator.
All generators SHOULD have enough defaults to require only a handful of arguments (tailored to your display needs) before they're popping out noiseclouds.
The most useful generators are the Perlin generator and the Mk II dungeon map generator, but they all have their own unique capabilities.



Generators currently include:

   PlasmaFractalGenerator()
   PerlinNoiseGenerator()
   SimplexNoiseGenerator()
   DungeonMapGenerator()
   RoomFilledMapGenerator()
   MarkIIDungeonMapGenerator()

Of these, the Simplex generator is the most technically complex but is theoretically faster at creating a noise map than the Plasma and Perlin generators.
It's not clear whether my implementation is even close to optimized for speed, though. I don't yet know enough about python/C integration to try speeding it up.

The Perlin generator return the best-looking terrain maps, possibly tied with the Simplex generator. They both require some fiddling with generator input parameters to get better-looking results.

The plasma generator has some gridwards bias, but it too produces decent noise clouds, as long as you don't look too closely or get too unlucky.
It was the first noise generator I made, before I realized I wanted to make all the parameters of the various generators more similar to each other.
I might go back and change it to that at some point, but I have no especial reason to given its technical inferiority to the simplex and Perlin generators.

TerrainMapGenerators contains noise generators and "dungeon map generators," which are more like signal than noise, as they return maps full of rooms and corridors illustrated using two Z values (0 and 1).

The DungeonMapGenerator produces randomly placed rectangular rooms that all connect to each other using L-shaped corridors daisy chained from one room's centerpoint to the next, in the order of room placement. This algorithm was inspired by/copied from the libtcod roguelike tutorial at < http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python%2Blibtcod,_part_1 >.

The RoomFilledMapGenerator creates maps packed full of rectangular rooms. Has significant bias and no connecting corridors. I didn't really like the direction it was going in, but it can probably be turned into something decent with some upgrading and tweaking. 

The MarkIIDungeonMapGenerator is my favorite one so far. It produces maps wherein the rooms are connected in a branching pattern such that dungeons have "wings" which can be quite lengthy and significantly subdivided.





Note that the dependencies do NOT include pygame, even though the display program I created for demonstrations does.

'''


import random
import sys
import math








#### Classes ####



		
	

	
	
	
	
class PlasmaFractalGenerator:	
	
	
	''' Create a fractal generator that returns a list of ((word for things that come in parentheses)) consisting of three floating point values: x, y and z coordinates for constructing a plasma fractal for use as a noise map. '''
	
	
	
	def __init__(self, array_root=2, corners_min=0, corners_max=255, displacement_min=(-35), displacement_max=35, minimum_separation_distance=1, uleft_corner=None, uright_corner=None, lleft_corner=None, lright_corner=None):

		
		## The root of the array (it's square root, or side measurement):
		self.array_root = array_root
		
		## Save the width and height of the map as state. We'll be using this to construct a new map to hold the plasma fractal in a method designed for this purpose.
		self.array_width =  (self.array_root * 2)
		self.array_height = (self.array_root * 2)
		
		## Init the plasma fractal's handler, the noise array, as None:
		self.saved_noise_array = None
		
		## Min and max values for randomly generated corner Z values:
		self.corners_min = corners_min
		self.corners_max = corners_max
		
		## The range of randomness that can be applied to each midpoint displacement.
		## Usual supplied values have a negative min and a positive max.
		self.displacement_min = displacement_min
		self.displacement_max = displacement_max
		
		## The distance at which the fractal stops subdividing itself and returns a value for the next least coordinate point ( 1.004 --> 1, 1.000 --> 1, 0.996 --> 0 etc if min_sep_dist is 1).
		self.minimum_separation_distance = minimum_separation_distance
		
		## Corners' initial zee values, can be set manually in __init__() parameters:
		self.uleft_corner =  uleft_corner
		self.uright_corner = uright_corner
		self.lleft_corner =  lleft_corner
		self.lright_corner = lright_corner
		
		## Someone might want the corners to be preset values, so check if they didn't at the time of initialization.
		## ...
		## This section may be a candidate for refactorization in the future, with the addition of parameters to reinitialize_corners()
		if self.uleft_corner is None:
			self.uleft_corner =  random.randint(self.corners_min, self.corners_max)
		if self.uright_corner is None:
			self.uright_corner = random.randint(self.corners_min, self.corners_max)
		if self.lleft_corner is None:
			self.lleft_corner =  random.randint(self.corners_min, self.corners_max)
		if self.lright_corner is None:
			self.lright_corner = random.randint(self.corners_min, self.corners_max)
						
						



						
	def reinitialize_corners(self, uleft_corner=None, uright_corner=None, lleft_corner=None, lright_corner=None):
	
		if uleft_corner == None:
			self.uleft_corner =  random.randint(self.corners_min, self.corners_max)
		else:
			self.uleft_corner = uleft_corner

		if uright_corner == None:			
			self.uright_corner = random.randint(self.corners_min, self.corners_max)
		else:
			self.uright_corner = uright_corner

		if lleft_corner == None:
			self.lleft_corner = random.randint(self.corners_min, self.corners_max)
		else:
			self.lleft_corner = lleft_corner

		if lright_corner == None:
			self.lright_corner = random.randint(self.corners_min, self.corners_max)
		else:
			self.lright_corner = lright_corner

		
		
		
	def generate_noise(self, x=None, y=None, supplied_width=None, supplied_height=None, uleft_corner=None, uright_corner=None, lleft_corner=None, lright_corner=None):
		
		''' This function is the gateway function to generate_plasma(). '''
		
		del self.saved_noise_array
		
		self.saved_noise_array = []
		
		
		
		## This section necessitated by the combination of my desire to make generate_noise() callable with arbitrary arguments and Python's refusal to accept self.foo as parameters for a method.
		if x == None:
			x = 0
		if y == None:
			y = 0
			
		if supplied_width == None:
			supplied_width = self.array_width
		if supplied_height == None:
			supplied_height = self.array_height
			
		if uleft_corner == None:
			uleft_corner = self.uleft_corner
		if uright_corner == None:
			uright_corner = self.uright_corner
			
		if lleft_corner == None:
			lleft_corner = self.lleft_corner
		if lright_corner == None:
			lright_corner = self.lright_corner
								
		
		
		## Remember, no call to self in the parameters when a method is calling another method. The definition of the second method will invoke its own self, don't worry. :p
		self.plasma_recursion(x=x, y=y, supplied_width=supplied_width, supplied_height=supplied_height, uleft_corner=uleft_corner, uright_corner=uright_corner, lleft_corner=lleft_corner, lright_corner=lright_corner)

		
		####print("  Debug: self.saved_noise_array == ")
		#for each in self.saved_noise_array:
		#	###print("    " + str(each))
		
		
		## Now convert that giant list into a tuple with the same ordering as the PerlinNoiseGenerator's results.
		
		array_to_return = []
		
		for each_array_height_index in range(0, supplied_height):    # y

			## Fill the array_to_return with rows full of -1s so we only have to iterate through it once in the next step!
			
			new_row = []
			
			for each_array_width_index in range(0, supplied_width):  # x
				
				new_row.append(-1)
			
			array_to_return.append(new_row)
		
		####print("  Debug: array_to_return == " + str(array_to_return) + "\n")
			
			
		for each_cell in self.saved_noise_array:
				
			## Round down x and y since the values are probably all floats.
			## This will ALMOST CERTAINLY give me bad results and I'm gonna have to change something, maybe cleverer rounding??
			## I may have to round up and down more precisely than int() depending on exactly what ends up happening with the results. :S
					
					
			'''
			## EDIT: The following is probably not the best way to do this. I added the -1 overwrite procedure instead.
			
			## ...
			
			## Complicated syntax is actually very shallow conceptually.
			## array[a].insert([b], [c])
			## a == the rounded down y value of the cell
			## b == the rounded down x value of the cell
			## c == the floating point z value of the cell
			## Rounding is currently being done by int() calls, this may very well be a bad idea. See above note.
			## All index variables are referenced by their index number in each_cell; hence the square brackets.
			
			array_to_return[int(each_cell[1])].insert(int(each_cell[0]), each_cell[2])
			'''	
			
			####print("  Debug: each_cell    == " + str(each_cell)) 
			####print("         each_cell[0] == " + str(each_cell[0]))
			####print("         each_cell[1] == " + str(each_cell[1]))
			####print("         each_cell[2] == " + str(each_cell[2]))			
			
			## The syntax is now:
			## array[y][x] = z
			## where y, x and z are extracted from their respective indices in each_cell.
			## Rounding is once again involved at this step. See above notes in this method.
			## DEBUG: Testing -1 to see if it always rounds one way or does a split at 0.5
			array_to_return[int(each_cell[1])][int(each_cell[0])] = each_cell[2]
			
			
		## If this line is left out the generator will use the same corner values and make a whole new map between them.
		## Remember, self.reinitialize_corners() can be called in the main program.
		#self.reinitialize_corners()		
		
		return array_to_return
		
		
	def plasma_recursion(self, x, y, supplied_width, supplied_height, uleft_corner, uright_corner, lleft_corner, lright_corner):
		## This method is intended to be called by self.generate_noise()
		## The results of calling this separately from self.generate_noise() will be a long list of [x, y, z] values rather than a tuple with the form ( array[y][x] == (z) ).
			
			
		''' Recursively supply [x, y, z]-formatted plasma fractal elements to self.saved_noise_array, as called by self.generate_noise() '''	
			
		new_width  = (supplied_width  / 2)
		new_height = (supplied_height / 2)

		
		
		if ( (supplied_width > self.minimum_separation_distance) or (supplied_height > self.minimum_separation_distance) ):
			
			## This step must happen during this part of the conditional tree. Not after the else!
			random_midpoint_displacement = random.randint(self.displacement_min, self.displacement_max)
			
			## Create midpoint's zee by averaging corners' zees and mixing in the random_midpoint_displacement:
			mid_z    =  ( ( (uleft_corner + uright_corner + lleft_corner + lright_corner) / 4 ) + random_midpoint_displacement )

			## Deduce sides' zees:
			top_z    =  ( (uleft_corner + uright_corner)  / 2 )
			bottom_z =  ( (lleft_corner + lright_corner)  / 2 )
			left_z   =  ( (uleft_corner + lleft_corner)   / 2 )
			right_z  =  ( (uright_corner + lright_corner) / 2 )

			## Recursion. Note this happens inside the earlier if statement. The alternative is not recurring at this call, and instead returning a value.
			uleft_quadrant  =  self.plasma_recursion(x=x,             y=y,              supplied_width=new_width, supplied_height=new_height, uleft_corner=uleft_corner, uright_corner=top_z,         lleft_corner=left_z,       lright_corner=mid_z         )
			uright_quadrant =  self.plasma_recursion(x=(x+new_width), y=y,              supplied_width=new_width, supplied_height=new_height, uleft_corner=top_z,        uright_corner=uright_corner, lleft_corner=mid_z,        lright_corner=right_z       )
			lleft_quadrant  =  self.plasma_recursion(x=x,             y=(y+new_height), supplied_width=new_width, supplied_height=new_height, uleft_corner=left_z,       uright_corner=mid_z,         lleft_corner=lleft_corner, lright_corner=bottom_z      )
			lright_quadrant =  self.plasma_recursion(x=(x+new_width), y=(y+new_height), supplied_width=new_width, supplied_height=new_height, uleft_corner=mid_z,        uright_corner=right_z,       lleft_corner=bottom_z,     lright_corner=lright_corner )
	
		else:
			
			## When the distance between the corners drops below the minimum separation distance, create an [x, y, z] cell and return it up the chain:
	
			new_z_value = ( (uleft_corner + uright_corner + lleft_corner + lright_corner) / 4 )
	
			new_coordinate = [x, y, new_z_value]
			
			self.saved_noise_array.append(new_coordinate)
            
            
            
            
            
            
class PerlinNoiseGenerator:
	
	
	def __init__(self):
	
		## The generator saves its noise-map state:
		self.noise_array = []
		self.noise_width = 0
		noise_height = 0
		
		
	def generate_noise(self, width, height, frequency, octaves):
		
		''' Returns a tuple of [parameter 2] lists each containing [parameter 1] randomly generated integer numbers between $FIX_ME_MINIMUM and $FIX_ME_MAXIMUM, fractally smoothed as Perlin noise using a frequency of [parameter 3] and an octave count of [parameter 4]. '''
		
		## Octaves?
		## It's used for calling turbulence(), which considers that parameter to be "size".
		## The original function declared that changing octaves changes how far in or out from the noise you are zoomed.
		## Which seems like a decent interpretation of the results.
		## Raising the frequency makes it spikier (which is reminiscent of zooming out).
		## Raising the octaves make it smoother (which is reminiscent of zooming in).
		## Note that keeping the ratios of frequency to octaves the same will keep the results looking similar!
		## For this reason I recommend using small octave values, since that governs the recursor runtime.
		

		
		
		## First, clear the currently saved noise map:
		## ...
		## actually self.noise_array is used internally to the generator's function and does not save the actual noise map.
		## Interesting, that.
		del self.noise_array[:]
		
		## Now assign this NoiseGenerator's current noise_width and noise_height to the values supplied by the function call parameters:
		## Note that the NoiseGenerator saves these as state because they need to be referenced in the sub-functions below.
		self.noise_width = width
		self.noise_height = height
		
		
		## Initializing the noise_array with random numbers.
		## This for loop provides the raw random data smeuthanized into a pretty, pretty vapor cloud further in the program.
		## Create a bunch of rows, equal in number to self.noise_height...
		for each_row in range(0, self.noise_height):
			
			noise_row_handler = []
			
			## ... and fill them with randint()s equal in number to self.noise_width:
			for each_column in range(0, self.noise_width):
				
				noise_value = ( random.randint(0, 1000) / 1000.0 )
				
				noise_row_handler.append(noise_value)
				
			## Attach each row to the noise_array.
			self.noise_array.append(noise_row_handler)
			## The generator's noise_array should now be full of rows which are full of integers.
		
			## The noise_array isn't the finished product. It's used to create it, in the below functions.
	
	
	
			
		result = []
		
	
	
		## Turbulating the noise array ##
	
			
		for each_y in range(0, self.noise_height):
		
		
			turbulated_noise_row_handler = []

			
			for each_x in range(0, self.noise_width):
				
			
				## Note: Frequency is rolled into the parameters here!
				turbulated_noise_value = int(self.totally_justified_turbulence_function((each_x * frequency), (each_y * frequency), octaves))
			
				turbulated_noise_row_handler.append(turbulated_noise_value)
			
			
			
			result.append(turbulated_noise_row_handler)

		
		## NOTE that the NoiseGenerator does NOT save the result as state.
		## It hands it off to whatever called its generate_noise() function.
		## This is where this generator's entire function chain ends:
		return result
			
	
	
	
	
	

	def totally_justified_turbulence_function(self, x, y, size):
		
		## noise_value is "built up" by smooth_noise():
		noise_value = 0.0
		
		## Floats it:
		size *= 1.0
		
		initial_size = size
		
		
		## This is kind of like fractally splitting a grid, except it just sort of "resonates" itself in half and applies noise smoothening or something. Octaves.
		while (size >= 1):
			
			
			the_smooth_noise = self.smooth_noise((x / size), (y / size))
			
			the_smooth_noise *= size
			
			## Add it to the noise_value pile:
			noise_value += the_smooth_noise
			
			## Paring down the size... iterating downwards...
			size /= 2.0
			
			
		## Order of Operations suggests division before multiplication, so:
		noise_value /= initial_size	
			
		## ???
		## Experiment to figure out what it does! o_o	
		## ...
		## Biases the resulting z values to average out at this number:
		noise_value *= 128.0

		
		return noise_value
			
			
	

			
	

	def smooth_noise(self, x, y):

		''' Return the average value of the 4 neighbors of the point (x, y) from self.noise_array. '''
			
		## NOTE! self.noise_array is a cranny full of state used for THIS FUNCTION ONLY.
		
		## The following is necessary because of modulo calls further down that would ignore it, but it needs to be saved.
		## Get the trailing part of the floats of x and y:
		fractional_element_of_x = ( x - int(x) )
		fractional_element_of_y = ( y - int(y) )


		
		x1 = ( (int(x) + self.noise_width) % self.noise_width )
		y1 = ( (int(y) + self.noise_height) % self.noise_height )
		
		
		## I think the -1 is to compensate for the fractional_element_of_foo being extracted earlier.
		## Remember, that fractional_element is added back in below.
		## Apart from that, this is exactly the same as \
		## figuring out the length of a line between \
		## (x1, y1) and (x2, y2) in a noise plane.
		## Or something like that. Surely.
		x2 = ( (x1 + self.noise_width - 1) % self.noise_width )
		y2 = ( (y1 + self.noise_height - 1) % self.noise_height )



		## Take NOTE of the use of self.noise_array below...
		## It's the place it really matters in this ridiculous three-function chain, \
		## even though it's stored at the object level.
			
		## Begin the cooking process by taking out a bowl.
		value = 0.0

		## Place inside the bowl the fractional element of X times the fractional element of Y times the noise value at location (y1, x1)
		value += ( fractional_element_of_x * fractional_element_of_y * self.noise_array[y1][x1] )

		## Next, stir in the fractional element of X times (one minus the fractional element of y) times the noise value at location (y2, x1)
		value += ( fractional_element_of_x * (1 - fractional_element_of_y) * self.noise_array[y2][x1] )

		## Sprinkle liberal amounts of (one minus the fractional element of X) times the fractional element of Y times the noise value at location (y1, x2)
		value += ( (1 - fractional_element_of_x) * fractional_element_of_y * self.noise_array[y1][x2] )
		
		## Line baking pan with a mixture of (one minus the fractional element of X) times (one minus the fractional element of Y) times the noise value at location (y2, x2)
		value += ( (1 - fractional_element_of_x) * (1 - fractional_element_of_y) * self.noise_array[y2][x2] )
		
		## I'm not yet sure how adding four things and then not dividing by four returns the AVERAGE value of the four neighbors of point (x, y) in the noise array. (Maybe it's already taken into account?)
		## But slap that pan in the oven and let it burn for 0.002 ms.
		
		
		return value

	
	
	
	
	
class SimplexNoiseGenerator:	
	
	
	## These things are true for every instance of this class and does not require re-initting.
	
	## I don't really know what's going on here. Halp plix.
	## ...
	## The way it's referenced suggests that grad3 is an ordered list of simplex vertices.
	## gi0/gi1/gi2 gives numbers that somehow map to indices of this list via a quite arcane mathemagical cantrip with no justification given. See below in the noise generator.
	## I'm just gonna interpret all those Grad objects as simple boxes for vertex coordinates.
	grad3 = [   [1, 1, 0], [-1, 1, 0], [1, -1, 0], [-1, -1, 0],  \
				[1, 0, 1], [-1, 0, 1], [1, 0, -1], [-1, 0, -1],	 \
				[0, 1, 1], [0, -1, 1], [0, 1, -1], [0, -1, -1]   ]
	## ...
	## Wow I think they actually decided not to include a grad2 table because the mapping for grad3 technically works for grad2 too.
	## Wow.
	## I'm gonna go ahead and make a grad2 table based on my interpretation of what is going on here.
	grad2 = [	[1, 1], [-1, 1], [1, -1], [-1, -1],  \
				[1, 0], [-1, 0], [1, 0], [-1, 0],    \
				[0, 1], [0, -1], [0, 1], [0, -1]     ]
	## Nooope does not make more sense now.
	## I'm going to put all of my trust in the implicit knowledge of the Java coder here.
	## Just going to assume using the first two columns of the grad3 table works.
	## It probably should, given that in grad2, there are precisely 4 instances of each specific value across the table, in varying combinations.
	## So even though there are repeats I guess it still works somehow?!
	## Maybe the fact there's some modulus going on ensures the repeated indices get skipped or something?
	
	
		
	## The next section initializes the skewing and unskewing factors.
	## I looked in the Java code and these are just constants.
	## They should probably be called in preprocessing somehow, maybe at the top of this module...
	## But I want the generators to be able to whip out new worlds at high speeds...
	## So it's either top of the module, presolved here, or it takes too long. Choose one.
	
	#F2 = 0.3660254037844386 # 0.5*(Math.sqrt(3.0)-1.0); <-- IDLE gives me 0.3660254037844386 instead of what I had -- the lower-precision 0.36602540378 ... I clearly made a mistake while putting the formula into Google as an impromptu calculator substitute. Whatever, I hadn't considered putting the stuff in the base class at that time.
	#G2 = 0.21132486540518713 # (3.0-Math.sqrt(3.0))/6.0; apparently I copied it incorrectly. I had 2.71132486541 before I changed it to 0.21132486540518713
		
	## Trying out the math module for debugging purposes and it sort of makes it better anyways?
	F2 = ( 0.5 * (math.sqrt(3.0) - 1.0) )
	G2 = (  ( 3.0 - math.sqrt(3.0) ) / 6.0  )

	
	
	## There's a fastfloor algorithm in the Java code.
	## Whether or not any algorithm modifications like this in Python might help is currently beyond me and beyond my needs to implement this generator.
	## I'm skipping that.	
	
	
	
	
	
	def __init__(self, supplied_hash=255):
	
		## The following section initializes self.noise_array.
		## NOTE: The Java example just runs through the same list twice -- in Python this approach makes index errors with all the easy ways to do that behavior, so I'm using a separate Python implementation's technique of repeating the list twice, instead.
		## The list contains every integer from 0 to 255.
		self.noise_array_seed = [151,160,137,91,90,15, \
		131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,8,99,37,240,21,10,23, \
		190, 6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,35,11,32,57,177,33, \
		88,237,149,56,87,174,20,125,136,171,168, 68,175,74,165,71,134,139,48,27,166, \
		77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,55,46,245,40,244, \
		102,143,54, 65,25,63,161, 1,216,80,73,209,76,132,187,208, 89,18,169,200,196, \
		135,130,116,188,159,86,164,100,109,198,173,186, 3,64,52,217,226,250,124,123, \
		5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,189,28,42, \
		223,183,170,213,119,248,152, 2,44,154,163, 70,221,153,101,155,167, 43,172,9, \
		129,22,39,253, 19,98,108,110,79,113,224,232,178,185, 112,104,218,246,97,228, \
		251,34,242,193,238,210,144,12,191,179,162,241, 81,51,145,235,249,14,239,107, \
		49,192,214, 31,181,199,106,157,184, 84,204,176,115,121,50,45,127, 4,150,254, \
		138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,215,61,156,180]
		
		## Prep the noise_array variable for subsequent randomization. Remember, this is the __init__() for the generator. Things have to be initialized somewhere.
		self.noise_array = []
		
		## Hash number is a variable because someone might think to make the seed some other number than 255 and would want to change the hash to match.
		self.hash_number = supplied_hash

	
	
		## in Java I think you need to explicitly set the size of the array; not so in Python
		self.permutations_table       = []
		#self.permutations_table_Mod12 = []
	
	
			
		## Randomize the seed distribution (CURRENTLY DEBUGGING):
		self.randomize_the_noise_array_seed()
		
	

	
		## This may only be called after self.hash_number has been established.
		#self.generate_permutations_table()
	
	
	
	
	
	
	def generate_permutations_table(self):
	
		if self.hash_number == None:
			
			## Note that this presumes generate_permutations_table() will never be called when self.noise_array is zeroed out for regeneration or only half its normal size, which ought to always be the case.
			self.hash_number = ((len(self.noise_array) // 2) - 1)
			## The reasoning behind this is somewhat complex. It has to do with there being 512 numbers in the noise array...
			## which is constructed by taking the 256 numbers in the initial noise array and putting them in again on the end in the same order.
			## The noise array is that doubled size because of some sort of wraparound thing the simplex grid needs, I think.
			## But for the hash number, it needs to be 255 if there are 256 distinct values. Why, I forget, but it's somewhere in the logic behind needing a permutations_table.
			
	
		del self.permutations_table
	
		self.permutations_table = []
	
	
		## I changed 512 to 256 because it was giving me "list index out of range"
		## This was probably not a good idea but I'll figure out why once it gives me more meaningful results with its errors
		## ...
		## Comparing the java and python versions convinced me it should be the other way. Their tables are both supposed to be 512.
		## ...
		## Made hash number changeable.
		## Note that the permutations_table must be the size of the noise_array, since it is the table of permutations of that noise array's values, with a 1:1 correspondence (bijection??)
		for each_number in range(0, len(self.noise_array)):
		
			## 255 was what the Java code said, but 256 produces non-errored results. Why would it be 255 any not 256 anyways? Very strange! Is python's method of storing data really that different from Java's? Can a short in Java only be positive? Can a list in python only be positive?! Argh...
			## ...
			## Just use 255. The Python implementation doesn't have a Mod12 table...
			## I don't even know if it'll be faster, since I have to rehash everything every time I regenerate the array, anyways.
			## It's entirely possible the second table for modulus results is actually wasteful rather than helpful. Idk.
			## ...
			## In fact I think it raises bad new problems in Python, given my perhaps mistaken instinct to use self.noise_array in building the mod table rather than permutations_table which I think is what's supposed to be used in the Java program...
			## I'm going to drop the mod table and leave it here as evidence of my thought processes, for at least this version.
			self.permutations_table.append(self.noise_array[(each_number & self.hash_number)])
			




	def randomize_the_noise_array_seed(self, random_number_seed=None):		
			
		## Does not currently support random seeds. >_>
		## The parameter is there to inspire you to write it in, of course!
			
			
		## I bet handlers are un-Pythonic for some convoluted reason nobody bothered to explain to me.
		#noise_array_seed_handler = self.noise_array_seed
		## ^--- This didn't work because the assignment operation here made changes to noise_array_seed_handler propagate to self.noise_array_seed...
		## Which is undesirable for repeated randomizations.
		## Sooooo, instead, copy more explicitly:
		
		noise_array_seed_handler = []
		
		for each_number in self.noise_array_seed:
			noise_array_seed_handler.append(each_number)
		
		
		
		##print("DEBUG: noise_array_seed_handler == %s" % (str(noise_array_seed_handler)))
		
		new_noise_array = []
			
		## This whole function is about shuffling order of the noise array's contents while keeping the individual values of its contents the same.
		while len(noise_array_seed_handler) > 1:
			
			## + 1 because it needs to include the final index.
			## ...
			## Except random.randint DOES NOT work like range(x, y) -- it includes the zeroeth index and the maximum index, I think. Whyyyyy did they make it inconsistent!
			## ...
			## It's even worse -- it gave me out-of-range errors when it was simply nothing added or subtracted, too. Have to do - 1 to make it randomize properly.
			## This is something that should really be investigated when this routine is next improved.
			which_number_to_pick = random.randint(0, (len(noise_array_seed_handler) - 1))
			
			## DEBUGGING
			##print("len(noise_array_seed_handler) == %d\n  which_number_to_pick == %d" % (len(noise_array_seed_handler), which_number_to_pick))
			
			
			## Put the number at that index into the new_noise_array.
			new_noise_array.append(noise_array_seed_handler[which_number_to_pick])

			## Remove the number at that index from the list so this doesn't go on forever.
			noise_array_seed_handler.pop(which_number_to_pick)
			
		## The last one doesn't need and doesn't want to be randinted into existence.
		new_noise_array.append(noise_array_seed_handler[0])
			
		## Out with the old...	
		del self.noise_array
	
		## ... and in with the new:
		self.noise_array = new_noise_array
	
		## DEBUG
		##print("    Debug: self.noise_array == %s" % (str(self.noise_array)))
		## /DEBUG
	
		## The randomization call should be callable on its own, so include this to make it the proper length:
		self.double_the_noise_array()
	
		## This part is required because the permutations table draws from the noise array and is critical to making a new noise map. Forgot about that after taking a few days' break.
		## Always call generate_permutations_table() when the noise array is full and doubled.	
		self.generate_permutations_table()
	
		
		## Clean the list references:
		del noise_array_seed_handler
		del new_noise_array
		## ...
		## I think this step is likely to be unnecessary, but it rules out one problem I thought my current issue could have been.
	
	
	def double_the_noise_array(self):
		
		## Uses the supplied argument to construct a more Python-friendly way of handling the simplex noise seed.
		## This function supports the creation (and re-creation) of the noise array. Called in the noise generator's __init__() and reseed_noise() methods.
		
		noise_array_handler = []

		
		## I got an out-of-memory error when trying to call this on itself.
		## It just kept reading the array after it added all the numbers and looped endlessly. Oops.
		## Time to break out the handlers!
		## ...
		## After changing the range number to 3 and 1, it seems to not actually care about being doubled. o_o
		## Some day I'll know how simplex noise works. Eventually.
		## Untill then, we move onwards with the cargo cult programming boilerplate.
		for number_of_times_to_double_itself in range(0, 2):
			for each_number in self.noise_array:
				noise_array_handler.append(each_number)

				
		del self.noise_array
		
		
		self.noise_array = noise_array_handler
		

		
		
		
		
	def twodee_dot_product(self, supplied_gradient, x, y):
		## here I think I need to figure out what the grad class does
		## ...
		## I think it's just an object with a list of coords in it, like a MapTile.
		## Maaaaaybe.
		return ( (supplied_gradient[0] * x) + (supplied_gradient[1] * y) )
	
	
	
	
	
	def generate_octaved_noise(self, supplied_x, supplied_y, scale, octaves, persistence):
		
		'''
		
		From << http://code.google.com/p/battlestar-tux/source/browse/procedural/simplexnoise.py >>
		
		" 2D Multi-Octave Simplex noise.
		
		For each octave, a higher frequency/lower amplitude function will be added 
		to the original. The higher the persistence [0-1], the more of each
		succeeding octave will be added. "
			
		'''
		
		total_noise_for_this_cell = 0.0
		frequency = scale  # -_-
		amplitude = 1.0
		
		# " We have to keep track of the largest possible amplitude,
		# because each octave adds more, ad we need a value in [-1, 1]. "
		max_amplitude = 0.0
		
		for each_octave in range(octaves):
			
			new_x = supplied_x * frequency
			new_y = supplied_y * frequency
			
			total_noise_for_this_cell += ( self.generate_raw_unoctaved_noise(new_x, new_y) * amplitude )

			frequency *= 2.0
			
			max_amplitude += amplitude
			## max_amplitude is also what the total is divided by at the end.
			## This implies amplitude is some sort of average over all the iterations.
			
			
			amplitude *= persistence


		###print("  (total_noise_for_this_cell / max_amplitude) == " + str((total_noise_for_this_cell / max_amplitude)))
	
		return (total_noise_for_this_cell / max_amplitude)
	
	
	
	
	def generate_noise(self, supplied_x, supplied_y, scale, octaves, persistence, randseed=None):
	
		
		''' The gateway function for generate_octaved_noise(), this function makes sure the noise values are formatted according to the (array[y][x] == z) format used by my MapTile constructor. '''
	
		
		## IMPORTANT! I think there should be a reinitialize_noise_array() function called here.
		## That function would reshuffle or maybe change the hash value on the noise_array (the permutations table, per other sources).
		## ...
		## Ooooor maybe that should be optional, because we might want to generate a map from a specific hash.
		## I know: The hash should be changeable as a function outside this one that is invoked by the main program, like "rerandomized generator".
		## This function should also apply to the other generators too...
		## Perlin will be similar, plasma will be more of a hack involving saving state and giving that out unless a reset is requested, maybe?
		## Or perhaps plasma will be just the same and I'm forgetting something about the RNG calls there.
		## Check that.
		## ...
		## randomize_the_noise_array_seed() now handles randomization for this generator.
		## It may be supplied with a random seed... but only if some moxie-filled programmer supplies it with the ability to do that, first!
		
		## DEBUG
		##print("\n  Generating new array of simplex noise . . .\n")
		## /DEBUG
		
		self.randomize_the_noise_array_seed(random_number_seed=randseed)
	
		array_to_be_returned = []
	
		for each_y in range(0, supplied_y):
			
			new_row = []
			
			for each_x in range(0, supplied_x):
				
				new_z_value = self.generate_octaved_noise(each_x, each_y, scale, octaves, persistence)
				
				###print("    new_z_value == " + str(new_z_value))

				new_row.append(new_z_value)
			
			array_to_be_returned.append(new_row)
		
		##print("\n  New array of simplex noise has been generated.\n")
		
		## DEBUG
		##print("    array_to_be_returned == %s" % (str(array_to_be_returned)))
		## /DEBUG
		
		return array_to_be_returned
		
		
		
		
	def generate_raw_unoctaved_noise(self, supplied_x, supplied_y):
	
		## After some review...
		## The "skewing" is just multiplying the coord numbers by a constant so that everything we want to do on an x,y Cartesian board gets translated onto a simplex board.
		## i and j are the "coordinates" when translated into simplexese.
		## t uses G2 because it can't just do subtraction from the already-worked s value baked into i and j.
		## t is, I think, the Cartesian midpoint coordinate.
		## So essentially all the s, i, j, t, x0, y0 defining-lines are about getting simplex-to-Cartesian and vice versa translations.
	
	
	
	
		## "Skew the input space to determine which simplex cell we're in"
		s = (supplied_x + supplied_y) * self.F2	# they also said something about "hairy skew factor" ... wat.
			
		i = int((supplied_x + s))	# how is this supposed to work?!
			
		j = int((supplied_y + s))
		## I THINK the values of x and y are always 0 or 1... (?)
		## Which would be how all of these things can just add and subtract from eachother sensibly.
		## Maybe?!? This IS what I'm trying to find out by translating it from Java...
		## It isn't magic programming if I'm actually trying to understand how it works!
			
		t = (float(i + j) * self.G2)
	
	
	
		## "Unskew the cell origin back to (x, y) space" <--- "(x, y) space" means the whole Cartesian square coordinate thing, rather than... simplex-adjusted coordinates.
		unskewed_x_zero = (i - t)
		unskewed_y_zero = (j - t)
			
			
			
		## "The x,y distances from the cell origin" <--- by x,y they mean Cartesian rather than simplex-ian
		x0 = (supplied_x - unskewed_x_zero)
		y0 = (supplied_y - unskewed_y_zero)
			
			
		## "For the twodee case, the simplex shape is an equilateral triangle."
		## "Determine which simplex we are in."
		## i1, j1 are "offsets for second (middle) corner of simplex in (i, j) coords"
		## It's basically going top, right, bottom along the triangle, if I understand correctly.
		if x0 > y0:
			## "lower triangle, XY order: (0, 0) --> (1, 0) --> (1, 1)"
			i1 = 1
			j1 = 0
		else:
			## "upper triangle, YX order: (0, 0) --> (0, 1) --> (1, 1)"
			i1 = 0
			j1 = 1
	
			
			
		## "  A step of (1,0) in (i,j) means a step of (1-c,-c) in (x,y), and
		## a step of (0,1) in (i,j) means a step of (-c,1-c) in (x,y), where
		## c = (3-sqrt(3))/6  " ((c == G2))
	
	
		## "Offsets for second (middle) corner of simplex in (x,y) unskewed coords"
		x1 = (x0 - i1 + self.G2)
		y1 = (y0 - j1 + self.G2)
	
	
		## "Offsets for last corner in (x,y) unskewed coords"
		x2 = x0 - 1.0 + 2.0 * self.G2  # Why do people think not using parens on math is a good idea?
		y2 = y0 - 1.0 + 2.0 * self.G2  # I don't care about OoP. It's just sensible to give punctuation to that sort of thing. Someone COULD easily make a mistake, but with punctuation you trade the reader's interpretation time for safety, which is far better, imo.
	
	
	
		## "Work out the hashed gradient indices of the three simplex corners"
		## I think th
		## ...
		## I don't know why they would bother hashing it with 255.
		## Why does that even matter? Why not just do the operations on the base numbers?
			
		## It was 255 in the Java.
		## But I have no idea how that was supposed to work. Isn't it supposed to be 256 anyways?
		## ... the Python code I saw also uses 255 and had the 512 permutations buffer thing fixed by copying the array onto itself, which is what I'm gonna use, so I'll try the 255 thing again too.
		ii = int(i) & self.hash_number
		jj = int(j) & self.hash_number
	
	
		'''
		
		## NOTE: All of the following in this commented block is tainted by my mistaken mod table.
		## It was probably the reason I went through such trouble to debug it this way. Blah.
	
		####print("  Gradient DEBUG:\n  index of self.permutations_table[jj] == " + str(jj))
		####print("    Gradient DEBUG:\n    index of self.permutations_table_Mod12[(ii + self.permutations_table[jj])] == " + str((ii + self.permutations_table[jj])))
		####print("      Gradient DEBUG:\n      gradient_i_zero == " + str(self.permutations_table_Mod12[(ii + self.permutations_table[jj])]) + "\n")
		#gradient_i_zero = self.permutations_table_Mod12[ii + self.permutations_table[jj]]

		####print("  Gradient DEBUG:\n  index of self.permutations_table[(jj+j1)] == " + str((jj+j1)))
		####print("    Gradient DEBUG:\n    index of self.permutations_table_Mod12[(ii + i1 + self.permutations_table[(jj+j1)])] == " + str((ii + i1 + self.permutations_table[(jj+j1)])))
		####print("      Gradient DEBUG:\n      gradient_i_one == " + str(self.permutations_table_Mod12[(ii + i1 + self.permutations_table[(jj+j1)])]) + "\n")
		#gradient_i_one = self.permutations_table_Mod12[ii + i1 + self.permutations_table[jj+j1]]

		
		####print("  Gradient DEBUG:\n  index of self.permutations_table[(jj+j1)] == " + str((jj+j1)))
		####print("    Gradient DEBUG:\n    index of self.permutations_table_Mod12[(ii + 1 + self.permutations_table[(jj+1)])] == " + str((ii + 1 + self.permutations_table[(jj+1)])))
		####print("      Gradient DEBUG:\n      gradient_i_two == " + str(self.permutations_table_Mod12[(ii + 1 + self.permutations_table[(jj+1)])]) + "\n")
		#gradient_i_two = self.permutations_table_Mod12[ii + 1 + self.permutations_table[jj+1]]
	
	
		'''
		
		
		
		## Note that the 1 constants are balanced with omitted 0 constants in the lines with "missing" elements.
		gradient_i_zero = self.permutations_table[ii +      self.permutations_table[jj     ]] % 12
		gradient_i_one  = self.permutations_table[ii + i1 + self.permutations_table[jj + j1]] % 12	
		gradient_i_two  = self.permutations_table[ii +  1 + self.permutations_table[jj +  1]] % 12

		
			
		## "Calculate the contribution from the three corners"
		t0 = 0.5 - x0*x0 - y0*y0  # I really wish people would use parens in all multi-operator statements.
			
		if t0 < 0:
			n0 = 0.0
		else:
			t0 *= t0
				
			## " (x,y) of grad3 used for twodee gradient "
			###print("\n DEBUG:\n  t0 == " + str(t0) + "\n  twodee_dot_product == " + str(self.twodee_dot_product(self.grad3[gradient_i_zero], x0, y0)))
			n0 = t0 * t0 * self.twodee_dot_product(self.grad3[gradient_i_zero], x0, y0)
	
	
	
		t1 = 0.5 - x1*x1 - y1*y1
			
		if t1 < 0:
			n1 = 0.0
		else:
			t1 *= t1
			n1 = t1 * t1 * self.twodee_dot_product(self.grad3[gradient_i_one], x1, y1)
	
	
		###print("\nDEBUGGING x0 == " + str(x0))
		###print("DEBUGGING x1 == " + str(x1))
		###print("DEBUGGING x2 == " + str(x2))		
		
		###print("\nDEBUGGING y0 == " + str(y0))
		###print("DEBUGGING y1 == " + str(y1))
		###print("DEBUGGING y2 == " + str(y2))				
	
		###print("\nDEBUGGING (x2 * x2) == " + str((x2 * x2)))
		###print("DEBUGGING (y2 * y2) == " + str((y2 * y2)))
		###print("DEBUGGING ((x2 * x2) - (y2 * y2)) == " + str((x2 * x2) - (y2 * y2)))
		###print("DEBUGGING (0.5 - ((x2 * x2) - (y2 * y2))) == " + str((0.5 - ((x2 * x2) - (y2 * y2)))))
	
		## Apparently some clown thought it would be funny to allow order of operations to work all screwy in Java, or maybe someone sabatoged the code I was looking at.
		## I really couldn't guess why, but this was the original code, written in Java:
		## double t2 = 0.5 - x2*x2-y2*y2;
		## There were no parentheses anywhere there.
		
		t2 = 0.5 - x2*x2 - y2*y2
			
			
		###print("DEBUGGING t0 == " + str(t0))	
		###print("DEBUGGING t1 == " + str(t1))	
		###print("DEBUGGING t2 == " + str(t2))	
			
		
		## I think I understand it now! the t's are ticking down like octaves in the perlin generator, or something?
		## hrm it's multiplying, not dividing, so it couldn't get below zero that way unless it already was negative. ><
		## Nevermind. Still don't understand it yet.
		
		if t2 < 0:
			n2 = 0.0
		else:
			t2 *= t2
			n2 = t2 * t2 * self.twodee_dot_product(self.grad3[gradient_i_two], x2, y2)
	
			
			
		## "Add contributions from each corner to get the final noise value."
		## "The result is scaled to return values in the interval [-1, 1]."
		
		###print("\nDEBUGGING n0 == " + str(n0))
		###print("\nDEBUGGING n1 == " + str(n1))
		###print("\nDEBUGGING n2 == " + str(n2))		
		####print("\nDEBUGGING return " + str(70.0 * (n0 + n1 + n2)))
		
		#return 70.0 * (n0 + n1 + n2)
		

		number_to_return = ( 70.0 * (n0 + n1 + n2) )
		
		## My program would work better with a result scaled to 0-255. Therefore...		
		number_to_return += 1
		number_to_return *= 128.0
		## blah, getting NoneTypes after the octaves were added. Hrm...
		
		## debug:
		###print("\n number_to_return == " + str(number_to_return))
		
		return number_to_return
	
	
	
	
	
	

class DungeonMapGenerator:
	
	'''
	
	Generators for the creation of corridor-linked dungeon rooms for indoors maps.
	Output format uses z values to stand for different room types, eg: 0 = blocked 1 = unblocked 2 = corridor etc.
	
	'''
	
	
	## NOTE TO SELF!!
	## How to do FoV algorithm:
	## - Calculate a circle with a set radius (sight range) from the player's current position
	## - Find all MapTiles in that radius
	## - For each MapTile, draw a line from that MapTile to the player
	## - For each properly-rounded coordinate along that line (aligns to MapTile coords; partial cover? think on it...), check MapTiles with those coordinates for opacity
	## - If a MapTile with opacity is found, stop checking this line and set the MapTile whose line we're checking to "UNSEEN"
	
	
	
	
	def __init__(self, supplied_map_width=40, supplied_map_height=40, room_max_size=10, room_min_size=4, room_max_count=30, room_min_count=5):
	
		
		## Using the DungeonMapGenerator should always involve supplying some or all of these constants.
		## Defaults are being used here to make it simple for me to test and demonstrate.
		
	

		self.map_width = supplied_map_width
		self.map_height = supplied_map_height
		
		## -= 1 because doing it during room generation would be mildly wasteful -- the bottom and right edges must always be uncarved.
		## Doing it here, during the inits, guarantees that for all rooms and every map.
		self.map_width -= 1
		self.map_height -= 1		
		
		self.room_max_size = room_max_size
		self.room_min_size = room_min_size
		
		self.room_max_count = room_max_count
		self.room_min_count = room_min_count
	
	
	
	def check_these_two_rectangles_for_intersection(self, rectangle_alpha, rectangle_beta):
	
		''' Check two rectangles, both formatted [x, y, w, h] for intersection; return True if they intersect and False if they do not intersect. '''
		
		new_x  = rectangle_alpha[0]
		new_x2 = (rectangle_alpha[0] + rectangle_alpha[2])
		old_x  = rectangle_beta[0]
		old_x2 = (rectangle_beta[0] + rectangle_beta[2])
					
		new_y  = rectangle_alpha[1]
		new_y2 = (rectangle_alpha[1] + rectangle_alpha[3])
		old_y  = rectangle_beta[1]
		old_y2 = (rectangle_beta[1] + rectangle_beta[3])
		
		
		do_they_intersect = False
		
		
		
		if 	( (new_x >= old_x) and (new_x <= old_x2) ) or ( (new_x2 >= old_x) and (new_x2 <= old_x2) ):
						
			if 	( (new_y >= old_y) and (new_y <= old_y2) ) or ( (new_y2 >= old_y) and (new_y2 <= old_y2) ):
					
				do_they_intersect = True
						
							
		if 	( (old_x >= old_x) and (old_x <= new_x2) ) or ( (old_x2 >= new_x) and (old_x2 <= new_x2) ):
						
			if 	( (old_y >= new_y) and (old_y <= new_y2) ) or ( (old_y2 >= new_y) and (old_y2 <= new_y2) ):
					
				do_they_intersect = True
						
					
		## This if tree checks to see whether or not any rooms are forming crosses.
					
		if ((new_x >= old_x) and (new_x2 <= old_x2)) and ((new_y <= old_y) and (new_y2 >= old_y2)):
						
			do_they_intersect = True
						
						
		## ... and the same check in the other direction, for if the old room was the vertical bar of the cross rather than the new room, as is assumed in the preceding if tree:
		if ((old_x > new_x) and (old_x2 < new_x2)) and ((old_y < new_y) and (old_y2 > new_y2)):
						
			do_they_intersect = True
						
		
		return do_they_intersect
		
	
	
	
	
	
	def define_corridor(self, which_orientation, x, y, x2, y2):
		
		''' Create a corridor (actually a one-tile-by-n-tiles rectangular room) connecting point (x, y) and point ((x + w), (y + h)), using the rectangular room definition format. '''

		w = x2 - x
		h = y2 - y
		

		
		
		if which_orientation == 'horizontal':
			if w < 0:
				## ((This fix worked perfectly! Hooray))
				## If it's negative, flip it and deduct it from the index.
				## DO NOT put this before the orientation check, it doesn't need to care about which direction it isn't doing, and since it gets that info anyways it would just mess it up to flip and deduct in a direction it isn't going in (because that direction is the constant 1, see below).
				w *= -1
				x -= w
			## (x, y, width, height)
			new_corridor = [x, y, w + 1, 1]
			
		
		## Yes, it could be handled in less verbose ways.
		## This way makes it blindingly obvious what the code is supposed to do, which I prefer.
		## Code ought to be easy to maintain.
		
		if which_orientation == 'vertical':
			if h < 0:
				## If it's negative, flip it and deduct it from the index.
				## DO NOT put this before the orientation check, it doesn't need to care about which direction it isn't doing, and since it gets that info anyways it would just mess it up to flip and deduct in a direction it isn't going in (because that direction is the constant 1, see below).
				h *= -1
				y -= h
			## (x, y, width, height)		
			new_corridor = [x, y, 1, h + 1]
	
	
		return new_corridor
	

	def return_the_center_of_this_rectangle(self, upperleft_x, upperleft_y, width, height):

		
		centerpoint_x = ( upperleft_x + (width // 2) )
		centerpoint_y = ( upperleft_y + (height // 2) )
	
		return centerpoint_x, centerpoint_y
	
	
	
	
		
	def generate_noise(self, supplied_map_width=None, supplied_map_height=None, room_max_size=None, room_min_size=None, room_max_count=None, room_min_count=None):
		
		''' It's noise that looks like a dungeon map. If R2-D2 sneezed, this would be the random pattern left on the tissue. '''

		#### Arranging the generation parameters ####
		
		## All the generators save the state of the last map made.
		## The generate_noise() method of each generator accepts new parameters every time it's called, but if none are given, it goes back to the last parameters the generator worked with.
		## This makes it easy to implement deterministic map regeneration from randseeds.
		
		## -= 1 for the same reasoning as in the inits.
		if supplied_map_width != None:
			supplied_map_width -= 1
			self.map_width = supplied_map_width
		if supplied_map_height != None:
			supplied_map_height -= 1
			self.map_height = supplied_map_height
			
		if room_max_size != None:
			self.room_max_size = room_max_size
		if room_min_size != None:
			self.room_min_size = room_min_size
			
		if room_max_count != None:
			self.room_max_count = room_max_count
		if room_min_count != None:
			self.room_min_count = room_min_count		


			


	
	
		#### Generating the map ####
		
		## First, make a map full of zeroes. The rooms will be carved out of it.
		## Remember, every NoiseMapGenerator returns results formatted: map[y][x] == z
	
		
		new_dungeon_map = []
		
		for each_row in range(0, self.map_height):
		
			new_row = []
			
			for each_column in range(0, self.map_width):
				
				new_row.append(0)
			
			new_dungeon_map.append(new_row)
			
			

		## List comprehension method:
		## new_dungeon_map = [[ 0 for y in range(0, self.supplied_map_height)] for x in range(0, self.supplied_map_width)]
		## Try this and see how it goes.
		
		

		#### Generating room coordinates ####

		## DEBUG
		#number_of_corridors_at_map_finish = 0
		## \DEBUG
		
		## There must be at least room_min_count rooms in the end product.
		are_there_enough_rooms_yet = False
		
		while are_there_enough_rooms_yet == False:
		
			list_of_rooms = []
					

					
			for each_room_attempt_number in range(0, self.room_max_count):
				
				
				## DEBUG: Since walls are uncarved space, should the x and y randints begin at 1 or 0?
				## Watching the output process will solve this issue quickly.
				## ...
				## This issue needs to be straightened out early on due to how intersection tests have to work.
				## Only two edges need to have uncarved space in them, and every room will have those two edges uncarved.
				## I decree those two edges to be the lower and right edges.
				## The map will have upper and left edges uncarved so that any rooms at the edge of the map are properly walled.
				## Thus the randints will begin at 1 (the upper and left edges)...
				## and end at map_width and map_height, instead of (m_w - 1) and (m_h - 1).
				## By letting rooms gen to the edges with their width and height values, they can sit on an edge with their two designated built-in edge walls and everything will be fine.
				
				new_room_width = random.randint(self.room_min_size, self.room_max_size)
				new_room_height = random.randint(self.room_min_size, self.room_max_size)
				
				new_room_upperleft_x = random.randint(1, self.map_width - new_room_width)
				new_room_upperleft_y = random.randint(1, self.map_height - new_room_height)
		
				## [x, y, w, h]
				new_room = [new_room_upperleft_x, new_room_upperleft_y, new_room_width, new_room_height]
				
				
				## The checks for validity favor x,y modification first -- and always pushing it to the lower right --
				## and w,h modification second -- and always pushing it to the upper left --
				## because this should lead to a mild tendency for rooms to cluster, and towards the center, at that.
				## Which I think will look nice.
				## ...
				## or that's what I'd like to do, but not on the first implementation.
				
				
				## Checking to see if the rooms intersect:
					
				failed_intersection_test = False
				
				for each_other_room in list_of_rooms:
					
					if self.check_these_two_rectangles_for_intersection(new_room, each_other_room) == True:
					
						failed_intersection_test = True
					
					
				if failed_intersection_test == False:
					
					list_of_rooms.append(new_room)
		
		
		
			if len(list_of_rooms) >= self.room_min_count:
			
				are_there_enough_rooms_yet = True
		
			else:
				
				del list_of_rooms
		
		
		
		
		#### Carving successful room coordinates ####
	
		
		## Someone told me using range(foo, len(list)) is un-Pythonic, so I'm using an iterator to step through the list in parallel for the purposes of creating corridors to connect rooms.
		room_creation_iterator = -1

		for each_completed_room in list_of_rooms:
			
			for each_x_coordinate in range(each_completed_room[0], (each_completed_room[0] + each_completed_room[2])):
	
				for each_y_coordinate in range(each_completed_room[1], (each_completed_room[1] + each_completed_room[3])):
					
					## This conditional seems a bit hackish.
					if new_dungeon_map[each_y_coordinate][each_x_coordinate] == 0:
						## This is so simple it's bound to fail miserably.
						## ...
						## And yet it works.
						new_dungeon_map[each_y_coordinate][each_x_coordinate] += 1
	
			## Connect every room with corridors. (Note that there may be dungeons where this trait is not desirable for some reason; other behavior may be added as desired.)
			## Generate a random direction for the corridors to point in:
			which_direction_first = random.randint(0, 1) # remember, random.randint() includes min and max values, unlike range()
			
			
			#define_corridor(which_orientation, x, y, x2, y2)
			## Note: Corridors are created from the current room to the next room even though the next room hasn't actually be written in yet.
			## It works because the rooms already exist as rectangle coordinates.
			## This is likely to cause debugging confusion if you try to change this code without taking that into account. Be advised.
			
			## Find the centerpoints of both rooms and pack them as tuples.
			## Syntax is [ ( (list_of_rooms[n][w] // 2) + list_of_rooms[n][x] ), ( (list_of_rooms[n][h] // 2) + list_of_rooms[n][y] ) ]
			## Values resulting from this look like x, y and are just the centerpoints of the two rooms.
			## Another representation: [(width // 2 + x offset), (height // 2 + y offset)]
			## ...
			## If desired, it's possible to change this to use floor divide + 1 instead of just floor divide.
			## That would make it so that rooms with a thickness of 1 do not have projections off their sides.
			## Corridors would slice into the center of the room rather than the rounded-down center.
			#room_alpha_center = [ ( (list_of_rooms[room_creation_iterator][2] // 2) + list_of_rooms[room_creation_iterator][0] ), ( (list_of_rooms[room_creation_iterator][3] // 2) + list_of_rooms[room_creation_iterator][1] ) ]
			#room_beta_center =  [ ( (list_of_rooms[room_creation_iterator + 1][2] // 2) + list_of_rooms[room_creation_iterator + 1][0] ), ( (list_of_rooms[room_creation_iterator + 1][3] // 2) + list_of_rooms[room_creation_iterator + 1][1] ) ]
			
			## Redoing this to make my dungeon generator cooler.
			## Now, rooms will connect to the nearest two rooms, by centerpoint value!
			## Or one or zero rooms, as in the case for the second and first rooms created.
			## This should make tunnel connections a whole lot more friendly-looking.
			
			## The way we're going to do this is:
			## For each room in the rooms list:
			## Use my new return_the_center_of_this_rectangle() method on every room in the rooms list and compare their centers to the room currently being considered
			## The nearest two rooms that do not have centerpoints equal to the room being considered will be used as anchors for the define_corridor() method.
			
			
			
			
			the_centerpoint_of_this_room = self.return_the_center_of_this_rectangle()
			
			
			
			
			## DEBUG
			#print("\n  room_alpha_center == %s\n  room_beta_center == %s" % (str(room_alpha_center), str(room_beta_center)))
			## \DEBUG
			
			if which_direction_first == 0:
				## DEBUG
				#number_of_corridors_at_map_finish += 1
				## \DEBUG
				
				## It needs to take room alpha center and drag it out to room beta center in only the horizontal direction.
				## That's why vertical is as easy as swapping reference order to the rooms.
				## define_corridor() still needs a direction because I chose not to make it implicit by unpacking the centerpoint tuple here. I think it's more readable this way.
				## ...
				## Something is totally wrong here. This only works if alpha centerpoint > beta centerpoint because otherwise you get negative widths or something and that can't be drawn in can it?
				## Maybe it can? Let's try it and see what fails.
				new_horizontal_corridor = self.define_corridor('horizontal', room_alpha_center[0], room_alpha_center[1], room_beta_center[0], room_beta_center[1])
				new_vertical_corridor = self.define_corridor('vertical', room_beta_center[0], room_beta_center[1], room_alpha_center[0], room_alpha_center[1])

			
			elif which_direction_first == 1:
				## DEBUG
				#number_of_corridors_at_map_finish += 1
				## \DEBUG
				
				new_horizontal_corridor = self.define_corridor('horizontal', room_beta_center[0], room_beta_center[1], room_alpha_center[0], room_alpha_center[1])
				new_vertical_corridor = self.define_corridor('vertical', room_alpha_center[0], room_alpha_center[1], room_beta_center[0], room_beta_center[1])
			
			#print("\n    new_horizontal_corridor == %s\n    new_vertical_corridor == %s" % (str(new_horizontal_corridor), str(new_vertical_corridor)))
			

			## When the next-to-last room is connected to the last room, reset the iterator to 0 so that the last room may be connected to the first room.
			## NOTE! Linear dungeons should stop corridor creation when the next-to-last room is connected to the last room.
			
			## DEBUG
			#print("\n room_creation_iterator == %d\n len(list_of_rooms == %d" % (room_creation_iterator, len(list_of_rooms)))
			## \DEBUG

			if ( room_creation_iterator < (len(list_of_rooms) - 2) ):
				# plus equals to, NOT set equals to (incrementing, not rolling over)
				room_creation_iterator += 1
			else:
				# set equals to, NOT minus equals to (rolling over, not incrementing)
				room_creation_iterator = -1


			
			## This should probably be turned into a create_room() method.
			## First horizontal:
			
			## DEBUG
			#print("\nnew_horizontal_corridor[0] == %d\nnew_horizontal_corridor[2] == %d\nnew_horizontal_corridor[0] + [2] == %d" % (new_horizontal_corridor[0] ,new_horizontal_corridor[2], (new_horizontal_corridor[0] + new_horizontal_corridor[2])))
			#print("\nnew_horizontal_corridor[1] == %d\nnew_horizontal_corridor[3] == %d\nnew_horizontal_corridor[1] + [3] == %d" % (new_horizontal_corridor[1], new_horizontal_corridor[3], (new_horizontal_corridor[1] + new_horizontal_corridor[3])))
			## \DEBUG
			
			for each_horizontal_corridor_x_coordinate in range(new_horizontal_corridor[0], (new_horizontal_corridor[0] + new_horizontal_corridor[2])):		
				
				for each_horizontal_corridor_y_coordinate in range(new_horizontal_corridor[1], (new_horizontal_corridor[1] + new_horizontal_corridor[3])):		
					
					## If it's already walkable, don't turn it debug mauve.
					if new_dungeon_map[each_horizontal_corridor_y_coordinate][each_horizontal_corridor_x_coordinate] == 0:					
						new_dungeon_map[each_horizontal_corridor_y_coordinate][each_horizontal_corridor_x_coordinate] += 1

			## Second vertical:		
			
			## DEBUG
			#print("\nnew_vertical_corridor[0] == %d\nnew_vertical_corridor[2] == %d\nnew_vertical_corridor[0] + [2] == %d" % (new_vertical_corridor[0], new_vertical_corridor[2], (new_vertical_corridor[0] + new_vertical_corridor[2])))
			#print("\nnew_vertical_corridor[1] == %d\nnew_vertical_corridor[3] == %d\nnew_vertical_corridor[1] + [3] == %d" % (new_vertical_corridor[1], new_vertical_corridor[3], (new_vertical_corridor[1] + new_vertical_corridor[3])))
			## \DEBUG
			
			for each_vertical_corridor_x_coordinate in range(new_vertical_corridor[0], (new_vertical_corridor[0] + new_vertical_corridor[2])):		
				
				for each_vertical_corridor_y_coordinate in range(new_vertical_corridor[1], (new_vertical_corridor[1] + new_vertical_corridor[3])):		
					
					## If it's already walkable, don't turn it debug mauve.
					if new_dungeon_map[each_vertical_corridor_y_coordinate][each_vertical_corridor_x_coordinate] == 0:
						new_dungeon_map[each_vertical_corridor_y_coordinate][each_vertical_corridor_x_coordinate] += 1
					
		## DEBUG
		#print("\n        number_of_corridors_at_map_finish == %d\n        len(list_of_rooms) == %d" % (number_of_corridors_at_map_finish, len(list_of_rooms)))
		## \DEBUG
	
		return new_dungeon_map
		
	
	
	
	
	
	
	
	
	
class RoomFilledMapGenerator:


	## I don't like this generator. It is not worth the effort right now. Keeping it for legacy/future inspiration purposes.



	## To start, this code will be somewhat copypasted from DungeonMapGenerator. Mostly just the inits and some grid work.


	def __init__(self, supplied_map_width=40, supplied_map_height=40, room_max_size=10, room_min_size=4):
	
		
		## Using the RoomFilledMapGenerator should always involve supplying some or all of these constants.
		## Defaults are being used here to make it simple for me to test and demonstrate.
		
	
		## DEBUG
		## Let's see if storing new_dungeon_map as state magically solves it. Woooo
		## Nope, not in the least. And yes I did put in self.* tags on every reference in this class's generate_noise() method.
		#self.new_dungeon_map = []
		## \DEBUG
	
	

		self.map_width = supplied_map_width
		self.map_height = supplied_map_height
		
		## -= 1 because doing it during room generation would be mildly wasteful -- the bottom and right edges must always be uncarved.
		## Doing it here, during the inits, guarantees that for all rooms and every map.
		## DEBUG COMMENTED
		## The following adjustment is unnecessary with the way I've structured my code now. Good.
		#self.map_width -= 1
		#self.map_height -= 1		
		## \DEBUG COMMENTED
	
		## This generator does not need min/max room count settings, but it wouldn't be all that difficult to add them as some sort of conditional'd loop.
		
		
		
		
	def generate_noise(self, supplied_map_width=None, supplied_map_height=None, room_max_size=None, room_min_size=None):
		
		''' It's sorta like noise. Except blocky and in all these clean straight lines and right angles. '''

		#### Arranging the generation parameters ####
		
		## All the generators save the state of the last map made.
		## The generate_noise() method of each generator accepts new parameters every time it's called, but if none are given, it goes back to the last parameters the generator worked with.
		## This makes it easy to implement deterministic map regeneration from randseeds.
		
		if supplied_map_width != None:
			## -= 1 for the same reasoning as in the inits.
			## Is unnecessary with the way I've structured my code now.
			## DEBUG COMMENTED
			#supplied_map_width -= 1
			## \DEBUG COMMENTED
			self.map_width = supplied_map_width
			
		if supplied_map_height != None:
			## Is unnecessary with the way I've structured my code now.
			## DEBUG COMMENTED
			#supplied_map_height -= 1
			## \DEBUG COMMENTED
			self.map_height = supplied_map_height
			
		if room_max_size != None:
			self.room_max_size = room_max_size
		if room_min_size != None:
			self.room_min_size = room_min_size
			
		## Room count will be determined by the other parameters since the map will be filled with rooms.
		
		

		

	
	
		#### Generating the map ####
		
		## First, make a map full of zeroes. The rooms will be carved out of it.
		## Remember, every NoiseMapGenerator returns results formatted: map[y][x] == z
			
			
		## Refactoring this might involve making a generate_blank_map() method.
		## It would also be useful for DungeonMapGenerators.
		## Maybe DungeonMapGenerator should be a base class and these room-based map generators would all draw from it.
		
		
		
		new_dungeon_map = []
		
		for each_row in range(0, self.map_height):
		
			new_row = []
			
			for each_column in range(0, self.map_width):
				
				new_row.append(0)
			
			new_dungeon_map.append(new_row)
			
			
		## List comprehension version:
		## new_dungeon_map = [[ 0 for y in range(0, self.supplied_map_height)] for x in range(0, self.supplied_map_width)]
		## Try this and see how it goes.
		
				
		
		
		
		#### Filling the blank map with rooms ####
		
		
		## I seriously don't understand why you wouldn't want to do for loops with index numbers. It makes dealing with the data SO much easier!
		for each_row_index in range(1, (len(new_dungeon_map) - 1)):
		
			
			for each_column_index in range(1, (len(new_dungeon_map[each_row_index]) - 1)):
			
				## IMPORTANT!
				## The syntax is the same for all of these map generators:
				##
				##      new_dungeon_map[y][x] == z
				##
				## If there is some confusion about row/column stuff or sublist ordering, remember to compare it to this fact.
				
			
				#### ATTEMPT NUMBER TWO ####
				
				## I'm just beating my hands on the keyboard and code is coming out
			
			
				## Initialize the validator variable:
				should_we_start_a_room_here = 1

				
				## Whip up a potential room:
				new_room_width = random.randint(self.room_min_size, self.room_max_size)#(4, 10) # <-- does not help at all
				new_room_height = random.randint(self.room_min_size, self.room_max_size)#(4, 10) # :(
				
				## Now check if the width or height go out of bounds and adjust to fit if possible; if not possible, set the validator toggle to False:
				if (each_column_index + new_room_width) >= (len(new_dungeon_map[each_row_index]) - 1): # len(map[row]) because we're checking this particular row's width, and -1 because of uncarved side 
					
					difference_between_maximum_room_width_and_attempted_room_width = ( each_column_index + new_room_width - (len(new_dungeon_map[each_row_index]) - 1) )
					new_room_width -= difference_between_maximum_room_width_and_attempted_room_width
					
					if new_room_width < self.room_min_size:
						should_we_start_a_room_here = 0
					
				if (each_row_index + new_room_height) >= (len(new_dungeon_map) - 1): # len(map) because we're checking the height of columns in this map, and -1 because of uncarved side 
					
					difference_between_maximum_room_height_and_attempted_room_height = ( each_row_index + new_room_height - (len(new_dungeon_map) - 1) )
					new_room_height -= difference_between_maximum_room_height_and_attempted_room_height
					
					if new_room_height < self.room_min_size:
						should_we_start_a_room_here = 0		
			
			
				## Determine if this is a good starting tile for a room:
				
				for each_nearby_tile_y in range(-1, 2):
				
					for each_nearby_tile_x in range(-1, 2):

						## Check every tile adjacent to the current tile (and the current tile, too) for carved space and Falsitivize the validator if any is found:
						if new_dungeon_map[(each_row_index + each_nearby_tile_y)][(each_column_index + each_nearby_tile_x)] != 0:
							
							should_we_start_a_room_here = 0
				
				
				## Next, check and see if this room will slice into another room at any point along its prospective length:
							
				
				## Init/reset the width decrementor:
				room_max_width = 0
			
				continue_incrementing_room_width = True
			
				## range(-1, 2) should step through (-1, 0, 1), ie (up, same, down) or (left, same, right)
				for each_next_unit_of_width in range(0, new_room_width):
				
					should_we_increment_room_max_width_by_one_tile = False
					
					for each_nearby_tile_y in range(-1, 2):
				
						for each_nearby_tile_x in range(-1, 2):

							## Check every tile adjacent to the current tile (and the current tile, too) for carved space and Falsitivize the validator if any is found:
							if continue_incrementing_room_width == True and new_dungeon_map[(each_row_index + each_nearby_tile_y)][(each_column_index + each_nearby_tile_x) + each_next_unit_of_width] == 0:
							

								#print("  INCREMENTING decrementor. checked tile == %d" % (new_dungeon_map[(each_row_index + each_nearby_tile_y)][(each_column_index + each_nearby_tile_x) + each_next_unit_of_width]))
						
								should_we_increment_room_max_width_by_one_tile = True
						
							else:
								
								
								continue_incrementing_room_width = False
								#print("  NOT incrementing decrementor. checked tile == %d" % (new_dungeon_map[(each_row_index + each_nearby_tile_y)][(each_column_index + each_nearby_tile_x) + each_next_unit_of_width]))
						
					if should_we_increment_room_max_width_by_one_tile == True and continue_incrementing_room_width == True:
							
						room_max_width += 1
			
				## Apply the decrementor and check if the room is too small:
				
				#print("\nnew_room_width == %d\n  room_width_decrementor == %d" % (new_room_width, room_width_decrementor))
				
				new_room_width = room_max_width
				
				#print("    new_room_width == %d" % (new_room_width))
				
				#print("      self.min_room_size == %d" % (self.room_min_size))
				
				if new_room_width < self.room_min_size:
					
					
					
					## Then the smallest possible room had to become too small to fit here and this tile should be skipped.
					should_we_start_a_room_here = 0
					
					#print("        should_we_start_a_room_here == %r" % (should_we_start_a_room_here))
				
				#else:
					
					
					#print("\nnew_room_width == %d\n  room_width_decrementor == %d" % (new_room_width, room_width_decrementor))
				
					#print("      self.min_room_size == %d" % (self.room_min_size))
				
					#print("             (t) should_we_start_a_room_here == %r" % (should_we_start_a_room_here))
				
				
				## Duplicating the width decrementor code even though it should never be necessary... o_o
				## ...
				## It runs but it didn't fix the problem. Still bizarre.
				
				
				## Init/reset the height decrementor:
				room_height_decrementor = 0
			
				## range(-1, 2) should step through (-1, 0, 1), ie (up, same, down) or (left, same, right)
				for each_next_unit_of_height in range(0, new_room_height):
				
					should_we_decrement_room_height_by_one_tile = False
					
					for each_nearby_tile_y in range(-1, 2):
				
						for each_nearby_tile_x in range(-1, 2):

							## Check every tile adjacent to the current tile (and the current tile, too) for carved space and Falsitivize the validator if any is found:
							if new_dungeon_map[(each_row_index + each_nearby_tile_y) + each_next_unit_of_height][(each_column_index + each_nearby_tile_x)] != 0:
							

								#print("  INCREMENTING decrementor. checked tile == %d" % (new_dungeon_map[(each_row_index + each_nearby_tile_y)][(each_column_index + each_nearby_tile_x) + each_next_unit_of_width]))
						
								should_we_decrement_room_height_by_one_tile = True
						
							#else:
								#print("  NOT incrementing decrementor. checked tile == %d" % (new_dungeon_map[(each_row_index + each_nearby_tile_y)][(each_column_index + each_nearby_tile_x) + each_next_unit_of_width]))
						
					if should_we_decrement_room_height_by_one_tile == True:
							
						room_height_decrementor += 1


						
			
				new_room_height -= room_height_decrementor				
				
				
				
				
				if new_room_height < self.room_min_size:
					
					
					
					## Then the smallest possible room had to become too small to fit here and this tile should be skipped.
					should_we_start_a_room_here = 0				
				
				
				
				#if should_we_start_a_room_here == 0:
				#	new_room_height = 0
				#	new_room_width = 0
				
				
				
				## Now that all checks have been passed, write the room to the map.
				if should_we_start_a_room_here == 1:
					
					for each_new_room_height_index in range(0, new_room_height):
					
						for each_new_room_width_index in range(0, new_room_width):
							
							new_dungeon_map[each_row_index + each_new_room_height_index][each_column_index + each_new_room_width_index] += 1
				
				else:
					
					pass
			



		return new_dungeon_map	
			
			
			
		'''
			
				#### ATTEMPT NUMBER ONE ####
			
				
				## Failed due to indexing or insufficient/incorrect tile validation.
				## IMPORTANT! This code all assumes tile validation begins iterating one tile right and one tile down and fills a map of zeroes of exactly the right size.
				
			
				## Let's switch to serial checks with a toggle rather than nested checks with a base case.
				## This will make it very easy to add and remove conditionals to alter how rooms are validated.
				
				
				should_we_start_a_room_on_this_tile = True
				
				if new_dungeon_map[each_row_index][each_column_index] != 0:
					## Then the current tile is carved and unusable.
					should_we_start_a_room_on_this_tile = False
				
				if new_dungeon_map[each_row_index][each_column_index + 1] != 0:
					## The next tile to the right is carved.
					should_we_start_a_room_on_this_tile = False

				if new_dungeon_map[each_row_index - 1][each_column_index] != 0:
					## The tile above the current tile is carved.
					should_we_start_a_room_on_this_tile = False				
					
				if new_dungeon_map[each_row_index][each_column_index - 1] != 0:
					## The tile to the left of the current tile is carved.
					should_we_start_a_room_on_this_tile = False					

				if new_dungeon_map[each_row_index - 1][each_column_index - 1] != 0:
					## The tile above and to the left of the current tile is carved.
					should_we_start_a_room_on_this_tile = False		

				if new_dungeon_map[each_row_index - 1][each_column_index + 1] != 0:
					## The tile above and to the right of the current tile is carved.
					should_we_start_a_room_on_this_tile = False							
					
				## The absurdity gallery. Should be logically impossible to get any hits here whatsoever.	
				if new_dungeon_map[each_row_index + 1][each_column_index] != 0:	
					should_we_start_a_room_on_this_time = False
				if new_dungeon_map[each_row_index + 1][each_column_index + 1] != 0:	
					should_we_start_a_room_on_this_time = False
				if new_dungeon_map[each_row_index + 1][each_column_index - 1] != 0:	
					should_we_start_a_room_on_this_time = False					
			
			
				## There has to be a check to see if the tile is fewer than self.room_min_size tiles away from the right and bottom edges of the map.
				## We will take this opportunity to define these handy and descriptive variables:
				##
				## DEBUG - 1 on the end of this? Yes or no? To handle uncarved space on the bottom+right sides... this should be what makes it uncarved, if included here.
				##
				distance_from_left_of_room_to_right_of_map = (self.map_width - each_column_index)
				distance_from_top_of_room_to_bottom_of_map = (self.map_height - each_row_index)
							
				## Check to see if the room's min size is too large for its seed location:
				if self.room_min_size >= distance_from_left_of_room_to_right_of_map:
					## This tile is too close to the right side of the map to be placed here.
					should_we_start_a_room_on_this_tile = False
				
				if self.room_min_size >= distance_from_top_of_room_to_bottom_of_map:
					## This tile is too close to the bottom of the map to be placed here.	
					should_we_start_a_room_on_this_tile = False

			
				## Get how wide and tall the room wants to be, so we can check it against its neighbors and the map edges:
				random_room_width = random.randint(self.room_min_size, self.room_max_size)
				random_room_height = random.randint(self.room_min_size, self.room_max_size)
				#random_room_height = 6		
						
				## If the tile is too close to the edge to fulfill its randomly generated width, decrement it untill it just fits.
				## Note: This step happens before the next validation step because if it didn't the room would generate an index-out-of-range error there.
				if random_room_width >= distance_from_left_of_room_to_right_of_map:

					random_room_width -= (random_room_width - distance_from_left_of_room_to_right_of_map)

				if random_room_height >= distance_from_top_of_room_to_bottom_of_map:

					random_room_height -= (random_room_height - distance_from_top_of_room_to_bottom_of_map)

								
								
				## Something is ridiculously wrong in the below code, but I have no idea what.
				## It's still generating overlaps even though I've put in all the conditionals that are supposed to make it not do that.				
								
				## To prevent the decrementer in the following for loop from clipping its own loop too short. I think.				
				random_room_width_adjustment_handler = 0				
								
				## random_room_width + 1 is the upperleft coordinate, the span of the room, and the wall on the right.	
				for each_next_tile_index in range(0, (random_room_width + 2)):
				
					## The following line of code (plus one or two index offsets) took quite some time to figure out was needed.
					if ((each_next_tile_index + each_column_index) <= (self.map_width - 1)):
					
						if (new_dungeon_map[each_row_index][(each_column_index + each_next_tile_index)] != 0) or (new_dungeon_map[(each_row_index - 1)][(each_column_index + each_next_tile_index)] != 0) or (new_dungeon_map[(each_row_index - 1)][(each_column_index + each_next_tile_index)] != 0):
							## Then something's in the way. Decrement the room's actual size.
							## ...
							## This used to be decrementing random_room_width, which I think made it end the for loop too early. Changing to a handler to disconnect those parts.
							## ...
							## I don't think that solved it. It SHOULDN'T solve it regardless. Leaving it in just to be safe. Refactor it out later.
							random_room_width_adjustment_handler += 1

				## DEBUG
				#if random_room_width_adjustment_handler > 0:
				#	random_room_width_adjustment_handler += 0
				## \DEBUG
				
				## Apply the accrued adjustment.
				random_room_width -= random_room_width_adjustment_handler

					
				## One final check to ensure the previous validation step did not make the room too small:		
				if random_room_width <= self.room_min_size:
					should_we_start_a_room_on_this_tile = False
			
				## DEBUG
				## Direct checking for intersection after the room is defined.
				## Even though it solves all the debug mauve, it doesn't fix the inappropriate abuttment issue, and it also doesn't fill the map as cleanly as resizing rooms if they're too big.
				
				#for each_new_tile_y_offset in range(0, random_room_height):
						
				#	for each_new_tile_x_offset in range(0, random_room_width):			
						
				#		if new_dungeon_map[(each_row_index + each_new_tile_y_offset)][(each_column_index + each_new_tile_x_offset)] != 0:
							
				#			should_we_start_a_room_on_this_tile = False
				## \DEBUG
			
				
				
				## Another absurdity gallery -- the following should never turn up any hits due to logic.
				random_room_height_adjustment_handler = 0				

				for each_next_tile_index in range(0, (random_room_height + 2)):

					if ((each_next_tile_index + each_row_index) <= (self.map_height - 1)):
					
						if (new_dungeon_map[each_row_index + each_next_tile_index][(each_column_index)] != 0) or (new_dungeon_map[(each_row_index + each_next_tile_index)][(each_column_index + 1)] != 0) or (new_dungeon_map[(each_row_index + each_next_tile_index)][(each_column_index - 1)] != 0):

							random_room_height_adjustment_handler += 1				

							
				random_room_height -= random_room_height_adjustment_handler

				if random_room_height <= self.room_min_size:
					should_we_start_a_room_on_this_tile = False				
				
				
				
				
				

				
				## If it passes all the checks, write the room to the map.
				if should_we_start_a_room_on_this_tile == True:
					
					for each_new_tile_y_offset in range(0, random_room_height):
						
						for each_new_tile_x_offset in range(0, random_room_width):
							
							if new_dungeon_map[(each_row_index + each_new_tile_y_offset)][(each_column_index + each_new_tile_x_offset)] >= 1:
								## DEBUG
								print("Error: Mauve for random_room_width %d, random_room_height %d\n                   min_size %d max_size %d" % (random_room_width, random_room_height, self.room_min_size, self.room_max_size))
								## \DEBUG
							
							new_dungeon_map[(each_row_index + each_new_tile_y_offset)][(each_column_index + each_new_tile_x_offset)] += 1
			
			

		return new_dungeon_map						
								
		'''						
							
			
		'''
		
				#### ATTEMPT NUMBER ZERO ####
				
				
				## Ugh, I don't know why none of this works.
				## The indices seem perfect on paper but changing one index makes the results better or worse in ways that don't make any obvious kind of sense.
				## I'm going to assume I made some error in figuring out what checking was needed.
				
				
				
				## Step 1
				if new_dungeon_map[each_row_index][each_column_index] == 0:
					
					
					## Theory section...
					## Imagine the algorithm makes a tall room, a wide room and another tall room on the first line.
					## When it passes through the second line it would need to:
					## 1. Detect uncarved space at (x, y)
					## 2. Check ((x + 1), y) for uncarved space
					## If False, then it's about to break into a room to the right; if True...
					## 3. Check ((x + 1), y - 1) for uncarved space
					## 3a If False, then it's a wall beneath a room; if True...
					## 4. Check ((x + 2), y) for uncarved space
					## 4a If False, then it's the end of a wall beneath a room and also abutting another room to the right.
					## 4b If True then this is a good spot to place a room as it is not going to be carving out a wall from any adjacent rooms.
					## ...
					## There needs to be a check-ahead to make the room actually fill all the space infront of it, x-ly speaking.
					## Or at least to make it easy to put an upper bound on the room width in this location.
					## A similar procedure may need to happen at the bottom of the map for height of the room.
					## ...
					## 5. For each in range(0, room_max_size): Check ((x + each), y) for uncarved space, return sum_of_this_loop
					## ... stuff.

		
					## Step 2
					if new_dungeon_map[each_row_index][(each_column_index + 1)] == 0:

						## Step 3
						if new_dungeon_map[(each_row_index - 1)][(each_column_index + 1)] == 0:
							
							## Step 4
							## DEBUG Let's throw more conditionals onto the last uniform step, here, to see if something is the right one:
							if (new_dungeon_map[each_row_index][(each_column_index + 2)] == 0) and (new_dungeon_map[each_row_index][each_column_index - 1] == 0) and (new_dungeon_map[each_row_index - 1][each_column_index - 1] == 0):


								## A good spot to place a room has been found.
								## Determine the limiting condition for the width and height randint ranges based on distance between room edge and map edge:
									
								distance_from_left_of_room_to_right_of_map = (self.map_width - each_column_index)
								distance_from_top_of_room_to_bottom_of_map = (self.map_height - each_row_index)
									
							
								random_room_width = random.randint(self.room_min_size, self.room_max_size)
								random_room_height = random.randint(self.room_min_size, self.room_max_size)
									
									
									
								## Forbidding the rooms to be larger than the map:
								if random_room_width >= distance_from_left_of_room_to_right_of_map:
									random_room_width = (distance_from_left_of_room_to_right_of_map - 1)

								if random_room_height >= distance_from_top_of_room_to_bottom_of_map:
									random_room_height = (distance_from_top_of_room_to_bottom_of_map - 1)

									
									
								## Note: Step 5 comes after a tentative room width has been generated so that it doesn't have to check any further than it needs to.
								
								
								how_wide_to_actually_make_the_room = 0
								
								
								## Step 5
								for each_next_tile_index in range(0, random_room_width):
									
									if new_dungeon_map[each_row_index][(each_column_index + each_next_tile_index + 1)] == 0:
										
										how_wide_to_actually_make_the_room += 1
									else:
										how_wide_to_actually_make_the_room += 0
																	
								
								
								## Now we know how wide to make the room and, implicitly, how tall to make it, since rooms are rectilinear and will never be placed to undercut other rooms, only to block their horizontal propagation.
								## The maximum width is how_wide_to_actually_make_the_room, since it uses random_room_width (already bounded for map edge purposes) in its randrange.
								## The maximum height is simply random_room_height, now that it's been bounded by distance_from_top_of_room_to_bottom_of_map.
								## ...
								## It occurred to me it might be simpler to make the map a large carved room one or two tiles wider than the end result is supposed to be, and simply "uncarve" the map inside it before starting any of this.
								## Then is-carved checking would implicitly incorporate the distance to the edge in it too.
								## Ah well, that's for some adventurous refactoring spree!
								
								
								
								new_room_rectangle = [each_row_index, each_column_index, how_wide_to_actually_make_the_room, random_room_height]
								
								
								## Now write the room to the map so it can continue properly.
								
								for each_new_tile_y in range(1, random_room_height + 1):
									
									for each_new_tile_x in range(1, (how_wide_to_actually_make_the_room + 1)):
									
										new_dungeon_map[(each_row_index + each_new_tile_y)][(each_column_index + each_new_tile_x)] += 1
								
								

		return new_dungeon_map						
								
								
												
								
								
		'''				
								
				
								
								
								
								
								



	
	
class MarkIIDungeonMapGenerator:
	
	
	## Thinking of renaming this WingedDungeonGenerator, because it loves to make floorplans split into several "wings" each of which may be impressively lengthy at larger sizes.
	## The effect is pretty cool, actually. Code could use some efficiency polish, though.
	
	'''
	
	Idea remembered from the old WanderingLineGenerator:
	
	"
	Decided I didn't quite like the "wandering line" idea and I'm going to try something inspired by http://donjon.bin.sh/d20/dungeon/index.cgi instead.
	It's going to use the DungeonMapGenerator algorithm to place rooms and a new algorithm for tunnel connection.
	Specifically it will use the WanderingLineMapGenerator idea of keeping an in-object list of rooms and using that to do things like is-connected-yet checks and intersection testing.
	"
	
	
	'''



	def __init__(self, supplied_map_width=40, supplied_map_height=40, room_max_size=10, room_min_size=4, room_max_count=30, room_min_count=5):
		

		self.map_width = supplied_map_width
		self.map_height = supplied_map_height
		
		## The bottom and right edges must always be uncarved.
		## Doing it here, during the inits, guarantees that for all rooms and every map.
		## ...
		## I probably have no idea what I'm doing since testing it is easier than figuring out whether Python feels like pretending 0 is an ordinal or not this time.
		self.map_width -= 1
		self.map_height -= 1		
		
		self.room_max_size = room_max_size
		self.room_min_size = room_min_size
		
		self.room_max_count = room_max_count
		self.room_min_count = room_min_count
	
	
		## Saving it as state for brain friendliness purposes. Can be changed later.
		self.list_of_created_rooms = []
	
	
	
	
	def define_corridor(self, which_orientation, x, y, x2, y2):
		
		''' Create a corridor (actually a one-tile-by-n-tiles rectangular room) connecting point (x, y) and point ((x + width), (y + height)), using the rectangular room definition format. '''

		width = x2 - x
		height = y2 - y
		
		
		if which_orientation == 'horizontal':
		
			if width < 0:

				width *= -1
				x -= width
				
			new_corridor = [x, y, width + 1, 1]

			
		if which_orientation == 'vertical':
		
			if height < 0:

				height *= -1
				y -= height
				
			new_corridor = [x, y, 1, height + 1]
	
	
		return new_corridor	
	
	
	
	

	def return_the_center_of_this_rectangle(self, upperleft_x, upperleft_y, width, height):

		## This is for placing corridors.
		
		centerpoint_x = ( upperleft_x + (width // 2) )
		centerpoint_y = ( upperleft_y + (height // 2) )
	
		return [centerpoint_x, centerpoint_y]
		
		
		
	
	
	def check_these_two_rectangles_for_intersection(self, rectangle_alpha, rectangle_beta):
	
		''' Check two rectangles, both formatted [x, y, w, h] for intersection; return True if they intersect and False if they do not intersect. '''
		
		new_x  = rectangle_alpha[0]
		new_x2 = (rectangle_alpha[0] + rectangle_alpha[2])
		old_x  = rectangle_beta[0]
		old_x2 = (rectangle_beta[0] + rectangle_beta[2])
					
		new_y  = rectangle_alpha[1]
		new_y2 = (rectangle_alpha[1] + rectangle_alpha[3])
		old_y  = rectangle_beta[1]
		old_y2 = (rectangle_beta[1] + rectangle_beta[3])
		
		
		do_they_intersect = False
		
		
		
		if 	( (new_x >= old_x) and (new_x <= old_x2) ) or ( (new_x2 >= old_x) and (new_x2 <= old_x2) ):
						
			if 	( (new_y >= old_y) and (new_y <= old_y2) ) or ( (new_y2 >= old_y) and (new_y2 <= old_y2) ):
					
				do_they_intersect = True
						
							
		if 	( (old_x >= old_x) and (old_x <= new_x2) ) or ( (old_x2 >= new_x) and (old_x2 <= new_x2) ):
						
			if 	( (old_y >= new_y) and (old_y <= new_y2) ) or ( (old_y2 >= new_y) and (old_y2 <= new_y2) ):
					
				do_they_intersect = True
						
					
		## This if tree checks to see whether or not any rooms are forming crosses.
					
		if ((new_x >= old_x) and (new_x2 <= old_x2)) and ((new_y <= old_y) and (new_y2 >= old_y2)):
						
			do_they_intersect = True
						
						
		## ... and the same check in the other direction, for if the old room was the vertical bar of the cross rather than the new room, as is assumed in the preceding if tree:
		if ((old_x > new_x) and (old_x2 < new_x2)) and ((old_y < new_y) and (old_y2 > new_y2)):
						
			do_they_intersect = True
						
		## DEBUG
		#print("Successfully checked for intersection")
		## \DEBUG
		
		return do_they_intersect	
	
	
	
	
	def generate_noise(self, supplied_map_width=None, supplied_map_height=None, room_max_size=None, room_min_size=None, room_max_count=None, room_min_count=None):
		
		
		
		## I have this sinking feeling it's un-Pythonic to have this kind of optional state for my MapGenerator objects.
		
		
		if supplied_map_width != None:
		
			self.map_width = supplied_map_width
			self.map_width -= 1
			
		if supplied_map_height != None:
		
			self.map_height = supplied_map_height
			self.map_height -= 1		

			
		if room_max_size != None:
			self.room_max_size = room_max_size
			
		if room_min_size != None:	
			self.room_min_size = room_min_size
		
		if room_max_count != None:
			self.room_max_count = room_max_count
			
		if room_min_count != None:	
			self.room_min_count = room_min_count
		
		
		
		


			
		list_of_candidate_rooms = []
		
		
		while (len(list_of_candidate_rooms) < self.room_min_count):
		
		
			for each_new_room_attempt in range(0, self.room_max_count):
					
				#print("each_new_room_attempt == %d" % (each_new_room_attempt))	
					
				## Width and height are defined BEFORE x/y position.
				## Doing it this way makes it unnecessary to check if the room extends off the map.
				new_room_width = random.randint(self.room_min_size, self.room_max_size)
				new_room_height = random.randint(self.room_min_size, self.room_max_size)
					
				new_room_x = random.randint(1, ((self.map_width - 1) - new_room_width))
				new_room_y = random.randint(1, ((self.map_height - 1) - new_room_height))
				
				
				new_room_candidate = [new_room_x, new_room_y, new_room_width, new_room_height]
		
				should_we_append_this_room = True
				
				for each_other_room in list_of_candidate_rooms:
					
					if (self.check_these_two_rectangles_for_intersection(new_room_candidate, each_other_room) == True):
						
						should_we_append_this_room = False
				
						#print("Failed a room intersect test")
				
				if should_we_append_this_room == True:
						
					list_of_candidate_rooms.append(new_room_candidate)
						
					#print("Appended a room")
							
			if (len(list_of_candidate_rooms) < self.room_min_count):
		
				del list_of_candidate_rooms[:]
				
				#print("Gotta use a while loop eventually") # Do we? Doesn't seem like it now.
		
				
				
		## Now create corridors linking rooms.
		
		## The list_of_all_centerpoints is not the same as the list_of_candidate_rooms or list_of_new_corridors, but I guess it technically could be merged with a small redesign. Keeping them separate for now to preserve the conceptual history of the things.
		## Note the reason this is done after the list_of_candidate_rooms is filled is because that list gets wiped during generation if the genned number is lower than the minimum.
		## Corridor generation doesn't do that, so it can append corridors as they're created.
				
		list_of_all_centerpoints = []

		
		## "Colors" are an abstraction used to represent the fact that each room has a connected-to-these-other-rooms quality, which is common to all of them.
		## Thinking of this quality as a color makes for an easily relatable analogy.
		## The list_of_room_connection_colors is going to be a list of lists which is constructed as corridors are added (eg, as rooms pass their first and only classical connection check).
		
		list_of_room_connection_colors = []
		
		
		list_of_new_corridors = []
				
		
		
		for each_room in list_of_candidate_rooms:
		
			## Appends [centerpoint_x, centerpoint_y] to the list, so it's a 2-ple: [ [],[],[],[],[]... ]



			list_of_all_centerpoints.append(self.return_the_center_of_this_rectangle(upperleft_x=each_room[0], upperleft_y=each_room[1], width=each_room[2], height=each_room[3]))
		
		
		
		
		
		## In the following for loop, all created rooms are connected to the closest other room or corridor (technically the closest centerpoint, which stores both).
		## The connecton of a room involves creating precisely one vertical and one horizontal corridor attaching it to another room.
		## It also involves appending the centerpoints of the two corridors and the two rooms they connect to the list_of_room_connection_colors in their proper color.
		## It does NOT involve connecting colors to each other. That comes after this "first pass" of room connection.
		
		for each_room in list_of_candidate_rooms:
			
			## The first step is to find which other room's centerpoint is the closest to the current room's centerpoint.
			
			alpha_room_centerpoint_x, alpha_room_centerpoint_y = self.return_the_center_of_this_rectangle(upperleft_x=each_room[0], upperleft_y=each_room[1], width=each_room[2], height=each_room[3])
			
		
			the_shortest_hypotenuse_found_for_this_room = None
				
			which_centerpoint_is_closest = None
			
			
			for each_centerpoint in list_of_all_centerpoints:
				
				## DEBUG
				#print("  each_centerpoint == %s" % (str(each_centerpoint)))
				## \DEBUG
				
				beta_room_centerpoint_x, beta_room_centerpoint_y = each_centerpoint[0], each_centerpoint[1]
				
				
				
				if (alpha_room_centerpoint_x == beta_room_centerpoint_x) and (alpha_room_centerpoint_y == beta_room_centerpoint_y):
				
					## Then they're the same centerpoint and should be skipped for this step.
					
					pass
						
						
				else:
					
					## Then these centerpoints should be checked to see if they're the closest to each other as of this iteration.
				
					x_distance_between_the_two = abs(beta_room_centerpoint_x - alpha_room_centerpoint_x)
					y_distance_between_the_two = abs(beta_room_centerpoint_y - alpha_room_centerpoint_y)
						
					hypotenuse_distance_between_the_two = math.sqrt((x_distance_between_the_two ** 2) + (y_distance_between_the_two ** 2))
			
			
					if (the_shortest_hypotenuse_found_for_this_room == None) or (hypotenuse_distance_between_the_two < the_shortest_hypotenuse_found_for_this_room):
							
						## Then these centerpoints are in fact the closest to each other as of this iteration.	
							
						the_shortest_hypotenuse_found_for_this_room = hypotenuse_distance_between_the_two
							
						which_centerpoint_is_closest = each_centerpoint

				
				
				
			## Now that the closest room rectangle has been found, draw a corridor between it's and the current room's centerpoints:
				
			which_direction_first = random.randint(0, 1) # remember, random.randint() includes min and max values, unlike range()

			## NOTE! It might be a good idea to check for intersection here and, if detected, invert which_direction_first via: which_direction_first = abs(which_direction_first - 1)
			## That would make it slightly less favorable to crossed tunnels, though it should already have rather few of those. I think.
				
				
			## Redefining these terms so we can use them to create corridors. This may not be maximally Pythonic... It would be a decent candidate for refactoring.	
			alpha_room_centerpoint_x, alpha_room_centerpoint_y = self.return_the_center_of_this_rectangle(upperleft_x=each_room[0], upperleft_y=each_room[1], width=each_room[2], height=each_room[3])
			beta_room_centerpoint_x, beta_room_centerpoint_y = which_centerpoint_is_closest[0], which_centerpoint_is_closest[1]
						
				
				
			if which_direction_first == 0:

				new_horizontal_corridor = self.define_corridor('horizontal', alpha_room_centerpoint_x, alpha_room_centerpoint_y, beta_room_centerpoint_x, beta_room_centerpoint_y)
				new_vertical_corridor = self.define_corridor('vertical', beta_room_centerpoint_x, beta_room_centerpoint_y, alpha_room_centerpoint_x, alpha_room_centerpoint_y)

				
			elif which_direction_first == 1:

				new_horizontal_corridor = self.define_corridor('horizontal', beta_room_centerpoint_x, beta_room_centerpoint_y, alpha_room_centerpoint_x, alpha_room_centerpoint_y)
				new_vertical_corridor = self.define_corridor('vertical', alpha_room_centerpoint_x, alpha_room_centerpoint_y, beta_room_centerpoint_x, beta_room_centerpoint_y)
						
				
			## Save the corridors:
			list_of_new_corridors.append(new_horizontal_corridor)
			list_of_new_corridors.append(new_vertical_corridor)
	
			## Also save the corridors' centerpoints:
			horizontal_corridor_centerpoint = self.return_the_center_of_this_rectangle(upperleft_x=new_horizontal_corridor[0], upperleft_y=new_horizontal_corridor[1], width=new_horizontal_corridor[2], height=new_horizontal_corridor[3])
			vertical_corridor_centerpoint = self.return_the_center_of_this_rectangle(upperleft_x=new_vertical_corridor[0], upperleft_y=new_vertical_corridor[1], width=new_vertical_corridor[2], height=new_vertical_corridor[3])
			
			list_of_all_centerpoints.append(horizontal_corridor_centerpoint)
			list_of_all_centerpoints.append(vertical_corridor_centerpoint)
	

	
	
			## We're going to absolutely have to ensure they're all connected.
			
			## 1. I think the way to do this is to have corridors, upon creation, append their centerpoints along with their associated rooms' to a list which will later be crosschecked with the list_of_all_centerpoints.
			## 2. The first room connected this way will have a color associated with it that colors the centerpoints of itself, the corridor, and the room it's connected to.
			## 3. When a new corridor is created, it will check if start or end have colors associated with them and adopt it as its own color if so; if not, a new color will be created which follows this pattern.
			## 4. When the map is finished creating corridors via the classical closest-centerpoints method, the color lists will be cross-checked and if any centerpoint appears in at least two color lists simultaneously, those colors are considered connected.
			## 5. If this process completes and certain colors remain unconnected, the closest centerpoints in each of them will be discerned and connected to each other.
			## 6. Steps 4 and 5 will iterate untill no colors remain unconnected.
	
			## Since this is where every room has a corridor added on to it, we'll begin here.
			
			
			## list_of_room_connection_colors will be a three-ple:
			## [ [ [x, y], [x, y], [x, y] ], [ [x, y], [x, y], [x, y] ], ... ]

			## If there are no colors yet...
			if len(list_of_room_connection_colors) == 0:
				
				## Make the current room the source of the first color.
				new_color = []
				
				new_color.append([alpha_room_centerpoint_x, alpha_room_centerpoint_y])
				new_color.append([beta_room_centerpoint_x, beta_room_centerpoint_y])
				new_color.append(horizontal_corridor_centerpoint)
				new_color.append(vertical_corridor_centerpoint)
				
				list_of_room_connection_colors.append(new_color)
				
				#print("\n\nlist_of_room_connection_colors == \n%s\n\n" % (str(list_of_room_connection_colors)))
				## That part worked correctly the very first time!
				
			
			## Otherwise, check the list of colors for cross-results with all four centerpoints currently being considered:
			else:
			
				does_this_room_fit_in_any_color = False
			
				for each_color in list_of_room_connection_colors:
					
					do_these_centerpoints_connect_to_this_color = False
				
					we_can_append_alpha_room_centerpoint = True
					we_can_append_beta_room_centerpoint = True
					we_can_append_horizontal_corridor_centerpoint = True
					we_can_append_vertical_corridor_centerpoint = True
					
					for each_centerpoint in each_color:
					
						## Notice the split between do_these_centerpoints_connect_to_this_color and we_can_append_foo_centerpoint
						## This is because the former gates the adding of all centerpoints, and the latter gates the adding of specific centerpoints.
						## Without the latter it would add too many centerpoints, creating duplicates.
						## Important: This part of the function does NOT pare down colors, it can only build them up. It does try to build them up only when previous colors are insufficient, however.
					
						if ((each_centerpoint[0] == alpha_room_centerpoint_x) and (each_centerpoint[1] == alpha_room_centerpoint_y)):
							do_these_centerpoints_connect_to_this_color = True
							we_can_append_alpha_room_centerpoint = False
						
						if ((each_centerpoint[0] == beta_room_centerpoint_x) and (each_centerpoint[1] == beta_room_centerpoint_y)):
							do_these_centerpoints_connect_to_this_color = True
							we_can_append_beta_room_centerpoint = False
							
						if ((each_centerpoint[0] == horizontal_corridor_centerpoint[0]) and (each_centerpoint[1] == horizontal_corridor_centerpoint[1])):
							do_these_centerpoints_connect_to_this_color = True
							we_can_append_horizontal_corridor_centerpoint = False
							
						if ((each_centerpoint[0] == vertical_corridor_centerpoint[0]) and (each_centerpoint[1] == vertical_corridor_centerpoint[1])):
							do_these_centerpoints_connect_to_this_color = True
							we_can_append_vertical_corridor_centerpoint = False

						
					if do_these_centerpoints_connect_to_this_color == True:
							
						if we_can_append_alpha_room_centerpoint == True:
							each_color.append([alpha_room_centerpoint_x, alpha_room_centerpoint_y])

						if we_can_append_beta_room_centerpoint == True:
							each_color.append([beta_room_centerpoint_x, beta_room_centerpoint_y])
						
						if we_can_append_horizontal_corridor_centerpoint == True:
							each_color.append(horizontal_corridor_centerpoint)
							
						if we_can_append_vertical_corridor_centerpoint == True:
							each_color.append(vertical_corridor_centerpoint)

						does_this_room_fit_in_any_color = True
						
							
						
						
						
	
				if does_this_room_fit_in_any_color == False:
					
					## I thiiiiiink there's going to be a slight problem with needing more than one pass to connect colors, after these steps are done.
					## Limited by the number of colors, but still, would be nice to narrow that down to get minimum runtime and maximum cleanness.

					
					the_newly_required_color = []
						
						
					## This absolutely cannot be the best way to do this kind of checking, but the tutorials didn't tell me any better way, and this way certainly works.
					## It's also very flat and readable.
					## ...
					## It also saved me a whole lot of processing time, from the looks of my debug statements.
					## ...
					## I think this was mistakenly placed. Newly-required colors should not have to check for duplicates again, since this happened in the preceding part of this conditional tree -- see just above here.
					## Commenting it all for rumination and debugging purposes.
						
					#we_can_append_alpha_room_centerpoint = True
					#we_can_append_beta_room_centerpoint = True
					#we_can_append_horizontal_corridor_centerpoint = True
					#we_can_append_vertical_corridor_centerpoint = True
						
						
					#for each_other_color in list_of_room_connection_colors:
					#	for each_other_centerpoint in each_other_color:
					#		if each_other_centerpoint == [alpha_room_centerpoint_x, alpha_room_centerpoint_y]:
					#			we_can_append_alpha_room_centerpoint = False
					#		if each_other_centerpoint == [beta_room_centerpoint_x, beta_room_centerpoint_y]:
					#			we_can_append_beta_room_centerpoint = False
					#		if each_other_centerpoint == horizontal_corridor_centerpoint:
					#			we_can_append_horizontal_corridor_centerpoint = False
					#		if each_other_centerpoint == vertical_corridor_centerpoint:
					#			we_can_append_vertical_corridor_centerpoint = False
									
									
									
					#if we_can_append_alpha_room_centerpoint == True:
					the_newly_required_color.append([alpha_room_centerpoint_x, alpha_room_centerpoint_y])
					#if we_can_append_beta_room_centerpoint == True:
					the_newly_required_color.append([beta_room_centerpoint_x, beta_room_centerpoint_y])
					#if we_can_append_horizontal_corridor_centerpoint == True:
					the_newly_required_color.append(horizontal_corridor_centerpoint)
					#if we_can_append_vertical_corridor_centerpoint == True:
					the_newly_required_color.append(vertical_corridor_centerpoint)
						
						
					#if len(the_newly_required_color) != 0:
					list_of_room_connection_colors.append(the_newly_required_color)
				
			
				
				
				
		#print("pre-step: list_of_room_connection_colors == ")
		
		#for each_color in list_of_room_connection_colors:
		#	print("  " + str(each_color))
		#	print("|||||||||||||||||||||||")	

		## The rooms are placed, connected with classical, first-pass corridors, and the initial color lists have been established.
		## Next we must winnow down the color lists to the bare minimum, since there will be some colors that are connected which were not recognized as such in the establishment pass.
		

		
	
		
		
		'''		
		print("PRE-STEP: list_of_room_connection_colors == ")
		
		for each_color in list_of_room_connection_colors:
			print("  " + str(each_color))
			print("|||||||||||||||||||||||")	
		'''	
			
		
		## The next step is to connect the disconnected colors.
		##
		## This will be accomplished by:
		## 1. Taking the color in the list_of_room_connection_colors at index 0 (hereafter "color alpha"), finding its centerpoint and comparing it to all other colors' centerpoints, saving:
		## 	a. the centerpoint of color alpha
		##	b. the centerpoint of the closest color to color alpha (hereafter "color beta")
		##	c. a list containing all the centerpoints inside the color beta (eg, identical to color beta at the time of its discovery)
		## 2. Finding the room inside color alpha which is closest to 1.b.
		## 3. Finding the room inside color beta which is closest to 1.a.
		## 4. Connecting 2. and 3. with an L-corridor and adding its two components' centerpoints to color gamma
		## 5. Appending every room centerpoint in color alpha and color beta to color gamma
		## 6. Appending color gamma to the next pass's new color list
		## 7. If any colors remain, appending every color not in alpha, beta, or gamma to the next pass's color list
		## 8. If the next pass's color list length is greater than 1, repeat this process, starting at step 1.
		
				
		## Number of passes is just the length of the color list, since this algorithm is guaranteed to step through each and every color, connecting them individually.	
		for each_remaining_color in range(0, len(list_of_room_connection_colors)):
		
		
			## Giant conditional.
			if (len(list_of_room_connection_colors) > 1):
		
				color_alpha = list_of_room_connection_colors[0]
				
				## Figure out the average centerpoint of color alpha:
				
				color_alpha_average_x_stack = 0
				color_alpha_average_y_stack = 0
				
				for each_color_alpha_centerpoint in color_alpha:
					
					color_alpha_average_x_stack += each_color_alpha_centerpoint[0]
					color_alpha_average_y_stack += each_color_alpha_centerpoint[1]				
					
				color_alpha_average_x = (color_alpha_average_x_stack // len(color_alpha))	
				color_alpha_average_y = (color_alpha_average_y_stack // len(color_alpha))	
			
						
				the_shortest_hypotenuse_found_for_this_color = None		
				
				#the_closest_beta_average_x = None
				#the_closest_beta_average_y = None

				
				## Yes, we have to use the index value for this, since equality checking lists doesn't seem to work, based on previous experiments.
				for each_beta_color_index in range(1, len(list_of_room_connection_colors)):		
					
					color_beta = list_of_room_connection_colors[each_beta_color_index]
					
					color_beta_average_x_stack = 0
					color_beta_average_y_stack = 0
						
					for each_beta_centerpoint in color_beta:
						
						
						color_beta_average_x_stack += each_beta_centerpoint[0]
						color_beta_average_y_stack += each_beta_centerpoint[1]				
					
					color_beta_average_x = (color_beta_average_x_stack // len(color_beta))
					color_beta_average_y = (color_beta_average_y_stack // len(color_beta))
						
						
						
					x_distance_between_the_two_colors = abs(color_beta_average_x - color_alpha_average_x)
					y_distance_between_the_two_colors = abs(color_beta_average_y - color_alpha_average_y)
							
					hypotenuse_distance_between_the_two_colors = math.sqrt((x_distance_between_the_two_colors ** 2) + (y_distance_between_the_two_colors ** 2))
				
				
					if (the_shortest_hypotenuse_found_for_this_color == None) or (hypotenuse_distance_between_the_two_colors < the_shortest_hypotenuse_found_for_this_color):
								
						## Then these centerpoints are in fact the closest to each other as of this iteration.	
								
						the_shortest_hypotenuse_found_for_this_color = hypotenuse_distance_between_the_two_colors
								
						which_color_is_closest = color_beta
						which_beta_color_index_is_closest = each_beta_color_index
						
						## Do I need to make these globals? Is python telling me to refactor my function into a zillion impossible to track tiny functions? =/

						the_closest_beta_average_x = color_beta_average_x
						the_closest_beta_average_y = color_beta_average_y
				

				## Now that we've found the beta color with an average centerpoint closest to the alpha color's average centerpoint, we need to find the alpha room centerpoint closest to the beta average centerpoint:

				the_shortest_hypotenuse_found_between_alpha_room_and_beta_average = None
				
				for each_color_alpha_centerpoint in color_alpha:
				
					x_distance_between_this_alpha_room_and_the_beta_average = abs(the_closest_beta_average_x - each_color_alpha_centerpoint[0])
					y_distance_between_this_alpha_room_and_the_beta_average = abs(the_closest_beta_average_y - each_color_alpha_centerpoint[1])
						
					hypotenuse_distance_between_alpha_room_and_beta_average = math.sqrt((x_distance_between_this_alpha_room_and_the_beta_average ** 2) + (y_distance_between_this_alpha_room_and_the_beta_average ** 2))
				
					if (the_shortest_hypotenuse_found_between_alpha_room_and_beta_average == None) or (hypotenuse_distance_between_alpha_room_and_beta_average < the_shortest_hypotenuse_found_between_alpha_room_and_beta_average):
						
						the_shortest_hypotenuse_found_between_alpha_room_and_beta_average = hypotenuse_distance_between_alpha_room_and_beta_average
						
						which_alpha_centerpoint_is_closest_to_beta_average = each_color_alpha_centerpoint
						
						
				## Mirror the above process to find the beta room with a centerpoint closest to the alpha color's average centerpoint:		
				
				the_shortest_hypotenuse_found_between_beta_room_and_alpha_average = None
				
				for each_color_beta_centerpoint in which_color_is_closest:
				
					x_distance_between_this_beta_room_and_the_alpha_average = abs(color_alpha_average_x - each_color_beta_centerpoint[0])
					y_distance_between_this_beta_room_and_the_alpha_average = abs(color_alpha_average_y - each_color_beta_centerpoint[1])
						
					hypotenuse_distance_between_beta_room_and_alpha_average = math.sqrt((x_distance_between_this_beta_room_and_the_alpha_average ** 2) + (y_distance_between_this_beta_room_and_the_alpha_average ** 2))
				
					if (the_shortest_hypotenuse_found_between_beta_room_and_alpha_average == None) or (hypotenuse_distance_between_beta_room_and_alpha_average < the_shortest_hypotenuse_found_between_beta_room_and_alpha_average):
						
						the_shortest_hypotenuse_found_between_beta_room_and_alpha_average = hypotenuse_distance_between_beta_room_and_alpha_average
						
						which_beta_centerpoint_is_closest_to_alpha_average = each_color_beta_centerpoint
						
						
						
						
				## Now that we have the alpha and beta room centerpoints closest to each other, connect them with a corridor.
				
				which_direction_first = random.randint(0, 1) # remember, random.randint() includes min and max values, unlike range()

				if which_direction_first == 0:

					new_horizontal_corridor = self.define_corridor('horizontal', which_alpha_centerpoint_is_closest_to_beta_average[0], which_alpha_centerpoint_is_closest_to_beta_average[1], which_beta_centerpoint_is_closest_to_alpha_average[0], which_beta_centerpoint_is_closest_to_alpha_average[1])
					new_vertical_corridor = self.define_corridor('vertical', which_beta_centerpoint_is_closest_to_alpha_average[0], which_beta_centerpoint_is_closest_to_alpha_average[1], which_alpha_centerpoint_is_closest_to_beta_average[0], which_alpha_centerpoint_is_closest_to_beta_average[1])

				elif which_direction_first == 1:

					new_horizontal_corridor = self.define_corridor('horizontal', which_beta_centerpoint_is_closest_to_alpha_average[0], which_beta_centerpoint_is_closest_to_alpha_average[1], which_alpha_centerpoint_is_closest_to_beta_average[0], which_alpha_centerpoint_is_closest_to_beta_average[1])
					new_vertical_corridor = self.define_corridor('vertical', which_alpha_centerpoint_is_closest_to_beta_average[0], which_alpha_centerpoint_is_closest_to_beta_average[1], which_beta_centerpoint_is_closest_to_alpha_average[0], which_beta_centerpoint_is_closest_to_alpha_average[1])
						
				
				## Save the corridors:
				list_of_new_corridors.append(new_horizontal_corridor)
				list_of_new_corridors.append(new_vertical_corridor)
					
				
				
				
				
				
				## And now merge alpha and beta colors and delete beta color:
				
				## DEBUG
				#print("which_color_is_closest == %s" % (str(which_color_is_closest)))
				## \DEBUG
				
				
				for each_beta_centerpoint in which_color_is_closest:
						
					color_alpha.append(each_beta_centerpoint)
				
				## The following line wasn't sufficient, since it only deleted this call-by-value variable rather than the call-by-reference pointer I was pretending it would be. Obvious in hindsight.
				#del which_color_is_closest
				
				## Fortunately the index was already available! See above.
				del list_of_room_connection_colors[which_beta_color_index_is_closest]
				
				## And now everything works as perfectly as I knew it would.
				
				
		'''			
		print("  POST-STEP: list_of_room_connection_colors == ")
		
		for each_color in list_of_room_connection_colors:
			print("  " + str(each_color))
			print("|||||||||||||||||||||||")	
		'''						
					
					
		## Having generated enough rooms and corridors, create the map:		
		
		the_dungeon_map = []
		
		for each_row in range(0, self.map_height):
		
			new_row = []
		
			for each_column in range(0, self.map_width):
			
				new_row.append(0)
			
			the_dungeon_map.append(new_row)
				
				
		## Write the rooms...
		for each_successful_room_candidate in list_of_candidate_rooms:
		
			for each_room_height_unit in range(0, each_successful_room_candidate[3]):
			
				for each_room_width_unit in range(0, each_successful_room_candidate[2]):
				
					the_dungeon_map[(each_successful_room_candidate[1] + each_room_height_unit)][(each_successful_room_candidate[0] + each_room_width_unit)] += 1
		

		
		
		## and write the corridors:
		for each_corridor in list_of_new_corridors:
		
			#print("Attempting to write a corridor...")
		
			for each_corridor_height_unit in range(0, each_corridor[3]):

				for each_corridor_width_unit in range(0, each_corridor[2]):
				
					## Check for uncarved space. When defining corridors this is the simplest way to go about it since the debug mauve is only really important for debugging room generation.
					if the_dungeon_map[(each_corridor[1] + each_corridor_height_unit)][(each_corridor[0] + each_corridor_width_unit)] == 0:
					
						the_dungeon_map[(each_corridor[1] + each_corridor_height_unit)][(each_corridor[0] + each_corridor_width_unit)] += 1
		
		
				
				
			
		return the_dungeon_map	
			
			
			
			
			
			
			
			
			

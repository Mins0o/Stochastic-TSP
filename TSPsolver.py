import sys, argparse
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def get_options(file_default = "./rl11849.tsp", p_default = 1000, f_default = 5000):
	p = p_default
	f = f_default
	
	arguments = argparse.ArgumentParser()
	arguments.add_argument("inputfile", nargs = "?", default = file_default)
	arguments.add_argument("--population", "-p")
	arguments.add_argument("--fit_eval_limit", "-f")
	arguments.add_argument("--verbose", "-v", action = 'store_true')
	arguments.add_argument("--save", "-s", action = 'store_true')
	args = arguments.parse_args()
	p = args.population
	f = args.fit_eval_limit
		
	# Convert to integer
	try:
		p = int(p)
	except:
		p = p_default
	try:
		f = int(f)
	except:
		f = f_default
		
	return (args.inputfile, p, f, args.verbose, args.save)
	
def read_tsp(filepath = "./rl11849.tsp"):
	with open(filepath, 'r') as file:
		lines = pd.DataFrame(list(csv.reader(file, delimiter = ' '))[6:-1],columns = ["Number","X","Y"])
		lines = lines[['X','Y']].astype(float)
	return(lines)

def read_sequence(filepath = "./solution.csv"):
	with open(filepath, 'r') as file:
		lines = np.array(list(csv.reader(file))).reshape(-1).astype('int')
		print(lines)
	return(lines - 1)

def measure_distance(sequence, points):
	rearranged_points = points.reindex(sequence)
	distance = 0
	
	square_diff = np.diff(rearranged_points, axis = 0)**2
	distance_per_pair = np.sum(square_diff, axis = 1)**0.5
	distance = np.sum(distance_per_pair)
	
	distance += ((rearranged_points.iloc[-1]-rearranged_points.iloc[0])**2).sum() ** 0.5
	
	### Previous attempt
	"""prev = points.iloc[0]
	for i in sequence:
		curr = points.iloc[i]
		square_diff = (curr-prev) ** 2
		distance += ( square_diff.sum() )**0.5
		prev = curr
		
	# Returning trip
	distance += (((points.iloc[0] - curr) ** 2).sum())**0.5
	"""
	
	return distance

def dist(a,b):
	a = np.array(a)
	b = np.array(b)
	return((b-a)**2).sum()**0.5

def two_opt(a, b, sequence):
	# Safety check
	length = len(sequence)
	if a >= length or b >= length:
		print("Two_opt error: index out of range.\nThe two opt was not executed.\ntwo_opt(" + str(a) + ", " + str(b)+", seq)")
		return
	
	# This does affect the parameter outside this method
	new_sequence = sequence.copy()
	temp = new_sequence[a]
	new_sequence[a] = new_sequence[b]
	new_sequence[b] = temp
	return new_sequence
	
def random_steepest(prev_sequence, points, iteration = 11849, verbose = False, filename = ""):
	distance = measure_distance(prev_sequence, points)
	length = len(points)
	# Variables for displaying
	_dist = distance
	_last = 0
	
	for i in range(iteration):
		# Random neighbor
		a,b = np.random.randint(length, size = 2)
		new_sequence = two_opt(a, b, prev_sequence)
		
		# Progression bar
		if verbose:
		###if True:
			print("["+ filename + "]\t" + str(i) + " / " + str(iteration-1), end = "\r")
		
		# Compare fitness and decide
		new_distance = measure_distance(new_sequence, points)
		if(new_distance < distance):
			prev_sequence = new_sequence
			distance = new_distance
			_last = i
			if verbose:
				print(new_distance, end = "\t")
				print((a,b), end = str(i) + " / " + str(iteration-1) + "\n")
	if verbose:
		print("\t\t\t\t\t\t\t",end = "")
		print("\nLast alteration: " + str(_last) + " - Distance: " + str(new_distance))
		print("\nStarted from {0}, ended with {1}".format(_dist,new_distance))
	return prev_sequence, distance

def simulated_annealing(prev_sequence, points, initial_temperature = 1, cool_rate = 1, iteration = 11849, verbose = False, filename = ""):
	distance = measure_distance(prev_sequence, points)
	length = len(points)
	temperature = initial_temperature
	_dist = distance
		
	for i in range(iteration):
		# Random neighbor
		a,b = np.random.randint(length, size = 2)
		new_sequence = two_opt(a, b, prev_sequence)
		
		# Progression bar
		if verbose:
		###if True:
			print("["+ filename + "]\t" + str(i) + " / " + str(iteration-1), end = "\r")
			
		# Compare fitness and decide
		new_distance = measure_distance(new_sequence, points)
		if(annealed_possibility(new_distance, distance, temperature,verbose)):
			prev_sequence = new_sequence
			distance = new_distance
			_last = i
			if verbose:
				print(new_distance, end = "\t")
				print((a,b), end = str(i) + " / " + str(iteration-1) + "\n")
		temperature =  initial_temperature / np.log(cool_rate * i + np.exp(1))
	if verbose:
		print("\t\t\t\t\t\t\t",end = "")
		print("\nStarted from {0}, ended with {1}".format(_dist,new_distance))
	return prev_sequence, distance

def annealed_possibility(new_distance, distance, temperature, verbose = False):
	if (new_distance < distance):
		return True
	exp_number = (distance - new_distance) / temperature
	return_bool = np.exp(exp_number) > np.random.randint(2)
	if verbose and return_bool:
		print("\nDistance Increased")
	return(return_bool)

def genetic_algorithm(epoch_limit, population):
	# How can I merge two different sequence into a permutation?
	pass
	
def initial_sequence_generation(points):
	"""generates initial condition where each nodes are connected to the nearest neighbor"""
	curr = 0
	sequence = [0]
	for i in range(len(points)-1):
		temp = points.loc[curr]
		points = points.drop(curr)
		nearest = points.iloc[((points - temp)**2).sum(axis = 1).argmin()]
		curr = nearest.name
		sequence.append(curr)
	return(np.array(sequence))
		
		

def plot_single_path(sequence, points):
	rearranged_points = points.reindex(np.append(sequence,sequence[0]))
	plt.plot(rearranged_points["X"],rearranged_points["Y"])

if __name__ == "__main__":
	filepath, population, fitness_limit, verbose, save_ = get_options()
	points = read_tsp(filepath)
	
	# Initial condition
	#initial_sequence = initial_sequence_generation(points)
	#print(measure_distance(initial_sequence,points))
	### Random initial condition
	initial_sequence = np.arange(len(points))
	np.random.shuffle(initial_sequence)
	
	### Execute algorithms
	### Algo 1
	### random_steepest(prev_sequence, points, iteration = 11849, verbose = False, filename = "")
	#seq_algo1, dist_algo1 = random_steepest(initial_sequence,points,fitness_limit, verbose, filepath)
	#print(dist_algo1)
	
	### Algo 2
	### simulated_annealing(prev_sequence, points, inertia = 1, cool_rate = 1, iteration = 11849, verbose = False, filename = "")
	seq_algo2, dist_algo2 = simulated_annealing(initial_sequence, points, initial_temperature = 30, cool_rate = 15, iteration = fitness_limit, verbose = verbose, filename = filepath)
	print(dist_algo2)
	
	final_seq = seq_algo2
	
	# Save sequence
	if True:
	#if save_:
		file_name = "solution"
		#file_name = input("What is the name of this solution?\n(You can exclude '.csv' at the end.")
		with open(file_name + ".csv", 'w') as output_file:
			output_file.writelines("\n".join(map(str,list(final_seq+1))))
		
	### Display plot
	## Display start state
	#plt.subplot(211)
	#plot_single_path(initial_sequence, points)
	## Display end state
	#plt.subplot(212)
	#plot_single_path(final_seq, points)
	#
	#plt.show()
import string
import random
import numpy as np

def generate_random_id(length=4):
    # Define the characters to choose from
    characters = string.ascii_uppercase + string.digits  # You can customize this as needed
    
    # Generate a random 4-character ID
    random_id = ''.join(random.choice(characters) for _ in range(length))
    
    return random_id

def expon_distribution(mean: float):
    '''
    Generate a random number from exponential distribution with given mean
    '''
    return np.random.exponential(mean)
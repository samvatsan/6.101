"""
6.101 Lab 3: Sam Vinu-Srivatsan
Bacon Number
"""

#!/usr/bin/env python3

import pickle

# NO ADDITIONAL IMPORTS ALLOWED!


def transform_data(raw_data):
    """
    Input: raw_data, list of tuples. Transform raw_data into 1 tuple of
    2 dictionaries. First dictionary cast maps each actor (by ID) to a
    set of IDs of all those they have acted with. Second dictionary
    films maps each film ID to the actor IDs in it.
    """
    cast = {}
    films = {}
    # walk through the tuples in raw_data
    for film_tuple in raw_data:
        actor1,actor2,movie = film_tuple
        # setting up cast dict
        if actor1 not in cast: # if an actor hasn't been recorded yet
            cast[actor1] = {actor1,actor2} # add new actor and colleagues
        else: #
            cast[actor1].add(actor2)
        if actor2 not in cast:
            cast[actor2] = {actor1,actor2}
        else:
            cast[actor2].add(actor1) # add colleague
        # setting up films dict by the same process
        if movie not in films:
            films[movie]={actor1,actor2} # add new film, add actors
        else: # add actors to existing film
            films[movie].add(actor1)
            films[movie].add(actor1)
    return (cast,films)

def acted_together(transformed_data2, actor_id_1, actor_id_2):
    """
    Inputs: a tuple of 2 dictionaries, int actor ID, int actor ID
    Returns Boolean value indicating if they acted together
    """
    # focus on the relevant dictionary in tuple
    transformed_data = transformed_data2[0]
    # check if one actor is in other's set of colleagues
    if actor_id_2 in transformed_data[actor_id_1]:
        return True
    return False

def actors_with_bacon_number(transformed_data2, n):
    """
    A Bacon number (n) is the degree of separation between Kevin Bacon
    and any other actor. Inputs: tuple of 2 dictionaries, int n
    Returns set of actors with Bacon number n
    """
    transformed_data = transformed_data2[0]
    bacon_id = 4724
    visited = {bacon_id}
    current_ids = {bacon_id} # IDs to traverse through for each n
    next_ids = set() # to hold direct colleagues of current_ids
    if n == 0:
        return {bacon_id}
    # for any n > 0
    for _ in range(n): # the degree of separation to traverse
        for actor in current_ids:
            for colleague in transformed_data[actor]:
                if colleague not in visited:
                    next_ids.add(colleague)
                    visited.add(colleague) # default only adds unique values anyway
        current_ids = next_ids.copy()
        if len(next_ids) == 0:
            return set()
        next_ids = set() # reset next_ids for every iteration
    return current_ids

def bacon_path(transformed_data, actor_id):
    # calls actor_to_actor_path on Bacon and actor_id
    bacon_id = 4724
    return actor_to_actor_path(transformed_data,bacon_id,actor_id)

def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    # x is the variable actor passed into goal_test_function()
    return actor_path(transformed_data,actor_id_1,
                      goal_test_function=lambda x: x==actor_id_2)
    # goal_test_function() returns True if x == actor_id_2 (fixed actor)

def actor_path(transformed_data2, actor_id_1, goal_test_function):
    """
    Inputs: tuple of 2 dictionaries, int actor ID, function
    Actor_path will find a path through transformed_data2 to satisfy function.
    Returns list of actor IDs or None
    """
    transformed_data = transformed_data2[0]
    if goal_test_function(actor_id_1):
        return [actor_id_1]
    def get_colleagues(actor):
        return transformed_data[actor] # return set of colleagues
    # visited set: all actors ever added to agenda
    visited = {actor_id_1}
    # agenda list: actors still to explore
    agenda = [[actor_id_1]]
    # while still actors to explore
    while agenda:
        # remove an actor from agenda
        actpath = agenda.pop(0)
        actor = actpath[-1]
        for colleague in get_colleagues(actor):
            if colleague not in visited:
                new_actor_path = actpath + [colleague]
                if goal_test_function(colleague):
                    return new_actor_path
                agenda.append(new_actor_path)
                visited.add(colleague)
    return None

def movies_connecting_actors(transformed_data2,actor1,actor2):
    """
    Takes in a tuple of dictionaries and 2 actor IDs.
    Returns list of movie IDs connecting 2 actors.
    """
    transformed_data = transformed_data2[1] # extract only films dict
    actorpath = actor_to_actor_path(transformed_data2,actor1,actor2)
    filmpath = []
    for i in range(1,len(actorpath)):
        # find the movie that consecutive actors were both in
        for film in transformed_data:
            if actorpath[i] in transformed_data[film] and \
                actorpath[i-1] in transformed_data[film]:
                filmpath.append(film)
    return filmpath

def actors_connecting_films(transformed_data, film1, film2):
    """
    Takes in tuple of dictionaries and 2 movie IDs.
    Returns a list of actor IDs connecting the movies.
    """
    if film1 not in transformed_data[1] or film2 not in transformed_data[1]:
        return None
    # set of actors in starting and ending films
    film1_cast = transformed_data[1][film1]
    film2_cast = transformed_data[1][film2]
    # nested loop through each of the start and end actors
    # set shortest_path to unreasonably big path (with len = total actors+1)
    shortest_path = list(transformed_data[0].keys())+[0]
    for actor1 in film1_cast:
        # compare actor1 against any x (actor2 in film2) to find shortest path
        path = actor_path(transformed_data,actor1,lambda x: x in film2_cast)
        if path is not None:
            # pick the shortest list as long as it isn't None
            shortest_path = min(shortest_path,path,key=len)
    # if shortest_path has never changed
    if shortest_path == list(transformed_data[0].keys())+[0]:
        return None
    return shortest_path

if __name__ == "__main__":
    with open("resources/small.pickle", "rb") as f:
        smalldb = pickle.load(f)

    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.

    # 2.2 UNDERSTANDING THE NAMES DATABASE
    with open("resources/names.pickle", "rb") as f:
        names = pickle.load(f)
    # Python dictionary with keys = actor names and values = actor ID
    # print(names)
    # print(names["Yehudit Ravitz"])
    # for actor in names.keys():
    #     if names[actor] == 92857:
    #         print(actor)
    # 4 TESTING ACTING TOGETHER
    # data = transform_data(smalldb)
    # a = names["Samuel L. Jackson"]
    # b = names["David Morse"]
    # c = names["Jean-Marc Roulot"]
    # d = names["Natascha McElhone"]
    # print("Jackson and Morse: ",acted_together(data,a,b))
    # print("Roulot and McElhone",acted_together(data,c,d))
    with open("resources/tiny.pickle", "rb") as f:
        tiny = pickle.load(f)
    # print(transform_data(tiny))

    # 5 TESTING BACON NUMBER
    with open("resources/large.pickle", "rb") as f:
        large = pickle.load(f)
    # actor_ids = actors_with_bacon_number(transform_data(large), 6)

    # 6 TESTING BACON PATH AND ACTOR TO ACTOR PATH
    # a lot of commented code has been reused/moved around 6 and 7
    # to answer different website questions about these functions
    # get banks ID number
    # banks = names["Monty Banks"]
    # lion = names["Laura Lion"]
    # gorney = names["Walt Gorney"]
    # actor_ids = actor_to_actor_path(transform_data(large),lion,gorney)

    # 7 TESTING MOVIE PATHS
    # with open("resources/movies.pickle", "rb") as f:
    #     movies = pickle.load(f)
    # sheen = names["Michael Sheen"]
    # radacic = names["Anton Radacic"]
    # filmpath = movies_connecting_actors(transform_data(large),sheen,radacic)
    # # print names of films for website question
    # movie_names = []
    # for id in filmpath:
    #     for name in movies:
    #         if movies[name] == id:
    #             movie_names.append(name)
    # print(movie_names)

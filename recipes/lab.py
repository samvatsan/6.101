"""
6.101 Lab 5: Sam Vinu-Srivatsan
Recipes
"""

import pickle
import sys

sys.setrecursionlimit(20_000)
# NO ADDITIONAL IMPORTS!


def atomic_ingredient_costs(recipes):
    """
    Given a recipes list, make and return a dictionary mapping each atomic food item
    name to its cost.
    """
    ingredient_costs = {}
    for item in recipes:
        types,food,cost = item # unpack tuple
        if types == "atomic":
            ingredient_costs[food] = cost
    return ingredient_costs

def compound_ingredient_possibilities(recipes):
    """
    Given recipes, a list containing compound and atomic food items, make and
    return a dictionary that maps each compound food item name to a list
    of all the ingredient lists associated with that name.
    """
    compound_dict = {}
    for item in recipes:
        types,food,ingredients = item
        if types == "compound":
            if food not in compound_dict:
                compound_dict[food] = [ingredients]
            else: # if the compound exists
                # add this ingredients list
                compound_dict[food].append(ingredients)
    return compound_dict

def remove_forbidden_items(recipes,forbidden_items):
    """
    Defined my own function to remove forbidden items to abstract this out
    of lowest_cost and cheapest_flat_recipe.
    Input:
    Output: tuple of dictionaries
    """
    atomic_dict = atomic_ingredient_costs(recipes)
    compound_dict = compound_ingredient_possibilities(recipes) # access all recipes

    for forbidden in forbidden_items:
        if forbidden in atomic_dict: # if the food is a key in atomic
            del atomic_dict[forbidden]
        elif forbidden in compound_dict: # if forbidden food is a compound
            del compound_dict[forbidden]
        # any other case where it is in neither dict is accounted for
        # in lowest_cost and cheapest_flat_recipe
    return (atomic_dict,compound_dict)

def lowest_cost(recipes, food_item,forbidden_items=[]):
    """
    Given a recipes list and the name of a food item, return the lowest cost of
    a full recipe for the given food item.
    """
    atomic_dict,compound_dict = remove_forbidden_items(recipes,forbidden_items)
    if food_item not in atomic_dict and food_item not in compound_dict:
        return None

    def recipe_cost(food):
        """
        Helper function to break down a larger cost comparison function
        into base and recursive cases.
        Input: food item (string), Output: minimum cost of making it (float)
        """
        min_cost = float("inf") # set a max comparison value
        # base case: if we hit the atomic ingredient
        if food in atomic_dict: # in atomic ingredient dict
            return atomic_dict[food]
        else: # still recursion through a compound
            for recipe in compound_dict[food]: # look at each recipe for food
                total_cost = 0
                for ingred,amount in recipe:
                    # if no other way, return None
                    if ingred not in atomic_dict and ingred not in compound_dict:
                        total_cost = float("inf")
                        break # try next recipe
                    else:
                        total_cost += amount*recipe_cost(ingred)
                min_cost = min(min_cost,total_cost)
        return min_cost
    if recipe_cost(food_item) == float("inf"):
        # min_cost never changed so no valid recipe
        return None
    return recipe_cost(food_item)


def scaled_flat_recipe(flat_recipe, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.
    """
    scaled_recipe = {}
    for ingredient,amount in flat_recipe.items():
        scaled_recipe[ingredient] = amount*n
    return scaled_recipe

def add_flat_recipes(flat_recipes):
    """
    Given a list of flat_recipe dictionaries that map food items to quantities,
    return a new overall 'grocery list' dictionary that maps each ingredient name
    to the sum of its quantities across the given flat recipes.

    For example,
        add_flat_recipes([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}
    """
    grocery_list = {}
    for recipe in flat_recipes: # iterate through list
        for ingredient,amount in recipe.items(): # iterate through dictionary
            if ingredient not in grocery_list:
                grocery_list[ingredient] = amount
            else: # if ingredient exists
                grocery_list[ingredient] += amount
    return grocery_list


def cheapest_flat_recipe(recipes, food_item,forbidden_items=[]):
    """
    Given a recipes list and the name of a food item, return a dictionary
    (mapping atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.
    """
     # find all recipes, keep track of minimum cost
    atomic_dict,compound_dict = remove_forbidden_items(recipes,forbidden_items)

    if food_item not in atomic_dict and food_item not in compound_dict:
        return None

    # first, eliminate all invalid recipes
    cheapest_cost = lowest_cost(recipes,food_item,forbidden_items)
    if cheapest_cost is None: # there was never a valid lowest cost
        return None

    def sub_recipe(ingredient):
        """
        Finds the cheapest sub_recipe for any ingredient, call this recursively
        to find the cheapest recipe for the overarching food_item.
        Input: ingredient (string), a food item that we want the recipe for
        Output: a recipe list with {atomic ingredient (string):quantity (int)}
        """
        # base case: if we hit the atomic ingredient
        if ingredient in atomic_dict:
            return {ingredient:1}

        # ingredient does not exist
        if ingredient not in atomic_dict and ingredient not in compound_dict:
            return None

        # if ingredient is in compound dict
        min_cost = float("inf")
        final_recipe = {}
        # iterate through possible recipes to make ingredient
        for recipe in compound_dict[ingredient]:
            print("the current recipe that we will look over",recipe)
            # find the lowest cost
            cost = 0
            flat_recipe = {}
            valid_recipe = True

            for item,amount in recipe:
                print("the current item and its amount",item,amount)
                # recipe for an item in our recipe
                sub_rec = sub_recipe(item)
                if not sub_rec: # if empty dict
                    print("WE HAVE ENTERED NONE")
                    # this recipe is totally invalid
                    valid_recipe = False
                    break
                # if sub_rec is valid
                flat_recipe = add_flat_recipes(
                    [flat_recipe,scaled_flat_recipe(sub_rec,amount)])
                print("current flat recipe",flat_recipe)
            if valid_recipe:
                cost = get_flat_recipe_cost(flat_recipe)
                min_cost = min(min_cost,cost)
                if min_cost == cost: # new recipe is the minimum
                    final_recipe = flat_recipe
        return final_recipe

    def get_flat_recipe_cost(flat_recipe):
        """
        Abstract away calculating the cost of a flat recipe to eventually
        compare it in minimum cost recipe calculation.
        Input: dictionary of {ingredient (string):amount (int)}
        Output: recipe cost to make the ingredient (float)
        """
        recipe_cost = 0
        for ingredient,amount in flat_recipe.items():
            cost = atomic_dict[ingredient] # price per 1 unit of ingredient
            recipe_cost += cost*amount
        return recipe_cost

    return sub_recipe(food_item)



def combined_flat_recipes(flat_recipes):
    """
    Given a list of lists of dictionaries, where each inner list represents all
    the flat recipes for a certain ingredient, compute and return a list of flat
    recipe dictionaries that represent all the possible combinations of
    ingredient recipes.
    """
    # base case: combined only has 0 or 1 things
    if not flat_recipes:
        return []

    if len(flat_recipes) == 1: # [[{}]]
        return flat_recipes[0] # [{}]

    # recursive case: [[{},{},{}],[{},{}]]
    # if length n, we combine 1st and rest from n (1 and n-1)
    first_ingredient = flat_recipes[0]
    rest_ingredients = flat_recipes[1:] # a list of lists
    result = []
    # break down to atomic case
    for first_recipe in combined_flat_recipes([first_ingredient]):
         # combined outputs a list of recipe dictionaries
        for second_recipe in combined_flat_recipes(rest_ingredients):
            result.append(add_flat_recipes([first_recipe,second_recipe])) # [{}]
    return result


def all_flat_recipes(recipes, food_item,forbidden_items=[]):
    """
    Given a list of recipes and the name of a food item, produce a list (in any
    order) of all possible flat recipes for that category.

    Returns an empty list if there are no possible recipes
    """
    atomic_dict,compound_dict = remove_forbidden_items(recipes,forbidden_items)

    if food_item not in atomic_dict and food_item not in compound_dict:
        return []

    # base case: atomic
    if food_item in atomic_dict:
        return [{food_item:1}]

    final_flat_recipes = [] # return a list of dictionaries (flat recipes)
    recipe_possibilities = compound_dict[food_item]
    # [[(),()],[(),()]] list of lists of ingredients
    for recipe in recipe_possibilities:
        recipe_flat_list = [] # outer list: all flat recipes for 1 ingredient
        for ingredient,amount in recipe:
            ingredients_list = []  # all flat recipes for 1 subingredient
            # recursive case: compound
            for flat in all_flat_recipes(recipes,ingredient,forbidden_items):
                ingredients_list.append(scaled_flat_recipe(flat,amount))
            recipe_flat_list.append(ingredients_list)
        # add in dictionaries inside combined_list to final_flat_recipes
        final_flat_recipes.extend(combined_flat_recipes(recipe_flat_list))
    return final_flat_recipes

if __name__ == "__main__":
    # load example recipes from section 3 of the write-up
    with open("test_recipes/example_recipes.pickle", "rb") as f:
        example_recipes = pickle.load(f)
    # you are free to add additional testing code here!
    # ingred_costs = atomic_ingredient_costs(example_recipes)
    # total_cost = sum(ingred_costs.values())
    # print("total cost of buying one of each food item", total_cost)
    # possibilities = compound_ingredient_possibilities(example_recipes)
    # many = 0
    # for comp in possibilities:
    #     if len(possibilities[comp]) > 1:
    #         many+=1
    # print("compounds with many recipes",many)
    # soup = {"carrots": 5, "celery": 3, "broth": 2,
     #    "noodles": 1, "chicken": 3, "salt": 10}
    # carrot_cake = {"carrots": 5, "flour": 8,
    #    "sugar": 10, "oil": 5, "eggs": 4, "salt": 3}
    # bread = {"flour": 10, "sugar": 3, "oil": 3, "yeast": 15, "salt": 5}
    # grocery_list = [soup, carrot_cake, bread]
    # print(add_flat_recipes(grocery_list))
    dairy_recipes = [
    ('compound', 'milk', [('cow', 2), ('milking stool', 1)]),
    ('compound', 'cheese', [('milk', 1), ('time', 1)]),
    ('compound', 'cheese', [('cutting-edge laboratory', 11)]),
    ('atomic', 'milking stool', 5),
    ('atomic', 'cutting-edge laboratory', 1000),
    ('atomic', 'time', 10000),
    ('atomic', 'cow', 100),
    ]
    print(cheapest_flat_recipe(dairy_recipes,"cheese",["milking stool"]))

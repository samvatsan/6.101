"""
6.101 Lab: Sam Vinu-Srivatsan
SAT Solver
"""

#!/usr/bin/env python3

import sys
import typing

sys.setrecursionlimit(10_000)
# NO ADDITIONAL IMPORTS

def update_formula(formula,assignment):
    """
    Take in a formula and an assignment, return updated formula based on assignment.
    assignment = ('variable',Boolean)
    """
    # create a new formula so that we don't mutate the original formula
    # can still backtrack later
    newformula = []
    for clause in formula: # inner list is "or"
        all_literals = []
        add_all_literals = True
        for literal in clause: # inner tuple is each variable and value
            # if literal[1] != assignment[1]: # different variables, copy to new list
            # two Trues or two Falses negate - always True
            if literal[0] == assignment[0] and literal[1] == assignment[1]:
                # entire clause satisfied, unnecessary
                add_all_literals = False # don't need to copy it over
                break
            if not (literal[0] == assignment[0] and literal[1] != assignment[1]):
                all_literals.append(literal)
        if add_all_literals:
            newformula.append(all_literals)
    return newformula

def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    # base: no possible solution
    if [] in formula:
        return None
    # base: no further work needed, already solved
    if len(formula) == 0:
        return {}
    var = unit_clause_test(formula)
    if var is None:
        return None
    formula,solution = var
    if [] in formula:
        return None
        # empty list if all unit clauses are true
    if len(formula) == 0:
        return solution

    # recursive: ongoing, needs to test more variable assignments
    test_var = formula[0][0][0] # try first variable

    # try true value and then false value
    # get rid of the first variable
    for boolvar in (True,False):
        true_formula = update_formula(formula,(test_var,boolvar))
        satisfy_true = satisfying_assignment(true_formula)
        if satisfy_true is not None:
            # add recursed dict values to solution to backtrack/keep track of path
            solution.update({test_var:boolvar})
            solution.update(satisfy_true)
            return solution

    return None

def unit_clause_test(formula):
    # check for unit clauses
    solution = {}
    while True:
        unit = False # assume no unit clauses in formula
        for clause in formula:
            if len(clause) == 0:
                return None
            elif len(clause) == 1:
                unit = True
                # add unit clause to solution
                solution[clause[0][0]] = clause[0][1]
                break
        if not unit:
            break
        formula = update_formula(formula,clause[0])
    return (formula,solution)

def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    rule1 = desired_rooms(student_preferences)
    rule2 = one_room_per_student(student_preferences, room_capacities)
    rule3 = room_capacity(student_preferences, room_capacities)
    rules = rule1 + rule2 + rule3
    return rules

def desired_rooms(student_preferences):
    """
    Each student is assigned to at least one room from their preference list.
    """
    outer = []
    for student, rooms in student_preferences.items():
        student_clause = [(f"{student}_{room}", True) for room in rooms]
        outer.append(student_clause)
    return outer

def one_room_per_student(student_preferences, room_capacities):
    """
    # each student assigned to max 1 room
    # for any pair of rooms, a student can only be in one of them
    """
    room_pairs_set = set()
    # all room pairs
    for room1 in room_capacities: # all types of rooms
        for room2 in room_capacities:
            if room1 != room2:
                room_pairs_set.add((room1,room2))
    outer = []
    # iterate through all students
    for student in student_preferences:
        for room_pairs in room_pairs_set:
            pair_clause = []
            for room in room_pairs:
                pair_clause.append((f"{student}_{room}",False))
            outer.append(pair_clause)
    return outer


def room_capacity(student_preferences, room_capacities):
    """
    No room has more assigned students than it can fit.
    Take in two dictionaries, output a cnf format.
    """

    def all_student_combos(capacity_n,students):
        """
        # get a list of all combinations of n students
        """
        # base case
        if capacity_n == 0: # 1 student
            #return {(student,) for student in students}
            return [[]]
        combinations = []
        for i in range(len(students)):
            first = students[i]
            rest = students[i+1:]
            for rest_combo in all_student_combos(capacity_n-1,rest):
                combinations.append([first]+rest_combo)
        return combinations


    all_clauses = []
    for room,capacity in room_capacities.items():
        if capacity >= len(student_preferences):
            continue
            # all groups of n+1 students within room
        stud = list(student_preferences)
        student_combos = all_student_combos(capacity+1,stud)
        for students in student_combos:
            # clause for 1 group of n+1 students within room
            current_clause = []
            for student in students:
                current_clause.append((f"{student}_{room}",False))
            all_clauses.append(current_clause)
    return all_clauses

if __name__ == "__main__":
    import doctest

    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)

    # schedule = boolify_scheduling_problem({'Alex': {'basement', 'penthouse'},
    #                         'Blake': {'kitchen'},
    #                         'Chris': {'basement', 'kitchen'},
    #                         'Dana': {'kitchen', 'penthouse', 'basement'}},
    #                        {'basement': 1,
    #                         'kitchen': 2,
    #                         'penthouse': 4})
    # print(schedule)
    test_form = [[('Alex_penthouse', True)],
                 [('Chris_kitchen', True), ('Chris_basement', True)], [('Dana_kitchen', True), ('Dana_penthouse', True),
                                                                       ('Dana_basement', True)]]
    print(satisfying_assignment(test_form))

"""
6.101 Lab: Sam Vinu-Srivatsan
LISP Interpreter Part 1
"""

#!/usr/bin/env python3

import sys

sys.setrecursionlimit(20_000)

# NO ADDITIONAL IMPORTS!

#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    tokens = []
    comment = False
    index = 0

    while index < len(source):
        char = source[index]
        if comment == False: # treat normally
            if char == ";": # enter comment
                comment = True
                index+=1
            elif char in (" ","\n"): # no comment
                index+=1
                #continue
            elif char in ("(",")"):
                tokens.append(char)
                index+=1
            else:  # if char is anything else
                atomic,index = collect_num(source,index)
                tokens.append(atomic)
                if index < len(source):
                    char = source[index]
                continue
        else: # if in a comment
            if char == "\n": # escape comment
                comment = False
                index+=1
            else:
                index+=1 # stay in comment, keep increasing indices
    #print(tokens)
    return tokens

def collect_num(string,cur_index):
    atomic = string[cur_index]
    cur_index+=1
    while cur_index < len(string) and string[cur_index] not in ("(",")"," ","\n"):
        # keep collecting you hit a stop character
        atomic+=string[cur_index]
        cur_index+=1
    return atomic,cur_index


# def expression(inp):
#     """
#     Tokenize and parse strings into symbolic expressions.
#     """
#     tokens = tokenize(inp)
#     parsed = parse(tokens)
#     return parsed


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    def parse_expression(index):
        if tokens[index] not in "()":
            #  base case with number/symbol hwere character is inside an expression
            val_type = number_or_symbol(tokens[index])
            return val_type,index+1
        elif tokens[index] == "(":
            sublist = []
            if len(tokens) > 1:
                index+=1
            else:
                raise SchemeSyntaxError
            while tokens[index] != ")":
                exp,ind = parse_expression(index)
                sublist.append(exp)
                index=ind
                if index >= len(tokens):
                    raise SchemeSyntaxError
            return sublist,index+1
        else:
            raise SchemeSyntaxError("malformed expression")
    parsed_expression, next_index = parse_expression(0)

    if len(tokens) > next_index:
        # there are things after final closed parens
        raise SchemeSyntaxError("malformed expression")
    return parsed_expression


######################
# Built-in Functions #
######################


def multiply(args):
    product = 1
    for arg in args:
        product*=arg
    return product

def divide(args):
    div = args[0]
    for i in range(1,len(args)):
        div/=args[i]
    return div

scheme_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": multiply,
    "/": divide
}

##############
# Evaluation #
##############

def evaluate(tree,frame=None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if frame is None:
        frame = make_initial_frame() # new empty frame

    if not isinstance(tree,list):
        val = number_or_symbol(str(tree))
        if type(val) in (float,int):
            return val
        else: # if string
            return frame[val]
    # recursive case: tree is a list

    # SPECIAL FORMS
    if tree[0] == "define":
        if not isinstance(tree[1],list):
            # EXPLICIT CASE
            # assuming 2 elements: name, expr
            name = tree[1]
            expr = evaluate(tree[2],frame)
            frame.set_value(name,expr)
            return expr
        else: # if first element is S-list
            # IMPLICIT CASE
            name_vars = tree[1] # list
            name = name_vars[0]
            vars = name_vars[1:]
            body = tree[2]
            # create a new lambda object
            func = Function(vars,body,frame)
            frame.set_value(name,func)
            return func

    elif tree[0] == "lambda": # [funcname,[args],[body]]
        # built in function
        args = tree[1]
        body = tree[2]
        func = Function(args,body,frame)
        return func
    # DOES RECURSION take care of functions wrapped in () to return the result of evaluating them

    # NONSPECIAL FORMS
    iter = []
    for nested in tree:
        iter.append(evaluate(nested,frame))

    if callable(iter[0]):
        func = iter[0]
        return func(iter[1:])
    else:
        raise SchemeEvaluationError("first element in S-expression not function")

class Function:
    def __init__(self,params,body,frame):
        self.params = params
        self.body = body
        self.frame = frame

    def __call__(self,evaluated_args):
        # map the parameters to the arguments
        child_frame = Frame(self.frame)
        # check length before looping through to map
        if len(self.params) != len(evaluated_args):
            raise SchemeEvaluationError
        for index in range(len(evaluated_args)):
            child_frame.set_value(self.params[index],evaluated_args[index])
        # execute the body
        return evaluate(self.body,child_frame)

        # self.frame is enclosing (where a function is defined)
        # cur_frame is where the function is called
        # child_frame is what gets created to evaluate the function call

class Frame:
    def __init__(self,parent):
        # instance attribute because variables will be different for every frame
        self.vals = {} # map names to expression values
        self.parent = parent

    def __getitem__(self,name):
        if name in self.vals:
            return self.vals[name]
        elif self.parent is None:
            raise SchemeNameError
        else: # search recursively
            return self.parent[name]

    def set_value(self,name,expr):
        self.vals[name] = expr

def make_initial_frame():
    frame = Frame(None)
    for key in scheme_builtins:
        frame.vals[key] = scheme_builtins[key]
    newframe = Frame(frame)
    return newframe

if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    testtoken = ['(', '+', '2', '(', '-', '5', '3.75', ')', '7', '8', ')']
    parsed = parse(testtoken)
    print(parsed)
    # # print(evaluate(parsed))
    # # print(number_or_symbol('3.75'))
    # f2 = Frame()
    # f1 = Frame()
    # f1.parent_point(f2)
    # # print(f1.parent)
    # print(tokenize(parse("(lambda () (+ 2 3))")))
    thing1 = "(2 3 4)"
    thing2 = "((lambda (x) x) 2 3)"
    print(evaluate(tokenize(parse(thing2))))
    # import os
    # sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    # import schemerepl
    # schemerepl.SchemeREPL(use_frames=True, verbose=False).cmdloop()

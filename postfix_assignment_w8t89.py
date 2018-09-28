# -*- coding: utf-8 -*-
"""
Created on Fri March 11 13:20:43 2018

@author: David Elks
"""


#!/usr/bin/python

from tkinter import *
import re
import sys


#Define constants - lower and higher precedent operators
low_operators = ['+', '-']
high_operators = ['*', '/']
factor_types = ['float', 'integer', 'variable']
bracket_types = ['open_bracket', 'close_bracket']

def tokenise(expression):
    '''Break expression into a list of tuples which include the token and 
    a description based upon the token such as float, operator or opening or 
    closing parenthesis. We use the re.scanner function to parse through 
    the input stream searching for the various types of entities found below.
    ''' 
    
    scanner = re.Scanner([
        (r'[0-9]\.[0-9]+', lambda label, tipe: ('float', tipe)),
        (r'[0-9]+', lambda label, tipe: ('integer', tipe)),
        (r'[a-z_]+', lambda label, tipe: ('variable', tipe)),
        (r'\(', lambda label, tipe: ('open_bracket', tipe)),
        (r'\)', lambda label, tipe: ('close_bracket', tipe)),
        (r'[+\-*/]', lambda label, tipe: ('operator', tipe)),
        (r'\s+', None)
    ])
    tokens, label = scanner.scan(expression)
    return tokens

def parse(tokens):
    '''Parse a list of tokens and use the Binary Tree class to create a tree.
    Return an error if the process fails
    '''
    expression_length = len(tokens)
    count = 0
    #initialise tree
    tree = BinaryTree("", count, tokens, expression_length)
    tree.set_initial_token() #Set token pointer to start
    #Create the tree using a recursive process explained in BinaryTree class.
    output = tree.parse_add_sub()
    return output, tree.error

class BinaryOperator():
     """A class that defines a type to handle operators +-/* within an 
     expression."""
     def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Num():
    """ A class that handles integers, floats and variables"""
    def __init__(self, token):
        self.token = token
        self.value = token
   
class BinaryTree:
    """An abstract data type which takes an input of a python list representing
    a valid infix expression of brackets, factors and operators and outputs
    an abstract syntax tree.
    
    The core methods for inserting left and right nodes, and getting 
    child values are from
    Problem Solving with Algorithms and Data Structures by Miller and Ranum.
    
    The recursive methods are modified from an algorithm described at:
         http://www.sunshine2k.de/coding/java/SimpleParser/SimpleParser.html
    
    """
    

    def __init__(self, root, count, tokens, expression_length):
        self.key = root
        self.left_child = None
        self.right_child = None
        self.current_token_type = None
        self.current_token_value = None
        self.count = count
        self.tokens = tokens
        self.error = False
        self.expression_length = expression_length - 1 #Adjust to start length from 0
        self.bracket_count = 0
    """The following methods are taken directly from
    Problem Solving with Algorithms and Data Structures by Miller and Ranum"""
    def insert_left(self, new_node):
        if self.left_child == None:
            self.left_child = BinaryTree(new_node)
        else:
            t = BinaryTree(new_node)
            t.left_child = self.left_child
            self.left_child = t
    def insert_right(self, new_node):
        if self.right_child == None:
            self.right_child = BinaryTree(new_node)
        else:
            t = BinaryTree(new_node)
            t.right_child = self.right_child
            self.right_child = t
    def get_right_child(self):
        return self.right_child
    def get_left_child(self):
        return self.left_child
    def set_root_val(self, obj):
        self.key = obj
    def get_root_val(self):
        return self.key
    
    def set_initial_token(self):
        self.current_token_type = self.tokens[0][0]
        self.current_token_value = self.tokens[0][1]
        
        
    def pop_token(self, token):
        '''A method which increments the counter to the next token within
        the expression and updates current values for 
        current_token_type and current_token_value. 
        '''
        
        if self.count == self.expression_length:
            return
        elif self.current_token_value == token:
            self.current_token_type = self.tokens[self.count+1][0]
            self.current_token_value = self.tokens[self.count+1][1]
            self.count += 1 #Move pointer on
        else:
            self.error = True  
        
    def parse_add_sub(self):
        """This is the first of three functions which recursively
        parse through the tokens and return nodes depending on the type of the 
        token to add to the emerging abstract syntax tree. This handles
        + and - operators.
        """
        node = self.parse_mult_div()
        while self.current_token_value in (low_operators):
            token = self.current_token_value
          
            if token == "+":
                self.pop_token("+")
            elif token == "-":
                self.pop_token("-")

            node = BinaryOperator(left=node, op=token, right=self.parse_mult_div())
        
        return node        
    def parse_mult_div(self):
        """This is the first of three functions which recursively
        parse through the tokens and return nodes depending on the type of the 
        token to add to the emerging abstract syntax tree. This handles
        * and / operators.
        """
        node = self.parse_factor()

        while self.current_token_value in (high_operators):
            token = self.current_token_value
            
            if token == "*":
                self.pop_token("*")
            elif token == "/":
                self.pop_token("/")

            node = BinaryOperator(left=node, op=token, right=self.parse_factor())

        return node

    
    def parse_factor(self):
        """This is the first of three functions which recursively
        parse through the tokens and return nodes depending on the type of the 
        token to add to the emerging abstract syntax tree. This handles
        floats, integers and text characters. It also handles parenthesis.
        """
        
        token = self.current_token_value
        
        if self.current_token_type in ("integer", "float", "variable"):
            self.pop_token(token)
            return Num(token)
        
             
        elif token == "(": 
            self.pop_token("(")
            node = self.parse_add_sub() 
            self.pop_token(")")
        
        return node

def process_expression(expr):
    """A wrapper function to handle the steps needed to tokenise an expression,
    make checks to ensure the expression has balanced parenthesis and
    is valid, before creating the tree.
    """
    tokens = tokenise(expr)
    #Check whether the expression has balanced brackets and is
    #a valid expression
    if par_checker(expr) and valid_expression_check(tokens):
         
         tree, error = parse(tokens)
    else:
         tree = None
         error = True
    return tree, error    
        

def postord(node, s):
    """A function that traverses the tree and outputs to a stack, s.
    Source: lecture notes."""
    if node is not None:
        if type(node).__name__ == "BinaryOperator":
            postord(node.left, s)
            postord(node.right, s)
            if node.op is not None:
                s.push(node.op)
          
        if type(node).__name__ == "Num":
            if node.value is not None:
                s.push(node.value)
    

class Stack:
    """A class to represent the Stack abstract data type. 
    Problem Solving with Algorithms and Data Structures by Miller and Ranum.""" 
    def __init__(self):
       self.items = []
    def is_empty(self):
       return self.items == []
    def push(self, item):
       self.items.append(item)
    def pop(self):
       return self.items.pop()
    def peek(self):
       return self.items[len(self.items)-1]
    def size(self):
       return len(self.items)

def par_checker(string): 
     '''A sanity check based on the work in the book 
     Problem Solving with Algorithms and Data Structures by Miller, 
     Ranum (2013).
     '''
     #extract brackets from input
     symbol_string = "".join(re.findall(r"[()]+", string)) 
     s = Stack() 
     balanced = True 
     index = 0 
     while index < len(symbol_string) and balanced: 
         symbol = symbol_string[index] 
         if symbol == "(": 
             s.push(symbol) 
         else: 
             if s.is_empty(): 
                balanced = False 
             else: 
                 s.pop()
         index = index + 1
     if balanced and s.is_empty(): 
         return True 
     else: 
         return False




def test(actual, expected):
    """ Compare the actual to the expected value,
        and print a suitable message.
        Taken from http://www.ict.ru.ac.za/Resources/cspw/thinkcspy3/thinkcspy3/fruitful_functions.html
    """
    linenum = sys._getframe(1).f_lineno   # Get the caller's line number.
    if (expected == actual):
        msg = "Test on line {0} passed.".format(linenum)
    else:
        msg = ("Test on line {0} failed. Expected '{1}', but got '{2}'."
                .format(linenum, expected, actual))
    print(msg)



def valid_expression_check(tokens):
     """Check that the first and last components of expression are factors
     and that the the pattern of types is alternating factor and then operator.
     """
     
     balanced = True
     
     token_types = [t[0] for t in tokens]
     no_brackets_list = [x for x in token_types if x not in bracket_types]
     
     first_token_type = no_brackets_list[0]
     last_token_type = no_brackets_list[-1]
     
     
     if first_token_type not in factor_types:
         
          return False
     if last_token_type not in factor_types:
          return False
        
     if len(no_brackets_list) < 3:
          return False
     
     count = 1 #set pointer to next token
     
     while count < len(tokens) and balanced == True:
          previous_token_type = tokens[count-1]
          current_token_type = tokens[count]
          
          if previous_token_type == current_token_type:
               balanced = False
          count += 1
     return balanced

def test_scaffold(exp):
     """Wrapper to examine final output from tree for valid expressions"""
     stack = Stack()
     nodes, error = process_expression(exp)
     if error:
          output_string = "There's an error in your expression. Try again"
     else:
          postord(nodes, stack)
          output_string = " ".join(stack.items)
     return output_string

def test_suite():
    """ Run the suite of tests for code.
    """ 
    test(tokenise("7 + 3 * (10 / 12 / (3 + 3) -1 )"), 
    [('integer', '7'),
    ('operator', '+'),
    ('integer', '3'),
    ('operator', '*'),
    ('open_bracket', '('),
    ('integer', '10'),
    ('operator', '/'),
    ('integer', '12'),
    ('operator', '/'),
    ('open_bracket', '('),
    ('integer', '3'),
    ('operator', '+'),
    ('integer', '3'),
    ('close_bracket', ')'),
    ('operator', '-'),
    ('integer', '1'),
    ('close_bracket', ')')])
    
    valid_tokens = tokenise("7 + 3 * (10 / 12 / (3 + 3) -1 )")
    
    imbalanced = tokenise("((7 + 3)")
    test(valid_expression_check(valid_tokens), True)
    test(valid_expression_check(imbalanced), False)
    
    test(par_checker("7 + 3 * (10 / 12 / (3 + 3) -1 )"), True)
    test(par_checker("((7 + 3)"), False)
    
    """Any errors after creating tree?"""
    test(process_expression("7 + 3 * (10 / 12 / (3 + 3) -1 )")[1], False) 
    test(process_expression("(7 + 3)+")[1], True)
    test(process_expression("1.25 - 10")[1], False)
    test(process_expression("a*x + b")[1], False)
    
    
    """test output from tree against results from 
    https://www.mathblog.dk/tools/infix-postfix-converter/"""
    
    test(test_scaffold("7 + 3 * (10 / 12 / (3 + 3) -1 )"), 
         "7 3 10 12 / 3 3 + / 1 - * +")
    test(test_scaffold("7 + 3+5"), 
         "7 3 + 5 +")
    test(test_scaffold("(7 + 3)+5"), 
         "7 3 + 5 +")
    test(test_scaffold("6 /3 /2"), 
         "6 3 / 2 /")
    test(test_scaffold("6 /3 /2"), 
         "6 3 / 2 /")
    test(test_scaffold("(3+5)*2+(6-3)"), 
         "3 5 + 2 * 6 3 - +")
    test(test_scaffold("(3+5)*2+6-3"), 
         "3 5 + 2 * 6 + 3 -")
    test(test_scaffold("(1-2)/(0+5)"), 
         "1 2 - 0 5 + /")  
    test(test_scaffold("a*x + b"), 
         "a x * b +")  
    test(test_scaffold("1.25 - 10"), 
         "1.25 10 -")  
test_suite()        # Here is the call to run the tests




window = Tk()
window.title("Postfix evaluator")
window.geometry('500x200')
lbl = Label(window, text="Enter the infix expression to be translated")
lbl.grid(column=0, row=0)
txt = Entry(window, width=10)
txt.grid(column=1, row=0)
def clicked():
    output_string = ""
    expression = txt.get()
    # Check whether the input has balanced brackets
    if par_checker(expression):
         stack = Stack()
         nodes, error = process_expression(expression)
         if error:
             output_string = "There's an error in your expression. Try again"
         else:
             postord(nodes, stack)
             output_string = stack.items
    else:
            output_string = "Your expression doesn't have balanced parameters."
    

    lbl.configure(text= output_string)
btn = Button(window, text="Submit", command=clicked)
btn.grid(column=2, row=0)
window.mainloop()

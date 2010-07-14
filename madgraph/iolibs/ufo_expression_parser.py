################################################################################
#
# Copyright (c) 2009 The MadGraph Development team and Contributors
#
# This file is a part of the MadGraph 5 project, an application which 
# automatically generates Feynman diagrams and matrix elements for arbitrary
# high-energy processes in the Standard Model and beyond.
#
# It is subject to the MadGraph license which should accompany this 
# distribution.
#
# For more information, please visit: http://madgraph.phys.ucl.ac.be
#
################################################################################

"""Parsers for algebraic expressions coming from UFO, outputting into
different languages/frameworks (Fortran and Pythia8). Uses the PLY 3.3
Lex + Yacc framework"""

import sys
import os

root_path = os.path.split(os.path.dirname(os.path.realpath( __file__ )))[0]
sys.path.append(os.path.join(root_path, os.path.pardir))

import vendor.ply.lex as lex
import vendor.ply.yacc as yacc

# PLY lexer class

class UFOExpressionParser:
    """A base class for parsers for algebraic expressions coming from UFO."""

    def __init__(self, **kw):
        """Ininitialize the lex and yacc"""
        lex.lex(module=self)
        yacc.yacc(module=self)        

    def parse(self, buf):
        """Parse the string buf"""
        yacc.parse(buf)

    # List of tokens and literals
    tokens = (
        'POWER', 'SIN', 'COS', 'TAN', 'SQRT', 'CONJ', 'PI',
        'VARIABLE', 'NUMBER'
        )
    literals = "=+-*/()"

    # Definition of tokens

    def t_SIN(self, t):
        r'cmath\.sin'
        return t
    def t_COS(self, t):
        r'cmath\.cos'
        return t
    def t_TAN(self, t):
        r'cmath\.tan'
        return t
    def t_SQRT(self, t):
        r'cmath\.sqrt|sqrt'
        return t
    def t_PI(self, t):
        r'cmath\.pi'
        return t
    def t_CONJ(self, t):
        r'complexconjugate'
        return t
    def t_VARIABLE(self, t):
        r'[a-zA-Z_][0-9a-zA-Z_]*'
        return t

    t_NUMBER = r'([0-9]+\.[0-9]*|\.[0-9]+|[0-9]+)([eE][+-]{0,1}[0-9]+){0,1}'
    t_POWER  = r'\*\*'

    t_ignore = " \t"

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Build the lexer
    def build(self,**kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    # Definitions for the PLY yacc parser

    # Parsing rules
    precedence = (
        ('left','='),
        ('left','+','-'),
        ('left','*','/'),
        ('right','UMINUS'),
        ('left','POWER'),
        ('right','SIN'),
        ('right','COS'),
        ('right','TAN'),
        ('right','SQRT'),
        ('right','CONJ')
        )

    # Dictionary of parser expressions
    def p_statement_expr(self, p):
        'statement : expression'
        print(p[1])

    def p_expression_binop(self, p):
        '''expression : expression '=' expression
                      | expression '+' expression
                      | expression '-' expression
                      | expression '*' expression
                      | expression '/' expression'''
        p[0] = p[1] + p[2] + p[3]

    def p_expression_uminus(self, p):
        "expression : '-' expression %prec UMINUS"
        p[0] = '-' + p[2]

    def p_group_parentheses(self, p):
        "group : '(' expression ')'"
        p[0] = '(' + p[2] +')'

    def p_expression_group(self, p):
        "expression : group"
        p[0] = p[1]

    def p_expression_variable(self, p):
        "expression : VARIABLE"
        p[0] = p[1]

    def p_expression_number(self, p):
        "expression : NUMBER"
        p[0] = p[1]

    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")

class UFOExpressionParserFortran(UFOExpressionParser):
    """A parser for UFO algebraic expressions, outputting
    Fortran-style code."""

    # The following parser expressions need to be defined for each
    # output language/framework

    def p_expression_power(self, p):
        'expression : expression POWER expression'
        p[0] = p[1] + "**" + p[3]

    def p_expression_func(self, p):
        '''expression : SIN group
                      | COS group
                      | TAN group
                      | SQRT group
                      | CONJ group'''
        if p[1] == 'cmath.sin': p[0] = 'sin' + p[2]
        elif p[1] == 'cmath.cos': p[0] = 'cos' + p[2]
        elif p[1] == 'cmath.tan': p[0] = 'tan' + p[2]
        elif p[1] == 'cmath.sqrt' or p[1] == 'sqrt': p[0] = 'dsqrt' + p[2]
        elif p[1] == 'complexconjugate': p[0] = 'conjg' + p[2]

    def p_expression_pi(self, p):
        '''expression : PI'''
        p[0] = 'pi'

class UFOExpressionParserPythia8(UFOExpressionParser):
    """A parser for UFO algebraic expressions, outputting
    C++-style code."""

    # The following parser expressions need to be defined for each
    # output language/framework

    def p_expression_power(self, p):
        'expression : expression POWER expression'
        p1=p[1]
        p3=p[3]
        if p[1][0] == '(' and p[1][-1] == ')':
            p1 = p[1][1:-1]
        if p[3][0] == '(' and p[3][-1] == ')':
            p3 = p[3][1:-1]
        p[0] = 'pow(' + p1 + ',' + p3 + ')'        

    def p_expression_func(self, p):
        '''expression : SIN group
                      | COS group
                      | TAN group
                      | SQRT group
                      | CONJ group'''
        if p[1] == 'cmath.sin': p[0] = 'sin' + p[2]
        elif p[1] == 'cmath.cos': p[0] = 'cos' + p[2]
        elif p[1] == 'cmath.tan': p[0] = 'tan' + p[2]
        elif p[1] == 'cmath.sqrt' or p[1] == 'sqrt': p[0] = 'sqrt' + p[2]
        elif p[1] == 'complexconjugate': p[0] = 'conj' + p[2]

    def p_expression_pi(self, p):
        '''expression : PI'''
        p[0] = 'pi'

if __name__ == '__main__':

    if len(sys.argv) == 1:
        print "Please specify a parser: fortran or pythia8"
        exit()
    if sys.argv[1] == "fortran":
        calc = UFOExpressionParserFortran()
    elif sys.argv[1] == "pythia8":
        calc = UFOExpressionParserPythia8()
    else:
        print "Please specify a parser: tex, fortran or pythia8"
        print "You gave", sys.argv
        exit()        

    while 1:
        try:
            s = raw_input('calc > ')
        except EOFError:
            break
        if not s: continue
        calc.parse(s)

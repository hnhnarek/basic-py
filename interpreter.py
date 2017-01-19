#!/usr/bin/python
# -*- coding: utf-8 -*-

import enum
import re

#
# Հայտարարված ու սահմանված ենթածրագրերի ցուցակ
#
subroutines = dict()

#
# Ֆունկցիա կամ պրոցեդուրա
#
class Procedure:
    name = None
    parameters = []
    body = None

    def __init__(self, nm, prs):
        self.name = nm
        self.parameters = prs
        self.body = None

    def setBody(self, bo):
        self.body = bo

    def __str__(self):
        result = 'PROCEDURE ' + self.name
        result += '(' + str(self.parameters) + ')\n'
        result += str(self.body)
        result += '\nEND'
        return result

#
# Հաստատուն
#
class Number:
    value = 0.0
    
    def __init__(self, vl):
        self.value = vl

    def evaluate(self, env):
        return self.value

#
# Փոփոխական
#
class Variable:
    name = None
    
    def __init__(self, nm):
        self.name = nm

    def evaluate(self, env):
        return env[self.name]

    def __str__(self):
        return self.name

#
# Ունար գործողություն
#
class Unary:
    operation = None
    subexpr = None
    
    def __init__(self, op, ex):
        self.operation = op
        self.subexpr = ex

    def evaluate(self, env):
        ro = self.subexpr.evaluate(env)
        if self.operation == '-':
            return -ro
        return ro

    def __str__(self):
        s0 = str(self.subexpr)
        return '(' + self.operation + s0 + ')'

#
# Բինար գործողություն
#
class Binary:
    operation = None
    subexpro = None
    subexpri = None

    def __init__(self, op, exo, exi):
        self.operation = op
        self.subexpro = exo
        self.subexpri = exi

    def evaluate(self, env):
        ro = self.subexpro.evaluate(env)
        ri = self.subexpri.evaluate(env)
        if self.operation == '+':
            return ro + ri
        if self.operation == '-':
            return ro - ri
        if self.operation == '*':
            return ro * ri
        if self.operation == '/':
            # ստուգել 0֊ի վրա բաժանելը
            return ro / ri
        return 0.0

    def __str__(self):
        s0 = str(self.subexpro)
        s1 = str(self.subexpri)
        return '(' + s0 + ' ' + self.operation + ' ' + s1 + ')'

#
# Ֆունկցիայի կանչ
#
class Apply:
    caleename = None
    arguments = []

    def __init__(self, cl, ags):
        self.caleename = cl
        self.arguments = ags

    def evaluate(self, env):
        # ստուգել caleename֊ի գոյությունը subroutines֊ում
        calee = subroutines[self.caleename]
        # ստուգել len(calee.parametrs) == len(self.arguments)
        envext = dict(env)
        for k,v in zip(calee.parameters, self.arguments):
            envext[k] = v.evaluate(env)
        return calee.body.evaluate(envext)

#
# Արտածում
#
class Print:
    subexpr = None
    
    def __init__(self, ex):
        self.subexpr = ex

    def execute(self, env):
        v0 = self.subexpr.evaluate(env)
        print(v0)

    def __str__(self):
        return 'PRINT ' + str(self.subexpr)

#
# Պայման կամ ճյուղավորում
#
class Branch:
    condition = None
    #
    #

    def __init__(self, co, ac, de):
        self.condition = co

    def execute(self, env):
        pass

    def __str__(self):
        pass

#
# Թոքեններ
#
class Token(Enum):
    xNull   = 0
    xNumber = 1
    xIdent  = 2
    # թվաբանություն
    xAdd = 20
    xSub = 21
    xMul = 22
    xDiv = 23
    # համեմատություն
    xEq = 24
    xNe = 25
    xGt = 26
    xGe = 27
    xLt = 28
    xLe = 29
    # տրամաբանական
    xAnd = 30
    xOr  = 31
    xNot = 32
    # ծառայողական նիշեր
    xLPar  = 36
    xRPar  = 37
    xComma = 38
    xEol   = 39
    # ծառայողական բառեր
    xDeclare  = 40
    xFunction = 41
    xEnd      = 42
    xPrint    = 43
    xInput    = 44
    xLet      = 45
    xIf       = 46
    xThen     = 47
    xElseIf   = 48
    xElse     = 49
    xWhile    = 50
    xFor      = 51
    xTo       = 52
    xStep     = 53    

#
# Բառային վերլուծություն
#
class Scanner:
    # ծառայողական բառեր
    keywords = {
        'DECLARE'  : Token.xDeclare,
        'FUNCTION' : Token.xFunction,
        'END'      : Token.xEnd,
        'PRINT'    : Token.xPrint,
        'INPUT'    : Token.xInput,
        'LET'      : Token.xLet,
        'IF'       : Token.xIf,
        'THEN'     : Token.xThen,
        'ELSEIF'   : Token.xElseIf,
        'ELSE'     : Token.xElse,
        'WHILE'    : Token.xWhile,
        'FOR'      : Token.xFor,
        'TO'       : Token.xTo,
        'STEP'     : Token.xStep,
        'AND'      : Token.xAnd,
        'OR'       : Token.xOr,
        'NOT'      : Token.xNot
    }
    # գործողություններ
    operations = {
        '+'  : Token.xAdd,
        '-'  : Token.xSub,
        '*'  : Token.xMul,
        '/'  : Token.xDiv,
        '='  : Token.xEq,
        '<>' : Token.xNe,
        '>'  : Token.xGt,
        '>=' : Token.xGe,
        '<'  : Token.xLt,
        '<=' : Token.xLe
    }

    #
    def __init__(self, src):
        self.source = src + '@'
        self.rxNumber = re.compile(r'^[0-9]+(\.[0-9]+)?')
        self.rxIdent = re.compile(r'^[a-zA-Z][a-zA-Z0-9]*')
        self.rxRelOps = re.compile(r'^<>|<=|>=|=|>|<')
        self.rxSymbols = re.compile(r'^[\n\(\),]')
        
    #
    def scan(self):
        # մաքրել բացատները
        k = 0
        while self.source[k] == ' ' or self.source[k] == '\t':
            k += 1
        if k != 0:
            self.source = self.source[k:]

        

#
# Շարահյուսական վերլուծություն
#

##
## TEST
##
if __name__ == '__main__':
    # env = dict()

    # n0 = Number(3.14)
    # print(n0.evaluate(env))

    # env['x'] = 1.234
    # v0 = Variable('x')
    # print(v0.evaluate(env))

    # u0 = Unary('-', Number(7))
    # print(u0.evaluate(env))

    # env['y'] = 222
    # b0 = Binary('*', Number(2), Variable('y'))
    # print(b0.evaluate(env))

    # s0 = Procedure('f', ['x', 'y'])
    # s0.setBody(Binary('+', Variable('x'), Variable('y')))
    # subroutines['f'] = s0
    # print(s0)
    # print(env)
    # a0 = Apply('f', [Number(123), Number(456)])
    # print(a0.evaluate(env))

    scan = Scanner('FUNCTION')
    print(scan.keywords)
    print(scan.scan())



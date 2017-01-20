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
    def __init__(self, vl):
        self.value = vl

    def evaluate(self, env):
        return self.value

#
# Փոփոխական
#
class Variable:
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
# Վերագրում
#
class Assign:
    def __init__(self, nm, ex):
        self.varname = nm
        self.subexpr = ex

    def execute(self, env):
        pass

    def __str__(self):
        nm = self.varname
        ex = str(self.subexpr)
        return 'LET {} = {}'.format(nm, ex)

#
# Արտածում
#
class Print:
    def __init__(self, ex):
        self.subexpr = ex

    def execute(self, env):
        v0 = self.subexpr.evaluate(env)
        print(v0)

    def __str__(self):
        so = str(self.subexpr)
        return 'PRINT {}'.format(so)

#
# Ներմուծում
#
class Input:
    def __init__(self, nm):
        self.varname = ex

    def execute(self, env):
        pass

    def __str__(self):
        return 'INPUT {}'.format(self.varname)

#
# Պայման կամ ճյուղավորում
#
class Branch:
    def __init__(self, co, de, al):
        self.condition = co
        self.decision = de
        self.alternative = al

    def execute(self, env):
        pass

    def __str__(self):
        pass

#
# Նախապայմանով ցիկլ
#
class WhileLoop:
    def __init__(self, co, bo):
        self.condition = co
        self.body = bo

    def execute(self, env):
        pass

    def __str__(self):
        pass

#
# Պարամետրով ցիկլ
#
class ForLoop:
    def __init__(self, pr, be, en, sp, bo):
        self.parameter = pr
        self.begin = be
        self.end = en
        self.step = sp
        self.body = bo

    def execute(self, env):
        pass

    def __str__(self):
        pass

#
# Պրոցեդուրայի կանչ
#
class Call:
    def __init__(self, cl, ags):
        self.call = Apply(cl, ags)

    def execute(self, env):
        self.call.evaluate(env)

    def __str__(self):
        pass

#
# Թոքեններ
#
class Token(enum.Enum):
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
    xCall     = 54

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
        'CALL'     : Token.xCall,
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
    # մետասիմվոլներ
    symbols = {
        '('  : Token.xLPar,
        ')'  : Token.xRPar,
        ','  : Token.xComma,
        '\n' : Token.xEol
    }

    #
    def __init__(self, src):
        self.source = src + '@'
        self.rxNumber = re.compile(r'^[0-9]+(\.[0-9]+)?')
        self.rxIdent = re.compile(r'^[a-zA-Z][a-zA-Z0-9]*')
        self.rxMathOps = re.compile(r'^<>|<=|>=|=|>|<|\+|\-|\*|/')
        self.rxSymbols = re.compile(r'^[\n\(\),]')

    #
    def __iter__(self):
        return self
    
    #
    def __next__(self):
        # մաքրել բացատները
        k = 0
        while self.source[k] in ' \t':
            k += 1
        if k != 0:
            self.source = self.source[k:]

        # հոսքի վերջը
        if self.source[0] == '@':
            raise StopIteration()

        # 
        meo = self.rxIdent.match(self.source)
        if meo:
            lexeme = meo.group(0)
            self.source = self.source[meo.end():]
            token = self.keywords.get(lexeme, Token.xIdent)
            return (lexeme, token)

        #
        meo = self.rxNumber.match(self.source)
        if meo:
            lexeme = meo.group(0)
            self.source = self.source[meo.end():]
            return (lexeme, Token.xNumber)

        #
        meo = self.rxMathOps.match(self.source)
        if meo:
            lexeme = meo.group(0)
            self.source = self.source[meo.end():]
            token = self.operations[lexeme]
            return (lexeme, token)

        #
        meo = self.rxSymbols.match(self.source)
        if meo:
            lexeme = meo.group(0)
            self.source = self.source[meo.end():]
            token = self.symbols[lexeme]
            return (lexeme, token)

        return None

        

#
# Շարահյուսական վերլուծություն
#
class Parser:
    #
    def __init__(self, name):
        text = ''
        with open(name, 'r') as source:
            text = source.read()
        self.scan = Scanner(text)


    # լեքսեմ
    def L(self):
        return self.lookahead[0]
    # թոքենի ստուգում
    def T(self, token):
        return token == self.lookahead[1]

    #
    def parse(self):
        self.lookahead = next(self.scan)
        self.parseEols()
        while True:
            if self.T(Token.xDeclare):
                self.parseDeclare()
            elif self.T(Token.xFunction):
                self.parseFunction()
            else:
                break
    
    #
    def match(self, token):
        if self.T(token):
            self.lookahead = next(self.scan)
        else:
            raise 1

    #
    def parseEols(self):
        self.match(Token.xEol)
        while self.T(Token.xEol):
            next(self.scan)

    #
    def parseHeader(self):
        self.match(Token.xFunction)
        name = self.L()
        self.match(Token.xIdent)
        params = []
        self.match(Token.xLPar)
        if self.T(Token.xIdent):
            self.match(Token.xIdent)
            while self.T(Token.xComma):
                self.match(Token.xComma)
                params.append(self.L())
                self.match(Token.xIdent)
        self.match(Token.xRPar)
        self.parseEols()
        return Function(name, params)

    #
    def parseDeclare(self):
        self.match(Token.xDeclare)
        return self.parseHeader()

    #
    def parseFunction(self):
        header = self.parseHeader()
        self.parseStatement()
        self.match(Token.xEnd)
        self.match(Token.xFunction)

    #
    def parseStatement(self):
        stats = []
        while True:
            if self.T(Token.xLet) or self.T(Token.xIdent):
                stats.append(self.parseAssign())
            elif self.T(Token.xPrint):
                stats.append(self.parsePrint())
            elif self.T(Token.xInput):
                stats.append(self.parseInput())
            elif self.T(Token.xIf):
                stats.append(self.parseBranch())
            elif self.T(Token.xWhile):
                stats.append(self.parseWhile())
            elif self.T(Token.xFor):
                stats.append(self.parseFor())
            elif self.T(Token.xCall):
                stats.append(self.parseCall())
            else:
                break
        return stats

    #
    def parseAssign(self):
        if self.T(Token.xLet):
            next(self.lookahead)
        name = self.L()
        self.match(Token.xIdent)
        self.match(Token.xEq)
        expr = self.parseDisjunction()
        return Assign(name, expr)

    #
    def parsePrint(self):
        self.match(Token.xPrint)
        expr = self.parseDisjunction()
        return Print(expr)

    #
    def parseInput(self):
        self.match(Token.xInput)
        name = self.L()
        self.match(Token.xIdent)
        return Input(name)

    #
    def parseBranch(self):
        return None

    #
    def parseWhile(self):
        self.match(Token.xWhile)
        cond = self.parseDisjunction()
        self.parseEols()
        # TODO վերլուծել մարմին
        self.match(Token.xEnd)
        self.match(Token.xWhile)
        return None

    #
    def parseFor(self):
        return None

    #
    def parseCall(self):
        return None




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

    text0 = '''FUNCTION fact(n)
                IF n = 1 THEN
                    fact = 1
                ELSE
                    fact = n * fact(n - 1)
                END IF
            END FUNCTION'''

    scan = Scanner(text0)
    #for i in range(0, 35):
    #    print(scan.scan())
    for kv in scan:
        print(kv)



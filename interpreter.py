#!/usr/bin/python
# -*- coding: utf-8 -*-

import enum
import functools
import re
import sys

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
        result = 'FUNCTION ' + self.name
        result += '(' + (', '.join(self.parameters)) + ')\n'
        for stat in self.body:
            result += str(stat)
            result += '\n'
        result += 'END'
        return result

#
# Հաստատուն
#
class Number:
    def __init__(self, vl):
        self.value = vl

    def evaluate(self, env):
        return self.value

    def __str__(self):
        return str(self.value)

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
        return '({} {})'.format(self.operation, s0)

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
        return '({} {} {})'.format(s0, self.operation, s1)

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

    def __str__(self):
        return None

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
        self.varname = nm

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
        result = 'FOR ' + str(self.parameter)
        result += ' = ' + str(self.begin)
        result += ' TO ' + str(self.end)
        result += ' STEP ' + str(self.step) + '\n'
        for se in self.body:
            result += str(se) + '\n'
        result += 'END FOR'
        return result

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
class Kind(enum.Enum):
    Null   = 0
    Eof    = 1
    Number = 2
    Ident  = 3
    # թվաբանություն
    Add = 20
    Sub = 21
    Mul = 22
    Div = 23
    Pow = 24
    # համեմատություն
    Eq = 25
    Ne = 26
    Gt = 27
    Ge = 28
    Lt = 29
    Le = 30
    # տրամաբանական
    And = 33
    Or  = 34
    Not = 35
    # ծառայողական նիշեր
    LPar  = 36
    RPar  = 37
    Comma = 38
    Eol   = 39
    # ծառայողական բառեր
    Declare  = 40
    Function = 41
    End      = 42
    Print    = 43
    Input    = 44
    Let      = 45
    If       = 46
    Then     = 47
    ElseIf   = 48
    Else     = 49
    While    = 50
    For      = 51
    To       = 52
    Step     = 53
    Call     = 54

#
# Բառային վերլուծություն
#
class Scanner:
    # ծառայողական բառեր
    keywords = {
        'DECLARE'  : Kind.Declare,
        'FUNCTION' : Kind.Function,
        'END'      : Kind.End,
        'PRINT'    : Kind.Print,
        'INPUT'    : Kind.Input,
        'LET'      : Kind.Let,
        'IF'       : Kind.If,
        'THEN'     : Kind.Then,
        'ELSEIF'   : Kind.ElseIf,
        'ELSE'     : Kind.Else,
        'WHILE'    : Kind.While,
        'FOR'      : Kind.For,
        'TO'       : Kind.To,
        'STEP'     : Kind.Step,
        'CALL'     : Kind.Call,
        'AND'      : Kind.And,
        'OR'       : Kind.Or,
        'NOT'      : Kind.Not
    }
    # գործողություններ
    operations = {
        '+'  : Kind.Add,
        '-'  : Kind.Sub,
        '*'  : Kind.Mul,
        '/'  : Kind.Div,
        '='  : Kind.Eq,
        '<>' : Kind.Ne,
        '>'  : Kind.Gt,
        '>=' : Kind.Ge,
        '<'  : Kind.Lt,
        '<=' : Kind.Le
    }
    # մետասիմվոլներ
    symbols = {
        '('  : Kind.LPar,
        ')'  : Kind.RPar,
        ','  : Kind.Comma,
        '\n' : Kind.Eol
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
            return ('EOF', Kind.Eof)

        # 
        meo = self.rxIdent.match(self.source)
        if meo:
            lexeme = meo.group(0)
            self.source = self.source[meo.end():]
            token = self.keywords.get(lexeme, Kind.Ident)
            return (lexeme, token)

        #
        meo = self.rxNumber.match(self.source)
        if meo:
            lexeme = meo.group(0)
            self.source = self.source[meo.end():]
            return (lexeme, Kind.Number)

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
class SyntaxError(Exception):
    def __init__(self, mes):
        self.message = mes

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
    def T(self, *tokens):
        for tok in tokens:
            if tok == self.lookahead[1]:
                return True
        return False

    #
    def parse(self):
        self.lookahead = next(self.scan)

        while self.T(Kind.Eol):
            self.eat()

        program = []
        while True:
            if self.T(Kind.Declare):
                subr = self.parseDeclare()
            elif self.T(Kind.Function):
                subr = self.parseFunction()
            else:
                break
            program.append(subr)

        return program
    
    #
    def eat(self):
        self.lookahead = next(self.scan)
    def match(self, token):
        if self.T(token):
            self.eat()
        else:
            mes = 'Expected {}, but got {}'.format(token, self.lookahead)
            raise SyntaxError(mes)

    #
    def parseEols(self):
        self.match(Kind.Eol)
        while self.T(Kind.Eol):
            self.eat()

    #
    def parseHeader(self):
        self.match(Kind.Function)
        name = self.L()
        self.match(Kind.Ident)
        params = []
        self.match(Kind.LPar)
        if self.T(Kind.Ident):
            params.append(self.L())
            self.match(Kind.Ident)
            while self.T(Kind.Comma):
                self.match(Kind.Comma)
                params.append(self.L())
                self.match(Kind.Ident)
        self.match(Kind.RPar)
        self.parseEols()
        return Procedure(name, params)

    #
    def parseDeclare(self):
        self.match(Kind.Declare)
        return self.parseHeader()

    #
    def parseFunction(self):
        subr = self.parseHeader()
        body = self.parseStatements()
        subr.setBody(body)
        self.match(Kind.End)
        self.match(Kind.Function)
        return subr

    #
    def parseStatements(self):
        stats = []
        while True:
            if self.T(Kind.Let) or self.T(Kind.Ident):
                stats.append(self.parseAssign())
            elif self.T(Kind.Print):
                stats.append(self.parsePrint())
            elif self.T(Kind.Input):
                stats.append(self.parseInput())
            elif self.T(Kind.If):
                stats.append(self.parseBranch())
            elif self.T(Kind.While):
                stats.append(self.parseWhile())
            elif self.T(Kind.For):
                stats.append(self.parseFor())
            elif self.T(Kind.Call):
                stats.append(self.parseCall())
            else:
                break
            self.parseEols()
        return stats

    #
    def parseAssign(self):
        if self.T(Kind.Let):
            self.eat()
        name = self.L()
        self.match(Kind.Ident)
        self.match(Kind.Eq)
        expr = self.parseDisjunction()
        return Assign(name, expr)

    #
    def parsePrint(self):
        self.match(Kind.Print)
        expr = self.parseDisjunction()
        return Print(expr)

    #
    def parseInput(self):
        self.match(Kind.Input)
        name = self.L()
        self.match(Kind.Ident)
        return Input(name)

    #
    def parseBranch(self):
        self.match(Kind.If)
        return None

    #
    def parseWhile(self):
        self.match(Kind.While)
        cond = self.parseDisjunction()
        self.parseEols()
        bdy = self.parseStatements()
        self.match(Kind.End)
        self.match(Kind.While)
        return WhileLoop(cond, bdy)

    #
    def parseFor(self):
        ''' Statement = FOR IDENT '=' E TO E [STEP [(+|-)]E] Eols Statements END FOR'''
        self.match(Kind.For)
        param = self.L()
        self.match(Kind.Ident)
        self.match(Kind.Eq)
        begin = self.parseAddition()
        self.match(Kind.To)
        end = self.parseAddition()
        step = Number(1)
        if self.T(Kind.Step):
            self.match(Kind.Step)
            sign = '+'
            if self.T(Kind.Add, Kind.Sub):
                sign = self.L()
                self.eat()
            spv = self.L()
            self.match(Kind.Number)
            exo = Number(spv)
            step = Unary('-', spv) if sign == '-' else exo
        self.parseEols()
        body = self.parseStatements()
        self.match(Kind.End)
        self.match(Kind.For)
        return ForLoop(param, begin, end, step, body)

    #
    def parseCall(self):
        self.match(Kind.Call)
        name = self.L()
        self.match(Kind.Ident)
        
        argus = []
        if self.T(Kind.Number, Kind.Ident, Kind.Sub, Kind.Not, Kind.LPar):
            exi = self.parseDisjunction()
            argus.append(exi)
            while self.T(Kind.Comma):
                self.match(Kind.Comma)
                exi = self.parseDisjunction()
                argus.append(exi)

        return Call(name, argus)

    #
    def parseDisjunction(self):
        exo = self.parseConjunction()
        while self.T(Kind.Or):
            oper = self.L()
            self.eat()
            exi = self.parseConjunction()
            exo = Binary('OR', exo, exi)
        return exo

    #
    def parseConjunction(self):
        exo = self.parseEquality()
        while self.T(Kind.And):
            oper = self.L()
            self.eat()
            exi = self.parseEquality()
            exo = Binary('AND', exo, exi)
        return exo

    #
    def parseEquality(self):
        exo = self.parseComparison()
        while self.T(Kind.Eq, Kind.Ne):
            oper = self.L()
            self.eat()
            exi = self.parseComparison()
            exo = Binary(oper, exo, exi)
        return exo

    #
    def parseComparison(self):
        exo = self.parseAddition()
        while self.T(Kind.Gt, Kind.Ge, Kind.Lt, Kind.Le):
            oper = self.L()
            self.eat()
            exi = self.parseAddition()
            exo = Binary(oper, exo, exi)
        return exo

    #
    def parseAddition(self):
        exo = self.parseMultiplication()
        while self.T(Kind.Add, Kind.Sub):
            oper = self.L()
            self.eat()
            exi = self.parseMultiplication()
            exo = Binary(oper, exo, exi)
        return exo

    #
    def parseMultiplication(self):
        exo = self.parsePower()
        while self.T(Kind.Mul, Kind.Div):
            oper = self.L()
            self.eat()
            exi = self.parsePower()
            exo = Binary(oper, exo, exi)
        return exo

    #
    def parsePower(self):
        exo = self.parseFactor()
        if self.T(Kind.Pow):
            self.eat()
            exi = self.parsePower()
            exo = Binary('^', exo, exi)
        return exo

    #
    def parseFactor(self):
        #
        if self.T(Kind.Number):
            value = float(self.L())
            self.match(Kind.Number)
            return Number(value)

        #
        if self.T(Kind.Ident):
            name = self.L()
            self.match(Kind.Ident)
            if self.T(Kind.LPar):
                argus = []
                self.match(Kind.LPar)
                if self.T(Kind.Number, Kind.Ident, Kind.Sub, Kind.Not, Kind.LPar):
                    exi = self.parseDisjunction()
                    argus.append(exi)
                    while self.T(Kind.Comma):
                        self.match(Kind.Comma)
                        exi = self.parseDisjunction()
                        argus.append(exi)
                self.match(Kind.RPar)
                return Apply(name, argus)
            else:
                return Variable(name)

        #
        if self.T(Kind.Sub, Kind.Not):
            oper = self.L()
            self.eat()
            suex = self.parseFactor()
            return Unary(oper, suex)

        #
        if self.T(Kind.LPar):
            self.match(Kind.LPar)
            suex = self.parseDisjunction()
            self.match(Kind.RPar)
            return suex

        return None




##
## TEST
##
if __name__ == '__main__':
    parser = Parser('C:/Projects/basic-py/case05.bas')
    prog = parser.parse()
    for pr in prog:
        print(str(pr))



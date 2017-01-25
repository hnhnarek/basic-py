#!/usr/bin/python
# -*- coding: utf-8 -*-

import enum
import functools
import math
import operator
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
    def __init__(self, nm, prs, bo):
        self.name = nm
        self.parameters = prs
        self.body = bo

#
# Հաստատուն
#
class Number:
    def __init__(self, vl):
        self.value = vl

    def evaluate(self, env):
        return self.value

#
#
#
class Text:
    def __init__(self, bv):
        self.value = bv

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

#
# Բինար գործողություն
#
class Binary:
    __opdict = {
        '+'   : operator.add,
        '-'   : operator.sub,
        '*'   : operator.mul,
        '/'   : operator.truediv,
        '^'   : operator.pow,
        '='   : operator.eq,
        '<>'  : operator.ne,
        '>'   : operator.gt,
        '>='  : operator.ge,
        '<'   : operator.lt,
        '<='  : operator.le,
        'AND' : lambda a, b: a and b,
        'OR'  : lambda a, b: a or b
    }
    
    def __init__(self, op, exo, exi):
        self.operation = op
        self.subexpro = exo
        self.subexpri = exi

    def evaluate(self, env):
        ro = self.subexpro.evaluate(env)
        ri = self.subexpri.evaluate(env)
        opc = self.__opdict.get(self.operation)
        return opc(ro, ri) if opc else 0.0

#
#
#
class RuntimeError:
    def __init__(self, mes):
        self.message = mes

#
# Ֆունկցիայի կանչ
#
class Apply:
    builtins = {
        'SQR' : math.sqrt
    }
    
    def __init__(self, cl, ags):
        self.calleename = cl
        self.arguments = ags

    def evaluate(self, env):
        # builtins
        if self.calleename in self.builtins:
            agv = self.arguments[0].evaluate(env)
            return self.builtins[self.calleename](agv)

        # ստուգել caleename֊ի գոյությունը subroutines֊ում
        callee = subroutines.get(self.calleename)
        if not callee:
            raise RuntimeError('')

        # ստուգել len(callee.parametrs) == len(self.arguments)
        if len(self.arguments) != len(callee.parameters):
            raise RuntimeError('')

        envext = dict(env)
        envext[self.calleename] = 0
        for k,v in zip(callee.parameters, self.arguments):
            envext[k] = v.evaluate(env)

        callee.body.execute(envext)

        return envext[self.calleename]

#
# Վերագրում
#
class Assign:
    def __init__(self, nm, ex):
        self.varname = nm
        self.subexpr = ex

    def execute(self, env):
        e0 = self.subexpr.evaluate(env)
        env[self.varname] = e0

#
# Արտածում
#
class Print:
    def __init__(self, ex):
        self.subexpr = ex

    def execute(self, env):
        v0 = self.subexpr.evaluate(env)
        print(v0)

#
# Ներմուծում
#
class Input:
    def __init__(self, nm):
        self.varname = nm

    def execute(self, env):
        text = input('? ')
        env[self.varname] = float(text)

#
# Պայման կամ ճյուղավորում
#
class Branch:
    def __init__(self, co, de):
        self.condition = co
        self.decision = de
        self.alternative = None

    def setElse(self, al):
        self.alternative = al

    def execute(self, env):
        if self.condition.evaluate(env) != 0.0:
            self.decision.execute(env)
        else:
            self.alternative.execute(env)

#
# Նախապայմանով ցիկլ
#
class WhileLoop:
    def __init__(self, co, bo):
        self.condition = co
        self.body = bo

    def execute(self, env):
        while self.condition.evaluate(env) != 0.0:
            self.body.execute(env)

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
        pr = self.parameter
        be = self.begin.evaluate(env)
        en = self.end.evaluate(env)
        sp = self.step.evaluate(env)
        
        env[pr] = be
        while env[pr] <= en if sp > 0 else env[pr] >= en:
            self.body.execute(env)
            env[pr] = env[pr] + sp
        del env[pr]

#
# Պրոցեդուրայի կանչ
#
class Call:
    def __init__(self, cl, ags):
        self.call = Apply(cl, ags)

    def execute(self, env):
        self.call.evaluate(env)

#
# 
#
class Sequence:
    def __init__(self, sl):
        self.items = sl

    def execute(self, env):
        for se in self.items:
            se.execute(env)

#
# Թոքեններ
#
class Kind(enum.Enum):
    Null   = 0
    Eof    = 1
    Number = 2
    Text   = 3
    Ident  = 4
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
    Function = 61
    End      = 62
    Print    = 63
    Input    = 64
    Let      = 65
    If       = 66
    Then     = 67
    ElseIf   = 68
    Else     = 69
    While    = 70
    For      = 71
    To       = 72
    Step     = 73
    Call     = 74


#
# Բառային վերլուծություն
#
class Scanner:
    # ծառայողական բառեր
    keywords = {
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
        '^'  : Kind.Pow,
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
        self.line = 1

        self.rxComment = re.compile(r'^\'.*')
        self.rxNumber = re.compile(r'^[0-9]+(\.[0-9]+)?')
        self.rxText = re.compile(r'"[^"]*"')
        self.rxIdent = re.compile(r'^[a-zA-Z][a-zA-Z0-9]*')
        self.rxMathOps = re.compile(r'^<>|<=|>=|=|>|<|\+|\-|\*|/|\^')
        self.rxSymbols = re.compile(r'^[\n\(\),]')

    #
    def __iter__(self):
        return self

    #
    def cutLexeme(self, ma):
        lexeme = ma.group(0)
        self.source = self.source[ma.end():]
        return lexeme

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
            return ('EOF', Kind.Eof, self.line)

        # մեկնաբանություն
        meo = self.rxComment.match(self.source)
        if meo:
            self.source = self.source[meo.end():]
            return self.__next__()
        
        # 
        meo = self.rxIdent.match(self.source)
        if meo:
            lexeme = self.cutLexeme(meo)
            token = self.keywords.get(lexeme, Kind.Ident)
            return (lexeme, token, self.line)

        #
        meo = self.rxNumber.match(self.source)
        if meo:
            lexeme = self.cutLexeme(meo)
            return (lexeme, Kind.Number, self.line)

        #
        meo = self.rxText.match(self.source)
        if meo:
            lexeme = self.cutLexeme(meo)
            return (lexeme, Kind.Text, self.line)

        #
        meo = self.rxMathOps.match(self.source)
        if meo:
            lexeme = self.cutLexeme(meo)
            token = self.operations[lexeme]
            return (lexeme, token, self.line)

        #
        meo = self.rxSymbols.match(self.source)
        if meo:
            lexeme = self.cutLexeme(meo)
            token = self.symbols[lexeme]
            if '\n' == lexeme:
                self.line += 1
            return (lexeme, token, self.line)

        return None

        

#
# Շարահյուսական վերլուծություն
#
class SyntaxError(Exception):
    def __init__(self, mes):
        self.message = mes

#
#
class Parser:
    '''
    Շարահյուսական վերլուծիչն իրականացված
    '''

    #
    def __init__(self, name):
        text = ''
        with open(name, 'r') as source:
            text = source.read()
        self.scan = Scanner(text)


    # լեքսեմ
    def __L(self):
        return self.lookahead[0]
    # թոքենի ստուգում
    def __T(self, *tokens):
        for tok in tokens:
            if tok == self.lookahead[1]:
                return True
        return False

    #
    def parse(self):
        try:
            self.lookahead = next(self.scan)

            while self.__T(Kind.Eol):
                self.__eat()

            #
            while self.__T(Kind.Function):
                subr = self.parseFunction()
                subroutines[subr.name] = subr

            #
            stats = self.parseStatements()
            entryf = Procedure('entry', [], stats)
            subroutines['entry'] = entryf
        except SyntaxError as se:
            print(se)
            return False

        return True

    #
    def __eat(self):
        self.lookahead = next(self.scan)
    def __match(self, token):
        if self.__T(token):
            self.__eat()
        else:
            mes = 'Expected {}, but got {}'.format(token, self.lookahead)
            raise SyntaxError(mes)

    #
    def parseNewLines(self):
        self.__match(Kind.Eol)
        while self.__T(Kind.Eol):
            self.__eat()

    #
    def parseFunction(self):
        self.__match(Kind.Function)
        name = self.__L()
        self.__match(Kind.Ident)
        params = []
        self.__match(Kind.LPar)
        if self.__T(Kind.Ident):
            params.append(self.__L())
            self.__match(Kind.Ident)
            while self.__T(Kind.Comma):
                self.__match(Kind.Comma)
                params.append(self.__L())
                self.__match(Kind.Ident)
        self.__match(Kind.RPar)
        self.parseNewLines()
        body = self.parseStatements()
        self.__match(Kind.End)
        self.__match(Kind.Function)
        self.parseNewLines()
        subr = Procedure(name, params, body)
        return subr

    #
    def parseStatements(self):
        stats = []
        while True:
            if self.__T(Kind.Let) or self.__T(Kind.Ident):
                stats.append(self.parseAssign())
            elif self.__T(Kind.Print):
                stats.append(self.parsePrint())
            elif self.__T(Kind.Input):
                stats.append(self.parseInput())
            elif self.__T(Kind.If):
                stats.append(self.parseBranch())
            elif self.__T(Kind.While):
                stats.append(self.parseWhile())
            elif self.__T(Kind.For):
                stats.append(self.parseFor())
            elif self.__T(Kind.Call):
                stats.append(self.parseCall())
            else:
                break
            self.parseNewLines()
        return Sequence(stats)

    #
    def parseAssign(self):
        if self.__T(Kind.Let):
            self.__eat()
        name = self.__L()
        self.__match(Kind.Ident)
        self.__match(Kind.Eq)
        expr = self.parseDisjunction()
        return Assign(name, expr)

    #
    def parsePrint(self):
        self.__match(Kind.Print)
        expr = self.parseDisjunction()
        return Print(expr)

    #
    def parseInput(self):
        self.__match(Kind.Input)
        name = self.__L()
        self.__match(Kind.Ident)
        return Input(name)

    #
    def parseBranch(self):
        self.__match(Kind.If)
        cond = self.parseDisjunction()
        self.__match(Kind.Then)
        self.parseNewLines()
        deci = self.parseStatements()
        statbr = Branch(cond, deci)
        bi = statbr
        while self.__T(Kind.ElseIf):
            self.__match(Kind.ElseIf)
            coe = self.parseDisjunction()
            self.__match(Kind.Then)
            self.parseNewLines()
            ste = self.parseStatements()
            bre = Branch(coe, ste)
            bi.setElse(bre)
            bi = bre
        if self.__T(Kind.Else):
            self.__match(Kind.Else)
            self.parseNewLines()
            bre = self.parseStatements()
            bi.setElse(bre)
        self.__match(Kind.End)
        self.__match(Kind.If)
        return statbr

    #
    def parseWhile(self):
        self.__match(Kind.While)
        cond = self.parseDisjunction()
        self.parseNewLines()
        bdy = self.parseStatements()
        self.__match(Kind.End)
        self.__match(Kind.While)
        return WhileLoop(cond, bdy)

    #
    def parseFor(self):
        ''' Statement = FOR IDENT '=' E TO E [STEP [(+|-)]E] Eols Statements END FOR'''
        self.__match(Kind.For)
        param = self.__L()
        self.__match(Kind.Ident)
        self.__match(Kind.Eq)
        begin = self.parseAddition()
        self.__match(Kind.To)
        end = self.parseAddition()
        step = Number(1)
        if self.__T(Kind.Step):
            self.__match(Kind.Step)
            sign = '+'
            if self.__T(Kind.Add, Kind.Sub):
                sign = self.__L()
                self.__eat()
            spv = self.__L()
            self.__match(Kind.Number)
            exo = Number(float(spv))
            step = Unary('-', exo) if sign == '-' else exo
        self.parseNewLines()
        body = self.parseStatements()
        self.__match(Kind.End)
        self.__match(Kind.For)
        return ForLoop(param, begin, end, step, body)

    #
    def parseCall(self):
        self.__match(Kind.Call)
        name = self.__L()
        self.__match(Kind.Ident)
        
        argus = []
        if self.__T(Kind.Number, Kind.Ident, Kind.Sub, Kind.Not, Kind.LPar):
            exi = self.parseDisjunction()
            argus.append(exi)
            while self.__T(Kind.Comma):
                self.__match(Kind.Comma)
                exi = self.parseDisjunction()
                argus.append(exi)

        return Call(name, argus)

    #
    def parseDisjunction(self):
        exo = self.parseConjunction()
        while self.__T(Kind.Or):
            oper = self.__L()
            self.__eat()
            exi = self.parseConjunction()
            exo = Binary('OR', exo, exi)
        return exo

    #
    def parseConjunction(self):
        exo = self.parseEquality()
        while self.__T(Kind.And):
            oper = self.__L()
            self.__eat()
            exi = self.parseEquality()
            exo = Binary('AND', exo, exi)
        return exo

    #
    def parseEquality(self):
        exo = self.parseComparison()
        while self.__T(Kind.Eq, Kind.Ne):
            oper = self.__L()
            self.__eat()
            exi = self.parseComparison()
            exo = Binary(oper, exo, exi)
        return exo

    #
    def parseComparison(self):
        exo = self.parseAddition()
        while self.__T(Kind.Gt, Kind.Ge, Kind.Lt, Kind.Le):
            oper = self.__L()
            self.__eat()
            exi = self.parseAddition()
            exo = Binary(oper, exo, exi)
        return exo

    #
    def parseAddition(self):
        exo = self.parseMultiplication()
        while self.__T(Kind.Add, Kind.Sub):
            oper = self.__L()
            self.__eat()
            exi = self.parseMultiplication()
            exo = Binary(oper, exo, exi)
        return exo

    #
    def parseMultiplication(self):
        exo = self.parsePower()
        while self.__T(Kind.Mul, Kind.Div):
            oper = self.__L()
            self.__eat()
            exi = self.parsePower()
            exo = Binary(oper, exo, exi)
        return exo

    #
    def parsePower(self):
        exo = self.parseFactor()
        if self.__T(Kind.Pow):
            self.__eat()
            exi = self.parsePower()
            exo = Binary('^', exo, exi)
        return exo

    #
    def parseFactor(self):
        #
        if self.__T(Kind.Number):
            value = float(self.__L())
            self.__match(Kind.Number)
            return Number(value)

        #
        if self.__T(Kind.Text):
            value = self.__L()
            self.__match(Kind.Text)
            return Text(value.strip('"'))

        #
        if self.__T(Kind.Ident):
            name = self.__L()
            self.__match(Kind.Ident)
            if self.__T(Kind.LPar):
                argus = []
                self.__match(Kind.LPar)
                if self.__T(Kind.Number, Kind.Ident, Kind.Sub, Kind.Not, Kind.LPar):
                    exi = self.parseDisjunction()
                    argus.append(exi)
                    while self.__T(Kind.Comma):
                        self.__match(Kind.Comma)
                        exi = self.parseDisjunction()
                        argus.append(exi)
                self.__match(Kind.RPar)
                return Apply(name, argus)
            else:
                return Variable(name)

        #
        if self.__T(Kind.Sub, Kind.Not):
            oper = self.__L()
            self.__eat()
            suex = self.parseFactor()
            return Unary(oper, suex)

        #
        if self.__T(Kind.LPar):
            self.__match(Kind.LPar)
            suex = self.parseDisjunction()
            self.__match(Kind.RPar)
            return suex

        return None

   
##
## TEST
##
if __name__ == '__main__':
    parser = Parser('tests/case09.bas')
    if parser.parse():
        try:
            Call('entry', []).execute({})
        except RuntimeError as er:
            print(er)


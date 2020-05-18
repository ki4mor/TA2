import ply.yacc as yacc
from ply.lex import LexError
import sys
from typing import List, Dict, Tuple, Any

from lexer.lexer import Lexer
from SyntaxTree.Tree import TreeNode


class Parser(object):
    tokens = Lexer.tokens

    def __init__(self):
        self.ok = True
        self.lexer = Lexer()
        self.parser = yacc.yacc(module=self)
        self._functions = dict()

    def parse(self, t):
        try:
            res = self.parser.parse(t)
            return res, self.ok, self._functions
        except LexError:
            sys.stderr.write(f'Illegal token {t}\n')

    def p_program(self, p):
        """program : statements"""
        p[0] = TreeNode('program', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_statements(self, p):
        """statements : statements statement
                        | statement"""
        if len(p) == 2:
            p[0] = TreeNode('statement', children=p[1])
        else:
            p[0] = TreeNode('statements', children=[p[1], TreeNode('statement', children=p[2])])

    def p_statement(self, p):#мб знак завершения предложения
        """statement : empty NEWLINE
                        | declaration NEWLINE
                        | assignment NEWLINE
                        | conversion NEWLINE
                        | CHECK NEWLINE
                        | UNTIL NEWLINE
                        | go NEWLINE
                        | rr NEWLINE
                        | rl NEWLINE
                        | function NEWLINE
                        | function_call NEWLINE"""
        p[0] = p[1]

    def p_empty(self, p):
        """empty : """
        pass
#declaration
    def p_declaration(self, p):
        """declaration : type variants
                        | type variants LASIGNMENT DECIMAL
                        | field type type variants
                        | field type type variants LASIGNMENT DECIMAL"""
        if len(p) == 3:# посмотреть ещё раз
            p[0] = TreeNode('declaration', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        elif p[1] != 'field':
            p[0] = TreeNode('declaration', value=p[1],
                            children=[TreeNode('init', value=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1)), p[4],
                                      TreeNode('init_end')], lineno=p.lineno(1), lexpos=p.lexpos(1))
        elif len(p) == 5:
            p[0] = TreeNode('declaration', value=p[1],
                            children=[TreeNode('init', value=p[2],
                                      children=[TreeNode(value=p[3], children=p[4],lineno=p.lineno(1), lexpos=p.lexpos(1))],
                                      lineno=p.lineno(1), lexpos=p.lexpos(1)), p[4],
                                      TreeNode('init_end')], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = TreeNode('declaration', value=p[1],
                            children=[TreeNode('init', value=p[2], children=[TreeNode(value=p[3],
                            children=[TreeNode(value=p[4], children=p[6], lineno=p.lineno(1), lexpos=p.lexpos(1))],
                            lineno=p.lineno(1), lexpos=p.lexpos(1),)], lineno=p.lineno(1), lexpos=p.lexpos(1)),
                            TreeNode('init_end')], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_variants(self, p):
        """variants : variants variant
                        | variant"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = TreeNode('variants', children=[p[1], p[2]])

    def p_variant(self, p):
        """variant : NAME"""
        p[0] = p[1]

    def p_indices(self, p):
        """indices : LSQBRACKET expression expression RSQBRACKET"""
        p[0] = TreeNode('indices', children=[p[2], p[4]], lineno=p.lineno(2), lexpos=p.lexpos(2))


    def p_type(self, p):
        """type : tiny
                    | small
                    | normal
                    | big"""
        p[0] = p[1]
#expression
    def p_expression(self, p):
        """expression : math_expression
                        | decimal_const
                        | variant
                        | expression RASIGNMENT variant
                        | variant LASIGNMENT expression
                        | function_call"""
        p[0] = TreeNode('expression', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_math_expression(self, p):
        """math_expression : expression PLUS expression
                            | LRNDBRACKET expression PLUS expression RRNDBRACKET
                            | expression MINUS expression
                            | LRNDBRACKET expression MINUS expression RRNDBRACKET
                            | expression MULT expression
                            | expression DIV expression
                            | expression MORE expression
                            | expression LESS expression
                            | expression MOREEQ expression
                            | expression LESSEQ expression"""
        if p[2] == 'PLUS':
            p[0] = TreeNode('addition', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))
        elif p[3] == 'PLUS':
            p[0] = TreeNode('addition', value=p[3], children=[p[2], p[4]], lineno=p.lineno(2), lexpos=p.lexpos(2))
        elif p[2] == 'MINUS':
            p[0] = TreeNode('subtraction', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))
        elif p[3] == 'MINUS':
            p[0] = TreeNode('subtraction', value=p[3], children=[p[2], p[4]], lineno=p.lineno(2), lexpos=p.lexpos(2))
        elif p[2] == 'MULT':
            p[0] = TreeNode('multiplication', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))
        elif p[2] == 'DIV':
            p[0] = TreeNode('division', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))
        elif p[2] == 'MORE':
            p[0] = TreeNode('M_comparison', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))
        elif p[2] == 'LESS':
            p[0] = TreeNode('L_comparison', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))
        elif p[2] == 'MOREEQ':
            p[0] = TreeNode('MEQ_comparison', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))
        elif p[2] == 'LESSEQ':
            p[0] = TreeNode('LEQ_comparison', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))

    def p_decimal_const(self, p):
        """decimal_const : DECIMAL"""
        p[0] = TreeNode('decimal_const', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_assignment(self, p):
        """assignment : variant LASIGNMENT expression
                        | expression RASIGNMENT variant
                        | variant indices LASIGNMENT expression
                        | expression RASIGNMENT variant indices
                        | variant LASIGNMENT expression RASIGNMENT variant
                        | expression RASIGNMENT variant LASIGNMENT expression"""
        if p[2] == 'LASIGNMENT':
             p[0] = TreeNode('L_assignment', value=p[1], children=p[3], lineno=p.lineno(2), lexpos=p.lexpos(2))
        else:
            p[0] = TreeNode('R_assignment', value=p[3], children=p[1], lineno=p.lineno(2), lexpos=p.lexpos(2))

    def p_conversion(self, p):
        """conversion : MINUS variant
                        | PLUS variant"""
        p[0] = TreeNode('conversion', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_UNTIL(self, p):
        """UNTIL : until math_expression do NEWLINE statements """ #запятые точки
        p[0] = TreeNode('until', children={'condition': p[2], 'body': p[5]}, lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_CHECK(self, p):
        """CHECK : check math_expression do NEWLINE statements """
        p[0] = TreeNode('check', children={'condition': p[2], 'body': p[5]}, lineno=p.lineno(1), lexpos=p.lexpos(1))

#rr rl sonar compass ???

#func

    def p_function(self, p):
        """function : type NAME LSQBRACKET parameters RSQBRACKET begin NEWLINE func_statements end""" #точки запятые
        self._functions[p[2]] = TreeNode('function', children={'body': p[8]}, lineno=p.lineno(1), lexpos=p.lexpos(1))
        p[0] = TreeNode('func_descriptor', value=p[2], lineno=p.lineno(1), lexpos=p.lexpos(2))

    def p_func_statements(self, p):
        """func_statements : func_statements func_statement
                        | func_statement"""
        if len(p) == 2:
            p[0] = TreeNode('func_statement', children=p[1])
        else:
            p[0] = TreeNode('func_statements', children=[p[1], TreeNode('func_statement', children=p[2])])

    def p_func_statement(self, p):
        """func_statement : empty NEWLINE
                        | declaration NEWLINE
                        | assignment NEWLINE
                        | conversion NEWLINE
                        | CHECK NEWLINE
                        | UNTIL NEWLINE
                        | go NEWLINE
                        | rr NEWLINE
                        | rl NEWLINE
                        | function_call NEWLINE
                        | RETURN NEWLINE"""
        p[0] = p[1]

    def p_parameters(self, p):
        """parameters : parameters COMMA parameter
                        | parameter"""
        if len(p) == 2:
            p[0] = TreeNode('parameter', children=p[1])
        else:
            p[0] = TreeNode('parameters', children=[p[1], TreeNode('parameter', children=p[3])])

    def p_parameter(self, p):
        """parameter : type NAME """
        p[0] = TreeNode('parameter', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_function_call(self, p):
        """function_call : NAME LRNDBRACKET variants RRNDBRACKET
                        | NAME LRNDBRACKET RRNDBRACKET"""
        if len(p) == 4:
            p[0] = TreeNode('function_call', value={'name': p[2]}, lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = TreeNode('function_call', value={'name': p[2]}, children=p[4], lineno=p.lineno(1),
                            lexpos=p.lexpos(1))


    def p_RETURN(self, p):
        """RETURN : return expression"""
        p[0] = TreeNode('return', children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
#errors
    def p_error(self, p):
        try:
            sys.stderr.write(f'Error at {p.lineno} line\n')
        except:
            sys.stderr.write(f'Error\n')
        self.ok = False

    def p_decl_error(self, p):
        """declaration : type error
                        | type variants  LASIGNMENT error
                        | field type type error
                        | field type type variants LASIGNMENT error
                        | declaration error"""
        if len(p) == 3 or p[1] == 'field':
            p[0] = TreeNode('error', value='Declaration error', lineno=p.lineno(2), lexpos=p.lexpos(2))
            sys.stderr.write(f'==> Error in variant declaration\n')
        else:
            p[0] = TreeNode('error', value='Initialization error', lineno=p.lineno(2), lexpos=p.lexpos(2))
            sys.stderr.write(f'==> Error in variant initialization\n')

    def p_indices_error(self, p):
        """indices : LSQBRACKET error RSQBRACKET
                    | LSQBRACKET error expression RSQBRACKET
                    | LSQBRACKET expression error RSQBRACKET
                    | LSQBRACKET error error RSQBRACKET
                    | indices error"""
        p[0] = TreeNode('error', value='Variant index error', lineno=p.lineno(1), lexpos=p.lexpos(1))
        sys.stderr.write(f'==> Error in variant index!\n')

    def p_assignment_error(self, p): #может быть ошибка везде?
        """assignment : variant LASIGNMENT error
                        | error LASIGNMENT expression
                        | error RASIGNMENT variant
                        | expression RASIGNMENT error
                        | error indices LASIGNMENT expression
                        | variant indices LASIGNMENT error
                        | error RASIGNMENT variant indices
                        | expression RASIGNMENT error indices
                        | error LASIGNMENT expression RASIGNMENT variant
                        | variant LASIGNMENT error RASIGNMENT variant
                        | variant LASIGNMENT expression RASIGNMENT error
                        | error LASIGNMENT error RASIGNMENT variant
                        | variant LASIGNMENT error RASIGNMENT error
                        | error LASIGNMENT expression RASIGNMENT error
                        | error RASIGNMENT variant LASIGNMENT expression
                        | expression RASIGNMENT error LASIGNMENT expression
                        | expression RASIGNMENT variant LASIGNMENT error
                        | error RASIGNMENT error LASIGNMENT expression
                        | expression RASIGNMENT error LASIGNMENT error
                        | error RASIGNMENT variant LASIGNMENT error"""
        p[0] = TreeNode('error', value='Assignment error', children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        sys.stderr.write(f'==> Assignment error!\n')#доделать вариации описания

    def p_conversion_error(self, p):
        """conversion : MINUS error
                        | PLUS error
                        | conversion error"""
        p[0] = TreeNode('error', value='Сonversion error', lineno=p.lineno(1), lexpos=p.lexpos(1))
        sys.stderr.write(f'==> Error in conversion!\n')


#rr rl sonar compass ???
    def p_UNTIL_error(self, p):
        """UNTIL : until error do NEWLINE statements
                    | UNTIL error"""
        if len(p) == 6:
            p[0] = TreeNode('until_error', value='Until error', children={'body': p[5]}, lineno=p.lineno(1),
                            lexpos=p.lexpos(1))
            sys.stderr.write(f'==> Error in \'until\'!\n')
        else:
            p[0] = TreeNode('UNTIL_error', value='Until error', lineno=p.lineno(1), lexpos=p.lexpos(1))
            sys.stderr.write(f'==> Error in \'until\'!\n')


    def p_CHECK_error(self, p):
        """CHECK : check error do NEWLINE statements
                    | CHECK error"""
        if len(p) == 6:
            p[0] = TreeNode('CHECK_error', value='Check error', children={'body': p[5]}, lineno=p.lineno(1),
                            lexpos=p.lexpos(1))
            sys.stderr.write(f'==> Error in \'check\'!\n')
        else:
            p[0] = TreeNode('CHECK_error', value='Check error', lineno=p.lineno(1), lexpos=p.lexpos(1))
            sys.stderr.write(f'==> Error in \'check\'!\n')

    def p_function_error(self, p):
        """function :  type error LSQBRACKET parameters RSQBRACKET begin NEWLINE func_statements end
                    | type NAME LSQBRACKET error RSQBRACKET begin NEWLINE func_statements end
                    | type NAME LSQBRACKET parameters RSQBRACKET error NEWLINE func_statements end
                    | type NAME LSQBRACKET parameters RSQBRACKET begin NEWLINE func_statements error
                    | type error LSQBRACKET error RSQBRACKET begin NEWLINE func_statements end
                    | type NAME LSQBRACKET error RSQBRACKET error NEWLINE func_statements end
                    | type NAME LSQBRACKET parameters RSQBRACKET error NEWLINE func_statements error
                    | type error LSQBRACKET parameters RSQBRACKET begin NEWLINE func_statements error
                    | type error LSQBRACKET parameters RSQBRACKET error NEWLINE func_statements end
                    | type NAME LSQBRACKET error RSQBRACKET begin NEWLINE func_statements error
                    | type error LSQBRACKET error RSQBRACKET error NEWLINE func_statements end
                    | type NAME LSQBRACKET error RSQBRACKET error NEWLINE func_statements error
                    | type error LSQBRACKET parameters RSQBRACKET error NEWLINE func_statements error
                    | type error LSQBRACKET error RSQBRACKET begin NEWLINE func_statements error
                    | function error
                   """
        if len(p) == 10:
            self._functions[p[2]] = TreeNode('function_error', children={'body': p[8]}, lineno=p.lineno(1),
                                             lexpos=p.lexpos(1))
            p[0] = TreeNode('func_error', value='Function error!', lineno=p.lineno(1), lexpos=p.lexpos(2))
            sys.stderr.write(f'==> Error in a function syntax!\n')
        else:
            p[0] = TreeNode('func_error', value='Function error!', lineno=p.lineno(1), lexpos=p.lexpos(2))
            sys.stderr.write(f'==> Error in a function!\n')

    def p_RETURN_error(self, p):
        """RETURN : return error
                    | RETURN error"""
        p[0] = TreeNode('RETURN_error', value='Return error', lineno=p.lineno(1), lexpos=p.lexpos(1))
        sys.stderr.write(f'==> Error in return!\n')

data = '''
big main [small b] begin
small n << 4,
small c << 0,
c << fib(n).
end

small fib [small n] begin
small num1 << 1,
small num2 << 1,
small num3 << 0,
check n<=0 do
return num3.
check n<=2 do
return num1.
until n-2>0 do
num3 << num1+num2,
num2 << num1,
num1 << num3,
n << n-1.
return num3.
end
'''
lexer = Lexer()
lexer.input(data)
while True:
    token = lexer.token()
    if token is None:
        break
    else:
        print(token)

parser = Parser()
tree, ok, functions = parser.parse(data)
tree.print()
print(ok)
functions['func'].children['body'].print()
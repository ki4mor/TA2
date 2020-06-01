import ply.yacc as yacc
from ply.lex import LexError
import sys
import os
from lexer.lexer import Lexer
from SyntaxTree.Tree import TreeNode


class Parser(object):
    tokens = Lexer.tokens
    precedence = Lexer.precedence

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
        """program : functions"""
        p[0] = TreeNode('program', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    # func
    def p_functions(self, p):
        """functions : functions function
                        | function"""
        if len(p) == 2:
            p[0] = TreeNode('function', children=p[1])
        else:
            p[0] = TreeNode('functions', children=[p[1], TreeNode('function', children=p[2])])

    def p_function(self, p):
        """function : type NAME LSQBRACKET parameters RSQBRACKET begin NEWLINE statements DOT NEWLINE end NEWLINE"""

        self._functions[p[2]] = TreeNode('function', children={'body': p[8], 'param': p[4]}, lineno=p.lineno(1), lexpos=p.lexpos(1))
        p[0] = TreeNode('func_descriptor', value=p[2], lineno=p.lineno(1), lexpos=p.lexpos(2))


    def p_statements(self, p):
        """statements : statements COMMA NEWLINE statement
                        | statement"""
        if len(p) == 2:
            p[0] = TreeNode('statement', children=p[1])
        else:
            p[0] = TreeNode('statements', children=[p[1], TreeNode('statement', children=p[4])])

    def p_statement(self, p):
        """statement : empty
                        | declaration
                        | assignment
                        | conversion
                        | CHECK
                        | UNTIL
                        | function_call
                        | RETURN"""
        p[0] = p[1]


    def p_parameters(self, p):
        """parameters : parameter COMMA parameters
                        | parameter"""
        if len(p) == 2:
            p[0] = TreeNode('parameter', children=p[1])
        else:
            p[0] = TreeNode('parameters', children=[p[1], TreeNode('parameter', children=p[3])])

    def p_parameter(self, p):
        """parameter : type NAME
                    | empty """
        if len(p) == 3:
            p[0] = TreeNode('parameter', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = p[1]

    def p_function_call(self, p):
        """function_call : NAME LRNDBRACKET variants RRNDBRACKET
                        | NAME LRNDBRACKET RRNDBRACKET"""
        if len(p) == 4:
            p[0] = TreeNode('function_call', value={'name': p[1]}, lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = TreeNode('function_call', value={'name': p[1]}, children=p[3], lineno=p.lineno(1),
                            lexpos=p.lexpos(1))


    def p_RETURN(self, p):
        """RETURN : return expression"""
        p[0] = TreeNode('return', p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))


    def p_empty(self, p):
        """empty : """
        pass
#declaration
    def p_declaration(self, p):
        """declaration : type variants LASIGNMENT decimal_expression
                        | field type type variants LASIGNMENT decimal_expression"""

        if len(p) == 5 and p[1] != 'field':
            p[0] = TreeNode('declaration', value=p[1],
                            children=[TreeNode('init', value=p[2], children=p[4], lineno=p.lineno(1), lexpos=p.lexpos(1))],
                            lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = TreeNode('declaration', value=[p[1], p[2], p[3]],
                            children=[TreeNode('init', value=p[4], children=p[6], lineno=p.lineno(1), lexpos=p.lexpos(1))],
                            lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_variants(self, p):
        """variants : variant variants
                        | variant"""
        if len(p) == 2:
            p[0] = TreeNode('variants', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = TreeNode('variants', children=[p[1], p[2]], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_variant(self, p):
        """variant : NAME
                    | NAME indices"""
        if len(p) == 2:
            p[0] = TreeNode('variant', p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = TreeNode('variant', p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_indices(self, p):
        """indices : LSQBRACKET expression expression RSQBRACKET"""
        p[0] = TreeNode('indices', children=[p[2], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))


    def p_type(self, p):
        """type : tiny
                    | small
                    | normal
                    | big"""
        p[0] = p[1]

#expression
    def p_expression(self, p):
        """expression : math_expression
                        | decimal_expression
                        | variant
                        | robot_command
                        | ext_assig
                        | function_call"""
        if len(p) == 2:
            p[0] = TreeNode('expression', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = TreeNode('expression', children=[p[1], p[2], p[3]], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_ext_assig(self, p):
        """ext_assig : assig"""
        p[0] = TreeNode('ext_assig', p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_assig(self, p):
        """assig : expression RASIGNMENT variant
                        | variant LASIGNMENT expression"""
        p[0] = TreeNode('assignment', value=p[1], children=p[3], lineno=p.lineno(2), lexpos=p.lexpos(2))

    def p_math_expression(self, p):
        """math_expression : expression PLUS expression
                            | expression MINUS expression
                            | expression MULT expression
                            | expression DIV expression
                            | expression MORE expression
                            | expression LESS expression
                            | expression MOREEQ expression
                            | expression LESSEQ expression
                            | LRNDBRACKET expression PLUS expression RRNDBRACKET
                            | LRNDBRACKET expression MINUS expression RRNDBRACKET
                            | LRNDBRACKET expression MULT expression RRNDBRACKET
                            | LRNDBRACKET expression DIV expression RRNDBRACKET
                            | LRNDBRACKET expression MORE expression RRNDBRACKET
                            | LRNDBRACKET expression LESS expression RRNDBRACKET
                            | LRNDBRACKET expression MOREEQ expression RRNDBRACKET
                            | LRNDBRACKET expression LESSEQ expression RRNDBRACKET"""
        if len(p) == 4:
            p[0] = TreeNode('binary_expression', p[2], children=[p[1], p[3]], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = TreeNode('binary_expression', p[3], children=[p[2], p[4]], lineno=p.lineno(1), lexpos=p.lexpos(1))


    def p_decimal_const(self, p):
        """decimal_const : DECIMAL"""
        p[0] = TreeNode('decimal_const', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_decimal_expression(self, p):
        """decimal_expression : decimal_const
                            | PLUS decimal_const
                            | MINUS decimal_const"""
        if len (p) == 2:
            p[0] = TreeNode('unsigned', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = TreeNode('signed', value=p[2], children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_robot_command(self, p):
        """robot_command : rl
                        | rr
                        | go
                        | sonar
                        | compass"""
        p[0] = TreeNode('robot', p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_assignment(self, p):
        """assignment : variant LASIGNMENT expression
                        | expression RASIGNMENT variant
                        | variant LASIGNMENT expression RASIGNMENT variant
                        | expression RASIGNMENT variant LASIGNMENT expression"""
        if len(p) == 4:
            p[0] = TreeNode('assignment', value=p[1], children=p[3], lineno=p.lineno(2), lexpos=p.lexpos(2))
        elif len(p) == 6 and p[2] == '<<':
            p[0] = TreeNode('assignment', value=[p[1], p[5]], children=p[3], lineno=p.lineno(2), lexpos=p.lexpos(2))
        elif len(p) == 6 and p[2] == '>>':
            p[0] = TreeNode('assignment', value=p[3], children=[p[1], p[5]], lineno=p.lineno(2), lexpos=p.lexpos(2))
        print()

    def p_conversion(self, p):
        """conversion : MINUS NAME
                        | PLUS NAME"""
        p[0] = TreeNode('conversion', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_UNTIL(self, p):
        """UNTIL : until expression do NEWLINE statements DOT"""
        p[0] = TreeNode('until', children={'condition': p[2], 'body': p[5]}, lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_CHECK(self, p):
        """CHECK : check expression do NEWLINE statements DOT"""
        p[0] = TreeNode('check', children={'condition': p[2], 'body': p[5]}, lineno=p.lineno(1), lexpos=p.lexpos(1))




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
        if len(p) == 3 or (p[1] == 'field' and len(p) == 5):
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

    def p_assignment_error(self, p):
        """assignment : variant LASIGNMENT error
                        | error LASIGNMENT expression
                        | error RASIGNMENT variant
                        | expression RASIGNMENT error
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
        sys.stderr.write(f'==> Assignment error!\n')

    def p_conversion_error(self, p):
        """conversion : MINUS error
                        | PLUS error
                        | conversion error"""
        p[0] = TreeNode('error', value='Сonversion error', lineno=p.lineno(1), lexpos=p.lexpos(1))
        sys.stderr.write(f'==> Error in conversion!\n')



    def p_UNTIL_error(self, p):
        """UNTIL : until error do NEWLINE statements DOT
                    | UNTIL error"""
        if len(p) == 3:
            p[0] = TreeNode('UNTIL_error', value='Until error', lineno=p.lineno(1), lexpos=p.lexpos(1))
            sys.stderr.write(f'==> Error in \'until\'!\n')
        elif len(p) == 6:
            p[0] = TreeNode('until_error', value='Until error', children={'body': p[5]}, lineno=p.lineno(1),
                            lexpos=p.lexpos(1))
            sys.stderr.write(f'==> Error in \'until\'!\n')


    def p_CHECK_error(self, p):
        """CHECK : check error do NEWLINE statements DOT
                    | CHECK error"""

        if len(p) == 3:
            p[0] = TreeNode('CHECK_error', value='Check error', lineno=p.lineno(1), lexpos=p.lexpos(1))
            sys.stderr.write(f'==> Error in \'check\'!\n')
        elif len(p) == 6:
            p[0] = TreeNode('CHECK_error', value='Check error', children={'body': p[5]}, lineno=p.lineno(1),
                            lexpos=p.lexpos(1))
            sys.stderr.write(f'==> Error in \'check\'!\n')

    def p_function_error(self, p):
        """function : type error LSQBRACKET parameters RSQBRACKET begin NEWLINE statements DOT NEWLINE end NEWLINE
                    | type NAME LSQBRACKET error RSQBRACKET begin NEWLINE statements DOT NEWLINE end NEWLINE
                    | type NAME LSQBRACKET parameters RSQBRACKET error NEWLINE statements DOT NEWLINE end NEWLINE
                    | type NAME LSQBRACKET parameters RSQBRACKET begin NEWLINE statements DOT NEWLINE error NEWLINE
                    | type error LSQBRACKET error RSQBRACKET begin NEWLINE statements DOT NEWLINE end NEWLINE
                    | type NAME LSQBRACKET error RSQBRACKET error NEWLINE statements DOT NEWLINE end NEWLINE
                    | type NAME LSQBRACKET parameters RSQBRACKET error NEWLINE statements DOT NEWLINE error NEWLINE
                    | type error LSQBRACKET parameters RSQBRACKET begin NEWLINE statements DOT NEWLINE error NEWLINE
                    | type error LSQBRACKET parameters RSQBRACKET error NEWLINE statements DOT NEWLINE end NEWLINE
                    | type NAME LSQBRACKET error RSQBRACKET begin NEWLINE statements DOT NEWLINE error NEWLINE
                    | type error LSQBRACKET error RSQBRACKET error NEWLINE statements DOT NEWLINE end NEWLINE
                    | type NAME LSQBRACKET error RSQBRACKET error NEWLINE statements DOT NEWLINE error NEWLINE
                    | type error LSQBRACKET parameters RSQBRACKET error NEWLINE statements DOT NEWLINE error NEWLINE
                    | type error LSQBRACKET error RSQBRACKET begin NEWLINE statements DOT NEWLINE error NEWLINE
                    | function error
                   """
        if len(p) == 3:
            p[0] = TreeNode('func_error', value='Function error!', lineno=p.lineno(1), lexpos=p.lexpos(2))
            sys.stderr.write(f'==> Error in a function!\n')
        elif len(p) == 13:
            self._functions[p[2]] = TreeNode('function_error', children={'body': p[8]}, lineno=p.lineno(1),
                                             lexpos=p.lexpos(1))
            p[0] = TreeNode('func_error', value='Function error!', lineno=p.lineno(1), lexpos=p.lexpos(2))
            sys.stderr.write(f'==> Error in a function syntax!\n')


    def p_RETURN_error(self, p):
        """RETURN : return error
                    | RETURN error"""
        p[0] = TreeNode('RETURN_error', value='Return error', lineno=p.lineno(1), lexpos=p.lexpos(1))
        sys.stderr.write(f'==> Error in return!\n')

# data = '''big MAIN [big SDG, normal GG] begin
# small N A D<< +4,
# field small big A <<5 ,
# field big normal D << 3,
# small A << 2,
# A << A,
# A[2 3] << 3,
# until A>1 do
# small A<< 2.,
# +A,
# small A D F << 1,
# return A>F.
# end
#
# big KEG [] begin
# small C <<5.
# end
# '''



# data = '''big MAIN[] begin
# big COUNTER << -0,
# small SONARRESULT << 0,
# small NEEDBREAK << -0,
# small FORSONAR1 << 2,
# small FORSONAR2 << 0,
# small RES << +0,
# small FORCOM << 0,
# big INDEX << 40000,
# small BIT2 << 0,
# until INDEX do
# INDEX << INDEX - 1,
# SONARRESULT << sonar,
# NEEDBREAK << 0,
# BIT2 << GETBIT(SONARRESULT FORSONAR1),
# check INVERT(BIT2) do
# check COUNTER > 0 do
# FORROT << rr,
# COUNTER << COUNTER - 1,
# NEEDBREAK << -16..,
# RES << GETBIT(SONARRESULT FORSONAR2),
# RES << RES + NEEDBREAK,
# check INVERT(RES) do
# FORCOM << go,
# NEEDBREAK << -16.,
# check NEEDBREAK => 0 do
# FORCOM << rl,
# COUNTER << COUNTER + 1,
# NEEDBREAK << -16..,
# return -1.
# end
#
# tiny INVERT[tiny BIT] begin
# check BIT do
# return 0.,
# return 1.
# end
#
# small GETBIT[small A, small NUMBER] begin
# check NUMBER < 0 do
# return -1.,
# check NUMBER => 5 do
# return -1.,
# until NUMBER > 0 do
# A << A / 2,
# NUMBER << NUMBER - 1.,
# return ISNOTEVENSMALL(A).
# end
#
# tiny ISNOTEVENSMALL[small NUMBER] begin
# check NUMBER => 16 do
# NUMBER << NUMBER - 16.,
# check NUMBER => 8 do
# NUMBER << NUMBER - 8.,
# check NUMBER => 4 do
# NUMBER << NUMBER - 4.,
# check NUMBER => 2 do
# NUMBER << NUMBER - 2.,
# check NUMBER=>1 do
# check NUMBER<=1 do
# return 1..,
# return 0.
# end
# '''
# lexer = Lexer()
# lexer.input(data)
# while True:
#     token = lexer.token()
#     if token is None:
#         break
#     else:
#         print(token)
#
# parser = Parser()
# tree, ok, functions = parser.parse(data)
# tree.print()
# print(ok)
# functions['MAIN'].children['body'].print()
# functions = parser.parser.parse(data, debug=True)
# print()
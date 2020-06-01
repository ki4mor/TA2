import sys
import ply.lex as lex


class Lexer:
    def __init__(self):
        self.lexer = lex.lex(module=self)

    tokens = ['until', 'tiny',
              'small', 'normal', 'big',
              'field', 'do', 'check', 'go', 'rr', 'rl',
              'sonar', 'compass', 'begin',
              'return', 'end', 'DECIMAL', 'NAME',
              'LASIGNMENT', 'RASIGNMENT',
              'MORE', 'LESS',
              'MOREEQ', 'LESSEQ',
              'MULT', 'DIV',
              'PLUS', 'MINUS',
              'RRNDBRACKET', 'LRNDBRACKET',
              'LSQBRACKET', 'RSQBRACKET',
              'COMMA', 'DOT', 'NEWLINE'
    ]

    precedence = (
        ('left', 'MULT', 'DIV'),
        ('left', 'PLUS', 'MINUS'),
    )

    t_LASIGNMENT = r'[<]{2}'
    t_RASIGNMENT = r'[>]{2}'
    t_MORE = r'\>'
    t_LESS = r'\<'
    t_MOREEQ = r'\=\>'
    t_LESSEQ = r'\<\='
    t_MULT = r'\*'
    t_DIV = r'\/'
    t_PLUS = r'\+'
    t_MINUS = r'\-'
    t_RRNDBRACKET = r'\)'
    t_LRNDBRACKET = r'\('
    t_LSQBRACKET = r'\['
    t_RSQBRACKET = r'\]'
    t_COMMA = r'\,'
    t_DOT = r'\.'
    t_ignore =' '

    def t_until(self, t):
        r'until|unti|unt|un|u'
        t.type = 'until'
        return t

    def t_tiny(self, t):
        r'tiny|tin|ti|t'
        t.type = 'tiny'
        return t

    def t_small(self, t):
        r'small|smal|sma|sm'
        t.type = 'small'
        return t

    def t_normal(self, t):
        r'normal|norma|norm|nor|no|n'
        t.type = 'normal'
        return t

    def t_big(self, t):
        r'big|bi'
        t.type = 'big'
        return t

    def t_field(self, t):
        r'field|fiel|fie|fi|f'
        t.type = 'field'
        return t

    def t_do(self, t):
        r'do|d'
        t.type = 'do'
        return t

    def t_check(self, t):
        r'check|chec|che|ch'
        t.type = 'check'
        return t

    def t_go(self, t):
        r'go|g'
        t.type = 'go'
        return t

    def t_rr(self, t):
        r'rr'
        t.type = 'rr'
        return t

    def t_rl(self, t):
        r'rl'
        t.type = 'rl'
        return t

    def t_sonar(self, t):
        r'sonar|sona|son|so'
        t.type = 'sonar'
        return t

    def t_compass(self, t):
        r'compass|compas|compa|comp|com|co'
        t.type = 'compass'
        return t

    def t_begin(self, t):
        r'begin|begi|beg|be'
        t.type = 'begin'
        return t

    def t_return(self, t):
        r'return|retur|retu|ret|re'
        t.type = 'return'
        return t

    def t_end(self, t):
        r'end|en|e'
        t.type = 'end'
        return t

    def t_DECIMAL(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_NAME(self, t):
        r'[A-Z][A-Z0-9]*'
        t.type = 'NAME'
        return t

    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        return t

    def t_error(self, t):
        sys.stderr.write(f'Illegal character: {t.value[0]} at line {t.lexer.lineno}\n')
        t.lexer.skip(1)

    def input(self, data):
        return self.lexer.input(data)

    def token(self):
        return self.lexer.token()


data = ''' 
unt N-2>0 do
bi MAIN [] be
sma N << (3+2)/2
small C << 0,
C << FIB(N).
en

small FIB [small N] begin
small NUM1 << 1,
small NUM2 << 1,
small NUM3 << 0,
check N<=0 do
return nNUM3.
check N<=2 do
return NUM1.
until N-2>0 do
NUM3 << NUM1+NUM2,
NUM2 << NUM1,
NUM1 << NUM3,
N << N-1.
return NUM3.
end
'''
# data = '''tiny d << 0
# small a << +15
# normal a << +511
# big a << +16383
# field small tiny a << 25
# a [5 4]<< 10
# a << b
# c<<a+b
# c<<a-b
# c<<a/b
# c<<a*b
# -a
# +b
# until a<b do
# check a+1 do
# a << sonar
# rr,rl,go
# small func [small fir, small sec] begin
# return fir.
# end
# c << func(a b)
# '''
lexer = Lexer()
lexer.input(data)
while True:
    token = lexer.token()
    if token is None:
        break
    else:
        print(token)
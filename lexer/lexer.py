import sys
import ply.lex as lex

reserved = {
    #variables
    'tiny': 'tiny',
    'small': 'small',
    'normal': 'normal',
    'big': 'big',
    'field': 'field',

    #cycle
    'until': 'until',
    'do': 'do',

    #if
    'check': 'check',

    #robot
    'go': 'go',
    'rl': 'rl',
    'rr': 'rr',
    'sonar': 'sonar',
    'compass': 'compass',

    #function
    'begin': 'begin',
    'return': 'return',
    'end': 'end',

}


class Lexer:
    def __init__(self):
        self.lexer = lex.lex(module=self)

    tokens = ['DECIMAL', 'NAME',
              'LASIGNMENT', 'RASIGNMENT',
              'MORE', 'LESS',
              'MOREEQ', 'LESSEQ',
              'MULT', 'DIV',
              'PLUS', 'MINUS',
              'RRNDBRACKET', 'LRNDBRACKET',
              'LSQBRACKET', 'RSQBRACKET',
              'COMMA', 'DOT', 'NEWLINE'
    ] + list(reserved.values())
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

    def t_DECIMAL(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_NAME(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value, 'NAME')
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
big main [] begin
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
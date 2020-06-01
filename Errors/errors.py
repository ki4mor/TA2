import sys
from SyntaxTree.Tree import TreeNode


class Error_Handler:
    def __init__(self):
        self.type = None
        self.node = None
        self.types = ['UnexpectedError',
                      'NoInputPoint',
                      'RedeclarationError',
                      'UndeclaredError',
                      'IndexError',
                      'TypeError',
                      'ValueError',
                      'ConvertationError',
                      'WrongParameters',
                      'RecursionError',
                      'CommandError',
                      'RobotError',
                      'FuncStatementsError',
                      'FuncDescriptionError',
                      'ApplicationCall',
                      'FuncCallError',
                      'ReturnError'
                      ]

    def call(self, error_type, node=None):
        self.type = error_type
        self.node = node
        sys.stderr.write(f'Error {self.types[int(error_type)]}: ')
        if self.type == 0:
            pass
        elif self.type == 1:
            sys.stderr.write(f'No "main" function detected\n')
            return
        elif self.type == 2:
            if isinstance(node.children, list):
                sys.stderr.write(f'Variant "{self.node.children[0].value}" at line {self.node.lineno} is already declared\n')
            else:
                sys.stderr.write(f'Variant "{self.node.children.value}" at line {self.node.lineno} is already declared\n')
        elif self.type == 3:
            if self.node.type == 'assignment':
                sys.stderr.write(f'Variant {self.node.value.value} at line {self.node.lineno} is used before declaration\n')
            else:
                sys.stderr.write(f'Something at line {self.node.lineno} is used before declaration\n')
        elif self.type == 4:
            if node.type == 'declaration':
                if isinstance(node.children, list):
                    sys.stderr.write(f'Variant "{node.children[0].value}" has wrong indexation at line {self.node.lineno}\n')
                else:
                    sys.stderr.write(f'Variant "{node.children.value}" has wrong indexation at line {self.node.lineno}\n')
            elif node.type == 'assignment':
                sys.stderr.write(f'Left-side variant element size doesn\'t match right-side variant at line {self.node.lineno}\n')
            elif node.type == 'expression':
                sys.stderr.write(f'Wrong indexation of right-side variant at line {self.node.lineno}\n')
            elif node.type == 'variant':
                sys.stderr.write(f'Variant "{node.value}" has wrong indexation at line {self.node.lineno}\n')
            else:
                sys.stderr.write(f'Wrong indexation\n')
        elif self.type == 5:
            if node.type == 'variant':
                sys.stderr.write(f'Variant "{node.value}" has wrong type at line {self.node.lineno}\n')
            else:
                sys.stderr.write(f'Wrong type\n')
        elif self.type == 6:
            if node.type == 'assignment':
                sys.stderr.write(f'Try assign wrong value to variant "{node.value}" at line {self.node.lineno}\n')
            elif node.type == 'declaration':
                sys.stderr.write(f'Try assign wrong value to variant "{node.value}" at line {self.node.lineno}\n')

        elif self.type == 7:
            sys.stderr.write(f'Can\'t converse variant "{node.children.value}" at line {self.node.lineno}\n')

        elif self.type == 8:
            sys.stderr.write(f'Bad parameters for function "{self.node.value}" at line '
                             f'{self.node.lineno} \n')

        elif self.type == 9:
            sys.stderr.write(f'Maximum recursion depth reached\n')

        elif self.type == 10:
            sys.stderr.write(f'Inappropriate word in robot command at line {self.node.lineno}\n')
        elif self.type == 11:
            sys.stderr.write(f'There are no robot to execute this command at line {self.node.lineno}\n')

        elif self.type == 12:
            sys.stderr.write(f'Function body statements is used not in function at line {self.node.lineno}\n')
        elif self.type == 13:
            sys.stderr.write(f'Function description in function at line {self.node.lineno}\n')
        elif self.type == 14:
            sys.stderr.write(f'Tried to call main function at line'
                             f' {self.node.lineno} \n')
        elif self.type == 15:
            sys.stderr.write(f'Unknown function call "{self.node.value}" at line '
                             f'{self.node.lineno} \n')
        elif self.type == 16:
            sys.stderr.write(f'Function return expression expected but missing at line {self.node.lineno}\n')




class InterpreterConvertationError(Exception):
    pass


class InterpreterRedeclarationError(Exception):
    pass


class InterpreterUndeclaredError(Exception):
    pass


class InterpreterRecursionError(Exception):
    pass


class InterpreterWrongParameters(Exception):
    pass


class InterpreterApplicationCall(Exception):
    pass


class InterpreterTypeError(Exception):
    pass


class InterpreterValueError(Exception):
    pass


class InterpreterIndexError(Exception):
    pass


class InterpreterCallFunctionError(Exception):
    pass

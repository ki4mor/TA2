import sys
import re
import copy
from PIL import Image
from ParseR.parser import Parser
from SyntaxTree.Tree import TreeNode
from Robot.robot import Robot, Cell, cells
from Errors.errors import Error_Handler
from Errors.errors import InterpreterConvertationError
from Errors.errors import InterpreterRedeclarationError
from Errors.errors import InterpreterIndexError
from Errors.errors import InterpreterTypeError
from Errors.errors import InterpreterUndeclaredError
from Errors.errors import InterpreterRecursionError
from Errors.errors import InterpreterApplicationCall
from Errors.errors import InterpreterWrongParameters
from Errors.errors import InterpreterValueError
from Errors.errors import InterpreterCallFunctionError
class Variable:
    def __init__(self, var_type, var_value, var_sign_type):

        if isinstance(var_type, list):
            size = 0
            if var_type[2] == 'tiny':
                size = 2
            elif var_type[2] == 'small':
                size = 32
            elif var_type[2] == 'normal':
                size = 1024
            elif var_type[2] == 'big':
                size = 32768

            matrix = []
            for i in range(size):
                vector = []
                for j in range(size):
                    vector.append(var_value)
                matrix.append(vector)

            self.type = var_type
            self.value = matrix
            self.sign_type = var_sign_type
        else:
            self.type = var_type
            self.value = var_value
            self.sign_type = var_sign_type


    def __repr__(self):
        return f'{self.type}, {self.value}'


class TypeConverter:
    def __init__(self):
        pass


class Interpreter:

    def __init__(self, parser=Parser(), converter=TypeConverter()):
        self.parser = parser
        self.converter = converter
        self.program = None
        self.sym_table = [dict()]
        self.tree = None
        self.funcs = None
        self.scope = 0
        self.robot = None
        self.exit = False
        self.correct = True
        self.error = Error_Handler()
        self.error_types = {'UnexpectedError': 0,
                            'NoInputPoint': 1,
                            'RedeclarationError': 2,
                            'UndeclaredError': 3,
                            'IndexError': 4,
                            'TypeError': 5,
                            'ValueError': 6,
                            'ConvertationError': 7,
                            'WrongParameters': 8,
                            'RecursionError': 9,
                            'CommandError': 10,
                            'RobotError': 11,
                            'FuncStatementsError': 12,
                            'FuncDescriptionError': 13,
                            'ApplicationCall': 14,
                            'FuncCallError': 15,
                            'ReturnError': 16}

    def interpreter(self, program=None, robot=None, tree_print=False):
        self.program = program
        self.robot = robot
        self.sym_table = [dict()]
        self.tree, _correctness, self.funcs = self.parser.parse(self.program)
        if _correctness:
            if 'MAIN' not in self.funcs.keys():
                self.error.call(self.error_types['NoInputPoint'])
                return
            self.interpreter_tree(self.tree)
            try:
                self.interpreter_node(self.funcs['MAIN'].children['body'])
                return True
            except RecursionError:
                sys.stderr.write(f'RecursionError: function calls itself too many times\n')
                sys.stderr.write("========= Program has finished with fatal error =========\n")
                return False
        else:
            sys.stderr.write(f'Can\'t intemperate incorrect input file\n')

    @staticmethod
    def interpreter_tree(tree):
        print("Program tree:\n")
        tree.print()
        print('\n')

    def interpreter_node(self, node) :
        if node is None:
            return
        # unexpected error
        if node.type == 'error':
            self.error.call
        # program
        elif node.type == 'program':
            self.interpreter_node(node.children)
        # program -> statements
        elif node.type == 'functions':
            for child in node.children:
                self.interpreter_node(child)
        elif node.type == 'function':
            self.interpreter_node(node.children)
        elif node.type == 'statements':
            for child in node.children:
                self.interpreter_node(child)
        elif node.type == 'statement':
            self.interpreter_node(node.children)
        # statements -> declaration
        elif node.type == 'declaration':
            self.sym_table[self.scope]['#result'] = "error"
            declaration_type = node.value

            var = []
            declaration_child = node.children[0]
            declaration_value = declaration_child.children
            declaration_var = declaration_child.value
            while isinstance(declaration_var.children, list):
                var.append(declaration_var.children[0].value)
                declaration_var = declaration_var.children[1]
            var.append(declaration_var.children.value)
            for ch in var:
                try:
                    self.declare_variable(ch, declaration_type, declaration_value )
                except InterpreterRedeclarationError:
                    self.error.call(self.error_types['RedeclarationError'], node)
                    self.correct = False
                except InterpreterValueError:
                    self.error.call(self.error_types['ValueError'], node)
                    self.correct = False
        elif node.type == 'assignment':
            try:
                index = None
                var = None
                exp = None
                if isinstance(node.value, TreeNode) and isinstance(node.children, TreeNode) == 1:
                    if node.value.type == 'variant':
                        var = node.value.value
                        exp = self.interpreter_node(node.children)
                        if node.value.children:
                            index = node.value.children.children
                    elif node.value.type == 'expression':
                        var = node.children.value
                        exp = self.interpreter_node(node.value)
                        if node.children.children:
                            index = node.children.children.children
                    if var not in self.sym_table[self.scope].keys():
                        self.error.call(self.error_types['UndeclaredError'], node)
                    else:
                        self.assign(self.sym_table[self.scope][var].type, var, exp, index)

                elif len(node.value) == 2 and node.value[1].type == 'variant':
                    exp = self.interpreter_node(node.children)

                    var = node.value[0].value
                    if node.value[0].children:
                        index = node.value[0].children.children
                    if var not in self.sym_table[self.scope].keys():
                        self.error.call(self.error_types['UndeclaredError'], node)
                    else:
                        self.assign(self.sym_table[self.scope][var].type, var, exp, index)

                    var = node.value[1].value
                    if node.value[1].children:
                        index = node.value[1].children.children
                    if var not in self.sym_table[self.scope].keys():
                        self.error.call(self.error_types['UndeclaredError'], node)
                    else:
                        self.assign(self.sym_table[self.scope][var].type, var, exp, index)


                elif len(node.children) == 2 and node.children[1].type == 'expression':
                    var = node.value.value
                    if var not in self.sym_table[self.scope].keys():
                        self.error.call(self.error_types['UndeclaredError'], node)
                    else:
                        if node.value.children:
                            index = node.value.children.children
                        exp = node.children[0].value
                        self.assign(self.sym_table[self.scope][var].type, var, exp, index)
                        exp = node.cheldren[1].value
                        self.assign(self.sym_table[self.scope][var].type, var, exp, index)

            except InterpreterTypeError:
                self.error.call(self.error_types['TypeError'], node)
            except InterpreterValueError:
                self.error.call(self.error_types['ValueError'], node)
            except InterpreterIndexError:
                self.error.call(self.error_types['IndexError'], node)

        #expresion
        elif node.type == 'expression':
            res = self.interpreter_node(node.children)
            if res is None:
                self.error.call(self.error_types['ReturnError'], node.children)
                self.correct = False
                res = 0
            return res
        elif node.type == 'ext_assig':
            self.interpreter_node(node.value)
            if node.value.value.type == 'variant':
                res = self.interpreter_node(node.value.value)
            if node.value.value.type == 'expression':
                res = self.interpreter_node(node.value.children)
            return res
        elif node.type == 'decimal_const':
            return node.value
        elif node.type == 'until':
            while self.int_to_bool(self.interpreter_node(node.children['condition'])):
                self.interpreter_node(node.children['body'])
        elif node.type == 'check':
            if self.interpreter_node(node.children['condition']) != 0:
                self.interpreter_node(node.children['body'])
        elif node.type == 'func_descriptor':
            if self.scope != 0:
                self.correct = False
                self.error.call(self.error_types['FuncDescriptionError'], node)

        elif node.type == 'binary_expression':
            try:
                if node.value == '+':
                    return self.bin_plus(node.children[0], node.children[1])
                elif node.value == '-':
                    return self.bin_minus(node.children[0], node.children[1])
                elif node.value == '*':
                    return self.bin_mult(node.children[0], node.children[1])
                elif node.value == '/':
                    return self.bin_div(node.children[0], node.children[1])
                elif node.value == '>':
                    return self.bin_gr(node.children[0], node.children[1])
                elif node.value == '<':
                    return self.bin_ls(node.children[0], node.children[1])
                elif node.value == '=>':
                    return self.bin_greq(node.children[0], node.children[1])
                elif node.value == '<=':
                    return self.bin_lseq(node.children[0], node.children[1])
            except TypeError:
                self.error.call(self.error_types['TypeError'], node)
        elif node.type == 'unsigned':
            return node.value.value
        elif node.type == 'signed':
            return [node.children, node.value.value]
        elif node.type == 'variants':
            var = []
            while isinstance(node.children, list):
                var.append(node.children[0])
                node = node.children[1]
            var.append(node.children)
            return var
        elif node.type == 'variant':
            if node.value not in self.sym_table[self.scope].keys():
                self.error.call(self.error_types['UndeclaredError'], node)
                self.correct = False
                buf = 0
            else:
                if node.children:
                    index = node.children.children

                else:
                    index = None
                try:
                    buf = self.get_variant_value(node, index)
                except InterpreterIndexError:
                    self.error.call(self.error_types['IndexError'], node)
                    self.correct = False
                    buf = 0
                except InterpreterTypeError:
                    self.error.call(self.error_types['TypeError'], node)
                    self.correct = False
                    buf = 0
                return buf

        elif node.type == 'conversion':
            if node.children not in self.sym_table[self.scope].keys():
                self.error.call(self.error_types['UndeclaredError'], node)
                self.correct = False
            try:
                self.convert(node)
            except InterpreterConvertationError:
                self.error.call(self.error_types['ConvertationError'], node)
                self.correct = False
        elif node.type == 'function_call':

            try:
                res = self.function_call(node, node.value.get('name'))
                return res
            except InterpreterApplicationCall:
                self.error.call(self.error_types['ApplicationCall'], node)
                self.correct = False
            except InterpreterCallFunctionError:
                self.error.call(self.error_types['FuncCallError'], node)
                self.correct = False
            except InterpreterWrongParameters:
                self.error.call(self.error_types['WrongParameters'], node)
                self.correct = False

        elif node.type == 'return':
            if '#RETURN' in self.sym_table[self.scope].keys():
                pass
            else:
                if isinstance(self.interpreter_node(node.value), list):
                    expression = int(self.interpreter_node(node.value)[0] + str(self.interpreter_node(node.value)[1]))
                    self.sym_table[self.scope]['#RETURN'] = expression
                else:
                    self.sym_table[self.scope]['#RETURN'] = self.interpreter_node(node.value)

        #robot
        elif node.type == 'robot':
            if node.value == 'rr':
                return self.robot_rr()
            elif node.value == 'rl':
                return self.robot_rl()
            elif node.value == 'go':
                 return self.robot_go()

            elif node.value == 'sonar':
                return self.robot_sonar()
            elif node.value == 'compass':
                return self.robot_compass()
            self.sym_table[self.scope]['#result'] = "error"
        # statements -> function

    # for declaration
    def declare_variable(self, var, _type, value):
        sign_type = value.type
        if sign_type == 'signed':
            var_value = int(value.children+str(value.value.value))
        else:
            var_value = int(value.value.value)
        res = self.check_value(_type, var_value, sign_type)
        if res == False:
            raise InterpreterValueError
        if var in self.sym_table[self.scope].keys() or var in self.funcs:
            raise InterpreterRedeclarationError
        else:
            self.sym_table[self.scope][var] = Variable(_type, var_value, sign_type)

    def assign(self, type, var, expression, index=None):
        if isinstance(expression, list):
            expression = int(expression[0]+str(expression[1]))
        if index:
            if isinstance(type, str):
                raise InterpreterTypeError
            else:
               res = self.check_index(index, type[2])
               if res == False:
                   raise InterpreterIndexError
               else:
                   expression = self.rounding(type, expression, self.sym_table[self.scope][var].sign_type)
                   self.sym_table[self.scope][var].value[self.interpreter_node(index[0])][self.interpreter_node(index[1])] = expression
        else:
            if isinstance(type, list):
                raise InterpreterTypeError
            else:
                expression = self.rounding(type, expression, self.sym_table[self.scope][var].sign_type)
                self.sym_table[self.scope][var].value = expression



    # for math operations

    def bin_plus(self, var1, var2):
        expr1 = self.interpreter_node(var1)
        expr2 = self.interpreter_node(var2)
        return expr1+expr2

    def bin_minus(self, var1, var2):
        expr1 = self.interpreter_node(var1)
        expr2 = self.interpreter_node(var2)
        return expr1-expr2

    def bin_mult(self, var1, var2):
        expr1 = self.interpreter_node(var1)
        expr2 = self.interpreter_node(var2)
        return expr1*expr2

    def bin_div(self, var1, var2):
        expr1 = self.interpreter_node(var1)
        expr2 = self.interpreter_node(var2)
        if expr2 == 0:
            if expr1 > 0:
                res = 99999
            if expr1 < 0:
                res = -99999
        else:
            res = expr1//expr2
        return res

    def bin_gr(self, var1, var2):
        expr1 = self.interpreter_node(var1)
        expr2 = self.interpreter_node(var2)
        return self.bool_to_int(expr1 > expr2)

    def bin_greq(self, var1, var2):
        expr1 = self.interpreter_node(var1)
        expr2 = self.interpreter_node(var2)
        return self.bool_to_int(expr1 >= expr2)

    def bin_ls(self, var1, var2):
        expr1 = self.interpreter_node(var1)
        expr2 = self.interpreter_node(var2)
        return self.bool_to_int(expr1 < expr2)

    def bin_lseq(self, var1, var2):
        expr1 = self.interpreter_node(var1)
        expr2 = self.interpreter_node(var2)
        return self.bool_to_int(expr1 <= expr2)

    def convert(self, node):
        sign_type = self.sym_table[self.scope][node.children].sign_type
        new_type = node.value
        if new_type == '+':
            if sign_type == 'unsigned':
                raise InterpreterConvertationError
            else:
                if isinstance(self.sym_table[self.scope][node.children].value, list):
                    for ch in self.sym_table[self.scope][node.children].value:
                        for c in ch:
                            res = self.check_value(self.sym_table[self.scope][node.children].type[1], c, 'unsigned')
                            if res == False:
                                raise InterpreterConvertationError
                    self.sym_table[self.scope][node.children].sign_type = 'unsigned'
                else:
                    res = self.check_value(self.sym_table[self.scope][node.children].type, self.sym_table[self.scope][node.children].value, 'unsigned')
                    if res == False:
                        raise InterpreterConvertationError
                    self.sym_table[self.scope][node.children].sign_type = 'unsigned'
        if new_type == '-':
            if sign_type == 'signed':
                raise InterpreterConvertationError
            else:
                if isinstance(self.sym_table[self.scope][node.children].value, list):
                    for ch in self.sym_table[self.scope][node.children].value:
                        for c in ch:
                            res = self.check_value(self.sym_table[self.scope][node.children].type[1], c, 'signed')
                            if res == False:
                                raise InterpreterConvertationError
                    self.sym_table[self.scope][node.children].sign_type = 'signed'
                else:
                    res = self.check_value(self.sym_table[self.scope][node.children].type,self.sym_table[self.scope][node.children].value, 'signed')
                    if res == False:
                        raise InterpreterConvertationError
                    self.sym_table[self.scope][node.children].sign_type = 'signed'

    def get_variant_value(self, variant, index=None):
        if variant.value not in self.sym_table[self.scope].keys():
            raise InterpreterUndeclaredError

        else:
            if index:
                res = self.check_index(index, self.sym_table[self.scope][variant.value].type[2])
                if res == False:
                    raise InterpreterIndexError
                elif isinstance(self.sym_table[self.scope][variant.value].type, str):
                    raise InterpreterTypeError
                else:
                    return self.sym_table[self.scope][variant.value].value[self.interpreter_node(index[0])][self.interpreter_node(index[1])]
            else:
                if isinstance(self.sym_table[self.scope][variant.value].type, list):
                    raise InterpreterTypeError
                return copy.deepcopy(self.sym_table[self.scope][variant.value].value)

    def function_call(self, node, func_name):
        if func_name not in self.funcs.keys():
            raise InterpreterCallFunctionError
        if func_name == 'main':
            raise InterpreterApplicationCall

        out_val = []
        out_var = []
        if node.children is not None:
            param = self.interpreter_node(node.children)
            try:
                for ch in param:
                    out_val.append(self.interpreter_node(ch))
                    out_var.append(ch.value)
            except InterpreterTypeError:
                self.error.call(self.error_types['TypeError'], node)
        else:
            param = None

        self.scope += 1
        if self.scope > 75:
            self.scope -= 1
            raise InterpreterRecursionError
        self.sym_table.append(dict())

        func_subtree = self.funcs[func_name]
        get = func_subtree.children.get('param')
        in_var = []
        in_type = []
        if get.children != None:
            while isinstance(get.children, list):
                in_var.append(get.children[0].children)
                in_type.append(get.children[0].value)
                get = get.children[1].children
            in_var.append(get.children.children)
            in_type.append(get.children.value)

        try:
            if in_var is not None and param is not None:
                if len(in_var) == len(out_var):
                   for i in range(len(param)):
                       if self.sym_table[self.scope-1][out_var[i]].type == in_type[i]:
                           self.sym_table[self.scope][in_var[i]] = Variable(in_type[i], out_val[i], self.sym_table[self.scope-1][out_var[i]].sign_type)
                else:
                    raise InterpreterWrongParameters
        except InterpreterTypeError:
            self.error.call(self.error_types['TypeError'], node)
            return
        self.interpreter_node(self.funcs[func_name].children['body'])
        if '#RETURN' in self.sym_table[self.scope].keys():
            result = self.sym_table[self.scope]['#RETURN']
        else:
            result = None
        self.sym_table.pop()
        self.scope -= 1
        return result

    def rounding(self, var_type, var_value, var_sign_type):
        res = var_value
        if var_sign_type == 'signed':
            if var_type == 'tiny':
                if var_value > 1:
                    res = 1
                if var_value < 0:
                    res = 0
            elif var_type == 'small':
                if var_value > 15:
                   res = 15
                if var_value < -16:
                    res = -16
            elif var_type == 'normal':
                if var_value > 511:
                    res = 511
                if var_value < -512:
                    res = -512
            elif var_type == 'big':
                if var_value > 16383:
                    res = 16383
                if var_value < -16384:
                    res = -16384
        else:
            if var_type == 'tiny':
                if var_value > 1:
                    res = 1
                if var_value < 0:
                    res = 0
            elif var_type == 'small':
                if var_value > 31:
                    res = 31
                if var_value < 0:
                    res = 0
            elif var_type == 'normal':
                if var_value > 1023:
                    res = 1023
                if var_value < 0:
                    res = 0
            elif var_type == 'big':
                if var_value > 32767:
                    res = 32767
                if var_value < 0:
                    res = 0
        return res

    def check_value(self, var_type, var_value, var_sign_type):
        res = True
        if isinstance(var_type, list):
            var_type = var_type[1]
        if var_sign_type == 'signed':
            if var_type == 'tiny':
                res = False
            elif var_type == 'small' and (var_value > 15 or var_value < -16):
                res = False
            elif var_type == 'normal' and (var_value > 511 or var_value < -512):
                res = False
            elif var_type == 'big' and (var_value > 16383 or var_value < -16384):
                res = False
        else:
            if var_type == 'tiny' and (var_value > 1 or var_value < 0):
                res = False
            elif var_type == 'small' and (var_value > 31 or var_value < 0):
                res = False
            elif var_type == 'normal' and (var_value > 1023 or var_value < 0):
                res = False
            elif var_type == 'big' and (var_value > 32767 or var_value < 0):
                res = False
        return res

    def check_index(self, index, var_type):
        res = True
        first = self.interpreter_node(index[0])
        second = self.interpreter_node(index[1])
        if var_type == 'tiny':
            if first > 1 or first < 0 or second > 1 or second < 0:
                res = False
        elif var_type == 'small':
            if first > 31 or first < 0 or second > 31 or second < 0:
                res = False
        elif var_type == 'normal':
            if first > 1023 or first < 0 or second > 1023 or second < 0:
                res = False
        elif var_type == 'big':
            if first > 32767 or first < 0 or second > 32767 or second < 0:
                res = False
        return res


    def bool_to_int(self, value):
        if value == True:
            return 1
        if value == False:
            return 0

    def int_to_bool(self, value):
        if value != 0:
            return True
        if value == 0:
            return False
    # for robot

    def robot_rr(self):
        self.robot.PreviousSonarBits = 0
        self.robot.SonarCallCount = 0
        return self.robot.RobotRR()

    def robot_rl(self):
        self.robot.PreviousSonarBits = 0
        self.robot.SonarCallCount = 0
        return self.robot.RobotRL()

    def robot_go(self):
        res = self.robot.RobotGo()
        if res == 2:
            self.exit = True
        return res

    def robot_sonar(self):
        return self.robot.RobotSonar()

    def robot_compass(self):
        return self.robot.RobotCompass()


def create_robot(descriptor):
    with open(descriptor) as file:
        text = file.read()
    text = text.split('\n')
    robot_info = text.pop(0).split(' ')
    map_size = text.pop(0).split(' ')
    Pos = []
    Pos.append(int(robot_info[0]))
    Pos.append(int(robot_info[1]))
    Rot = int(robot_info[2])
    map = [0] * int(map_size[0])

    for i in range(int(map_size[0])):
        map[i] = [0] * int(map_size[1])
    for i in range(int(map_size[0])):
        for j in range(int(map_size[1])):
            map[i][j] = Cell("EMPTY")
    posit = 0
    while len(text) > 0:
        line = list(text.pop(0))
        line = [Cell(cells[i]) for i in line]
        map[posit] = line
        posit += 1
    return Robot(Pos=Pos, Rot=Rot, map=map)

if __name__ == '__main__':
    tests = ['D:\Python\TA2\Data\_fib.txt', 'D:\Python\TA2\Data\_fib_recursion.txt', 'D:\Python\TA2\Data\_bad_recursion.txt', 'D:\Python\TA2\Data\_BubbleSort.txt', 'D:\Python\TA2\Data\_NoMain.txt']
    maps = ['D:\Python\TA2\Data\simple_map.txt', 'D:\Python\TA2\Data\\noExit_map.txt', 'D:\Python\TA2\Data\medium_map.txt', 'D:\Python\TA2\Data\island_map.txt', 'D:\Python\TA2\Data\middle_map.txt' ]
    algo = ['D:\Python\TA2\Data\Pledge_algo.txt']
    imgs = ['D:\Python\TA2\Data\simple_map.png', 'D:\Python\TA2\Data\\noExit_map.png', 'D:\Python\TA2\Data\medium_map.png', 'D:\Python\TA2\Data\island_map.png', 'D:\Python\TA2\Data\middle_map.png' ]
    print("Make your choice: 1 - test, 2 - robot")
    n = int(input())
    if n == 1:
        interpreter = Interpreter()
        print('Which test do you want to run?\n0 - Fibonacci numbers\n1 - Recursion Fibonacci\n2 - Bad recursion\n3 - Bubble sort\n4 - No Main')
        num = int(input())
        if num not in range(len(tests)):
            print('Wrong choice')
        else:
            prog = open(tests[num], 'r').read()
            res = interpreter.interpreter(program=prog, tree_print=False)
            if res:
                print('Result symbol table:')
                for key, value in interpreter.sym_table[0].items():
                    print(key,'=', value)
    elif n == 2:
        print("Which map do you want to use?\n0 - Simple map\n1 - Map without exit\n2 - Medium map\n3 - With island\n4 - Middle map")
        num = int(input())
        robot = create_robot(maps[num])
        img = Image.open(imgs[num])
        interpreter = Interpreter()
        prog = open(algo[0], 'r').read()
        res = interpreter.interpreter(robot=robot, program=prog)
        if res:
            print('Result symbol table:')
            for key, value in interpreter.sym_table[0].items():
                print(key,'=', value)
        if interpreter.exit:
            print('\n###### Exit has been found!!! ######\n')
        else:
            print('\n###### Exit hasn\'t been found :( ######\n')
        print('Robot:', interpreter.robot)
        print('Map:')
        img.show()

    else:
        print('Wrong choice!\n')


"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: JackTokenizer, output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.vm_writer = VMWriter(output_stream)
        self.input_stream = input_stream
        self.input_stream.advance()
        self.symbol_table = SymbolTable()
        self.label_counter = 0
        self.class_name = ""
        self.compile_class()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        # get the class name
        self.input_stream.advance()
        self.class_name = self.input_stream.identifier()
        self.input_stream.advance()
        self.input_stream.advance()

        # save static\field data
        while self.input_stream.token_type() == "KEYWORD" and \
                self.input_stream.keyword() in ['static', 'field']:
            self.compile_class_var_dec()

        while self.input_stream.token_type() == "KEYWORD" and \
                self.input_stream.keyword() in ['constructor', 'function', 'method']:
            self.compile_subroutine()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        kind = self.input_stream.keyword()
        self.input_stream.advance()
        var_type = self.compile_type()
        name = self.input_stream.identifier()
        self.input_stream.advance()

        self.symbol_table.define(name, var_type, "this")

        while self.input_stream.token_type() == "SYMBOL" and \
                self.input_stream.symbol() == ',':
            self.input_stream.advance()
            name = self.input_stream.identifier()
            self.input_stream.advance()
            self.symbol_table.define(name, var_type, "this")

        self.input_stream.advance()

    def compile_type(self):
        # todo: check that all useage knows that it returns value
        var_type = ""
        if self.input_stream.token_type() == 'KEYWORD':
            var_type = self.input_stream.keyword()
        else:
            var_type = self.input_stream.identifier()
        self.input_stream.advance()
        return var_type

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # function declaration
        subroutine_keyword = self.input_stream.keyword()
        self.input_stream.advance()
        subroutine_return_type = self.compile_type()
        # self.input_stream.advance()
        subroutine_name = self.input_stream.identifier()  # if constructor, name == new
        # self.input_stream.advance()

        # build subroutine symbol table
        self.symbol_table.start_subroutine()

        # add arguments list
        self.input_stream.advance()
        self.input_stream.advance()
        self.compile_parameter_list()

        # add local parameters
        self.input_stream.advance()
        self.input_stream.advance()
        self.compile_var_dec()
        # self.input_stream.advance()

        self.vm_writer.write_function(f"{self.class_name}.{subroutine_name}",
                                      self.symbol_table.var_count("local"))

        self.compile_body(subroutine_keyword)
        self.input_stream.advance()

    def compile_body(self, subroutine_keyword):
        # compile beginning
        if subroutine_keyword == "constructor":
            self.vm_writer.write_push("constant", self.symbol_table.var_count("this"))
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("pointer", 0)
        elif subroutine_keyword == "method":
            self.vm_writer.write_push("argument", 0)
            self.vm_writer.write_pop("pointer", 0)

        # compile middle
        while not (self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == '}'):
            self.compile_statements()
            # self.input_stream.advance()

        # compile ending
        #if subroutine_keyword == "constructor":
        #    self.vm_writer.write_push("pointer", 0)
        #    self.vm_writer.write_return()

    def compile_parameter_list(self):
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        if not (self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ')'):  # NOT )
            param_type = self.compile_type()
            param_name = self.input_stream.identifier()
            self.input_stream.advance()
            self.symbol_table.define(param_name, param_type, "argument")

            while self.input_stream.token_type() == "SYMBOL" and \
                    self.input_stream.symbol() == ',':
                self.input_stream.advance()
                param_type = self.compile_type()
                param_name = self.input_stream.identifier()
                self.symbol_table.define(param_name, param_type, "argument")
                self.input_stream.advance()

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        while self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword() == "var":
            self.input_stream.advance()
            var_type = self.input_stream.keyword()
            self.input_stream.advance()
            var_name = self.input_stream.identifier()
            self.symbol_table.define(var_name, var_type, "local")
            self.input_stream.advance()
            while self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ",":
                self.input_stream.advance()
                # var_type = self.input_stream.keyword()
                # self.input_stream.advance()
                var_name = self.input_stream.identifier()
                self.symbol_table.define(var_name, var_type, "local")
                self.input_stream.advance()
            self.input_stream.advance()

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        """ important! these method advance in their last step """
        while self.input_stream.token_type() == "KEYWORD":
            statement = self.input_stream.keyword()
            if statement == "let":
                self.compile_let()
            elif statement == "if":
                self.compile_if()
            elif statement == "while":
                self.compile_while()
            elif statement == "do":
                self.compile_do()
            elif statement == "return":
                self.compile_return()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.input_stream.advance()
        self.compile_subroutine_call()
        self.vm_writer.write_pop("TEMP", 0)
        self.input_stream.advance()

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.input_stream.advance()
        var_name = self.input_stream.identifier()
        self.input_stream.advance()

        if self.input_stream.token_type() == "SYMBOL" and \
                self.input_stream.symbol() == '[':

            self.vm_writer.write_push(self.symbol_table.kind_of(var_name), self.symbol_table.index_of(var_name))
            self.input_stream.advance()
            self.compile_expression()
            self.vm_writer.write_arithmetic("ADD")
            self.input_stream.advance()

            self.input_stream.advance()

            self.compile_expression()

            self.input_stream.advance()

            self.vm_writer.write_pop("TEMP", 0)
            self.vm_writer.write_pop("POINTER", 1)
            self.vm_writer.write_push("TEMP", 0)
            self.vm_writer.write_pop("THAT", 0)
        else:
            self.input_stream.advance()
            self.compile_expression()
            self.input_stream.advance()
            self.vm_writer.write_pop(self.symbol_table.kind_of(var_name), self.symbol_table.index_of(var_name))

    def compile_while(self) -> None:
        """Compiles a while statement."""
        while_index = self.label_counter
        self.label_counter += 1
        self.input_stream.advance()
        self.input_stream.advance()
        self.vm_writer.write_label(f"WHILE_EXP{while_index}")
        self.compile_expression()
        self.vm_writer.write_arithmetic("NOT")
        self.vm_writer.write_if(f"WHILE_END{while_index}")  # its the original counter + 1
        self.input_stream.advance()
        self.input_stream.advance()
        self.compile_statements()
        self.vm_writer.write_goto(f"WHILE_EXP{while_index}")
        self.vm_writer.write_label(f"WHILE_END{while_index}")
        self.input_stream.advance()

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.input_stream.advance()
        if self.input_stream.token_type() != "SYMBOL" or \
                (self.input_stream.token_type() == "SYMBOL" and
                 self.input_stream.symbol() != ';'):
            self.compile_expression()
        else:
            self.vm_writer.write_push("CONSTANT", 0)

        self.input_stream.advance()
        self.vm_writer.write_return()

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        if_index = self.label_counter
        self.label_counter += 1
        self.input_stream.advance()
        self.input_stream.advance()
        self.compile_expression()
        self.vm_writer.write_arithmetic("NOT")
        self.input_stream.advance()
        self.input_stream.advance()
        self.vm_writer.write_if(f"IF_FALSE{if_index}")

        self.compile_statements()
        self.vm_writer.write_goto(f"IF_END{if_index}")
        self.vm_writer.write_label(f"IF_FALSE{if_index}")  # L1
        self.input_stream.advance()

        if self.input_stream.token_type() == "KEYWORD" and \
                self.input_stream.keyword() == "else":
            self.input_stream.advance()
            self.input_stream.advance()

            self.compile_statements()
            self.input_stream.advance()

        self.vm_writer.write_label(f"IF_END{if_index}")  # L2 [FOR THE ELSE\NOTHING]

    def compile_expression(self) -> None:
        """Compiles an expression."""
        OP = {'+': 'ADD', '-': 'SUB', '*': '*', '/': '/', '&': 'AND', '|': 'OR', '<': 'LT', '>': 'GT', '=': "EQ"}

        self.compile_term()
        while self.input_stream.token_type() == "SYMBOL" and \
                self.input_stream.symbol() in OP.keys():
            op_name = OP[self.input_stream.symbol()]
            self.input_stream.advance()
            self.compile_term()
            self.vm_writer.write_arithmetic(op_name)

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """

        KEYWORD_CONSTANT = ['true', 'false', 'null', 'this']
        UNARY_OP = {'-': "NEG", '~': "NOT", '^': "SHIFTLEFT", '#': "SHIFTRIGHT"}

        if self.input_stream.token_type() == "INT_CONST":
            self.vm_writer.write_push("CONSTANT", self.input_stream.int_val())
            self.input_stream.advance()

        elif self.input_stream.token_type() == "STRING_CONST":
            current_str = self.input_stream.string_val()
            self.vm_writer.write_push("CONSTANT", len(current_str))
            self.vm_writer.write_call("String.new", 1)
            for c in current_str:
                self.vm_writer.write_push("CONSTANT", c)  # todo: check if it works with char
                self.vm_writer.write_call("String.appendChar", 1)
            self.input_stream.advance()

        elif self.input_stream.token_type() == "KEYWORD" and \
                self.input_stream.keyword() in KEYWORD_CONSTANT:
            if self.input_stream.keyword() in ['false', 'null']:
                self.vm_writer.write_push("CONSTANT", 0)
            elif self.input_stream.keyword() == 'true':
                self.vm_writer.write_push("CONSTANT", 0)
                self.vm_writer.write_arithmetic("NOT")
            else:
                self.vm_writer.write_push("POINTER", 0)
            self.input_stream.advance()

        elif self.input_stream.token_type() == "IDENTIFIER":
            var_name = self.input_stream.identifier()
            self.input_stream.advance()

            if self.input_stream.token_type() == "SYMBOL":
                if self.input_stream.symbol() == '[':

                    self.input_stream.advance()
                    self.compile_expression()
                    self.input_stream.advance()
                elif self.input_stream.symbol() == '(':
                    self.compile_subroutine_call(var_name)
                elif self.input_stream.symbol() == '.':
                    self.compile_subroutine_call(var_name)  # todo: check if its good
                else:
                    # todo: check if its good
                    self.vm_writer.write_push(self.symbol_table.kind_of(var_name), self.symbol_table.index_of(var_name))

        elif self.input_stream.token_type() == "SYMBOL":
            if self.input_stream.symbol() == '(':
                self.input_stream.advance()
                self.compile_expression()
                self.input_stream.advance()

            elif self.input_stream.symbol() in UNARY_OP:
                op = self.input_stream.symbol()
                self.input_stream.advance()
                self.compile_term()  # todo: check if its good
                self.vm_writer.write_arithmetic(UNARY_OP[op])

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        counter = 0
        if self.input_stream.token_type() != "SYMBOL" or \
                (self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() != ')'):
            counter += 1
            self.compile_expression()
            while self.input_stream.token_type() == "SYMBOL" and \
                    self.input_stream.symbol() == ",":
                counter += 1
                self.input_stream.advance()
                self.compile_expression()
        return counter

    def compile_subroutine_call(self, first_part_name=''):
        if self.input_stream.token_type() == "IDENTIFIER":
            first_part_name = self.input_stream.identifier()
            self.input_stream.advance()

        param_amount = 0
        second_part_name = ''
        function_name = first_part_name
        if self.input_stream.token_type() == "SYMBOL" and \
                self.input_stream.symbol() == '.':
            self.input_stream.advance()
            second_part_name = self.input_stream.identifier()
            self.input_stream.advance()
            function_name = function_name + f'.{second_part_name}'

        if self.symbol_table.contains(first_part_name) or "." not in function_name:  # method
            self.vm_writer.write_push("pointer", 0)
            if "." not in function_name:
                function_name = f"{self.class_name}.{function_name}"
            else:
                function_name = f"{self.symbol_table.type_of(first_part_name)}.{second_part_name}"
            param_amount += 1

        self.input_stream.advance()
        param_amount += self.compile_expression_list()
        self.input_stream.advance()

        self.vm_writer.write_call(function_name, param_amount)

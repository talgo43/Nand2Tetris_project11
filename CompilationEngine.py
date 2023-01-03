"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import JackTokenizer


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
        self.output_stream = output_stream
        self.input_stream = input_stream
        self.input_stream.advance()
        self.compile_class()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        self.output_stream.write("<class>\n")

        self.output_stream.write("<keyword> {keyword} </keyword>\n".format(keyword=self.input_stream.keyword()))

        self.input_stream.advance()
        self.output_stream.write(
            "<identifier> {class_name} </identifier>\n".format(class_name=self.input_stream.identifier()))

        self.input_stream.advance()
        self.output_stream.write("<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))

        self.input_stream.advance()
        while self.input_stream.token_type() == "KEYWORD" and \
                self.input_stream.keyword() in ['static', 'field']:
            self.compile_class_var_dec()
            # self.input_stream.advance()

        while self.input_stream.token_type() == "KEYWORD" and \
                self.input_stream.keyword() in ['constructor', 'function', 'method']:
            self.compile_subroutine()
            # self.input_stream.advance()

        self.output_stream.write("<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))

        self.output_stream.write("</class>\n")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        self.output_stream.write("<classVarDec>\n")

        self.output_stream.write("<keyword> {keyword} </keyword>\n".format(keyword=self.input_stream.keyword()))

        self.input_stream.advance()
        self.compile_type()

        # self.input_stream.advance()
        self.output_stream.write(
            "<identifier> {var_name} </identifier>\n".format(var_name=self.input_stream.identifier()))

        self.input_stream.advance()
        while self.input_stream.token_type() == "SYMBOL" and \
                self.input_stream.symbol() == ',':
            self.output_stream.write(
                "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
            self.input_stream.advance()
            self.output_stream.write(
                "<identifier> {var_name} </identifier>\n".format(var_name=self.input_stream.identifier()))
            self.input_stream.advance()

        self.output_stream.write("<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
        self.input_stream.advance()

        self.output_stream.write("</classVarDec>\n")

    def compile_type(self):
        if self.input_stream.token_type() == 'KEYWORD':
            self.output_stream.write(
                "<keyword> {keyword_name} </keyword>\n".format(keyword_name=self.input_stream.keyword()))
        else:
            self.output_stream.write(
                "<identifier> {identifier_name} </identifier>\n".format(identifier_name=self.input_stream.identifier()))
        self.input_stream.advance()

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Your code goes here!
        self.output_stream.write("<subroutineDec>\n")

        self.output_stream.write("<keyword> {keyword} </keyword>\n".format(keyword=self.input_stream.keyword()))

        self.input_stream.advance()
        self.compile_type()

        # self.input_stream.advance()
        self.output_stream.write(
            "<identifier> {var_name} </identifier>\n".format(var_name=self.input_stream.identifier()))

        self.input_stream.advance()
        self.output_stream.write("<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))

        self.input_stream.advance()

        self.compile_parameter_list()
        # self.input_stream.advance()

        self.output_stream.write("<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))

        self.input_stream.advance()
        self.compile_body()

        self.output_stream.write("</subroutineDec>\n")

    def compile_body(self):
        self.output_stream.write("<subroutineBody>\n")

        self.output_stream.write("<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))

        self.input_stream.advance()

        while self.input_stream.token_type() == "KEYWORD" and \
                self.input_stream.symbol() == 'var':
            self.compile_var_dec()
            # self.input_stream.advance()

        self.compile_statements()
        # self.input_stream.advance()

        self.output_stream.write("<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
        self.input_stream.advance()

        self.output_stream.write("</subroutineBody>\n")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        # Your code goes here!
        self.output_stream.write("<parameterList>\n")
        if not (self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ')'):  # NOT )
            self.compile_type()
            # self.input_stream.advance()
            self.output_stream.write(
                "<identifier> {var_name} </identifier>\n".format(var_name=self.input_stream.identifier()))
            self.input_stream.advance()

            while self.input_stream.token_type() == "SYMBOL" and \
                    self.input_stream.symbol() == ',':
                self.output_stream.write(
                    "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
                self.input_stream.advance()

                self.compile_type()
                # self.input_stream.advance()

                self.output_stream.write(
                    "<identifier> {var_name} </identifier>\n".format(var_name=self.input_stream.identifier()))
                self.input_stream.advance()

        self.output_stream.write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.output_stream.write("<varDec>\n")

        self.output_stream.write("<keyword> {keyword} </keyword>\n".format(keyword=self.input_stream.keyword()))
        self.input_stream.advance()

        self.compile_type()
        # self.input_stream.advance()

        self.output_stream.write(
            "<identifier> {var_name} </identifier>\n".format(var_name=self.input_stream.identifier()))
        self.input_stream.advance()

        while self.input_stream.token_type() == "SYMBOL" and \
                self.input_stream.symbol() == ',':
            self.output_stream.write(
                "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
            self.input_stream.advance()

            self.output_stream.write(
                "<identifier> {var_name} </identifier>\n".format(var_name=self.input_stream.identifier()))
            self.input_stream.advance()

        self.output_stream.write(
            "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))

        self.input_stream.advance()

        self.output_stream.write("</varDec>\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        """ important! these method advance in their last step """
        self.output_stream.write("<statements>\n")
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

        self.output_stream.write("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.output_stream.write("<doStatement>\n")

        self.output_stream.write("<keyword> {keyword} </keyword>\n".format(keyword=self.input_stream.keyword()))
        self.input_stream.advance()

        self.compile_subroutine_call()
        # self.input_stream.advance()

        self.output_stream.write(
            "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))

        self.input_stream.advance()

        self.output_stream.write("</doStatement>\n")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.output_stream.write("<letStatement>\n")

        self.output_stream.write("<keyword> {keyword} </keyword>\n".format(keyword=self.input_stream.keyword()))
        self.input_stream.advance()

        self.output_stream.write(
            "<identifier> {var_name} </identifier>\n".format(var_name=self.input_stream.identifier()))
        self.input_stream.advance()

        if self.input_stream.token_type() == "SYMBOL" and \
                self.input_stream.symbol() == '[':
            self.output_stream.write(
                "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
            self.input_stream.advance()

            self.compile_expression()
            # self.input_stream.advance()

            self.output_stream.write(
                "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
            self.input_stream.advance()

        self.output_stream.write(
            "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
        self.input_stream.advance()

        self.compile_expression()
        # self.input_stream.advance()

        self.output_stream.write(
            "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))

        self.input_stream.advance()

        self.output_stream.write("</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.output_stream.write("<whileStatement>\n")

        self.output_stream.write("<keyword> {keyword} </keyword>\n".format(keyword=self.input_stream.keyword()))
        self.input_stream.advance()

        self.output_stream.write(
            "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
        self.input_stream.advance()

        self.compile_expression()
        # self.input_stream.advance()

        self.output_stream.write(
            "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
        self.input_stream.advance()

        self.output_stream.write(
            "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
        self.input_stream.advance()

        self.compile_statements()
        # self.input_stream.advance()

        self.output_stream.write(
            "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
        self.input_stream.advance()

        self.output_stream.write("</whileStatement>\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.output_stream.write("<returnStatement>\n")

        self.output_stream.write("<keyword> {keyword} </keyword>\n".format(keyword=self.input_stream.keyword()))
        self.input_stream.advance()

        if self.input_stream.token_type() != "SYMBOL" or \
                (self.input_stream.token_type() == "SYMBOL" and
                 self.input_stream.symbol() != ';'):
            self.compile_expression()
            # self.input_stream.advance()

        self.output_stream.write(
            "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
        self.input_stream.advance()

        self.output_stream.write("</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.output_stream.write("<ifStatement>\n")

        self.output_stream.write("<keyword> {keyword} </keyword>\n".format(keyword=self.input_stream.keyword()))
        self.input_stream.advance()

        self.output_stream.write(
            "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
        self.input_stream.advance()

        self.compile_expression()
        # self.input_stream.advance()

        self.output_stream.write(
            "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
        self.input_stream.advance()

        self.output_stream.write(
            "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
        self.input_stream.advance()

        self.compile_statements()
        # self.input_stream.advance()

        self.output_stream.write(
            "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
        self.input_stream.advance()

        if self.input_stream.token_type() == "KEYWORD" and \
                self.input_stream.keyword() == "else":
            self.output_stream.write("<keyword> {keyword} </keyword>\n".format(keyword=self.input_stream.keyword()))
            self.input_stream.advance()

            self.output_stream.write(
                "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
            self.input_stream.advance()

            self.compile_statements()
            # self.input_stream.advance()

            self.output_stream.write(
                "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
            self.input_stream.advance()

        self.output_stream.write("</ifStatement>\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        OP = {'+': '+', '-': '-', '*': '*', '/': '/', '&': '&amp;', '|': '|', '<': '&lt;', '>': '&gt;', '=': '='}
        self.output_stream.write("<expression>\n")

        self.compile_term()
        while self.input_stream.token_type() == "SYMBOL" and \
                self.input_stream.symbol() in OP.keys():
            self.output_stream.write(
                "<symbol> {symbol_name} </symbol>\n".format(symbol_name=OP[self.input_stream.symbol()]))
            self.input_stream.advance()
            self.compile_term()

        # todo: do I realy need this: self.input_stream.advance() ?

        self.output_stream.write("</expression>\n")

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
        UNARY_OP = ['-', '~', '^', '#']

        self.output_stream.write("<term>\n")

        if self.input_stream.token_type() == "INT_CONST":
            self.output_stream.write(
                "<integerConstant> {int_val} </integerConstant>\n".format(int_val=self.input_stream.int_val()))
            self.input_stream.advance()

        elif self.input_stream.token_type() == "STRING_CONST":
            self.output_stream.write(
                "<stringConstant> {string_val} </stringConstant>\n".format(string_val=self.input_stream.string_val()))
            self.input_stream.advance()

        elif self.input_stream.token_type() == "KEYWORD" and \
                self.input_stream.keyword() in KEYWORD_CONSTANT:
            self.output_stream.write("<keyword> {keyword} </keyword>\n".format(keyword=self.input_stream.keyword()))
            self.input_stream.advance()

        elif self.input_stream.token_type() == "IDENTIFIER":
            self.output_stream.write(
                "<identifier> {var_name} </identifier>\n".format(var_name=self.input_stream.identifier()))
            self.input_stream.advance()

            if self.input_stream.token_type() == "SYMBOL":
                if self.input_stream.symbol() == '[':
                    self.output_stream.write(
                        "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
                    self.input_stream.advance()
                    self.compile_expression()
                    self.output_stream.write(
                        "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
                    self.input_stream.advance()
                elif self.input_stream.symbol() == '(':
                    self.compile_subroutine_call()
                elif self.input_stream.symbol() == '.':
                    self.compile_subroutine_call()  # todo: check if its good

        elif self.input_stream.token_type() == "SYMBOL":
            if self.input_stream.symbol() == '(':
                self.output_stream.write(
                    "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
                self.input_stream.advance()

                self.compile_expression()

                self.output_stream.write(
                    "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
                self.input_stream.advance()

            elif self.input_stream.symbol() in UNARY_OP:
                self.output_stream.write(
                    "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
                self.input_stream.advance()
                self.compile_term()  # todo: check if its good

        self.output_stream.write("</term>\n")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.output_stream.write("<expressionList>\n")

        if self.input_stream.token_type() != "SYMBOL" or \
                (self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() != ')'):

            self.compile_expression()
            while self.input_stream.token_type() == "SYMBOL" and \
                    self.input_stream.symbol() == ",":
                self.output_stream.write(
                    "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
                self.input_stream.advance()
                self.compile_expression()

        self.output_stream.write("</expressionList>\n")

    def compile_subroutine_call(self):
        if self.input_stream.token_type() == "IDENTIFIER":
            self.output_stream.write(
                "<identifier> {var_name} </identifier>\n".format(var_name=self.input_stream.identifier()))
            self.input_stream.advance()

        if self.input_stream.token_type() == "SYMBOL" and \
                self.input_stream.symbol() == '.':
            self.output_stream.write(
                "<symbol> {var_name} </symbol>\n".format(var_name=self.input_stream.symbol()))
            self.input_stream.advance()
            self.output_stream.write(
                "<identifier> {var_name} </identifier>\n".format(var_name=self.input_stream.identifier()))
            self.input_stream.advance()

        self.output_stream.write(
            "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
        self.input_stream.advance()

        self.compile_expression_list()

        self.output_stream.write(
            "<symbol> {symbol_name} </symbol>\n".format(symbol_name=self.input_stream.symbol()))
        self.input_stream.advance()

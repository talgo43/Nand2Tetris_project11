"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """
    CLASS_KIND = ["static", "this"]

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.class_symbols = dict()
        self.subroutine_symbols = dict()

    def get_symbol_table(self, kind):
        current_dict = self.subroutine_symbols
        if kind in SymbolTable.CLASS_KIND:
            current_dict = self.class_symbols
        return current_dict

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.subroutine_symbols.clear()

    def define(self, name: str, type: str, kind: str, is_method=False) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            is_method:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        current_dict = self.get_symbol_table(kind)
        index = self.var_count(kind)
        if is_method and kind == "argument":
            index += 1
        current_dict[name] = (type, kind, index)

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        current_dict = self.get_symbol_table(kind)
        counter = 0
        for s_type, s_kind, s_i in current_dict.values():
            if s_kind == kind:
                counter += 1
        return counter

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if name in self.class_symbols.keys():
            return self.class_symbols[name][1]
        else:
            return self.subroutine_symbols[name][1]

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if name in self.class_symbols.keys():
            return self.class_symbols[name][0]
        else:
            return self.subroutine_symbols[name][0]

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name in self.class_symbols.keys():
            return self.class_symbols[name][2]
        else:
            return self.subroutine_symbols[name][2]

    def contains(self, name: str) -> bool:
        return (name in self.class_symbols.keys()) or (name in self.subroutine_symbols.keys())

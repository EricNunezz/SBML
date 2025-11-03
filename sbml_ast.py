#Eric Nunez
#Student ID: 114806268

from dataclasses import dataclass
from typing import Union, List, Any

class SemanticError(Exception):
    pass

@dataclass
class NumberNode:
    value: Union[int, float]

    def eval(self):
        return self.value

    def __str__(self):
        return f"NumberNode({self.value})"

@dataclass
class BooleanNode:
    value: bool

    def eval(self):
        return self.value

    def __str__(self):
        return f"BooleanNode({self.value})"

@dataclass
class StringNode:
    value: str

    def eval(self):
        return self.value

    def __str__(self):
        return f"StringNode({self.value!r})"

@dataclass
class ListNode:
    elements: List[Any]

    def eval(self):
        return [elem.eval() for elem in self.elements]

    def __str__(self):
        inner = ", ".join(str(e) for e in self.elements)
        return f"ListNode([{inner}])"

@dataclass
class TupleNode:
    elements: List[Any]

    def eval(self):
        return tuple(elem.eval() if hasattr(elem, 'eval') else elem for elem in self.elements)

    def __str__(self):
        inner = ", ".join(str(e) for e in self.elements)
        return f"TupleNode([{inner}])"

def is_num(x):
    return isinstance(x, (int, float))

@dataclass
class BinaryOpNode:
    op: str
    left: Any
    right: Any


    def eval(self):
        op = '!=' if self.op in ('<>', '!=') else self.op

        if op == 'andalso':
            left_val = self.left.eval()
            if not isinstance(left_val, bool):
                raise SyntaxError("Operands or andalso must be booleans")
            if not left_val:
                return False
            right_val = self.right.eval()
            if not isinstance(right_val, bool):
                raise SyntaxError("Operands or andalso must be booleans")
            return left_val and right_val

        if op == 'orelse':
            left_val = self.left.eval()
            if not isinstance(left_val, bool):
                raise SyntaxError("Operands or orelse must be booleans")
            if not left_val:
                return False
            right_val = self.right.eval()
            if not isinstance(right_val, bool):
                raise SyntaxError("Operands or orelse must be booleans")
            return left_val or right_val

        left_val = self.left.eval()
        right_val = self.right.eval()

        if op == '+':
            if is_num(left_val) and is_num(right_val):
                return left_val + right_val
            if isinstance(left_val, str) and isinstance(right_val, str):
                return left_val + right_val
            if isinstance(left_val, list) and isinstance(right_val, list):
                return left_val + right_val
            raise SyntaxError("Operands of + must both be numbers")

        elif op == '-':
            if not (is_num(left_val) and is_num(right_val)):
                raise TypeError("Operands of '-' must be numbers.")
            return left_val - right_val

        elif op == '*':
            if not (is_num(left_val) and is_num(right_val)):
                raise TypeError("Operands of '*' must be numbers.")
            return left_val * right_val

        elif op == '/':
            if not (is_num(left_val) and is_num(right_val)):
                raise TypeError("Operands of '/' must be numbers.")
            if right_val == 0:
                raise ZeroDivisionError("Division by zero in SBML expression.")
            return left_val / right_val

        elif op == 'div':
            if not (isinstance(left_val, int) and isinstance(right_val, int)):
                raise TypeError("Operands of 'div' must be integers.")
            if right_val == 0:
                raise ZeroDivisionError("Division by zero in SBML expression.")
            return left_val // right_val

        elif op == 'mod':
            if not (isinstance(left_val, int) and isinstance(right_val, int)):
                raise TypeError("Operands of 'mod' must be numbers.")
            return left_val % right_val

        elif op == '**':
            if not (is_num(left_val) and is_num(right_val)):
                raise TypeError("Operands of '**' must be numbers.")
            return left_val ** right_val

        elif op in ('<', '<=', '==', '!=', '>=', '>'):
            if is_num(left_val) and is_num(right_val):
                if op == '<': return left_val < right_val
                elif op == '<=': return left_val <= right_val
                elif op == '==': return left_val == right_val
                elif op == '!=': return left_val != right_val
                elif op == '>=': return left_val >= right_val
                elif op == '>': return left_val > right_val
            if isinstance(left_val, str) and isinstance(right_val, str):
                if op == '<': return left_val < right_val
                elif op == '<=': return left_val <= right_val
                elif op == '==': return left_val == right_val
                elif op == '!=': return left_val != right_val
                elif op == '>=': return left_val >= right_val
                elif op == '>': return left_val > right_val
            raise SemanticError("Invalid Types for comparison.")

        elif op == '::':
            if not isinstance(right_val, list):
                raise TypeError("Right side of :: must be a list.")
            return [left_val] + right_val

        elif op == 'in':
            if not isinstance(right_val, (list, str)):
                raise TypeError("Right side of in must be a list or str")
            return left_val in right_val

        else:
            raise ValueError(f"Unknown operator: {op}")

    def __str__(self):
        return f"BinaryOpNode({self.left} {self.op} {self.right})"



@dataclass
class UnaryOpNode:
    op: str
    expr: Any

    def eval(self):
        value = self.expr.eval()

        if self.op == '-':
            return -value
        elif self.op == '+':
            return +value
        elif self.op == 'not':
            if not isinstance(value, bool):
                raise TypeError("Operand of 'not' must be boolean")
            return not value

        else:
            raise ValueError(f"Unknown unary op: {self.op}")

    def __str__(self):
        return f"UnaryOpNode({self.op} {self.expr})"

@dataclass
class IndexNode:
    collection: Any
    index: Any

    def eval(self):
        collection_value = self.collection.eval()
        index_value = self.index.eval()

        if not isinstance(index_value, int):
            raise TypeError("Index must be an integer.")

        if not isinstance(collection_value, (list, str)):
            raise TypeError("Can only index lists or strings.")

        if index_value < 0 or index_value >= len(collection_value):
            raise IndexError("Index out of bounds")

        result = collection_value[index_value]
        if isinstance(collection_value, str):
            return str(result)
        return result

    def __str__(self):
        return f"IndexNode({self.collection}[{self.index}])"


@dataclass
class TupleIndexNode:
    index: Any
    tuple_expr: Any

    def eval(self):
        index_val = self.index.eval()
        tuple_val = self.tuple_expr.eval()

        if not isinstance(index_val, int):
            raise TypeError("Tuple index must be an integer")
        if not isinstance(tuple_val, tuple):
            raise TypeError("Operand being indexed must be a tuple")


        if index_val < 1 or index_val > len(tuple_val):
            raise IndexError("Tuple index out of bounds")

        return tuple_val[index_val - 1]

    def __str__(self):
        return f"TupleIndexNode(#{self.index}({self.tuple_expr}))"

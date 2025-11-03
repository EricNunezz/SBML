#Eric Nunez
#Student ID: 114806268


import sys
from sbml_parser import parser, lexer

if len(sys.argv) != 3:
    print("Error not long enough")
    sys.exit(1)

mode = sys.argv[1]
filename = sys.argv[2]

try:
    with open(filename, 'r') as file:
        lines = file.readlines()
except FileNotFoundError:
    print(f"File '{filename}' not found.")
    sys.exit(1)

lines = [line.strip() for line in lines if line.strip()]


def print_ast(node, indent=0):
    pad = "  " * indent
    print(pad + f"Node Type: {type(node).__name__}")

    if hasattr(node, 'value'):
        print(pad + f"  Value: {node.value}")
    if hasattr(node, 'op'):
        print(pad + f"  Operator: {node.op}")

    if hasattr(node, '__dict__'):
        for key, val in node.__dict__.items():
            if isinstance(val, list):
                for elem in val:
                    if hasattr(elem, '__dict__'):
                        print_ast(elem, indent + 1)
            elif hasattr(val, '__dict__'):
                print_ast(val, indent + 1)



for line in lines:
    try:
        result = parser.parse(line, lexer=lexer)
    except Exception:
        print("SYNTAX ERROR")
        continue

    if result is None:
        print("SYNTAX ERROR")
        continue

    if mode == "-P":
        print_ast(result)
    elif mode == "-E":
        try:
            value = result.eval()
            if isinstance(value, str):
                print(f"'{value}'")
            else:
                print(value)
        except Exception:
            print("SEMANTIC ERROR")


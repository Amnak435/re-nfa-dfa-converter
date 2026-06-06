"""
regex_parser.py
---------------
Handles parsing of regular expressions and conversion to postfix notation.

Student : Amna Khurram
ID      : F24605061 | CS 2024-B
Instructor: Naveed Yousaf

Supported operators:
  |  – union / alternation
  *  – Kleene star (zero or more)
  +  – one or more
  ?  – zero or one
  .  – explicit concatenation (inserted automatically)
  ()  – grouping
"""

# ---------------------------------------------------------------------------
# Operator precedence (higher value = tighter binding)
# ---------------------------------------------------------------------------
PRECEDENCE = {
    '|': 1,   # lowest
    '.': 2,   # concatenation
    '*': 3,   # Kleene star
    '+': 3,   # one-or-more
    '?': 3,   # zero-or-one
}

UNARY_OPS  = {'*', '+', '?'}
BINARY_OPS = {'|', '.'}


def _insert_concat(regex: str) -> str:
    """
    Insert an explicit concatenation operator '.' between tokens that are
    implicitly concatenated in the user-written regex.

    Rules: insert '.' between (left, right) pairs when:
      left  is: literal, ')', '*', '+', '?'
      right is: literal, '('
    """
    result = []
    for i, ch in enumerate(regex):
        result.append(ch)
        if i + 1 < len(regex):
            left  = ch
            right = regex[i + 1]
            left_ok  = left  not in ('(', '|', '.')
            right_ok = right not in (')', '|', '*', '+', '?', '.')
            if left_ok and right_ok:
                result.append('.')
    return ''.join(result)


def to_postfix(regex: str) -> str:
    """
    Convert a (possibly user-friendly) infix regular expression to postfix
    (Reverse Polish Notation) using the shunting-yard algorithm.

    Returns the postfix string, which is consumed by the Thompson NFA builder.
    """
    # Step 1 – insert explicit concatenation dots
    regex = _insert_concat(regex)

    output = []   # output queue
    stack  = []   # operator stack

    for ch in regex:
        if ch == '(':
            stack.append(ch)

        elif ch == ')':
            # Pop until matching '('
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if not stack:
                raise ValueError("Mismatched parentheses in regex.")
            stack.pop()  # discard '('

        elif ch in PRECEDENCE:
            # Pop operators with higher-or-equal precedence (left-associative)
            while (stack and stack[-1] != '(' and
                   stack[-1] in PRECEDENCE and
                   PRECEDENCE[stack[-1]] >= PRECEDENCE[ch]):
                output.append(stack.pop())
            stack.append(ch)

        else:
            # Literal / symbol → goes straight to output
            output.append(ch)

    # Drain remaining operators
    while stack:
        op = stack.pop()
        if op in ('(', ')'):
            raise ValueError("Mismatched parentheses in regex.")
        output.append(op)

    return ''.join(output)


# ---------------------------------------------------------------------------
# Quick self-test (run: python regex_parser.py)
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    tests = [
        ('(a|b)*abb',   'ab|*.a.b.b.'),
        ('a*b',         'a*.b.'),
        ('(a|b)+',      'ab|+'),
        ('ab?c',        'a.b?.c.'),
    ]
    for regex, expected in tests:
        result = to_postfix(regex)
        status = '✓' if result == expected else f'✗ (expected {expected})'
        print(f"  {regex:20s}  →  {result}  {status}")

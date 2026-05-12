from langchain_classic.tools import Tool
import ast, operator

SAFE_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow, ast.USub: operator.neg
}

def safe_eval(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return SAFE_OPS[type(node.op)](safe_eval(node.left), safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return SAFE_OPS[type(node.op)](safe_eval(node.operand))
    raise ValueError(f"Unsupported operation: {type(node)}")

def calculator(expression: str) -> str:
    try:
        tree = ast.parse(expression.strip(), mode='eval')
        result = safe_eval(tree.body)
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"

calculator_tool = Tool(
    name="Calculator",
    func=calculator,
    description="Evaluate a mathematical expression. Input: a math expression like '25 * 4 + 10'."
)
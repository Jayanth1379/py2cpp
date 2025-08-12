from transpiler.python_to_cpp import py_to_cpp

def test_if():
    py = "x=5\nif x>3:\n    print(x)\n"
    cpp = py_to_cpp(py)
    assert "if ((x > 3))" in cpp
    assert "_print(x);" in cpp

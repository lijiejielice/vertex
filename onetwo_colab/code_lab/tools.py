import textwrap
import re

from onetwo.stdlib.code_execution import python_execution_safe_subset
from onetwo.stdlib.tool_use import llm_tool_use

# Python tool for executing a program in a Python sandbox.
PYTHON_EXAMPLE = textwrap.dedent("""\
  Python("1 + 1") returns "2".
  We can also run multiple lines of code like this:
  ```yaml
  Python:
    request: |
      a = []
      a.append(1)
      a.append(2)
      a
  ```
  returns [1, 2].""")

# Here we show the simplest case of a stateless Python tool. If we don't need
# to carry variable state over from one call to another, we can just create a
# fresh sandbox on each invocation of the Python tool.


async def run_stateless_python(request: str) -> str:
    temporary_sandbox = python_execution_safe_subset.PythonSandboxSafeSubset()
    async with temporary_sandbox.start() as temporary_sandbox:
        result = await temporary_sandbox.run(request)
        return str(result)

python_tool = llm_tool_use.Tool(
    name='Python',
    function=run_stateless_python,
    description='Python interpreter. Can be used as a calculator or to execute any Python code. Returns the result of execution.',
    example=PYTHON_EXAMPLE,
    color='plum',
)

# Here we register a simple mock Search tool that returns hard-coded responses.
# When using the agent for real, you can replace this with a function that calls
# a real search engine, or that retrieves relevant passages from an indexed
# corpus.


def mock_search(query: str) -> str:
    response_by_query = {
        'capital of France': 'Paris',
        'population of Tuebingen': 'Tübingen 91,877 Population [2021]',
        'population of Tübingen': 'Tübingen 91,877 Population [2021]',
        'population Tuebingen': 'Tübingen 91,877 Population [2021]',
        'population Tübingen': 'Tübingen 91,877 Population [2021]',
        'population of Zuerich': '402,762 (2017)',
        'population of Zurich': '402,762 (2017)',
        'population of Zürich': '402,762 (2017)',
        'population Zuerich': '402,762 (2017)',
        'population Zurich': '402,762 (2017)',
        'population Zürich': '402,762 (2017)',
        'first president of the United States': 'George Washington',
        'who was the first president of the United States?': 'George Washington',
        'wife of George Washington': 'Martha Washington',
        'who was the wife of George Washington?': 'Martha Washington',
        'Frozen box office': '$1.280 billion',
        'Frozen box office earnings': '$1.280 billion',
        'Frozen movie box office earnings': '$1.280 billion',
        'box office Frozen': '$1.280 billion',
        'box office for Frozen': '$1.280 billion',
        'box office of Frozen': '$1.280 billion',
        'box office earnings of Frozen': '$1.280 billion',
        'box office revenue Frozen': '$1.280 billion',
        'how much did Frozen make at the box office?': '$1.280 billion',
        'Lion King box office': '1.663 billion USD',
        'Lion King box office earnings': '1.663 billion USD',
        'Lion King movie box office earnings': '1.663 billion USD',
        'box office Lion King': '1.663 billion USD',
        'box office for Lion King': '1.663 billion USD',
        'box office of Lion King': '1.663 billion USD',
        'box office earnings of Lion King': '1.663 billion USD',
        'box office revenue Lion King': '1.663 billion USD',
        'how much did Lion King make at the box office?': '1.663 billion USD',
        'Titanic box office': 'worldwide theatrical total = $2.264 billion',
        'Titanic box office earnings': 'worldwide theatrical total = $2.264 billion',
        'Titanic movie box office earnings': 'worldwide theatrical total = $2.264 billion',
        'box office Titanic': 'worldwide theatrical total = $2.264 billion',
        'box office for Titanic': 'worldwide theatrical total = $2.264 billion',
        'box office of Titanic': 'worldwide theatrical total = $2.264 billion',
        'box office earnings of Titanic': 'worldwide theatrical total = $2.264 billion',
        'box office revenue Titanic': 'worldwide theatrical total = $2.264 billion',
        'how much did Titanic make at the box office?': 'worldwide theatrical total = $2.264 billion',
    }
    # Normalize capitalization.
    response_by_query = {k.lower(): v for k, v in response_by_query.items()}
    query = query.lower()
    return response_by_query.get(query, 'No results.')


search_tool = llm_tool_use.Tool(
    name='Search',
    function=mock_search,
    description='Search engine. Returns a relevant snippet or answer to query.',
    example=textwrap.dedent("Search('capital of France')  # returns 'Paris'"),
    color='darkseagreen',
)

# The "Finish" function provides the LLM with a way of indicating when it is
# ready to return a final answer. E.g., "Finish('USA')" returns 'USA'.
finish_tool = llm_tool_use.Tool(
    name='Finish',
    function=lambda x: x,
    description='Function for returning the final answer.',
)


def firstnumber(x):
    matches = re.match(r'[^\d]*([\d\.,]+).*', str(x).replace(',', ''))
    if matches:
        try:
            return float(matches.group(1))
        except Exception as e:
            return f'Error: could not parse {x} as a number ({e})'
    else:
        return f'Error: could not parse {x} as a number'


# Register a second tool called 'firstnumber' which is just a simple Python
# function that we define here, for extracting the first number from a block of
# text.
first_number_tool = llm_tool_use.Tool(
    name='firstnumber',
    function=firstnumber,
    description='Extracts the first number in a string.',
    example="firstnumber('it is 1,203m high')  # return 1203.0 as a float",
)

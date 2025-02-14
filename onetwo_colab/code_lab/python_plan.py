
import copy
import pprint
import re
import textwrap
from onetwo import ot

from onetwo.agents import python_planning
from onetwo.stdlib.tool_use import python_tool_use
from .tools import search_tool, first_number_tool


# Inspired by Python based tool based orchestration
# The PythonPlanningAgent is inspired by various various research in Python-based tool orchestration,
# such as ViperGPT (https://arxiv.org/pdf/2303.08128.pdf) and AdaPlanner (https://arxiv.org/pdf/2305.16653.pdf).

# In this strategy, we present the LLM with a list of tool descriptions with invocation examples,
# and then iteratively prompt the LLM to output a sequence of steps, each of which consists of a Python code block,
# with "thoughts", where relevant, in the form of code comments. At each step, we execute the LLM-generated code in a Python
# sandbox that provides access to the relevant tools via predefined functions. We then take everything that the code writes to stdout,
# and we include that in the LLM prompt in the next step, similarly to how we did with the "observation" in the ReAct strategy.

# While the ReActAgent performs exactly one tool call in each step, the PythonPlanningAgent can potentially make multiple tool
# calls from a single code block, and can include other control structures like loops and if-statements.
python_agent = python_planning.PythonPlanningAgent(
    exemplars=python_planning.DEFAULT_PYTHON_PLANNING_EXEMPLARS,
    environment_config=python_tool_use.PythonToolUseEnvironmentConfig(
        tools=[search_tool, first_number_tool],
    ),
    max_steps=10)


def python_planning_example_with_inspecting():
    question = 'Which movie had the larger box office: Frozen or Titanic?'
    answer, final_state = ot.run(python_agent(inputs=question, return_final_state=True))
    answer
    pprint.pprint(final_state, width=140)


def python_planning_example_with_tracing():
    question = 'Which movie had the larger box office: Frozen or Titanic?'
    answer, trace = ot.run(python_agent(inputs=question), enable_tracing=True)
    answer
    pprint.pprint(trace, width=140)


"""
updates=[PythonPlanningStep(is_finished=False,
    code='# First we need to find out how much each movie made.\n'
    "frozen_box_office = search('box office frozen')\n"
    "titanic_box_office = search('box office titanic')\n"
    "print(f'Frozen: {frozen_box_office}, Titanic: {titanic_box_office}')",
    result='The python code above raises an exception:\n'
    "SyntaxError - Code not supported by this sandbox (type=Call)): search('box office "
    "frozen') (parsed as: <ast.Call object at 0x7f8f086c38e0>)\n"
    'Rewrite the python code to eliminate the exception.\n',
    execution_status=<ExecutionStatus.EXECUTION_ERROR: 'EXECUTION_ERROR'>),
   
    PythonPlanningStep(is_finished=False,
    code='# First we need to find out how much each movie made.\n'
    "frozen_box_office = Search('box office frozen')\n"
    "titanic_box_office = Search('box office titanic')\n"
    "print(f'Frozen: {frozen_box_office}, Titanic: {titanic_box_office}')",
    result='Frozen: $1.280 billion, Titanic: worldwide theatrical total = $2.264 billion\n',
    execution_status=<ExecutionStatus.SUCCESS: 'SUCCESS'>),

    PythonPlanningStep(is_finished=False,
    code='# Now we extract the numbers.\n'
    'num1 = firstnumber(frozen_box_office)\n'
    'num2 = firstnumber(titanic_box_office)\n'
    '# And we compare them.\n'
    'print(num1 - num2)',
    result='-0.9839999999999998\n',
    execution_status=<ExecutionStatus.SUCCESS: 'SUCCESS'>),

    PythonPlanningStep(is_finished=True,
    code='# We can now give the answer and exit.\n'
    "print('Titanic had a larger box office than Frozen.')\n"
    \'exit()',
    result='Titanic had a larger box office than Frozen.\n',
    execution_status=<ExecutionStatus.SUCCESS: 'SUCCESS'>)])
"""

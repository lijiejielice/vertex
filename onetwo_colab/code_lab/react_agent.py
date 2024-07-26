from onetwo import ot
from onetwo.agents import react
from onetwo.core import results
from onetwo.stdlib.tool_use import python_tool_use
from tools import python_tool, search_tool, finish_tool
import pprint

# ReAct Model: combine reasoning (reasoning traces help the model induce, track, and update action plans as well as handle exceptions)
#  + action (interact with external resources) https://arxiv.org/abs/2210.03629

# In this strategy, we present the LLM with a list of tool descriptions with invocation examples,
# and then iteratively prompt the LLM to output a sequence of steps, each of which consists of
# a "thought", an "action" and an "observation".
# The "thought" and "action" are output by the LLM directly.
#
# At each step, we programmatically parse the LLM-generated "action" string,
# perform the corresponding tool call, and then use the result of that tool call as
# the "observation" that is included in the LLM prompt in the next step.

# You can specify your API key either here or as an environment variable.


react_agent = react.ReActAgent(
    exemplars=react.REACT_FEWSHOTS,
    environment_config=python_tool_use.PythonToolUseEnvironmentConfig(
        tools=[python_tool, search_tool, finish_tool],
    ),
    max_steps=10,
    stop_prefix='')


def react_example_with_tracing():
    question = 'What is the total population of Tuebingen and Zuerich?'
    answer, trace = ot.run(react_agent(inputs=question), enable_tracing=True)
    pprint.pprint(results.format_result(trace, color=True))


def react_example_with_inspecting():
    question = 'What is the total population of Tuebingen and Zuerich?'
    answer, final_state = ot.run(react_agent(
        inputs=question, return_final_state=True))
    answer
    pprint.pprint(final_state, width=140)

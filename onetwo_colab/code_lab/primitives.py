from onetwo import ot
from onetwo.builtins import composables, llm
from onetwo.core import content


def basic_executable():
    e = llm.generate_text(
        'Three not so well known cities in France are',
        max_tokens=20,
    )
    print("====Print generate_text Executable====")
    print("Generated text from 'Three not so well known cities in France are':", ot.run(e))

    messages = [
        content.Message(
            role=content.PredefinedRole.USER,
            content=(
                'Pretend that you are Albert Einstein in 1911.\n'
                'Hi, my name is Peter. Who are you?'
            ),
        ),
        content.Message(
            role=content.PredefinedRole.MODEL,
            content='Nice to meet you, Peter. My name is Albert.',
        ),
        content.Message(
            role=content.PredefinedRole.USER,
            content='Tell me more about yourself. Do you have a family and what is your job like?',
        ),
    ]
    e = llm.chat(messages, max_tokens=20)
    print("====Print chat Executable - provided chat history====")
    print(ot.run(e))

    # Issue a generate_text() request.
    e = llm.instruct(
        'Write a 4 line poem about the Swiss Alps.', max_tokens=30)
    print("====Print instruct Executable - model needs to follow instructions====")
    print(ot.run(e))


def chaining_executable():
    result1 = ot.run(
        llm.generate_text(
            'Q: What is the southernmost city in France? A:', max_tokens=20
        )
    )
    result2 = ot.run(
        llm.generate_text(
            f'Q: Who is the mayor of {result1}? A:', max_tokens=20)
    )
    print("====Print Chaining Executable====")
    print(result1)
    print(result2)


@ot.make_executable
async def f() -> str:
    result1 = await llm.generate_text(
        'Q: What is the southernmost city in France? A:',
        max_tokens=20,
    )
    print('Intermediate result:', result1)
    result2 = await llm.generate_text(
        f'Q: Who is the mayor of {result1}? A:',
        max_tokens=20,
    )
    return result2


def make_executable_example():
    print("====Print make_executable Executable====")
    result = ot.run(f())
    print(result)


def template_example():
    print("====Print template Executable====")
    template = composables.j("""\
    What is the southernmost city in France? {{ generate_text(max_tokens=20) }}
    Who is its mayor? {{ generate_text(max_tokens=20) }}
    """)
    result = ot.run(template)
    print(result)


def prompt_variable_example1():
    print("========Print Prompt Vairable Executable1========")
    question = 'France'
    prompt1 = f'Q: What is the capital of {question}?\nA:'
    res1 = ot.run(llm.generate_text(
        prompt1, max_tokens=10, stop=['Q:', '\n\n']))
    print(res1)
    prompt2 = f'Q: Who is the mayor of {res1}?\nA:'
    res2 = ot.run(llm.generate_text(
        prompt2, max_tokens=10, stop=['Q:', '\n\n']))
    print(res2)


# @ot.make_executable
@ot.make_executable
async def capital_mayor(country: str) -> str:
    prompt = f'Q: What is the capital of {country}?\nA:'
    res = await llm.generate_text(prompt, max_tokens=10, stop=['Q:', '\n\n'])
    prompt2 = f'Q: Who is the mayor of {res}?\nA:'
    return await llm.generate_text(prompt2, max_tokens=10, stop=['Q:', '\n\n'])


def prompt_variable_example():
    print("========Print Prompt Vairable Executable2========")
    print(ot.run(capital_mayor('France')))


# composables.store
def composables_store_executable():
    print("========Print Composible Store Example ========")
    e = (
        composables.f('Q: What is the capital of {question}?\nA:') +
        composables.store('city', composables.generate_text(max_tokens=10, stop=['Q:', '\n\n'])) +
        composables.f('\nQ: Who is the mayor of {city}?\nA:') +
        composables.store('mayor', composables.generate_text(
            max_tokens=10, stop=['Q:', '\n\n']))
    )
    res = ot.run(e(question='France'))
    print(res)
    print(e['city'], e['mayor'])


# -------------- Manual Evaluation --------------------
# Golden dataset to evaluate our prompting strategy.
dataset = [
    {'question': 'There are 100 people in a room. 55 are women and 70 are married. If 30 of the women are married, how many unmarried men are there?', 'answer': '15'},
    {'question': 'A farmer has 12 sheep and 6 cows. How many more sheep than cows does he have?', 'answer': '6'},
    {'question': 'A train travels 240 miles in 3 hours. What is its average speed in miles per hour?', 'answer': '80'},
    {'question': 'A rectangular garden is 12 meters long and 8 meters wide. What is its perimeter?', 'answer': '40'},
    {'question': 'If x + y = 10 and x - y = 2, what is the value of x?', 'answer': '6'},
    {'question': 'A store sells apples for $0.50 each and oranges for $0.75 each. If I buy 5 apples and 3 oranges, how much will I spend?', 'answer': '4.75'},
    {'question': 'A circle has a radius of 5 cm. What is its circumference in centimeters?', 'answer': '10*pi'},
    {'question': 'A cube has a volume of 27 cubic feet. What is the length of one side of the cube in feet?', 'answer': '3'},
    {'question': 'If 2^x = 16, what is the value of x?', 'answer': '4'},
    {'question': 'What is the sum of the first 10 positive odd numbers?', 'answer': '100'}
]


# Define a simple metric function that checks whether the correct answer is part
# of the model output.
def metric_fn(answer, example):
    correct = str(example['answer']) in answer
    extra_info = {}
    if not correct:
        index = hash(example['question'])
        extra_info = {index: {
            'question': example['question'][0:30] + '...',
            'golden': example['answer'],
            'answer': answer,
        }}
    return float(correct), extra_info


def llm_critic_evaluation_examplemanual_evaluation_example():
    print("========Print Manual Evaluation Example========")
    # We run the evaluation on the dataset.
    time_elapsed, avg_metric, aggr_info = ot.evaluate(
        strategy=strategy,
        examples=dataset,
        critic=metric_fn,
    )
    # We can look at the cases where the model got a wrong answer.
    for v in aggr_info.values():
        print(v)


# -------------- LLM Critic Evaluation --------------------
# We create another dataset of questions that do not necessarily have a fixed
# definite answer.
dataset = [
    {
        'question': 'Who developed the TCP/IP protocol?',
        'golden_answer': 'Bob Kahn and Vint Cerf',
    },
    {
        'question': 'What date was the declaration of independence signed (not written)?',
        'golden_answer': '8/2/1776'
    },
    {
        'question': 'How big is the area of a triangle with base a and height h',
        'golden_answer': '1/2 * ah',
    },
    {
        'question': 'Which countried border Guatemala?',
        'golden_answer': 'Mexico, Belize, Honduras, El Salvador',
    },
    {
        'question': 'How do vaccines work?',
        'golden_answer': (
            'Vaccines contain weakened or inactive pathogens that stimulate the'
            ' immune system to produce antibodies, which then protect against'
            ' future infections from the same pathogen.'
        ),
    },
]


# Define a simple strategy that passes the question directly to the model.
@ot.make_executable
async def strategy(question, **_):
    answer = await llm.generate_text(
        prompt=f'Question: {question} ?\nAnswer (concise):',
        stop=['Question:'],
        max_tokens=500,
    )
    return answer.strip()


def llm_critic_evaluation_example():
    print("========Print LLM Critic Evaluation Example========")
    # We run the evaluation on the dataset using an LLM critic.
    time_elapsed, total_votes, aggr_info = ot.evaluate(
        strategy=strategy,
        critic=ot.naive_evaluation_critic,
        examples=dataset,
    )

from dotenv import load_dotenv
from onetwo.backends import gemini_api
import os
# Module relative import, adding dot to the path
from .python_plan import python_planning_example_with_inspecting
# from react_agent import react_example_with_inspecting


load_dotenv()


def register_llm_backend():
    api_key = os.environ["API_KEY"]
    if not api_key and 'GOOGLE_API_KEY' not in os.environ:
        raise ValueError(
            'The api key must be specified either here or in the environment.')

    cache_filename = '/tmp/gemini_cache.txt'
    # Create the backend that we selected above and provide a cache filename.
    backend = gemini_api.GeminiAPI(
        api_key=api_key,
        temperature=0.0,
        cache_filename=cache_filename,
    )
    backend.register()
    print('Gemini API backend registered.')

    if os.path.isfile(cache_filename):
        print(f'Loading cache from {cache_filename}')
        backend.load_cache()
    else:
        print(f'Cache file does not exist: {cache_filename}')

    # You can then save the model cache at any time.
    backend.save_cache(overwrite=True)


def main():
    register_llm_backend()
    # react_example_with_inspecting()
    python_planning_example_with_inspecting()


if __name__ == '__main__':
    main()

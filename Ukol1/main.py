import json
from openai import OpenAI

from webwork import extract_seznam_titles


# This is a 1-day API key - will be invalid before publication of the code
openrouter_api_key = '...'
# model='google/gemma-4-31b-it:free'
model='openrouter/free'
max_iterations = 5    # avoid infinite cycle


client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=openrouter_api_key,
)

tools = [{
    'type': 'function',
    'function': {
                'name': 'extract_seznam_titles',
                'description': 'Get titles of articles on www.seznam.cz - returns article titles about politics, sport, celebrities, etc.',
                'parameters': {'type': 'object', 'properties': {}, 'required': [], 'additionalProperties': False},
                'strict': True,
                }
    }]

function_call_dict = {'extract_seznam_titles': extract_seznam_titles}


def run(prompt: str) -> str:
    messages = [{'role': 'system', 'content': 'You are an assistant. Be kind and helpful.'},
                {'role': 'user', 'content': prompt}]
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        extra_body={"reasoning": {"enabled": True}}
        )

    response = response.choices[0].message

    iteration = 0

    while (response.tool_calls is not None) and (len(response.tool_calls) > 0):

        print(response.content)
        tool_calls_out = [{'id': x.id, 'type': 'function', 'function': {'name': x.function.name, 'arguments': x.function.arguments}} for x in response.tool_calls]
        if response.content is not None:
            messages.append({'role': 'assistant', 'content': response.content, 'tool_calls': tool_calls_out})
        else:
            messages.append({'role': 'assistant', 'tool_calls': tool_calls_out})

        for call in response.tool_calls:
            function_to_call = call.function.name
            arguments = json.loads(call.function.arguments or "{}")
            tool_call_id = call.id

            res = function_call_dict[function_to_call](**arguments)
            res_str = ', '.join([f'"{x}"' for x in res])
            print(res_str)

            messages.append({'role': 'tool', 'tool_call_id': tool_call_id, 'content': res_str})

        iteration += 1
        if iteration >= max_iterations:
            raise Exception(f'Max number of iterations {max_iterations} exceeded')

        response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                extra_body={"reasoning": {"enabled": True}}
                )
        response = response.choices[0].message

    print(response.content)
    return response.content
    

if __name__ == '__main__':
    # run('Zjisti, co se aktuálně děje ve světě. Ignoruj bulvár a kroniku kuriózních úmrtí. Na sledování sportu nemám čas.')
    run('Kolik je 2 + 2?')

# PÁR PERLIČEK OD MODELU, KTERÝ ZROVNA NEXCELOVAL, ZATO BYL ZDARMA:
# **Vojenský a globální**
# *   NATO v extraleleze odmítá Antoše a vyhýbá Zábranského k akci.
# **Sociální a zdravotní**
# *   Data o rakovině, ktoré stále víc lidí pod 50 let má, i když kouří ani nealkoholuje.
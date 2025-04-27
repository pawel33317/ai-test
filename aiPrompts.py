from datetime import date

def load_and_replace_placeholders(file_path, placeholders):
    """Load a template file and replace placeholders with provided values."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    for placeholder, value in placeholders.items():
        content = content.replace(f'{{{{{placeholder}}}}}', value)
    return content

def get_do_you_know_the_answer_prompt(question):
    return load_and_replace_placeholders(
        'ai-prompts/do_you_know_the_answer.txt',
        {'current_date': date.today().strftime('%d.%m.%Y'), 'question': question}
    )

def get_is_the_answer_in_text_prompt(question, information):
    return load_and_replace_placeholders(
        'ai-prompts/is_the_answer_in_text.txt',
        {'question': question, 'information': information}
    )

def get_system_prompt(userPrompt=None):
    content = load_and_replace_placeholders(
        'ai-prompts/system_prompt.txt',
        {'date': date.today().strftime('%d.%m.%Y')}
    )
    if userPrompt:
        content += f"\n{userPrompt}"
    return content

def get_answer_with_internet_data_prompt(question):
    return load_and_replace_placeholders(
        'ai-prompts/answer_with_internet_data.txt',
        {'question': question}
    )

def get_data_from_internet_prompt(data):
    return load_and_replace_placeholders(
        'ai-prompts/data_from_internet.txt',
        {'data': data, 'current_date': date.today().strftime('%d.%m.%Y')}
    )

def get_history_prevous_question_prompt(question):
    return load_and_replace_placeholders(
        'ai-prompts/history_prevous_question.txt',
        {'question': question}
    )

def get_history_prevous_answer_prompt(answer):
    return load_and_replace_placeholders(
        'ai-prompts/history_prevous_answer.txt',
        {'answer': answer}
    )

def get_question_to_search_engine_prompt(question):
    return load_and_replace_placeholders(
        'ai-prompts/question_to_search_engine.txt',
        {'question': question}
    )

def get_recognize_language(data):
    return load_and_replace_placeholders(
        'ai-prompts/recognize_language.txt',
        {'data': data}
    )

def get_use_language_prompt(language):
    return load_and_replace_placeholders(
        'ai-prompts/use_language.txt',
        {'language': language}
    )
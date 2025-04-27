from datetime import date

def get_do_you_know_the_answer_prompt(question):
    file_path = 'ai-prompts/do_you_know_the_answer.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    content = content.replace('{{current_date}}', date.today().strftime('%d.%m.%Y'))
    content = content.replace('{{question}}', question)
    return content

def get_is_the_answer_in_text_prompt(question, information):
    file_path = 'ai-prompts/is_the_answer_in_text.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    content = content.replace('{{information}}', information)
    content = content.replace('{{question}}', question)
    return content

def get_system_prompt(userPrompt=None):
    file_path = 'ai-prompts/system_prompt.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    content = content.replace('{{date}}', date.today().strftime('%d.%m.%Y'))
    if userPrompt:
        content = content + "\n" + userPrompt
    return content

def get_answer_with_internet_data_prompt(question):
    file_path = 'ai-prompts/answer_with_internet_data.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.replace('{{question}}', question)
    return content

def get_data_from_internet_prompt(data):
    file_path = 'ai-prompts/data_from_internet.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    content = content.replace('{{data}}', data)
    content = content.replace('{{current_date}}', date.today().strftime('%d.%m.%Y'))
    return content

def get_history_prevous_question_prompt(question):
    file_path = 'ai-prompts/history_prevous_question.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.replace('{{question}}', question)
    return content

def get_history_prevous_answer_prompt(answer):
    file_path = 'ai-prompts/history_prevous_answer.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.replace('{{answer}}', answer)
    return content

def get_question_to_search_engine_prompt(question):
    file_path = 'ai-prompts/question_to_search_engine.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.replace('{{question}}', question)
    return content

def get_recognize_language(data):
    file_path = 'ai-prompts/recognize_language.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.replace('{{data}}', data)
    return content

def get_use_language_prompt(language):
    file_path = 'ai-prompts/use_language.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.replace('{{language}}', language)
    return content
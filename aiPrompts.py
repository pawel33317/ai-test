from datetime import date

def get_do_you_know_the_answer_prompt(question):
    file_path = 'ai-prompts/do_you_know_the_answer.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace placeholders
    content = content.replace('{{current_date}}', date.today().strftime('%d.%m.%Y'))
    content = content.replace('{{question}}', question)
    
    return content

def get_is_the_answer_in_text(question, information):
    file_path = 'ai-prompts/is_the_answer_in_text.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace placeholders
    content = content.replace('{{information}}', information)
    content = content.replace('{{question}}', question)
    
    return content

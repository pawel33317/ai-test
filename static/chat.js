// DOM Elements
const UI = {
    loader: document.getElementById('status-loader'),
    statusContent: document.getElementById('status-content'),
    form: document.getElementById('chat-form'),
    responsesContainer: document.querySelector('.responses-container'),
    submitButton: document.getElementById('chat-form').querySelector('button'),
    systemPrompt: document.getElementById('system-prompt'),
    applySystemPromptButton: document.getElementById('apply-system-prompt'),
    aiModel: document.getElementById('ai-model'),
    applyAiModel: document.getElementById('apply-ai-model'),
    clearConversation: document.getElementById('clear-conversation'),
    webSearchForm: document.getElementById('web-search-form')
};

// Status handling
const StatusManager = {
    startSpinner() {
        UI.loader.classList.add('spinner');
        UI.statusContent.innerHTML = "🕒";
    },
    stopSpinner() {
        UI.loader.classList.remove('spinner');
        UI.statusContent.innerHTML = "🆗";
    }
};

// Message handling
const MessageManager = {
    createMessageElement(className, text) {
        const div = document.createElement('div');
        div.className = `response ${className}`;
        div.innerHTML = text;
        UI.responsesContainer.appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
        return div;
    },
    
    async streamResponse(response) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let searchDivCreated = false;
        let responseDivCreated = false;
        let searchInfoDiv = null;
        let responseDiv = null;

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });

            if (chunk.startsWith('meta')) {
                if (!searchDivCreated) {
                    searchDivCreated = true;
                    searchInfoDiv = MessageManager.createMessageElement('search-message', '');
                }
                searchInfoDiv.innerHTML += chunk.replace(/^meta: /gm, ''); // Fixed: Use `innerHTML` instead of treating as a string
                searchInfoDiv.scrollIntoView({ behavior: 'smooth' });
            } else {
                if (!responseDivCreated) {
                    responseDivCreated = true;
                    responseDiv = MessageManager.createMessageElement('chat-message', '');
                }
                responseDiv.textContent += chunk.replace(/^data: /gm, '');
                responseDiv.scrollIntoView({ behavior: 'smooth' });
            }
        }
    }
};

// API calls
const ApiService = {
    async sendChatMessage(formData) {
        return await fetch('/chat-stream', {
            method: 'POST',
            body: formData
        });
    },

    async updateSystemPrompt(prompt) {
        return await fetch('/update-system-prompt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ system_prompt: prompt })
        });
    },

    async updateAiModel(model) {
        return await fetch('/update-ai-model', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ai_model: model })
        });
    },

    async updateWebSearchSettings(settings) {
        return await fetch('/update-web-search-settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
    }
};

// Event handlers
async function handleChatSubmit(e) {
    StatusManager.startSpinner();
    e.preventDefault();

    const userMessages = Array.from(document.querySelectorAll('.response.user-message')).map(div => div.textContent);
    const chatMessages = Array.from(document.querySelectorAll('.response.chat-message')).map(div => div.textContent);

    const userPrompt = UI.form.prompt.value;
    MessageManager.createMessageElement('user-message', userPrompt);
    
    UI.submitButton.disabled = true;

    const formData = new FormData(UI.form);
    // Check if chat history should be included
    if (document.getElementById('use-chat-history').checked) {
        formData.append('user_questions', JSON.stringify(userMessages));
        formData.append('user_responses', JSON.stringify(chatMessages));
    }

    try {
        const response = await ApiService.sendChatMessage(formData);
        await MessageManager.streamResponse(response);
    } catch (err) {
        StatusManager.setError('Failed to send chat message.');
    } finally {
        UI.submitButton.disabled = false;
        UI.form.reset();
        StatusManager.stopSpinner();
    }
}

async function handleSystemPromptUpdate() {
    MessageManager.createMessageElement('user-settings-request', '🔧 System prompt update requested');
    const responseDiv = MessageManager.createMessageElement('system-message', 'Updating system prompt...');
    
    const response = await ApiService.updateSystemPrompt(UI.systemPrompt.value);
    
    if (response.ok) {
        responseDiv.innerHTML = `System prompt updated successfully! New prompt:\n<b>${UI.systemPrompt.value}</b>`;
    } else {
        responseDiv.className = 'response system-error';
        responseDiv.textContent = 'Failed to update system prompt';
    }
}

async function handleWebSearchUpdate(e) {
    e.preventDefault(); // Prevent form submission
    StatusManager.startSpinner();

    const status = document.getElementById('web-search-status').value;
    const pages = document.getElementById('web-search-pages').value;
    MessageManager.createMessageElement('user-settings-request', '🔧 Web search settings update requested');
    const responseDiv = MessageManager.createMessageElement('system-message', 'Updating web search settings...');

    try {
        const response = await ApiService.updateWebSearchSettings({ status, pages });
        if (response.ok) {
            responseDiv.innerHTML = `Web search settings updated successfully! New settings:<br>Status: <b>${status}</b>, Pages: <b>${pages}</b>`;
        } else {
            throw new Error('Failed to update Web search settings');
        }
    } catch (err) {
        responseDiv.className = 'response system-error';
        responseDiv.textContent = err.message;
    } finally {
        StatusManager.stopSpinner();
    }
}

async function handleAiModelUpdate() {
    MessageManager.createMessageElement('user-settings-request', '🔧 AI model update requested');
    const responseDiv = MessageManager.createMessageElement('system-message', 'Updating AI model...');
    
    const response = await ApiService.updateAiModel(UI.aiModel.value);
    
    if (response.ok) {
        responseDiv.innerHTML = `System prompt updated successfully! New prompt:\n<b>${UI.aiModel.value}</b>`;
    } else {
        responseDiv.className = 'response system-error';
        responseDiv.textContent = 'Failed to update AI model';
    }
}

// Event listeners
UI.form.addEventListener('submit', handleChatSubmit);
UI.clearConversation.addEventListener('click', () => UI.responsesContainer.innerHTML = '');
UI.applySystemPromptButton.addEventListener('click', handleSystemPromptUpdate);
UI.applyAiModel.addEventListener('click', handleAiModelUpdate);
UI.webSearchForm.addEventListener('submit', handleWebSearchUpdate);

document.getElementById('prompt').addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault(); // Zapobiega dodaniu nowej linii
        document.querySelector('#chat-form button[type="submit"]').click(); // Kliknij przycisk "Send"
    }
});
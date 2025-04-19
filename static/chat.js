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
    clearConversation: document.getElementById('clear-conversation')
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
        div.textContent = text;
        UI.responsesContainer.appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
        return div;
    },
    
    async streamResponse(responseDiv, response) {
        responseDiv.textContent = '';
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, { stream: true });
            responseDiv.textContent += chunk.replace(/^data: /gm, '');
            responseDiv.scrollIntoView({ behavior: 'smooth' });
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
    }
};

// Event handlers
async function handleChatSubmit(e) {
    StatusManager.startSpinner();
    e.preventDefault();
    
    const userPrompt = UI.form.prompt.value;
    MessageManager.createMessageElement('user-message', userPrompt);
    const responseDiv = MessageManager.createMessageElement('chat-message', 'Thinking...');
    
    UI.submitButton.disabled = true;
    
    const response = await ApiService.sendChatMessage(new FormData(UI.form));
    await MessageManager.streamResponse(responseDiv, response);
    
    UI.submitButton.disabled = false;
    UI.form.reset();
    StatusManager.stopSpinner();
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
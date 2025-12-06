/**
 * Global AI Assistant - Available on all pages
 * Provides context-aware help for any learning activity
 */

(function() {
    'use strict';

    // Create floating AI button
    function createFloatingButton() {
        const button = document.createElement('button');
        button.id = 'ai-assistant-btn';
        button.innerHTML = '<i class="fas fa-robot"></i>';
        button.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #7c3aed, #2563eb);
            color: white;
            border: none;
            box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4);
            cursor: pointer;
            z-index: 9998;
            font-size: 24px;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        button.onmouseover = () => {
            button.style.transform = 'scale(1.1)';
            button.style.boxShadow = '0 6px 30px rgba(124, 58, 237, 0.6)';
        };
        
        button.onmouseout = () => {
            button.style.transform = 'scale(1)';
            button.style.boxShadow = '0 4px 20px rgba(124, 58, 237, 0.4)';
        };
        
        button.onclick = () => toggleAssistant();
        
        document.body.appendChild(button);
    }

    // Create AI chat widget
    function createChatWidget() {
        const widget = document.createElement('div');
        widget.id = 'ai-assistant-widget';
        widget.style.cssText = `
            position: fixed;
            bottom: 100px;
            right: 30px;
            width: 400px;
            max-width: calc(100vw - 60px);
            height: 600px;
            max-height: calc(100vh - 140px);
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 50px rgba(0, 0, 0, 0.3);
            z-index: 9999;
            display: none;
            flex-direction: column;
            overflow: hidden;
        `;

        widget.innerHTML = `
            <div style="background: linear-gradient(135deg, #7c3aed, #2563eb); color: white; padding: 20px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0; font-size: 18px; font-weight: bold;">AI Arabic Assistant</h3>
                    <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.9;">Ask me anything about this page</p>
                </div>
                <button id="ai-close-btn" style="background: rgba(255,255,255,0.2); border: none; color: white; width: 30px; height: 30px; border-radius: 50%; cursor: pointer; font-size: 18px;">×</button>
            </div>
            
            <div id="ai-status-bar" style="background: #f3f4f6; padding: 10px 20px; border-bottom: 1px solid #e5e7eb; font-size: 13px; color: #6b7280; display: none;">
                <i class="fas fa-spinner fa-spin"></i> Initializing AI...
            </div>
            
            <div id="ai-init-screen" style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 30px; text-align: center;">
                <i class="fas fa-robot" style="font-size: 60px; color: #7c3aed; margin-bottom: 20px;"></i>
                <h4 style="margin: 0 0 10px 0; font-size: 20px; color: #1f2937;">AI Assistant Ready</h4>
                <p style="color: #6b7280; margin-bottom: 20px; font-size: 14px;">Click below to activate your AI tutor. First time will download ~1GB model.</p>
                <button id="ai-init-btn" style="background: linear-gradient(135deg, #7c3aed, #2563eb); color: white; border: none; padding: 12px 24px; border-radius: 10px; cursor: pointer; font-size: 16px; font-weight: bold;">
                    <i class="fas fa-bolt"></i> Activate AI
                </button>
                <p style="margin-top: 15px; font-size: 11px; color: #9ca3af;">
                    <i class="fas fa-lock"></i> 100% Private • Runs in Browser
                </p>
            </div>
            
            <div id="ai-chat-interface" style="flex: 1; display: none; flex-direction: column;">
                <div id="ai-messages" style="flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px;">
                    <div style="background: #f3f4f6; padding: 12px; border-radius: 12px; font-size: 14px; color: #1f2937;">
                        <i class="fas fa-robot" style="color: #7c3aed; margin-right: 8px;"></i>
                        Hello! I can help you with questions about this page, Arabic grammar, vocabulary, or anything else you're learning.
                    </div>
                </div>
                
                <div style="padding: 15px; border-top: 1px solid #e5e7eb; background: #f9fafb;">
                    <div style="display: flex; gap: 10px;">
                        <input 
                            type="text" 
                            id="ai-input" 
                            placeholder="Ask about this page..."
                            style="flex: 1; padding: 12px; border: 2px solid #e5e7eb; border-radius: 10px; font-size: 14px; outline: none;"
                        >
                        <button 
                            id="ai-send-btn" 
                            style="background: linear-gradient(135deg, #7c3aed, #2563eb); color: white; border: none; padding: 12px 20px; border-radius: 10px; cursor: pointer; font-size: 16px;"
                        >
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                    <div style="margin-top: 8px; display: flex; gap: 5px; flex-wrap: wrap;">
                        <button class="ai-quick-btn" data-prompt="Explain this in simple terms">📝 Simplify</button>
                        <button class="ai-quick-btn" data-prompt="Give me examples">💡 Examples</button>
                        <button class="ai-quick-btn" data-prompt="How do I practice this?">🎯 Practice</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(widget);
        
        // Setup event listeners
        document.getElementById('ai-close-btn').onclick = () => toggleAssistant();
        document.getElementById('ai-init-btn').onclick = () => initializeAI();
        document.getElementById('ai-send-btn').onclick = () => sendMessage();
        document.getElementById('ai-input').onkeypress = (e) => {
            if (e.key === 'Enter') sendMessage();
        };
        
        // Quick buttons
        document.querySelectorAll('.ai-quick-btn').forEach(btn => {
            btn.style.cssText = 'background: #e5e7eb; border: none; padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer;';
            btn.onclick = () => sendQuickMessage(btn.dataset.prompt);
        });
    }

    function toggleAssistant() {
        const widget = document.getElementById('ai-assistant-widget');
        if (widget.style.display === 'none' || !widget.style.display) {
            widget.style.display = 'flex';
        } else {
            widget.style.display = 'none';
        }
    }

    let engine = null;
    let conversationHistory = [];
    
    async function initializeAI() {
        const initScreen = document.getElementById('ai-init-screen');
        const chatInterface = document.getElementById('ai-chat-interface');
        const statusBar = document.getElementById('ai-status-bar');
        const initBtn = document.getElementById('ai-init-btn');
        
        initBtn.disabled = true;
        initBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Initializing...';
        statusBar.style.display = 'block';
        
        try {
            // Import WebLLM
            const webllm = await import('https://esm.run/@mlc-ai/web-llm');
            
            // Progress callback
            const progressCallback = (progress) => {
                const percent = Math.round(progress.progress * 100);
                statusBar.innerHTML = `<i class="fas fa-download"></i> Loading model: ${percent}% - ${progress.text || ''}`;
            };
            
            // Create engine
            engine = await webllm.CreateMLCEngine(
                "Qwen2-1.5B-Instruct-q4f16_1-MLC",
                { initProgressCallback: progressCallback }
            );
            
            // Get page context
            const pageTitle = document.title;
            const pageContent = document.body.innerText.substring(0, 1000); // First 1000 chars
            
            // Initialize with context
            conversationHistory = [{
                role: "system",
                content: `You are an AI Arabic tutor helping a student. They are currently on a page titled "${pageTitle}". Provide helpful, concise answers about Arabic learning. Keep responses short and practical.`
            }];
            
            // Show chat interface
            initScreen.style.display = 'none';
            chatInterface.style.display = 'flex';
            statusBar.style.display = 'none';
            
        } catch (error) {
            console.error('AI initialization failed:', error);
            statusBar.innerHTML = '<i class="fas fa-exclamation-circle"></i> Error: ' + error.message;
            initBtn.disabled = false;
            initBtn.innerHTML = '<i class="fas fa-redo"></i> Retry';
        }
    }
    
    async function sendMessage() {
        const input = document.getElementById('ai-input');
        const message = input.value.trim();
        
        if (!message || !engine) return;
        
        input.value = '';
        input.disabled = true;
        
        addMessage(message, 'user');
        
        conversationHistory.push({ role: "user", content: message });
        
        const loadingId = addLoadingMessage();
        
        try {
            const chunks = await engine.chat.completions.create({
                messages: conversationHistory,
                temperature: 0.7,
                max_tokens: 400,
                stream: true,
            });
            
            let fullResponse = "";
            removeMessage(loadingId);
            const responseId = addMessage("", 'assistant');
            
            for await (const chunk of chunks) {
                const content = chunk.choices[0]?.delta?.content || "";
                fullResponse += content;
                updateMessage(responseId, fullResponse);
            }
            
            conversationHistory.push({ role: "assistant", content: fullResponse });
            
        } catch (error) {
            removeMessage(loadingId);
            addMessage("Sorry, I encountered an error. Please try again.", 'assistant');
        }
        
        input.disabled = false;
        input.focus();
    }
    
    function sendQuickMessage(prompt) {
        document.getElementById('ai-input').value = prompt;
        sendMessage();
    }
    
    let messageCounter = 0;
    
    function addMessage(content, role) {
        const messagesDiv = document.getElementById('ai-messages');
        const msgId = 'msg-' + (++messageCounter);
        
        const msgDiv = document.createElement('div');
        msgDiv.id = msgId;
        msgDiv.style.cssText = role === 'user' 
            ? 'background: linear-gradient(135deg, #7c3aed, #2563eb); color: white; padding: 12px; border-radius: 12px; font-size: 14px; align-self: flex-end; max-width: 80%;'
            : 'background: #f3f4f6; padding: 12px; border-radius: 12px; font-size: 14px; color: #1f2937; max-width: 80%;';
        
        msgDiv.textContent = content;
        messagesDiv.appendChild(msgDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        
        return msgId;
    }
    
    function updateMessage(msgId, content) {
        const msgDiv = document.getElementById(msgId);
        if (msgDiv) {
            msgDiv.textContent = content;
            document.getElementById('ai-messages').scrollTop = document.getElementById('ai-messages').scrollHeight;
        }
    }
    
    function addLoadingMessage() {
        const messagesDiv = document.getElementById('ai-messages');
        const loadingId = 'loading-' + Date.now();
        
        const loadingDiv = document.createElement('div');
        loadingDiv.id = loadingId;
        loadingDiv.style.cssText = 'background: #f3f4f6; padding: 12px; border-radius: 12px; font-size: 14px; color: #6b7280;';
        loadingDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Thinking...';
        
        messagesDiv.appendChild(loadingDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        
        return loadingId;
    }
    
    function removeMessage(msgId) {
        const msg = document.getElementById(msgId);
        if (msg) msg.remove();
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            createFloatingButton();
            createChatWidget();
        });
    } else {
        createFloatingButton();
        createChatWidget();
    }
})();

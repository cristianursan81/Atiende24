/**
 * ChatGenie Embeddable Widget - LinkEvolution Edition
 * Advanced AI Chat Assistant for Business Transformation Services
 * Version: 2.0.0 
 */

(function () {
  'use strict';

  const config = window.ChatGenieConfig || window.Atiende24Config;

  if (!config) {
    console.error("ChatGenie: Configuration not found. Please set window.ChatGenieConfig");
    return;
  }

  const { 
    businessId, 
    apiKey, 
    apiBaseUrl = "http://localhost:8000",
    branding = {},
    template = "general",
    language = "es-ES",
    quickActions = [],
    greeting = "¡Hola! ¿En qué puedo ayudarte?",
    position = "bottom-right",
    theme = "auto",
    enableVoice = true,
    enableDragging = true,
    showQuickActions = true,
    leadCapture = {},
    businessHours = {}
  } = config;

  // Widget state
  let conversationId = null;
  let sessionId = generateSessionId();
  let isLoading = false;
  let isMinimized = true;
  let messageHistory = JSON.parse(localStorage.getItem(`chatgenie-history-${businessId}`) || '[]');
  let recognition = null;
  let synthesis = window.speechSynthesis;
  let isDragging = false;
  let dragOffset = { x: 0, y: 0 };
  let isVoiceMode = false;
  let currentTheme = theme === 'auto' ? detectSystemTheme() : theme;
  let unreadCount = 0;
  let isBusinessHours = checkBusinessHours();

  // Initialize speech recognition if available
  if (enableVoice && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = language;
  }

  // Create chat session on initialization
  createChatSession();

  // Create main container
  const container = document.createElement("div");
  container.id = "chatgenie-container";
  container.style.cssText = `
    position: fixed;
    ${getPositionStyles(position)}
    z-index: 2147483647;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --primary-color: ${branding.primaryColor || '#667eea'};
    --secondary-color: ${branding.secondaryColor || '#764ba2'};
    --accent-color: ${branding.accentColor || '#FFD700'};
    --text-color: ${currentTheme === 'dark' ? '#ffffff' : '#333333'};
    --bg-color: ${currentTheme === 'dark' ? '#1a1a1a' : '#ffffff'};
    --border-color: ${currentTheme === 'dark' ? '#333333' : '#e1e5e9'};
  `;

  // Create floating button with notification badge
  const buttonContainer = document.createElement("div");
  buttonContainer.style.cssText = `
    position: relative;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  `;

  const button = document.createElement("button");
  button.innerHTML = "🧞‍♂️";
  button.title = `Conectar con ${branding.businessName || 'ChatGenie'}`;
  button.style.cssText = `
    width: 64px;
    height: 64px;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    font-size: 28px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  `;

  // Notification badge
  const badge = document.createElement("div");
  badge.style.cssText = `
    position: absolute;
    top: -8px;
    right: -8px;
    background: #ff4444;
    color: white;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    font-size: 12px;
    font-weight: bold;
    display: none;
    align-items: center;
    justify-content: center;
    animation: pulse 2s infinite;
  `;
  button.appendChild(badge);

  // Create chat window
  const chatWindow = document.createElement("div");
  chatWindow.style.cssText = `
    position: absolute;
    ${position.includes('right') ? 'right: 0;' : 'left: 0;'}
    ${position.includes('bottom') ? 'bottom: 80px;' : 'top: 80px;'}
    width: 380px;
    height: 600px;
    max-height: 80vh;
    max-width: 90vw;
    background: var(--bg-color);
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.2);
    display: none;
    flex-direction: column;
    overflow: hidden;
    border: 1px solid var(--border-color);
    backdrop-filter: blur(10px);
  `;

  // Chat header
  const header = document.createElement("div");
  header.style.cssText = `
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: ${enableDragging ? 'move' : 'default'};
  `;

  const headerInfo = document.createElement("div");
  headerInfo.style.cssText = `
    display: flex;
    align-items: center;
    gap: 12px;
  `;

  if (branding.logo) {
    const logo = document.createElement("img");
    logo.src = branding.logo;
    logo.alt = branding.businessName || 'Logo';
    logo.style.cssText = `
      width: 40px;
      height: 40px;
      border-radius: 50%;
      object-fit: cover;
    `;
    headerInfo.appendChild(logo);
  }

  const headerText = document.createElement("div");
  headerText.innerHTML = `
    <div style="font-weight: 600; font-size: 16px;">${branding.businessName || 'ChatGenie'}</div>
    <div style="font-size: 12px; opacity: 0.9;">${isBusinessHours ? '🟢 Online' : '🟡 Fuera de horario'}</div>
  `;
  headerInfo.appendChild(headerText);

  const headerButtons = document.createElement("div");
  headerButtons.style.cssText = `
    display: flex;
    gap: 8px;
  `;

  // Theme toggle button
  const themeButton = document.createElement("button");
  themeButton.innerHTML = currentTheme === 'dark' ? '☀️' : '🌙';
  themeButton.title = "Cambiar tema";
  themeButton.style.cssText = `
    background: none;
    border: none;
    color: white;
    cursor: pointer;
    font-size: 18px;
    padding: 4px;
    border-radius: 4px;
    opacity: 0.8;
    transition: opacity 0.3s;
  `;
  themeButton.onmouseover = () => themeButton.style.opacity = '1';
  themeButton.onmouseout = () => themeButton.style.opacity = '0.8';
  themeButton.onclick = toggleTheme;

  // Minimize button  
  const minimizeButton = document.createElement("button");
  minimizeButton.innerHTML = "−";
  minimizeButton.title = "Minimizar";
  minimizeButton.style.cssText = `
    background: none;
    border: none;
    color: white;
    cursor: pointer;
    font-size: 24px;
    padding: 4px 8px;
    border-radius: 4px;
    opacity: 0.8;
    transition: opacity 0.3s;
  `;
  minimizeButton.onmouseover = () => minimizeButton.style.opacity = '1';
  minimizeButton.onmouseout = () => minimizeButton.style.opacity = '0.8';
  minimizeButton.onclick = toggleChat;

  headerButtons.appendChild(themeButton);
  headerButtons.appendChild(minimizeButton);
  
  header.appendChild(headerInfo);
  header.appendChild(headerButtons);

  // Messages container
  const messagesContainer = document.createElement("div");
  messagesContainer.style.cssText = `
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    background: var(--bg-color);
  `;

  // Quick actions (only show if enabled and actions exist)
  let quickActionsContainer = null;
  if (showQuickActions && quickActions.length > 0) {
    quickActionsContainer = document.createElement("div");
    quickActionsContainer.style.cssText = `
      padding: 15px 20px;
      background: var(--bg-color);
      border-top: 1px solid var(--border-color);
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    `;

    quickActions.forEach(action => {
      const actionBtn = document.createElement("button");
      actionBtn.textContent = action.text;
      actionBtn.style.cssText = `
        background: var(--primary-color);
        color: white;
        border: none;
        padding: 8px 12px;
        border-radius: 20px;
        cursor: pointer;
        font-size: 12px;
        transition: all 0.3s;
      `;
      actionBtn.onmouseover = () => {
        actionBtn.style.transform = 'translateY(-2px)';
        actionBtn.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
      };
      actionBtn.onmouseout = () => {
        actionBtn.style.transform = 'translateY(0)';
        actionBtn.style.boxShadow = 'none';
      };
      actionBtn.onclick = () => {
        sendMessage(action.message, 'user');
        // Hide quick actions after use (optional)
        quickActionsContainer.style.display = 'none';
      };
      quickActionsContainer.appendChild(actionBtn);
    });
  }

  // Input container
  const inputContainer = document.createElement("div");
  inputContainer.style.cssText = `
    padding: 20px;
    background: var(--bg-color);
    border-top: 1px solid var(--border-color);
    display: flex;
    gap: 10px;
    align-items: flex-end;
  `;

  const messageInput = document.createElement("textarea");
  messageInput.placeholder = "Escribe tu mensaje...";
  messageInput.style.cssText = `
    flex: 1;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 12px 16px;
    resize: none;
    font-family: inherit;
    font-size: 14px;
    max-height: 80px;
    background: var(--bg-color);
    color: var(--text-color);
    transition: border-color 0.3s;
  `;
  messageInput.onfocus = () => {
    messageInput.style.borderColor = 'var(--primary-color)';
    messageInput.style.outline = 'none';
  };
  messageInput.onblur = () => {
    messageInput.style.borderColor = 'var(--border-color)';
  };

  // Auto-resize textarea
  messageInput.oninput = function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 80) + 'px';
  };

  const sendButton = document.createElement("button");
  sendButton.innerHTML = "📤";
  sendButton.title = "Enviar mensaje";
  sendButton.style.cssText = `
    background: var(--primary-color);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 16px;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.3s;
    min-width: 48px;
  `;
  sendButton.onmouseover = () => {
    sendButton.style.transform = 'translateY(-2px)';
    sendButton.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
  };
  sendButton.onmouseout = () => {
    sendButton.style.transform = 'translateY(0)';
    sendButton.style.boxShadow = 'none';
  };

  // Voice button (if enabled)
  let voiceButton = null;
  if (enableVoice && recognition) {
    voiceButton = document.createElement("button");
    voiceButton.innerHTML = "🎤";
    voiceButton.title = "Mensaje de voz";
    voiceButton.style.cssText = `
      background: var(--accent-color);
      color: white;
      border: none;
      border-radius: 12px;
      padding: 12px 16px;
      cursor: pointer;
      font-size: 16px;
      transition: all 0.3s;
      min-width: 48px;
    `;
    voiceButton.onmouseover = () => {
      voiceButton.style.transform = 'translateY(-2px)';
      voiceButton.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
    };
    voiceButton.onmouseout = () => {
      voiceButton.style.transform = 'translateY(0)';
      voiceButton.style.boxShadow = 'none';
    };
    voiceButton.onclick = toggleVoiceRecognition;
  }

  // Assemble input container
  inputContainer.appendChild(messageInput);
  if (voiceButton) inputContainer.appendChild(voiceButton);
  inputContainer.appendChild(sendButton);

  // Assemble chat window
  chatWindow.appendChild(header);
  chatWindow.appendChild(messagesContainer);
  if (quickActionsContainer) chatWindow.appendChild(quickActionsContainer);
  chatWindow.appendChild(inputContainer);

  // Assemble main container
  buttonContainer.appendChild(button);
  container.appendChild(buttonContainer);
  container.appendChild(chatWindow);

  document.body.appendChild(container);

  // Event listeners
  button.onclick = toggleChat;
  sendButton.onclick = () => sendMessage(messageInput.value.trim());
  messageInput.onkeypress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(messageInput.value.trim());
    }
  };

  // Dragging functionality
  if (enableDragging) {
    header.onmousedown = startDragging;
    document.onmousemove = drag;
    document.onmouseup = stopDragging;
  }

  // Initialize chat
  if (messageHistory.length === 0) {
    addMessage(greeting, 'bot');
  } else {
    // Restore previous conversation
    messageHistory.forEach(msg => {
      addMessage(msg.text, msg.sender, false);
    });
  }

  // Load message history from server
  loadChatHistory();

  // Functions
  function generateSessionId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  function detectSystemTheme() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  function getPositionStyles(pos) {
    const positions = {
      'bottom-right': 'bottom: 20px; right: 20px;',
      'bottom-left': 'bottom: 20px; left: 20px;',
      'top-right': 'top: 20px; right: 20px;',
      'top-left': 'top: 20px; left: 20px;'
    };
    return positions[pos] || positions['bottom-right'];
  }

  function checkBusinessHours() {
    if (!businessHours.timezone) return true;
    
    try {
      const now = new Date();
      const day = now.toLocaleDateString('en', { weekday: 'lowercase', timeZone: businessHours.timezone });
      const time = now.toLocaleTimeString('en-GB', { 
        hour12: false, 
        timeZone: businessHours.timezone,
        hour: '2-digit',
        minute: '2-digit'
      });

      const todayHours = businessHours[day];
      if (!todayHours || !todayHours.open || !todayHours.close) {
        return false;
      }

      return time >= todayHours.open && time <= todayHours.close;
    } catch (error) {
      console.warn('Error checking business hours:', error);
      return true;
    }
  }

  async function createChatSession() {
    try {
      const response = await fetch(`${apiBaseUrl}/api/sessions/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
          business_id: businessId,
          session_id: sessionId,
          channel: 'website',
          metadata: {
            user_agent: navigator.userAgent,
            url: window.location.href,
            referrer: document.referrer,
            timestamp: new Date().toISOString(),
            widget_config: {
              template: template,
              language: language,
              theme: currentTheme
            }
          }
        })
      });

      if (response.ok) {
        const session = await response.json();
        console.log('ChatGenie session created:', session.session_id);
      }
    } catch (error) {
      console.warn('Failed to create chat session:', error);
    }
  }

  async function loadChatHistory() {
    try {
      const response = await fetch(
        `${apiBaseUrl}/api/sessions/${sessionId}/messages`,
        {
          headers: {
            'Authorization': `Bearer ${apiKey}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        data.messages.forEach(msg => {
          if (!messageHistory.find(m => m.id === msg.id)) {
            addMessage(msg.content, msg.type === 'user' ? 'user' : 'bot', false);
          }
        });
      }
    } catch (error) {
      console.warn('Failed to load chat history:', error);
    }
  }

  function toggleChat() {
    isMinimized = !isMinimized;
    
    if (isMinimized) {
      chatWindow.style.display = 'none';
      button.innerHTML = "🧞‍♂️";
      button.style.transform = 'scale(1)';
    } else {
      chatWindow.style.display = 'flex';
      button.innerHTML = "−";
      button.style.transform = 'scale(0.9)';
      messageInput.focus();
      clearNotifications();
    }

    // Animation
    if (!isMinimized) {
      chatWindow.style.transform = 'scale(0.8) translateY(20px)';
      chatWindow.style.opacity = '0';
      setTimeout(() => {
        chatWindow.style.transform = 'scale(1) translateY(0)';
        chatWindow.style.opacity = '1';
        chatWindow.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s';
      }, 10);
    }
  }

  function toggleTheme() {
    currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
    themeButton.innerHTML = currentTheme === 'dark' ? '☀️' : '🌙';
    
    // Update CSS custom properties
    const textColor = currentTheme === 'dark' ? '#ffffff' : '#333333';
    const bgColor = currentTheme === 'dark' ? '#1a1a1a' : '#ffffff';
    const borderColor = currentTheme === 'dark' ? '#333333' : '#e1e5e9';
    
    container.style.setProperty('--text-color', textColor);
    container.style.setProperty('--bg-color', bgColor);
    container.style.setProperty('--border-color', borderColor);
    
    // Save preference
    localStorage.setItem(`chatgenie-theme-${businessId}`, currentTheme);
  }

  function addMessage(text, sender, saveToHistory = true) {
    const messageDiv = document.createElement('div');
    messageDiv.style.cssText = `
      margin-bottom: 16px;
      display: flex;
      ${sender === 'user' ? 'justify-content: flex-end;' : 'justify-content: flex-start;'}
    `;

    const messageBubble = document.createElement('div');
    messageBubble.textContent = text;
    messageBubble.style.cssText = `
      max-width: 80%;
      padding: 12px 16px;
      border-radius: 18px;
      font-size: 14px;
      line-height: 1.4;
      word-wrap: break-word;
      ${sender === 'user' 
        ? `background: var(--primary-color); color: white; border-bottom-right-radius: 4px;`
        : `background: var(--border-color); color: var(--text-color); border-bottom-left-radius: 4px;`
      }
      animation: messageSlide 0.3s ease-out;
    `;

    messageDiv.appendChild(messageBubble);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Save to history
    if (saveToHistory) {
      const messageData = {
        id: Date.now().toString(),
        text: text,
        sender: sender,
        timestamp: new Date().toISOString()
      };
      
      messageHistory.push(messageData);
      localStorage.setItem(`chatgenie-history-${businessId}`, JSON.stringify(messageHistory.slice(-50))); // Keep last 50 messages
      
      // Send to server
      saveChatMessage(messageData);
    }

    // Show notification if minimized
    if (isMinimized && sender === 'bot') {
      showNotification();
      
      // Text-to-speech for bot messages (if enabled)
      if (synthesis && synthesis.getVoices().length > 0) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = language;
        utterance.volume = 0.7;
        utterance.rate = 0.9;
        synthesis.speak(utterance);
      }
    }
  }

  async function saveChatMessage(messageData) {
    try {
      await fetch(`${apiBaseUrl}/api/sessions/${sessionId}/add-message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
          type: messageData.sender === 'user' ? 'user' : 'bot',
          content: messageData.text,
          metadata: {
            timestamp: messageData.timestamp,
            message_id: messageData.id
          }
        })
      });
    } catch (error) {
      console.warn('Failed to save message to server:', error);
    }
  }

  async function sendMessage(text, sender = 'user') {
    if (!text || isLoading) return;
    
    // Clear input
    if (sender === 'user') {
      messageInput.value = '';
      messageInput.style.height = 'auto';
    }
    
    // Add user message
    addMessage(text, sender);
    
    // Check for lead capture triggers
    if (leadCapture.enabled && sender === 'user') {
      checkLeadCapture(text);
    }

    if (sender === 'user') {
      isLoading = true;
      sendButton.disabled = true;
      sendButton.innerHTML = "⏳";

      try {
        // Send to ChatGenie API
        const response = await fetch(`${apiBaseUrl}/api/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
          },
          body: JSON.stringify({
            message: text,
            business_id: businessId,
            conversation_id: conversationId,
            session_id: sessionId,
            context: {
              template: template,
              business_hours: isBusinessHours,
              quick_actions: quickActions.map(a => a.action),
              user_data: getUserContext()
            }
          })
        });

        if (response.ok) {
          const data = await response.json();
          conversationId = data.conversation_id;
          
          addMessage(data.response, 'bot');
          
          // Handle lead generation
          if (data.lead_generated) {
            handleLeadGenerated(data.lead_data);
          }
        } else {
          const errorText = `Lo siento, ha ocurrido un error. ${!isBusinessHours ? businessHours.afterHoursMessage || 'Estamos fuera del horario de atención.' : 'Por favor, inténtalo de nuevo.'}`;
          addMessage(errorText, 'bot');
        }
      } catch (error) {
        console.error('Error sending message:', error);
        const errorText = `No puedo conectar ahora. ${!isBusinessHours ? businessHours.afterHoursMessage || 'Puedes contactarnos directamente.' : 'Por favor, verifica tu conexión.'}`;
        addMessage(errorText, 'bot');
      } finally {
        isLoading = false;
        sendButton.disabled = false;
        sendButton.innerHTML = "📤";
      }
    }
  }

  function getUserContext() {
    return {
      url: window.location.href,
      referrer: document.referrer,
      user_agent: navigator.userAgent,
      timestamp: new Date().toISOString(),
      session_duration: Date.now() - parseInt(sessionId.substring(0, 13)),
      message_count: messageHistory.length
    };
  }

  function checkLeadCapture(message) {
    const triggers = leadCapture.triggers || [];
    const lowerMessage = message.toLowerCase();
    
    for (const trigger of triggers) {
      if (lowerMessage.includes(trigger)) {
        // Trigger lead capture form
        setTimeout(() => {
          showLeadCaptureForm(trigger);
        }, 1000);
        break;
      }
    }
  }

  function showLeadCaptureForm(trigger) {
    const leadMessage = `Para ayudarte mejor con tu ${trigger}, me gustaría conocerte un poco más. ¿Podrías compartir tu nombre y email?`;
    addMessage(leadMessage, 'bot');
    
    // You could implement a custom form here or simply rely on conversational lead capture
  }

  function handleLeadGenerated(leadData) {
    console.log('Lead generated:', leadData);
    
    // Show success message
    const leadMessage = "¡Perfecto! He registrado tu información. Te contactaremos pronto para ayudarte con tu proyecto de transformación digital. 🚀";
    addMessage(leadMessage, 'bot');
    
    // Update UI to show lead captured
    const leadIndicator = document.createElement('div');
    leadIndicator.textContent = '✅ Lead capturado';
    leadIndicator.style.cssText = `
      background: #28a745;
      color: white;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 10px;
      position: absolute;
      top: -8px;
      left: 50%;
      transform: translateX(-50%);
    `;
    header.style.position = 'relative';
    header.appendChild(leadIndicator);
    
    setTimeout(() => {
      leadIndicator.remove();
    }, 5000);
  }

  function toggleVoiceRecognition() {
    if (!recognition) return;

    if (isVoiceMode) {
      recognition.stop();
      voiceButton.innerHTML = "🎤";
      voiceButton.style.background = "var(--accent-color)";
      isVoiceMode = false;
    } else {
      recognition.start();
      voiceButton.innerHTML = "⏹️";
      voiceButton.style.background = "#ff4444";
      isVoiceMode = true;
    }
  }

  function showNotification() {
    unreadCount++;
    badge.textContent = unreadCount.toString();
    badge.style.display = 'flex';
    
    // Bounce animation
    button.style.animation = 'bounce 0.5s ease-in-out';
    setTimeout(() => {
      button.style.animation = '';
    }, 500);
  }

  function clearNotifications() {
    unreadCount = 0;
    badge.style.display = 'none';
  }

  // Voice recognition events
  if (recognition) {
    recognition.onresult = function(event) {
      const transcript = event.results[0][0].transcript;
      messageInput.value = transcript;
      sendMessage(transcript);
    };

    recognition.onerror = function(event) {
      console.warn('Voice recognition error:', event.error);
      voiceButton.innerHTML = "🎤";
      voiceButton.style.background = "var(--accent-color)";
      isVoiceMode = false;
    };

    recognition.onend = function() {
      voiceButton.innerHTML = "🎤";
      voiceButton.style.background = "var(--accent-color)";
      isVoiceMode = false;
    };
  }

  // Dragging functions
  function startDragging(e) {
    if (!enableDragging) return;
    
    isDragging = true;
    const rect = container.getBoundingClientRect();
    dragOffset.x = e.clientX - rect.left;
    dragOffset.y = e.clientY - rect.top;
    container.style.cursor = 'grabbing';
    e.preventDefault();
  }

  function drag(e) {
    if (!isDragging || !enableDragging) return;
    
    const x = e.clientX - dragOffset.x;
    const y = e.clientY - dragOffset.y;
    
    // Keep within viewport bounds
    const maxX = window.innerWidth - container.offsetWidth;
    const maxY = window.innerHeight - container.offsetHeight;
    
    const constrainedX = Math.max(0, Math.min(x, maxX));
    const constrainedY = Math.max(0, Math.min(y, maxY));
    
    container.style.left = constrainedX + 'px';
    container.style.top = constrainedY + 'px';
    container.style.right = 'auto';
    container.style.bottom = 'auto';
  }

  function stopDragging() {
    if (!isDragging || !enableDragging) return;
    
    isDragging = false;
    container.style.cursor = 'default';
  }

  // Add CSS animations
  const style = document.createElement('style');
  style.textContent = `
    @keyframes messageSlide {
      from { transform: translateY(20px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes bounce {
      0%, 20%, 60%, 100% { transform: translateY(0); }
      40% { transform: translateY(-10px); }
      80% { transform: translateY(-4px); }
    }
    
    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.1); }
      100% { transform: scale(1); }
    }
    
    ${container.id} * {
      box-sizing: border-box;
    }
  `;
  document.head.appendChild(style);

  // Load saved theme preference
  const savedTheme = localStorage.getItem(`chatgenie-theme-${businessId}`);
  if (savedTheme && savedTheme !== currentTheme) {
    toggleTheme();
  }

  // Window events
  window.addEventListener('beforeunload', () => {
    // Save session data before page unload
    if (sessionId) {
      navigator.sendBeacon(`${apiBaseUrl}/api/sessions/${sessionId}/end`, JSON.stringify({
        reason: 'page_unload',
        duration: Date.now() - parseInt(sessionId.substring(0, 13))
      }));
    }
  });

  // System theme change detection
  if (theme === 'auto' && window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      const newTheme = e.matches ? 'dark' : 'light';
      if (newTheme !== currentTheme) {
        toggleTheme();
      }
    });
  }

  console.log(`ChatGenie loaded successfully for ${branding.businessName || 'business'}`);
  console.log(`Session ID: ${sessionId}`);
  console.log(`Template: ${template}`);
  console.log(`Language: ${language}`);
  console.log(`Business Hours: ${isBusinessHours ? 'Open' : 'Closed'}`);
})();
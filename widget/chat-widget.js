(function () {
  const config = window.Atiende24Config;

  if (!config) {
    console.error("Atiende24: falta configuración");
    return;
  }

  const { businessId, apiKey, apiBaseUrl } = config;

  let conversationId = null;
  let isLoading = false;
  let isDarkMode = localStorage.getItem('atiende24-dark-mode') === 'true';
  let isMinimized = false;
  let messageHistory = JSON.parse(localStorage.getItem('atiende24-history') || '[]');
  let recognition = null;
  let synthesis = window.speechSynthesis;
  let isDragging = false;
  let dragOffset = { x: 0, y: 0 };

  // Initialize speech recognition if available
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'es-ES';
  }

  // Create floating button with badge for unread messages
  const buttonContainer = document.createElement("div");
  buttonContainer.style.position = "fixed";
  buttonContainer.style.bottom = "20px";
  buttonContainer.style.right = "20px";
  buttonContainer.style.zIndex = "1000";

  const button = document.createElement("button");
  button.innerHTML = "💬";
  button.title = "Abrir chat de soporte";
  button.style.width = "60px";
  button.style.height = "60px";
  button.style.backgroundColor = isDarkMode ? "#1a1a1a" : "#007bff";
  button.style.color = "#fff";
  button.style.border = "none";
  button.style.borderRadius = "50%";
  button.style.cursor = "pointer";
  button.style.fontSize = "24px";
  button.style.boxShadow = `0 4px 20px ${isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,123,255,0.4)'}`;
  button.style.transition = "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)";
  button.style.position = "relative";
  button.style.overflow = "hidden";

  // Pulse animation
  const pulseRing = document.createElement("div");
  pulseRing.style.position = "absolute";
  pulseRing.style.top = "50%";
  pulseRing.style.left = "50%";
  pulseRing.style.transform = "translate(-50%, -50%)";
  pulseRing.style.width = "100%";
  pulseRing.style.height = "100%";
  pulseRing.style.borderRadius = "50%";
  pulseRing.style.border = `2px solid ${isDarkMode ? "#fff" : "#007bff"}`;
  pulseRing.style.animation = "atiende24-pulse 2s infinite";
  button.appendChild(pulseRing);

  // Notification badge
  const badge = document.createElement("div");
  badge.style.position = "absolute";
  badge.style.top = "-5px";
  badge.style.right = "-5px";
  badge.style.width = "20px";
  badge.style.height = "20px";
  badge.style.backgroundColor = "#ff4757";
  badge.style.borderRadius = "50%";
  badge.style.display = "none";
  badge.style.alignItems = "center";
  badge.style.justifyContent = "center";
  badge.style.fontSize = "12px";
  badge.style.fontWeight = "bold";
  badge.style.color = "#fff";
  badge.style.animation = "atiende24-bounce 0.5s ease";

  buttonContainer.appendChild(button);
  buttonContainer.appendChild(badge);

  // Add CSS animations
  const style = document.createElement("style");
  style.textContent = `
    @keyframes atiende24-pulse {
      0% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
      50% { opacity: 0.3; transform: translate(-50%, -50%) scale(1.1); }
      100% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
    }
    @keyframes atiende24-bounce {
      0%, 20%, 60%, 100% { transform: translateY(0); }
      40% { transform: translateY(-10px); }
      80% { transform: translateY(-5px); }
    }
    @keyframes atiende24-typing {
      0%, 60%, 100% { opacity: 0.3; }
      30% { opacity: 1; }
    }
    @keyframes atiende24-slideIn {
      0% { opacity: 0; transform: translateY(20px) scale(0.9); }
      100% { opacity: 1; transform: translateY(0) scale(1); }
    }
    @keyframes atiende24-slideOut {
      0% { opacity: 1; transform: translateY(0) scale(1); }
      100% { opacity: 0; transform: translateY(20px) scale(0.9); }
    }
    .atiende24-message-enter { animation: atiende24-slideIn 0.3s ease-out; }
    .atiende24-typing-dot {
      display: inline-block;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background-color: #666;
      margin: 0 2px;
      animation: atiende24-typing 1.4s infinite ease-in-out;
    }
    .atiende24-typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .atiende24-typing-dot:nth-child(3) { animation-delay: 0.4s; }
  `;
  document.head.appendChild(style);

  document.body.appendChild(buttonContainer);

  // Button hover effects
  button.onmouseenter = () => {
    button.style.transform = "scale(1.1)";
    button.style.boxShadow = `0 8px 25px ${isDarkMode ? 'rgba(255,255,255,0.2)' : 'rgba(0,123,255,0.6)'}`;
  };
  button.onmouseleave = () => {
    button.style.transform = "scale(1)";
    button.style.boxShadow = `0 4px 20px ${isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,123,255,0.4)'}`;
  };

  // Create chat container with advanced features
  const chatBox = document.createElement("div");
  const theme = isDarkMode ? 'dark' : 'light';
  chatBox.style.position = "fixed";
  chatBox.style.bottom = "90px";
  chatBox.style.right = "20px";
  chatBox.style.width = "380px";
  chatBox.style.height = isMinimized ? "60px" : "520px";
  chatBox.style.backgroundColor = isDarkMode ? "#1a1a1a" : "#fff";
  chatBox.style.border = "none";
  chatBox.style.borderRadius = "16px";
  chatBox.style.boxShadow = isDarkMode 
    ? "0 20px 40px rgba(0,0,0,0.3)" 
    : "0 20px 40px rgba(0,0,0,0.1)";
  chatBox.style.display = "none";
  chatBox.style.flexDirection = "column";
  chatBox.style.fontFamily = "system-ui, -apple-system, sans-serif";
  chatBox.style.zIndex = "1001";
  chatBox.style.transition = "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)";
  chatBox.style.backdropFilter = "blur(10px)";
  chatBox.style.overflow = "hidden";

  // Make draggable
  let chatBoxPos = { x: 20, y: 90 };

  document.body.appendChild(chatBox);

  // Advanced header with controls
  const chatHeader = document.createElement("div");
  chatHeader.style.backgroundColor = isDarkMode ? "#2d2d2d" : "#007bff";
  chatHeader.style.color = "#fff";
  chatHeader.style.padding = "15px 20px";
  chatHeader.style.borderRadius = "16px 16px 0 0";
  chatHeader.style.display = "flex";
  chatHeader.style.justifyContent = "space-between";
  chatHeader.style.alignItems = "center";
  chatHeader.style.cursor = "grab";
  chatHeader.style.userSelect = "none";
  
  const headerLeft = document.createElement("div");
  headerLeft.style.display = "flex";
  headerLeft.style.alignItems = "center";
  headerLeft.style.gap = "10px";

  const avatar = document.createElement("div");
  avatar.innerHTML = "🤖";
  avatar.style.width = "32px";
  avatar.style.height = "32px";
  avatar.style.borderRadius = "50%";
  avatar.style.backgroundColor = "rgba(255,255,255,0.2)";
  avatar.style.display = "flex";
  avatar.style.alignItems = "center";
  avatar.style.justifyContent = "center";
  avatar.style.fontSize = "18px";

  const headerInfo = document.createElement("div");
  const headerTitle = document.createElement("div");
  headerTitle.textContent = "Asistente Virtual";
  headerTitle.style.fontSize = "16px";
  headerTitle.style.fontWeight = "600";

  const statusIndicator = document.createElement("div");
  statusIndicator.innerHTML = "🟢 En línea";
  statusIndicator.style.fontSize = "12px";
  statusIndicator.style.opacity = "0.8";

  headerInfo.appendChild(headerTitle);
  headerInfo.appendChild(statusIndicator);
  headerLeft.appendChild(avatar);
  headerLeft.appendChild(headerInfo);

  const headerControls = document.createElement("div");
  headerControls.style.display = "flex";
  headerControls.style.gap = "8px";

  // Theme toggle button
  const themeButton = document.createElement("button");
  themeButton.innerHTML = isDarkMode ? "☀️" : "🌙";
  themeButton.title = isDarkMode ? "Modo claro" : "Modo oscuro";
  themeButton.style.backgroundColor = "transparent";
  themeButton.style.border = "none";
  themeButton.style.color = "#fff";
  themeButton.style.fontSize = "16px";
  themeButton.style.cursor = "pointer";
  themeButton.style.padding = "4px";
  themeButton.style.borderRadius = "4px";
  themeButton.onclick = toggleTheme;

  // Minimize button
  const minimizeButton = document.createElement("button");
  minimizeButton.innerHTML = isMinimized ? "⬆️" : "⬇️";
  minimizeButton.title = isMinimized ? "Expandir" : "Minimizar";
  minimizeButton.style.backgroundColor = "transparent";
  minimizeButton.style.border = "none";
  minimizeButton.style.color = "#fff";
  minimizeButton.style.fontSize = "16px";
  minimizeButton.style.cursor = "pointer";
  minimizeButton.style.padding = "4px";
  minimizeButton.style.borderRadius = "4px";
  minimizeButton.onclick = toggleMinimize;

  // Close button
  const closeButton = document.createElement("button");
  closeButton.innerHTML = "✕";
  closeButton.title = "Cerrar chat";
  closeButton.style.backgroundColor = "transparent";
  closeButton.style.border = "none";
  closeButton.style.color = "#fff";
  closeButton.style.fontSize = "18px";
  closeButton.style.cursor = "pointer";
  closeButton.style.padding = "4px";
  closeButton.style.borderRadius = "4px";
  closeButton.onclick = () => {
    chatBox.style.animation = "atiende24-slideOut 0.3s ease-in";
    setTimeout(() => {
      chatBox.style.display = "none";
      chatBox.style.animation = "";
    }, 300);
  };

  headerControls.appendChild(themeButton);
  headerControls.appendChild(minimizeButton);
  headerControls.appendChild(closeButton);

  chatHeader.appendChild(headerLeft);
  chatHeader.appendChild(headerControls);

  // Make header draggable
  chatHeader.onmousedown = startDrag;

  // Messages container with enhanced scrolling
  const messagesContainer = document.createElement("div");
  messagesContainer.style.flex = "1";
  messagesContainer.style.padding = "20px";
  messagesContainer.style.overflowY = "auto";
  messagesContainer.style.maxHeight = "380px";
  messagesContainer.style.scrollBehavior = "smooth";
  messagesContainer.style.display = isMinimized ? "none" : "block";

  // Quick actions bar
  const quickActions = document.createElement("div");
  quickActions.style.display = isMinimized ? "none" : "flex";
  quickActions.style.gap = "8px";
  quickActions.style.padding = "10px 20px";
  quickActions.style.borderTop = `1px solid ${isDarkMode ? '#333' : '#e9ecef'}`;
  quickActions.style.flexWrap = "wrap";

  const quickButtons = [
    { text: "💬 ¿Cómo puedo ayudarte?", action: () => sendQuickMessage("¿Cómo puedo ayudarte?") },
    { text: "📞 Contacto", action: () => sendQuickMessage("Quiero información de contacto") },
    { text: "⏰ Horarios", action: () => sendQuickMessage("¿Cuáles son sus horarios de atención?") },
    { text: "💰 Precios", action: () => sendQuickMessage("¿Me pueden proporcionar información sobre precios?") }
  ];

  quickButtons.forEach(btn => {
    const quickBtn = document.createElement("button");
    quickBtn.textContent = btn.text;
    quickBtn.style.padding = "6px 12px";
    quickBtn.style.border = `1px solid ${isDarkMode ? '#444' : '#ddd'}`;
    quickBtn.style.borderRadius = "20px";
    quickBtn.style.backgroundColor = "transparent";
    quickBtn.style.color = isDarkMode ? '#fff' : '#333';
    quickBtn.style.cursor = "pointer";
    quickBtn.style.fontSize = "12px";
    quickBtn.style.transition = "all 0.2s ease";
    quickBtn.onclick = btn.action;
    
    quickBtn.onmouseenter = () => {
      quickBtn.style.backgroundColor = isDarkMode ? '#333' : '#f8f9fa';
    };
    quickBtn.onmouseleave = () => {
      quickBtn.style.backgroundColor = "transparent";
    };
    
    quickActions.appendChild(quickBtn);
  });

  // Enhanced input container
  const inputContainer = document.createElement("div");
  inputContainer.style.padding = "20px";
  inputContainer.style.borderTop = `1px solid ${isDarkMode ? '#333' : '#e9ecef'}`;
  inputContainer.style.display = isMinimized ? "none" : "flex";
  inputContainer.style.gap = "10px";
  inputContainer.style.alignItems = "flex-end";
  inputContainer.style.backgroundColor = isDarkMode ? "#2d2d2d" : "#f8f9fa";

  const inputWrapper = document.createElement("div");
  inputWrapper.style.flex = "1";
  inputWrapper.style.position = "relative";
  inputWrapper.style.display = "flex";
  inputWrapper.style.alignItems = "center";
  inputWrapper.style.backgroundColor = isDarkMode ? "#1a1a1a" : "#fff";
  inputWrapper.style.borderRadius = "25px";
  inputWrapper.style.border = `2px solid ${isDarkMode ? '#444' : '#e9ecef'}`;
  inputWrapper.style.transition = "border-color 0.3s ease";

  // File upload button
  const fileButton = document.createElement("button");
  fileButton.innerHTML = "📎";
  fileButton.title = "Adjuntar archivo";
  fileButton.style.backgroundColor = "transparent";
  fileButton.style.border = "none";
  fileButton.style.color = isDarkMode ? '#ccc' : '#666';
  fileButton.style.cursor = "pointer";
  fileButton.style.padding = "8px 12px";
  fileButton.style.fontSize = "16px";

  const input = document.createElement("textarea");
  input.placeholder = "Escribe tu mensaje...";
  input.style.flex = "1";
  input.style.border = "none";
  input.style.outline = "none";  
  input.style.padding = "12px 8px";
  input.style.fontSize = "14px";
  input.style.backgroundColor = "transparent";
  input.style.color = isDarkMode ? '#fff' : '#333';
  input.style.resize = "none";
  input.style.minHeight = "20px";
  input.style.maxHeight = "80px";
  input.style.fontFamily = "inherit";

  // Auto-resize textarea
  input.oninput = () => {
    input.style.height = "20px";
    input.style.height = Math.min(input.scrollHeight, 80) + "px";
  };

  // Voice input button
  const voiceButton = document.createElement("button");
  voiceButton.innerHTML = "🎤";
  voiceButton.title = "Grabación de voz";
  voiceButton.style.backgroundColor = "transparent";
  voiceButton.style.border = "none";
  voiceButton.style.color = isDarkMode ? '#ccc' : '#666';
  voiceButton.style.cursor = recognition ? "pointer" : "not-allowed";
  voiceButton.style.padding = "8px 12px";
  voiceButton.style.fontSize = "16px";
  voiceButton.style.opacity = recognition ? "1" : "0.5";
  if (recognition) {
    voiceButton.onclick = toggleVoiceRecording;
  }

  // Emoji button
  const emojiButton = document.createElement("button");
  emojiButton.innerHTML = "😊";
  emojiButton.title = "Emojis";
  emojiButton.style.backgroundColor = "transparent";
  emojiButton.style.border = "none";
  emojiButton.style.color = isDarkMode ? '#ccc' : '#666';
  emojiButton.style.cursor = "pointer";
  emojiButton.style.padding = "8px 12px";
  emojiButton.style.fontSize = "16px";

  inputWrapper.appendChild(fileButton);
  inputWrapper.appendChild(input);
  inputWrapper.appendChild(voiceButton);
  inputWrapper.appendChild(emojiButton);

  // Enhanced send button
  const sendButton = document.createElement("button");
  sendButton.innerHTML = "➤";
  sendButton.style.width = "45px";
  sendButton.style.height = "45px";
  sendButton.style.backgroundColor = isDarkMode ? "#0066cc" : "#007bff";
  sendButton.style.color = "#fff";
  sendButton.style.border = "none";
  sendButton.style.borderRadius = "50%";
  sendButton.style.cursor = "pointer";
  sendButton.style.fontSize = "18px";
  sendButton.style.display = "flex";
  sendButton.style.alignItems = "center";
  sendButton.style.justifyContent = "center";
  sendButton.style.transition = "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)";
  sendButton.style.transform = "rotate(0deg)";

  sendButton.onmouseenter = () => {
    sendButton.style.backgroundColor = isDarkMode ? "#0052a3" : "#0056b3";
    sendButton.style.transform = "rotate(0deg) scale(1.05)";
  };
  sendButton.onmouseleave = () => {
    sendButton.style.backgroundColor = isDarkMode ? "#0066cc" : "#007bff";
    sendButton.style.transform = "rotate(0deg) scale(1)";
  };

  inputWrapper.onfocus = () => {
    inputWrapper.style.borderColor = isDarkMode ? "#0066cc" : "#007bff";
  };
  inputWrapper.onblur = () => {
    inputWrapper.style.borderColor = isDarkMode ? '#444' : '#e9ecef';
  };

  inputContainer.appendChild(inputWrapper);
  inputContainer.appendChild(sendButton);

  chatBox.appendChild(chatHeader);
  chatBox.appendChild(messagesContainer);
  chatBox.appendChild(quickActions);
  chatBox.appendChild(inputContainer);

  // Load message history
  if (messageHistory.length > 0) {
    messageHistory.forEach(msg => {
      addMessage(msg.text, msg.role, false, msg.timestamp);
    });
  } else {
    // Welcome message with personality
    const welcomeText = "¡Hola! 👋 Soy tu asistente virtual inteligente. Estoy aquí para ayudarte las 24 horas del día.\n\n✨ Puedes escribir o usar comandos de voz\n🎯 Tengo acceso a información actualizada\n💡 ¿En qué puedo ayudarte hoy?";
    addMessage(welcomeText, "assistant", false, new Date());
  }

  // Button click handler
  button.onclick = () => {
    const isVisible = chatBox.style.display !== "none";
    if (isVisible) {
      chatBox.style.animation = "atiende24-slideOut 0.3s ease-in";
      setTimeout(() => {
        chatBox.style.display = "none";
        chatBox.style.animation = "";
      }, 300);
    } else {
      chatBox.style.display = "flex";
      chatBox.style.animation = "atiende24-slideIn 0.3s ease-out";
      if (!isMinimized) {
        input.focus();
      }
    }
  };

  // Enhanced message display with timestamps and status
  function addMessage(text, role, animate = true, timestamp = new Date()) {
    const messageWrapper = document.createElement("div");
    messageWrapper.style.display = "flex";
    messageWrapper.style.justifyContent = role === "user" ? "flex-end" : "flex-start";
    messageWrapper.style.marginBottom = "20px";
    if (animate) messageWrapper.classList.add("atiende24-message-enter");

    const messageContent = document.createElement("div");
    messageContent.style.maxWidth = "85%";
    messageContent.style.display = "flex";
    messageContent.style.flexDirection = "column";
    messageContent.style.gap = "5px";

    const msg = document.createElement("div");
    msg.style.padding = "14px 18px";
    msg.style.fontSize = "14px";
    msg.style.lineHeight = "1.5";
    msg.style.wordWrap = "break-word";
    msg.style.position = "relative";
    msg.style.whiteSpace = "pre-wrap";

    if (role === "user") {
      msg.style.backgroundColor = isDarkMode ? "#0066cc" : "#007bff";
      msg.style.color = "#fff";
      msg.style.borderRadius = "20px 20px 6px 20px";
      msg.style.textAlign = "left";
    } else {
      msg.style.backgroundColor = isDarkMode ? "#2d2d2d" : "#f1f3f5";
      msg.style.color = isDarkMode ? "#fff" : "#333";
      msg.style.borderRadius = "20px 20px 20px 6px";
      msg.style.boxShadow = isDarkMode ? "0 2px 8px rgba(0,0,0,0.3)" : "0 2px 8px rgba(0,0,0,0.1)";
    }

    msg.textContent = text;

    // Add timestamp
    const timeEl = document.createElement("div");
    timeEl.style.fontSize = "11px";
    timeEl.style.opacity = "0.6";
    timeEl.style.textAlign = role === "user" ? "right" : "left";
    timeEl.style.color = isDarkMode ? "#ccc" : "#666";
    timeEl.textContent = timestamp.toLocaleTimeString('es-ES', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });

    messageContent.appendChild(msg);
    messageContent.appendChild(timeEl);
    messageWrapper.appendChild(messageContent);
    messagesContainer.appendChild(messageWrapper);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Save to history
    if (animate) {
      messageHistory.push({ text, role, timestamp });
      localStorage.setItem('atiende24-history', JSON.stringify(messageHistory.slice(-50))); // Keep last 50 messages
    }

    // Add message reactions for assistant messages
    if (role === "assistant" && animate) {
      setTimeout(() => addMessageReactions(msg), 1000);
    }
  }

  function addMessageReactions(msgElement) {
    const reactions = document.createElement("div");
    reactions.style.position = "absolute";
    reactions.style.bottom = "-25px";
    reactions.style.right = "10px";
    reactions.style.display = "flex";
    reactions.style.gap = "5px";
    reactions.style.opacity = "0";
    reactions.style.transition = "opacity 0.3s ease";

    ["👍", "👎", "❤️"].forEach(emoji => {
      const reaction = document.createElement("button");
      reaction.textContent = emoji;
      reaction.style.background = "none";
      reaction.style.border = "none";
      reaction.style.fontSize = "14px";
      reaction.style.cursor = "pointer";
      reaction.style.borderRadius = "12px";
      reaction.style.padding = "4px 6px";
      reaction.style.transition = "background-color 0.2s ease";
      
      reaction.onclick = () => {
        reaction.style.backgroundColor = isDarkMode ? "#444" : "#e9ecef";
        // Here you could send feedback to your backend
      };
      
      reactions.appendChild(reaction);
    });

    msgElement.style.position = "relative";
    msgElement.appendChild(reactions);

    msgElement.onmouseenter = () => {
      reactions.style.opacity = "1";
    };
    msgElement.onmouseleave = () => {
      reactions.style.opacity = "0";
    };
  }

  function showAdvancedLoadingIndicator() {
    const loadingWrapper = document.createElement("div");
    loadingWrapper.id = "loading-indicator";
    loadingWrapper.style.display = "flex";
    loadingWrapper.style.justifyContent = "flex-start";
    loadingWrapper.style.marginBottom = "20px";

    const loadingContent = document.createElement("div");
    loadingContent.style.maxWidth = "85%";
    loadingContent.style.display = "flex";
    loadingContent.style.flexDirection = "column";
    loadingContent.style.gap = "5px";

    const loadingMsg = document.createElement("div");
    loadingMsg.style.backgroundColor = isDarkMode ? "#2d2d2d" : "#f1f3f5";
    loadingMsg.style.color = isDarkMode ? "#ccc" : "#666";
    loadingMsg.style.padding = "14px 18px";
    loadingMsg.style.borderRadius = "20px 20px 20px 6px";
    loadingMsg.style.fontSize = "14px";
    loadingMsg.style.display = "flex";
    loadingMsg.style.alignItems = "center";
    loadingMsg.style.gap = "8px";

    const typingText = document.createElement("span");
    typingText.textContent = "Escribiendo";

    const dotsContainer = document.createElement("div");
    dotsContainer.style.display = "flex";
    dotsContainer.style.gap = "2px";

    for (let i = 0; i < 3; i++) {
      const dot = document.createElement("div");
      dot.classList.add("atiende24-typing-dot");
      dot.style.animationDelay = `${i * 0.2}s`;
      dotsContainer.appendChild(dot);
    }

    loadingMsg.appendChild(typingText);
    loadingMsg.appendChild(dotsContainer);
    loadingContent.appendChild(loadingMsg);
    loadingWrapper.appendChild(loadingContent);
    messagesContainer.appendChild(loadingWrapper);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function hideLoadingIndicator() {
    const indicator = document.getElementById("loading-indicator");
    if (indicator) {
      indicator.remove();
    }
  }

  async function sendMessage(text, isVoice = false) {
    if (!text.trim()) return;
    if (isLoading) return;

    isLoading = true;
    updateSendButton(true);
    
    addMessage(text, "user");
    showAdvancedLoadingIndicator();

    // Simulate AI thinking time for better UX
    const thinkingTime = Math.random() * 1000 + 500;
    await new Promise(resolve => setTimeout(resolve, thinkingTime));

    try {
      const response = await fetch(`${apiBaseUrl}/chat/message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": apiKey
        },
        body: JSON.stringify({
          business_id: businessId,
          message: text,
          conversation_id: conversationId
        })
      });

      hideLoadingIndicator();

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      conversationId = data.conversation_id;
      addMessage(data.reply, "assistant");

      // Text-to-speech for responses if enabled
      if (isVoice && synthesis) {
        speakMessage(data.reply);
      }

    } catch (error) {
      hideLoadingIndicator();
      console.error("Error sending message:", error);
      const errorMsg = "❌ Lo siento, ha ocurrido un error de conexión. Por favor, verifica tu conexión e inténtalo de nuevo.";
      addMessage(errorMsg, "assistant");
    } finally {
      isLoading = false;
      updateSendButton(false);
    }
  }

  function updateSendButton(loading) {
    if (loading) {
      sendButton.disabled = true;
      sendButton.innerHTML = "⏳";
      sendButton.style.backgroundColor = isDarkMode ? "#444" : "#6c757d";
      sendButton.style.animation = "atiende24-pulse 1s infinite";
    } else {
      sendButton.disabled = false;
      sendButton.innerHTML = "➤";
      sendButton.style.backgroundColor = isDarkMode ? "#0066cc" : "#007bff";
      sendButton.style.animation = "none";
    }
  }

  function toggleTheme() {
    isDarkMode = !isDarkMode;
    localStorage.setItem('atiende24-dark-mode', isDarkMode.toString());
    applyTheme();
    themeButton.innerHTML = isDarkMode ? "☀️" : "🌙";
    themeButton.title = isDarkMode ? "Modo claro" : "Modo oscuro";
  }

  function applyTheme() {
    // Update all theme-dependent styles
    const elements = [
      { el: chatBox, bg: isDarkMode ? "#1a1a1a" : "#fff" },
      { el: chatHeader, bg: isDarkMode ? "#2d2d2d" : "#007bff" },
      { el: inputContainer, bg: isDarkMode ? "#2d2d2d" : "#f8f9fa" },
      { el: inputWrapper, bg: isDarkMode ? "#1a1a1a" : "#fff", border: isDarkMode ? '#444' : '#e9ecef' },
      { el: button, bg: isDarkMode ? "#1a1a1a" : "#007bff" },
      { el: sendButton, bg: isDarkMode ? "#0066cc" : "#007bff" }
    ];

    elements.forEach(({ el, bg, border }) => {
      if (bg) el.style.backgroundColor = bg;
      if (border) el.style.borderColor = border;
    });

    input.style.color = isDarkMode ? '#fff' : '#333';
    
    // Update existing messages
    messagesContainer.querySelectorAll('div').forEach(msg => {
      if (msg.style.backgroundColor === (isDarkMode ? "#f1f3f5" : "#2d2d2d")) {
        msg.style.backgroundColor = isDarkMode ? "#2d2d2d" : "#f1f3f5";
        msg.style.color = isDarkMode ? "#fff" : "#333";
      }
    });
  }

  function toggleMinimize() {
    isMinimized = !isMinimized;
    chatBox.style.height = isMinimized ? "60px" : "520px";
    messagesContainer.style.display = isMinimized ? "none" : "block";
    quickActions.style.display = isMinimized ? "none" : "flex";
    inputContainer.style.display = isMinimized ? "none" : "flex";
    minimizeButton.innerHTML = isMinimized ? "⬆️" : "⬇️";
    minimizeButton.title = isMinimized ? "Expandir" : "Minimizar";
  }

  function sendQuickMessage(message) {
    input.value = message;
    handleSend();
  }

  function toggleVoiceRecording() {
    if (!recognition) return;

    if (recognition.listening) {
      recognition.stop();
      voiceButton.innerHTML = "🎤";
      voiceButton.style.backgroundColor = "transparent";
    } else {
      recognition.start();
      voiceButton.innerHTML = "🔴";
      voiceButton.style.backgroundColor = "rgba(255, 0, 0, 0.1)";
    }
  }

  if (recognition) {
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      input.value = transcript;
      sendMessage(transcript, true);
    };

    recognition.onerror = () => {
      voiceButton.innerHTML = "🎤";
      voiceButton.style.backgroundColor = "transparent";
    };

    recognition.onend = () => {
      voiceButton.innerHTML = "🎤";
      voiceButton.style.backgroundColor = "transparent";
    };
  }

  function speakMessage(text) {
    if (!synthesis) return;
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'es-ES';
    utterance.rate = 0.9;
    utterance.pitch = 1.0;
    synthesis.speak(utterance);
  }

  function startDrag(e) {
    isDragging = true;
    chatHeader.style.cursor = "grabbing";
    
    const rect = chatBox.getBoundingClientRect();
    dragOffset.x = e.clientX - rect.left;
    dragOffset.y = e.clientY - rect.top;

    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', stopDrag);
  }

  function drag(e) {
    if (!isDragging) return;
    
    const newX = window.innerWidth - (e.clientX - dragOffset.x) - chatBox.offsetWidth;
    const newY = window.innerHeight - (e.clientY - dragOffset.y) - chatBox.offsetHeight;
    
    chatBox.style.right = Math.max(10, Math.min(window.innerWidth - chatBox.offsetWidth - 10, newX)) + "px";
    chatBox.style.bottom = Math.max(10, Math.min(window.innerHeight - chatBox.offsetHeight - 10, newY)) + "px";
  }

  function stopDrag() {
    isDragging = false;
    chatHeader.style.cursor = "grab";
    document.removeEventListener('mousemove', drag);
    document.removeEventListener('mouseup', stopDrag);
  }

  function handleSend() {
    const text = input.value.trim();
    if (text) {
      input.value = "";
      input.style.height = "20px";
      sendMessage(text);
    }
  }

  // Event listeners
  sendButton.onclick = handleSend;

  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  });

  // Keyboard shortcuts
  document.addEventListener("keydown", function (e) {
    // Ctrl/Cmd + Shift + C to toggle chat
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
      button.click();
    }
    // Escape to close chat
    if (e.key === 'Escape' && chatBox.style.display !== "none") {
      closeButton.click();
    }
  });

  // Initialize with theme
  applyTheme();

  console.log("🎯 Atiende24 Advanced Chat Widget loaded successfully!");
  console.log("⌨️ Keyboard shortcuts:");
  console.log("  - Ctrl+Shift+C: Toggle chat");
  console.log("  - Escape: Close chat");
  console.log("  - Enter: Send message");
  console.log("  - Shift+Enter: New line");
})();
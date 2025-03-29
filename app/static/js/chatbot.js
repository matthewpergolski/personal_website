// Simple chatbot implementation for portfolio site
document.addEventListener('DOMContentLoaded', () => {
    console.log('Chatbot script loaded');
    
    // Get DOM elements
    const chatButton = document.getElementById('chatButton');
    const chatWindow = document.getElementById('chatWindow');
    const closeChat = document.getElementById('closeChat');
    const expandChat = document.getElementById('expandChat');
    const chatInput = document.getElementById('chatInput');
    const sendMessage = document.getElementById('sendMessage');
    const chatMessages = document.getElementById('chatMessages');
    const chatSuggestions = document.querySelectorAll('.chat-suggestion');
    
    // Check if we're on the resume page
    const isResumePage = window.location.pathname.includes('/resume');
    if (isResumePage) {
        console.log('Resume page detected - will apply fixes');
        
        // Create a single stylesheet with all needed fixes
        const resumePageStyle = document.createElement('style');
        resumePageStyle.id = 'chatbot-resume-fix';
        resumePageStyle.textContent = `
            /* Resume page fixes - single consolidated stylesheet */
            #expandChat .expand-icon {
                display: inline-block !important;
                visibility: visible !important;
                opacity: 1 !important;
            }
            
            #expandChat .collapse-icon {
                display: none !important;
            }
            
            /* Ensure chatbot button is visible */
            #chatButton {
                opacity: 1 !important;
                visibility: visible !important;
            }
        `;
        document.head.appendChild(resumePageStyle);
        
        // Use just two checks instead of continuous monitoring
        setTimeout(forceFixExpandIcon, 500);  // After initial page load
        setTimeout(forceFixExpandIcon, 2000); // After animations likely completed
    }
    
    // Expanded state tracking
    let isExpanded = false;
    
    // Original size and position
    let originalStyles = {
        width: '',
        height: '',
        bottom: '',
        right: '',
        borderRadius: ''
    };
    
    // Function to forcefully fix the icon state (defined early so all code can use it)
    function forceFixExpandIcon() {
        const expandIcon = expandChat?.querySelector('.expand-icon');
        const collapseIcon = expandChat?.querySelector('.collapse-icon');
        
        if (expandIcon) {
            expandIcon.classList.remove('hidden');
            // Only set the style attribute once - avoid expensive DOM operations
            if (!expandIcon.hasAttribute('data-fixed')) {
                expandIcon.setAttribute('style', 'display: inline-block; visibility: visible;');
                expandIcon.setAttribute('data-fixed', 'true');
            }
        }
        if (collapseIcon) {
            collapseIcon.classList.add('hidden');
        }
    }

    // Debug - log if elements exist
    console.log('Chat elements found:', {
        chatButton: !!chatButton,
        chatWindow: !!chatWindow,
        closeChat: !!closeChat,
        expandChat: !!expandChat,
        chatInput: !!chatInput,
        sendMessage: !!sendMessage,
        chatMessages: !!chatMessages,
        chatSuggestions: chatSuggestions.length
    });

    // Make sure elements exist before adding event listeners
    if (!chatButton || !chatWindow) {
        console.warn('Chatbot elements not found');
        return;
    }

    // Ensure expand icon is visible - fix for resume page
    if (expandChat) {
        const expandIcon = expandChat.querySelector('.expand-icon');
        const collapseIcon = expandChat.querySelector('.collapse-icon');
        
        // Basic fix for all pages
        if (expandIcon) expandIcon.classList.remove('hidden');
        if (collapseIcon) collapseIcon.classList.add('hidden');
        
        // Check once after a delay for all pages
        setTimeout(() => {
            if (expandIcon) expandIcon.classList.remove('hidden');
            if (collapseIcon) collapseIcon.classList.add('hidden');
        }, 100);
    }

    // Immediate test - try to show chat window
    console.log('Setting up click handler');
    
    // Force direct click handling - backup approach
    window.toggleChatWindow = function() {
        console.log('Manual toggle called');
        if (!chatWindow) return;
        
        // Ensure expand icon is visible
        if (expandChat && !isExpanded) {
            forceFixExpandIcon();
        }
        
        chatWindow.classList.toggle('hidden');
        chatWindow.classList.toggle('scale-95');
        chatWindow.classList.toggle('opacity-0');
        
        if (!chatWindow.classList.contains('hidden') && chatInput) {
            chatInput.focus();
        }
    };
    
    // Toggle chat window visibility
    chatButton.addEventListener('click', (e) => {
        console.log('Chat button clicked');
        e.preventDefault();
        e.stopPropagation();
        
        // Ensure expand icon is visible when opening chat window
        if (expandChat && !isExpanded) {
            forceFixExpandIcon();
        }
        
        chatWindow.classList.toggle('hidden');
        setTimeout(() => {
            chatWindow.classList.toggle('scale-95');
            chatWindow.classList.toggle('opacity-0');
        }, 10);
        
        // Focus input if window is visible
        if (!chatWindow.classList.contains('hidden')) {
            setTimeout(() => chatInput && chatInput.focus(), 300);
        }
        
        return false;
    });

    // Just in case, add additional click trigger
    chatButton.onclick = function(e) {
        console.log('Secondary click handler triggered');
        window.toggleChatWindow();
        return false;
    };

    // Close chat window
    if (closeChat) {
        closeChat.addEventListener('click', (e) => {
            console.log('Close chat clicked');
            // If expanded, collapse first
            if (isExpanded) {
                collapseChat();
                return;
            }
            
            chatWindow.classList.add('scale-95', 'opacity-0');
            setTimeout(() => {
                chatWindow.classList.add('hidden');
            }, 300);
        });
    }
    
    // Toggle expand/collapse chat window
    if (expandChat) {
        expandChat.addEventListener('click', (e) => {
            console.log('Expand chat clicked');
            e.preventDefault();
            e.stopPropagation();
            if (!isExpanded) {
                expandChatWindow();
            } else {
                collapseChat();
            }
        });
    }
    
    // Separate functions for expand and collapse to make it easier to call individually
    function expandChatWindow() {
        console.log('Expanding chat window');
        if (isExpanded) return;
        
        const expandIcon = expandChat.querySelector('.expand-icon');
        const collapseIcon = expandChat.querySelector('.collapse-icon');
        
        // First, remove any existing backdrop to start fresh
        const existingBackdrop = document.getElementById('chatBackdrop');
        if (existingBackdrop) {
            existingBackdrop.remove();
        }
        
        // Create the backdrop first, and append it directly to body
        // This ensures it's a sibling of the chat window, not a parent or child
        const backdrop = document.createElement('div');
        backdrop.id = 'chatBackdrop';
        backdrop.style.position = 'fixed';
        backdrop.style.top = '0';
        backdrop.style.left = '0';
        backdrop.style.right = '0';
        backdrop.style.bottom = '0';
        backdrop.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        backdrop.style.zIndex = '9998';
        backdrop.style.opacity = '0';
        backdrop.style.transition = 'opacity 0.3s ease';
        
        // Add click event to only the backdrop element itself
        backdrop.addEventListener('mousedown', function(e) {
            // If clicked outside chat window on the backdrop itself
            if (e.target === backdrop) {
                collapseChat();
            }
        });
        
        // Add the backdrop to the DOM before manipulating the chat window
        document.body.appendChild(backdrop);
        
        // Save original styles
        originalStyles = {
            width: chatWindow.style.width || getComputedStyle(chatWindow).width,
            height: chatWindow.style.height || getComputedStyle(chatWindow).height,
            bottom: chatWindow.style.bottom || getComputedStyle(chatWindow).bottom,
            right: chatWindow.style.right || getComputedStyle(chatWindow).right,
            borderRadius: chatWindow.style.borderRadius || getComputedStyle(chatWindow).borderRadius
        };
        
        // IMPORTANT: Move the chatWindow to be a direct child of body
        // This ensures it's completely separate from the backdrop in the DOM
        const chatParent = chatWindow.parentElement;
        document.body.appendChild(chatWindow);
        
        // Store original parent for later restoration
        chatWindow._originalParent = chatParent;
        
        // Expand the chat window
        chatWindow.style.transition = 'all 0.3s ease-in-out';
        chatWindow.style.width = '95vw';
        chatWindow.style.height = '90vh';
        chatWindow.style.bottom = '5vh';
        chatWindow.style.right = '2.5vw';
        chatWindow.style.borderRadius = '1rem';
        chatWindow.style.zIndex = '9999';
        
        // Actually make the backdrop visible now that chat window is in front
        setTimeout(() => {
            backdrop.style.opacity = '1';
        }, 10);
        
        // Toggle icons
        expandIcon.classList.add('hidden');
        collapseIcon.classList.remove('hidden');
        
        // Update state
        isExpanded = true;
        
        // Hide chat button when expanded
        chatButton.style.display = 'none';
        
        // Add Claude-like styling to messages
        chatWindow.classList.add('expanded');
        chatMessages.classList.add('expanded-messages');
        
        // Add expanded classes to input elements
        const inputContainer = document.querySelector('.chat-input-container');
        if (inputContainer) {
            inputContainer.classList.add('expanded');
        }
        
        if (chatInput) {
            chatInput.classList.add('expanded');
        }
        
        // Disable page scrolling
        document.body.style.overflow = 'hidden';
        
        // Focus input after expansion
        setTimeout(() => chatInput && chatInput.focus(), 300);
    }
    
    function collapseChat() {
        console.log('Collapsing chat window');
        if (!isExpanded) return;
        
        const expandIcon = expandChat.querySelector('.expand-icon');
        const collapseIcon = expandChat.querySelector('.collapse-icon');
        
        // First make backdrop transparent
        const backdrop = document.getElementById('chatBackdrop');
        if (backdrop) {
            backdrop.style.opacity = '0';
        }
        
        // Restore original styles with a slight delay
        setTimeout(() => {
            chatWindow.style.width = originalStyles.width;
            chatWindow.style.height = originalStyles.height;
            chatWindow.style.bottom = originalStyles.bottom;
            chatWindow.style.right = originalStyles.right;
            chatWindow.style.borderRadius = originalStyles.borderRadius;
            chatWindow.style.zIndex = '50'; // Reset to original z-index
            
            // Remove expanded classes from input elements
            const inputContainer = document.querySelector('.chat-input-container');
            if (inputContainer) {
                inputContainer.classList.remove('expanded');
            }
            
            if (chatInput) {
                chatInput.classList.remove('expanded');
            }
            
            // Remove backdrop completely
            if (backdrop) {
                backdrop.remove();
            }
            
            // Toggle icons
            expandIcon.classList.remove('hidden');
            collapseIcon.classList.add('hidden');
            
            // Update state
            isExpanded = false;
            
            // Return chat window to original parent
            if (chatWindow._originalParent) {
                chatWindow._originalParent.appendChild(chatWindow);
                delete chatWindow._originalParent;
            }
            
            // Show chat button
            chatButton.style.display = 'flex';
            
            // Remove Claude-like styling
            chatWindow.classList.remove('expanded');
            chatMessages.classList.remove('expanded-messages');
            
            // Enable page scrolling
            document.body.style.overflow = '';
            
            // Focus input after collapse
            setTimeout(() => chatInput && chatInput.focus(), 300);
        }, 150);
    }
    
    // Add emergency collapse on ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isExpanded) {
            collapseChat();
        }
    });
    
    // Function to reposition messages based on view mode
    function repositionMessages() {
        // Could add custom message layout here for expanded view
        // For now, just scroll to bottom
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // Simple message handling function
    const sendChatMessage = () => {
        if (!chatInput || !chatMessages) return;
        
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Add user message
        addMessage(message, 'user');
        chatInput.value = '';
        
        // Show typing indicator
        addTypingIndicator();
        
        // Respond after short delay
        setTimeout(() => {
            // Remove typing indicator
            const typingIndicator = document.querySelector('.typing-indicator');
            if (typingIndicator) typingIndicator.remove();
            
            // Always show the placeholder message
            addMessage("This feature is not available yet... stay tuned!", 'bot');
        }, 1000);
    };

    // Add message to chat
    const addMessage = (message, sender) => {
        if (!chatMessages) return;
        
        const messageElement = document.createElement('div');
        messageElement.classList.add('flex', 'items-start', 'mb-3', sender === 'user' ? 'justify-end' : '');
        
        if (isExpanded) {
            messageElement.classList.add('expanded-message');
        }
        
        const messageContent = document.createElement('div');
        messageContent.classList.add('p-3', 'rounded-lg', 'max-w-3/4');
        
        if (sender === 'user') {
            messageContent.classList.add('bg-blue-600', 'text-white');
            if (isExpanded) {
                messageContent.classList.add('expanded-user-bubble');
            }
        } else {
            messageContent.classList.add('bg-blue-100', 'dark:bg-blue-900', 'text-gray-800', 'dark:text-gray-200');
            if (isExpanded) {
                messageContent.classList.add('expanded-bot-bubble');
            }
        }
        
        messageContent.textContent = message;
        messageElement.appendChild(messageContent);
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    // Add typing indicator
    const addTypingIndicator = () => {
        if (!chatMessages) return;
        
        const typingElement = document.createElement('div');
        typingElement.classList.add('flex', 'items-start', 'typing-indicator', 'mb-3');
        
        const typingContent = document.createElement('div');
        typingContent.classList.add('bg-gray-200', 'dark:bg-gray-700', 'p-3', 'rounded-lg', 'flex', 'space-x-1');
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.classList.add('w-2', 'h-2', 'bg-gray-500', 'dark:bg-gray-400', 'rounded-full', 'animate-bounce');
            dot.style.animationDelay = `${i * 0.2}s`;
            typingContent.appendChild(dot);
        }
        
        typingElement.appendChild(typingContent);
        chatMessages.appendChild(typingElement);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    // Setup event listeners for sending messages
    if (sendMessage) {
        sendMessage.addEventListener('click', sendChatMessage);
    }

    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });
    }

    // Auto-resize textarea based on content
    if (chatInput && chatInput.tagName === 'TEXTAREA') {
        chatInput.addEventListener('input', function() {
            // Reset height to default to accurately calculate the new height
            this.style.height = 'auto';
            
            // Set new height based on content (with a max height)
            const newHeight = Math.min(this.scrollHeight, 180);
            this.style.height = newHeight + 'px';
        });
        
        // Initialize height
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 60) + 'px';
    }

    // Handle suggestion buttons
    chatSuggestions.forEach(button => {
        button.addEventListener('click', () => {
            if (!chatInput) return;
            const suggestion = button.textContent.trim();
            chatInput.value = suggestion;
            sendChatMessage();
        });
    });
    
    // Add CSS for expanded mode
    addExpandedModeStyles();
    
    // Function to add expanded mode styles
    function addExpandedModeStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* Basic styling for expanded mode */
            #chatWindow.expanded {
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            }
            
            #chatMessages.expanded-messages {
                padding: 2rem;
            }
            
            .expanded-message {
                max-width: 70%;
                margin: 1rem auto;
            }
            
            .expanded-user-bubble {
                font-size: 1.1rem;
                line-height: 1.5;
                border-radius: 1rem;
            }
            
            .expanded-bot-bubble {
                font-size: 1.1rem;
                line-height: 1.5;
                border-radius: 1rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            
            .chat-input-container.expanded {
                padding: 1.5rem;
            }
            
            #chatInput.expanded {
                font-size: 1.1rem;
                line-height: 1.6;
                min-height: 60px;
            }
        `;
        document.head.appendChild(style);
    }
}); 
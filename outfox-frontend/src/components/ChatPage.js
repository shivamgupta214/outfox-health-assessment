import React, { useState, useEffect, useRef } from 'react';

const ChatPage = () => {
  // messages state will store objects like { id: number, content: string, role: 'user' | 'ai' | 'status' }
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef(null); // Use useRef to persist the socket instance across renders
  const messagesEndRef = useRef(null); // Ref for scrolling to the latest message

  // Function to scroll to the bottom of the chat window
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Effect for WebSocket connection and message handling
  useEffect(() => {
    const connectWebSocket = () => {
      // Correct WebSocket URL to match your FastAPI endpoint
      const ws = new WebSocket('ws://localhost:8000/ws/ask');
      socketRef.current = ws; // Store the socket in the ref

      ws.onopen = () => {
        console.log('WebSocket connected.');
        setIsConnected(true);
        setMessages((prev) => [...prev, { id: Date.now(), content: 'Connected to AI Chat.', role: 'status' }]);
        scrollToBottom();
      };

      ws.onmessage = (event) => {
        // The server sends plain text summaries or error messages, not JSON
        const aiResponse = event.data;
        setMessages((prev) => [...prev, { id: Date.now(), content: aiResponse, role: 'ai' }]);
        scrollToBottom();
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event);
        setIsConnected(false);
        setMessages((prev) => [...prev, { id: Date.now(), content: 'Disconnected. Attempting to reconnect...', role: 'status' }]);
        // Attempt to reconnect after a delay
        setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setMessages((prev) => [...prev, { id: Date.now(), content: 'WebSocket error. Check console.', role: 'status' }]);
      };
    };

    connectWebSocket(); // Initial connection attempt

    // Cleanup function: close WebSocket when component unmounts
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []); // Empty dependency array means this runs once on mount

  // Effect to scroll to bottom whenever messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = () => {
    const query = input.trim();
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN && query) {
      // The server expects plain text (the natural language query itself)
      socketRef.current.send(query);
      setMessages((prev) => [...prev, { id: Date.now(), content: query, role: 'user' }]);
      setInput(''); // Clear input field
    } else if (!isConnected) {
      setMessages((prev) => [...prev, { id: Date.now(), content: 'Not connected to server. Please wait.', role: 'status' }]);
    } else if (!query) {
      // Optionally handle empty query
      setMessages((prev) => [...prev, { id: Date.now(), content: 'Please enter a query.', role: 'status' }]);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        AI Hospital Data Chat
      </div>

      {/* Chat Window */}
      <div className="chat-window">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`chat-message ${
              msg.role === 'user' ? 'user-message' :
              msg.role === 'ai' ? 'ai-message' :
              'status-message'
            }`}
          >
            {msg.content}
          </div>
        ))}
        <div ref={messagesEndRef} /> {/* Scroll target */}
      </div>

      {/* Input Area */}
      <div className="chat-input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={isConnected ? "Type your message..." : "Connecting..."}
          disabled={!isConnected}
          className="chat-input"
        />
        <button
          onClick={sendMessage}
          disabled={!isConnected || !input.trim()}
          className="chat-send-button"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatPage;

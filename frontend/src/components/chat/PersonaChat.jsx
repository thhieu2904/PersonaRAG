// frontend/src/components/chat/PersonaChat.jsx

import React, { useState, useEffect, useRef } from "react";
import chatService from "../../services/chatService";
import "./PersonaChat.css";

const PersonaChat = () => {
  const [characters, setCharacters] = useState([]);
  const [selectedCharacter, setSelectedCharacter] = useState("");
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef(null);

  // Scroll to bottom when new messages are added
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load characters on component mount
  useEffect(() => {
    const fetchCharacters = async () => {
      try {
        const charactersData = await chatService.getCharacters();
        console.log("📋 Fetched characters:", charactersData);

        // Ensure it's an array
        const charactersArray = Array.isArray(charactersData)
          ? charactersData
          : [];
        setCharacters(charactersArray);

        if (charactersArray.length > 0) {
          const firstChar = charactersArray[0];
          console.log("🎯 First character:", firstChar);
          console.log("🎯 Character ID:", firstChar.character_id);

          setSelectedCharacter(firstChar.character_id);
          // Add welcome message
          setMessages([
            {
              id: 1,
              type: "character",
              content: `Xin chào! Tôi là ${firstChar.name}. Tôi có thể giúp gì cho bạn?`,
              character: firstChar,
              timestamp: new Date(),
            },
          ]);
        } else {
          console.log("⚠️ No characters found");
        }
      } catch (err) {
        setError(
          "Không thể kết nối với server. Vui lòng kiểm tra backend đã chạy chưa."
        );
        console.error("Error fetching characters:", err);
      }
    };

    fetchCharacters();
  }, []);

  // Handle character selection change
  const handleCharacterChange = (characterId) => {
    console.log("🔄 Character change requested:", characterId);
    const character = characters.find((c) => c.character_id === characterId);
    console.log("🔄 Found character:", character);
    console.log("🔄 All characters:", characters);

    setSelectedCharacter(characterId);

    if (character) {
      // Add character introduction message
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          type: "character",
          content: `Xin chào! Tôi là ${character.name}. ${
            character.description || "Tôi có thể giúp gì cho bạn?"
          }`,
          character: character,
          timestamp: new Date(),
        },
      ]);
    }
  };

  // Send message to character
  const sendMessage = async () => {
    if (!currentMessage.trim() || !selectedCharacter) return;

    const userMessage = {
      id: Date.now(),
      type: "user",
      content: currentMessage.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setCurrentMessage("");
    setIsLoading(true);
    setError("");

    try {
      const responseData = await chatService.sendMessage(
        selectedCharacter,
        userMessage.content
      );

      const characterResponse = {
        id: Date.now() + 1,
        type: "character",
        content:
          responseData.advice ||
          responseData.response ||
          "Xin lỗi, tôi không thể trả lời lúc này.",
        character: characters.find((c) => c.character_id === selectedCharacter),
        timestamp: new Date(),
        metadata: {
          sources_used: responseData.sources_used || [],
          confidence_score: responseData.confidence_score || 1.0,
          response_time: responseData.response_time || 0,
          ...responseData.metadata,
        },
      };

      setMessages((prev) => [...prev, characterResponse]);
    } catch (err) {
      setError("Có lỗi khi gửi tin nhắn. Vui lòng thử lại.");
      console.error("Error sending message:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Clear chat
  const clearChat = () => {
    setMessages([]);
    setError("");
  };

  const currentCharacter = characters.find(
    (c) => c.character_id === selectedCharacter
  );

  console.log("🎯 Current state:", {
    selectedCharacter,
    currentCharacter,
    charactersCount: characters.length,
    textareaDisabled: isLoading || !selectedCharacter,
  });

  return (
    <div className="persona-chat">
      <div className="chat-header">
        <div className="character-selector">
          <select
            value={selectedCharacter}
            onChange={(e) => handleCharacterChange(e.target.value)}
            disabled={characters.length === 0}
          >
            <option value="">Chọn nhân vật...</option>
            {characters.map((character, index) => (
              <option
                key={character.character_id || `character-${index}`}
                value={character.character_id || ""}
              >
                {character.name || "Unnamed Character"}
              </option>
            ))}
          </select>
        </div>

        {currentCharacter && (
          <div className="character-info">
            <h3>{currentCharacter.name}</h3>
            <p>
              {currentCharacter.character_type} • {currentCharacter.origin}
            </p>
          </div>
        )}

        <div className="chat-controls">
          <button onClick={clearChat} className="clear-btn">
            🗑️ Xóa chat
          </button>
        </div>
      </div>

      {error && <div className="error-message">⚠️ {error}</div>}

      <div className="chat-messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-header">
              <span className="sender">
                {message.type === "user"
                  ? "👤 Bạn"
                  : `🎭 ${message.character?.name || "Nhân vật"}`}
              </span>
              <span className="timestamp">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
            <div className="message-content">{message.content}</div>
            {message.metadata && message.metadata.sources_used && (
              <div className="message-metadata">
                <small>📚 Dựa trên: {message.metadata.sources_used}</small>
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="message character loading">
            <div className="message-header">
              <span className="sender">
                🎭 {currentCharacter?.name || "Nhân vật"}
              </span>
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <div className="input-container">
          <textarea
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Hỏi ${
              currentCharacter?.name || "nhân vật"
            } một câu gì đó...`}
            disabled={isLoading || !selectedCharacter}
            rows="2"
          />
          <button
            onClick={sendMessage}
            disabled={!currentMessage.trim() || isLoading || !selectedCharacter}
            className="send-btn"
          >
            {isLoading ? "⏳" : "📨"}
          </button>
        </div>

        <div className="input-hint">
          💡 Ví dụ: "Làm thế nào để trở thành một nhà lãnh đạo giỏi?" hoặc "Tôi
          nên làm gì khi gặp khó khăn?"
        </div>
      </div>
    </div>
  );
};

export default PersonaChat;

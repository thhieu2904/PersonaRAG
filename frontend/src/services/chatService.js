// frontend/src/services/chatService.js

import api from "./api";

export const chatService = {
  // Get all available characters
  async getCharacters() {
    try {
      const response = await api.get("/characters/");
      return response.data;
    } catch (error) {
      console.error("Failed to fetch characters:", error);
      throw error;
    }
  },

  // Get specific character by ID
  async getCharacter(characterId) {
    try {
      const response = await api.get(`/characters/${characterId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch character ${characterId}:`, error);
      throw error;
    }
  },

  // Send chat message to character
  async sendMessage(characterId, message) {
    try {
      const response = await api.post("/rag/advice", {
        character_id: characterId,
        user_question: message,
      });
      return response.data;
    } catch (error) {
      console.error("Failed to send message:", error);
      throw error;
    }
  },

  // Get character advice (alias for sendMessage)
  async getAdvice(characterId, question) {
    return this.sendMessage(characterId, question);
  },
};

export default chatService;

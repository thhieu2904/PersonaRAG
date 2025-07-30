import axios from "axios";

// Địa chỉ của backend API. Hãy chắc chắn nó đúng.
const API_BASE_URL = "http://localhost:8000/api/v1/voice";

// Cấu hình một instance của axios để tái sử dụng
const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

/**
 * Lấy danh sách tất cả các nhân vật có sẵn từ backend.
 * @returns {Promise<Object>} Dữ liệu danh sách nhân vật.
 */
export const getCharacters = async () => {
  try {
    const response = await apiClient.get("/characters");
    return response.data;
  } catch (error) {
    console.error("Lỗi khi tải danh sách nhân vật:", error);
    // Ném lỗi ra ngoài để component có thể xử lý
    throw error;
  }
};

/**
 * Gửi yêu cầu tạo giọng nói từ văn bản.
 * @param {string} text - Đoạn văn bản cần đọc.
 * @param {string} characterName - Tên nhân vật được chọn.
 * @returns {Promise<string>} Một URL tạm thời của file audio có thể phát được.
 */
export const generateSpeech = async (text, characterName) => {
  try {
    const response = await apiClient.post(
      "/generate-speech",
      {
        text: text,
        character_name: characterName,
        language: "en",
      },
      {
        // Quan trọng: Yêu cầu backend trả về dữ liệu dạng 'blob'
        // 'blob' là viết tắt của Binary Large Object, phù hợp cho file.
        responseType: "blob",
      }
    );

    // Tạo một URL tạm thời từ dữ liệu audio nhận về
    // để thẻ <audio> của trình duyệt có thể phát được.
    const audioUrl = URL.createObjectURL(response.data);
    return audioUrl;
  } catch (error) {
    console.error("Lỗi khi tạo giọng nói:", error);
    throw error;
  }
};

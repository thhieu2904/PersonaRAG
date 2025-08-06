// frontend/src/services/api.js

import axios from "axios";

// API configuration
const API_BASE_URL = "http://localhost:8000/api/v1";

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes timeout for AI model responses
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log("API Request:", config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error("API Request Error:", error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log("API Response:", response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error("API Response Error:", {
      url: error.config?.url,
      status: error.response?.status,
      message: error.response?.data?.detail || error.message,
    });

    // Handle common errors
    if (error.code === "ECONNREFUSED") {
      throw new Error(
        "Không thể kết nối với server. Vui lòng kiểm tra backend đã chạy chưa."
      );
    }

    if (error.response?.status === 404) {
      throw new Error("API endpoint không tồn tại.");
    }

    if (error.response?.status >= 500) {
      throw new Error("Lỗi server. Vui lòng thử lại sau.");
    }

    return Promise.reject(error);
  }
);

export default api;

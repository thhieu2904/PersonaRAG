// frontend/src/components/debug/ApiTest.jsx

import React, { useState, useEffect } from "react";
import chatService from "../../services/chatService";

const ApiTest = () => {
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const testApi = async () => {
      try {
        console.log("🧪 Testing API...");
        const data = await chatService.getCharacters();
        console.log("📋 API Response:", data);
        console.log("📋 Type:", typeof data);
        console.log("📋 Is Array:", Array.isArray(data));

        if (Array.isArray(data)) {
          console.log("✅ Data is array with length:", data.length);
          data.forEach((char, index) => {
            console.log(`Character ${index}:`, {
              character_id: char.character_id,
              name: char.name,
              hasId: !!char.character_id,
              hasName: !!char.name,
            });
          });
        } else {
          console.log("❌ Data is not array:", data);
        }

        setCharacters(data);
      } catch (err) {
        console.error("❌ API Error:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    testApi();
  }, []);

  if (loading) return <div>🔄 Testing API...</div>;
  if (error) return <div style={{ color: "red" }}>❌ Error: {error}</div>;

  return (
    <div style={{ padding: "20px", fontFamily: "monospace" }}>
      <h2>🧪 API Test Results</h2>

      <div style={{ marginBottom: "20px" }}>
        <strong>Characters Data:</strong>
        <pre
          style={{
            background: "#f5f5f5",
            padding: "10px",
            borderRadius: "5px",
          }}
        >
          {JSON.stringify(characters, null, 2)}
        </pre>
      </div>

      <div style={{ marginBottom: "20px" }}>
        <strong>Characters Count:</strong> {characters.length}
      </div>

      <div style={{ marginBottom: "20px" }}>
        <strong>Select Options Test:</strong>
        <select style={{ width: "200px", padding: "5px" }}>
          <option value="">Chọn nhân vật...</option>
          {characters.map((character, index) => (
            <option
              key={character.character_id || index}
              value={character.character_id}
            >
              {character.name || "Unnamed Character"}
            </option>
          ))}
        </select>
      </div>

      <div>
        <strong>Character Details:</strong>
        <ul>
          {characters.map((character, index) => (
            <li
              key={character.character_id || index}
              style={{ marginBottom: "10px" }}
            >
              <strong>ID:</strong> {character.character_id || "No ID"} <br />
              <strong>Name:</strong> {character.name || "No Name"} <br />
              <strong>Type:</strong> {character.character_type || "No Type"}{" "}
              <br />
              <strong>Origin:</strong> {character.origin || "No Origin"}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ApiTest;

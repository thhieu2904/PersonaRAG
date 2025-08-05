import { useState } from "react";
import "./App.css";
import VoiceSynthesizer from "./components/chat/VoiceSynthesizer";
import PersonaChat from "./components/chat/PersonaChat";
import ApiTest from "./components/debug/ApiTest";
import React from "react";

function App() {
  const [activeTab, setActiveTab] = useState("chat");

  return (
    <div className="App">
      <nav className="app-nav">
        <div className="nav-brand">
          <h1>🎭 PersonaRAG</h1>
          <p>Chat với các nhân vật lịch sử</p>
        </div>
        <div className="nav-tabs">
          <button
            className={activeTab === "chat" ? "active" : ""}
            onClick={() => setActiveTab("chat")}
          >
            💬 Chat
          </button>
          <button
            className={activeTab === "voice" ? "active" : ""}
            onClick={() => setActiveTab("voice")}
          >
            🎙️ Giọng nói
          </button>
          <button
            className={activeTab === "debug" ? "active" : ""}
            onClick={() => setActiveTab("debug")}
          >
            🧪 Debug
          </button>
        </div>
      </nav>

      <main className="app-main">
        {activeTab === "chat" && <PersonaChat />}
        {activeTab === "voice" && <VoiceSynthesizer />}
        {activeTab === "debug" && <ApiTest />}
      </main>
    </div>
  );
}

export default App;

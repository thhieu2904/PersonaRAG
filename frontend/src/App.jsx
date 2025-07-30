import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import VoiceSynthesizer from './components/chat/VoiceSynthesizer'
import React from 'react'


function App() {
  return (
    <div className="App">
      <header className="App-header" style={{ padding: '20px' }}>
        {/* Hiển thị component tạo giọng nói ở đây */}
        <VoiceSynthesizer />
      </header>
    </div>
  );
}

export default App

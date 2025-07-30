import React, { useState, useEffect } from 'react';
import { getCharacters, generateSpeech } from '../../services/voiceService';

// Component giao diện chính
const VoiceSynthesizer = () => {
  // State để lưu danh sách nhân vật
  const [characters, setCharacters] = useState([]);
  // State để lưu nhân vật đang được chọn
  const [selectedCharacter, setSelectedCharacter] = useState('');
  // State cho văn bản người dùng nhập
  const [text, setText] = useState('Xin chào, đây là Hội đồng Quân sư.');
  // State để lưu URL của file audio đã tạo
  const [audioUrl, setAudioUrl] = useState(null);
  // State để quản lý trạng thái loading
  const [isLoading, setIsLoading] = useState(false);
  // State để hiển thị thông báo lỗi
  const [error, setError] = useState('');

  // Hook useEffect để tải danh sách nhân vật khi component được render lần đầu
  useEffect(() => {
    const fetchCharacters = async () => {
      try {
        const data = await getCharacters();
        const characterNames = (data.characters || []).map(c => c.name);
        setCharacters(characterNames);
        
        // Tự động chọn nhân vật đầu tiên trong danh sách nếu có
        if (characterNames.length > 0) {
          setSelectedCharacter(characterNames[0]);
        }
      } catch (err) {
        setError('Không thể tải danh sách nhân vật. Vui lòng kiểm tra xem backend đã chạy chưa.');
      }
    };
    
    fetchCharacters();
  }, []); // Mảng rỗng `[]` đảm bảo hook này chỉ chạy một lần duy nhất

  // Hàm xử lý khi người dùng nhấn nút "Tạo Giọng Nói"
  const handleGenerateSpeech = async () => {
    if (!text || !selectedCharacter) {
      setError('Vui lòng chọn nhân vật và nhập văn bản.');
      return;
    }
    
    setIsLoading(true);
    setError('');
    setAudioUrl(null); // Xóa audio cũ
    
    try {
      const url = await generateSpeech(text, selectedCharacter);
      setAudioUrl(url);
    } catch (err) {
      setError('Tạo giọng nói thất bại. Vui lòng thử lại.');
    } finally {
      setIsLoading(false);
    }
  };

  // JSX để render giao diện
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', maxWidth: '600px', margin: 'auto', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h2 style={{ textAlign: 'center' }}>Hội Đồng Quân Sư - Voice Synthesizer</h2>
      
      {/* Dropdown chọn nhân vật */}
      <div style={{ marginBottom: '15px' }}>
        <label htmlFor="character-select" style={{ marginRight: '10px' }}>Chọn nhân vật:</label>
        <select
          id="character-select"
          value={selectedCharacter}
          onChange={(e) => setSelectedCharacter(e.target.value)}
          disabled={characters.length === 0 || isLoading}
          style={{ padding: '8px' }}
        >
          {characters.length > 0 ? (
            characters.map((char) => (
              <option key={char} value={char}>
                {char}
              </option>
            ))
          ) : (
            <option>Đang tải...</option>
          )}
        </select>
      </div>

      {/* Textarea để nhập văn bản */}
      <div style={{ marginBottom: '15px' }}>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows="5"
          style={{ width: '100%', padding: '10px', boxSizing: 'border-box', resize: 'vertical' }}
          placeholder="Nhập văn bản cần đọc..."
          disabled={isLoading}
        />
      </div>

      {/* Nút bấm để tạo giọng nói */}
      <button
        onClick={handleGenerateSpeech}
        disabled={isLoading}
        style={{ padding: '10px 20px', cursor: 'pointer', width: '100%', fontSize: '16px' }}
      >
        {isLoading ? 'Đang xử lý...' : 'Tạo Giọng Nói 🎙️'}
      </button>

      {/* Hiển thị lỗi nếu có */}
      {error && <p style={{ color: 'red', marginTop: '15px' }}>{error}</p>}
      
      {/* Hiển thị trình phát audio khi đã có kết quả */}
      {audioUrl && (
        <div style={{ marginTop: '20px' }}>
          <h4>Kết quả:</h4>
          <audio controls autoPlay src={audioUrl} style={{ width: '100%' }}>
            Trình duyệt của bạn không hỗ trợ thẻ audio.
          </audio>
        </div>
      )}
    </div>
  );
};

export default VoiceSynthesizer;

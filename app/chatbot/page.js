'use client'
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MoonIcon, SunIcon } from '@heroicons/react/outline';
import Link from 'next/link';

export default function Chatbot() {
  const [text, setText] = useState('');
  const [messages, setMessages] = useState([]);
  const [isDarkTheme, setIsDarkTheme] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  // Load messages from localStorage on component mount
  useEffect(() => {
    const stored = localStorage.getItem('prof_chat_history');
    if (stored) {
      try {
        setMessages(JSON.parse(stored));
      } catch (e) {
        console.error('Failed to parse stored messages:', e);
      }
    }
  }, []);

  // Save messages to localStorage whenever messages change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('prof_chat_history', JSON.stringify(messages));
    }
  }, [messages]);

  const addMessage = (message) => {
    setMessages(prev => [...prev, { ...message, id: Date.now() + Math.random() }]);
  };

  const clearChat = () => {
    setMessages([]);
    localStorage.removeItem('prof_chat_history');
  };

  const handleSubmit = async () => {
    if (isLoading || !text.trim()) {
      if (!text.trim()) alert("Please enter a message");
      return;
    }

    const userMessage = text.trim();
    setText('');
    
    // Add user message
    addMessage({ text: userMessage, sender: 'user' });
    
    setIsLoading(true);
    
    // Add loading message
    const loadingId = Date.now();
    addMessage({ text: '', sender: 'bot', id: loadingId, loading: true });

    try {
      // Use the working API endpoint structure
      const response = await fetch('/api/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: userMessage }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      console.log('API Response:', data); // Debug log

      // Remove loading message
      setMessages(prev => prev.filter(m => m.id !== loadingId));

      // Add bot answer
      const answer = data.llm_answer || data.answer || "No answer returned";
      addMessage({ text: answer, sender: 'bot' });

      // Process professor results
      const professors = data.matches || data.professors || [];
      
      if (professors.length > 0) {
        // Create a single formatted message with all professors
        let professorText = "Found professors:\n\n";
        
        professors.slice(0, 5).forEach((prof, index) => {
          const name = prof.name || 'Unknown Professor';
          const subject = prof.subject || 'Unknown Subject';
          const rating = prof.rating || prof.stars || prof.avg_rating || 'N/A';
          const score = prof.final_score || prof.score || 0;
          
          professorText += `${index + 1}. ${name}\n`;
          professorText += `   Subject: ${subject}\n`;
          professorText += `   Rating: ${rating}⭐\n`;
          professorText += `   Match Score: ${(score * 100).toFixed(1)}%\n\n`;
        });
        
        addMessage({ 
          text: professorText, 
          sender: 'results',
          professors: professors.slice(0, 5)
        });
      }

    } catch (error) {
      console.error('Error:', error);
      // Remove loading message
      setMessages(prev => prev.filter(m => m.id !== loadingId));
      addMessage({ text: `Error: ${error.message}`, sender: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const toggleTheme = () => setIsDarkTheme(!isDarkTheme);

  return (
    <div className={`flex h-screen ${isDarkTheme ? 'bg-gray-900 text-white' : 'bg-white text-gray-900'}`}>
      {/* Sidebar */}
      <div className={`w-64 p-4 ${isDarkTheme ? 'bg-gray-800' : 'bg-gray-200'}`}>
        <div className="flex justify-between items-center mb-6">
          <h1 className={`text-2xl font-bold ${isDarkTheme ? 'text-white' : 'text-gray-900'}`}>
            Prof<span className="text-green-500">Finder</span>
          </h1>
          <motion.div 
            animate={{ rotate: 360 }} 
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className={`w-4 h-4 rounded-full ${isDarkTheme ? 'bg-green-400' : 'bg-green-600'}`} 
          />
        </div>
        
        <div className="space-y-2 mb-6">
          {["Mathematics", "Computer Science", "Chemistry", "Physics", "Psychology"].map((dept) => (
            <div key={dept} className={`rounded p-2 text-sm ${isDarkTheme ? 'bg-gray-700 text-gray-300' : 'bg-gray-300 text-gray-700'}`}>
              {dept}
            </div>
          ))}
        </div>
        
        <button 
          onClick={clearChat}
          className="w-full p-2 text-sm bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
        >
          Clear Chat
        </button>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header with controls */}
        <div className="absolute top-4 right-4 flex space-x-2">
          <Link href='/'>
            <motion.button 
              className="bg-green-600 text-white px-4 py-2 rounded-md font-medium hover:bg-green-700 transition-colors"
              whileHover={{ scale: 1.05 }} 
              whileTap={{ scale: 0.95 }}
            >
              Home
            </motion.button>
          </Link>
          
          <motion.button 
            onClick={toggleTheme}
            className={`p-2 rounded-full ${isDarkTheme ? 'bg-gray-800 text-white' : 'bg-gray-200 text-gray-900'}`}
            whileHover={{ scale: 1.1 }}
          >
            {isDarkTheme ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}
          </motion.button>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 pt-20">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-20">
              <h2 className="text-2xl font-bold mb-4">Welcome to ProfFinder!</h2>
              <p>Ask me about professors, courses, or anything related to academics.</p>
              <div className="mt-4 text-sm">
                <p>Try asking:</p>
                <ul className="mt-2 space-y-1">
                  <li>"Best calculus professors"</li>
                  <li>"Chemistry teachers with good ratings"</li>
                  <li>"Computer science courses"</li>
                </ul>
              </div>
            </div>
          )}
          
          {messages.map((message) => {
            if (message.sender === 'user') {
              return (
                <motion.div 
                  key={message.id} 
                  initial={{ opacity: 0, y: 20 }} 
                  animate={{ opacity: 1, y: 0 }}
                  className="max-w-[70%] ml-auto bg-green-600 text-white rounded-lg p-3"
                >
                  {message.text}
                </motion.div>
              );
            }
            
            if (message.sender === 'error') {
              return (
                <motion.div 
                  key={message.id} 
                  initial={{ opacity: 0, y: 20 }} 
                  animate={{ opacity: 1, y: 0 }}
                  className="max-w-[70%] bg-red-600 text-white rounded-lg p-3"
                >
                  {message.text}
                </motion.div>
              );
            }
            
            if (message.sender === 'results') {
              return (
                <motion.div 
                  key={message.id} 
                  initial={{ opacity: 0, y: 20 }} 
                  animate={{ opacity: 1, y: 0 }}
                  className={`max-w-[80%] rounded-lg p-4 ${isDarkTheme ? 'bg-gray-800' : 'bg-gray-100'}`}
                >
                  <div className="whitespace-pre-line font-mono text-sm">
                    {message.text}
                  </div>
                </motion.div>
              );
            }
            
            // Default bot message
            return (
              <motion.div 
                key={message.id} 
                initial={{ opacity: 0, y: 20 }} 
                animate={{ opacity: 1, y: 0 }}
                className={`max-w-[70%] rounded-lg p-3 ${isDarkTheme ? 'bg-gray-700' : 'bg-gray-200'}`}
              >
                {message.loading && (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-500"></div>
                    <span>{message.text}</span>
                  </div>
                )}
                {!message.loading && message.text}
              </motion.div>
            );
          })}
        </div>

        {/* Input Area */}
        <div className={`p-4 border-t ${isDarkTheme ? 'bg-gray-800 border-gray-700' : 'bg-gray-100 border-gray-200'}`}>
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about professors..."
              className={`flex-1 p-3 rounded-lg border ${isDarkTheme ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' : 'bg-white border-gray-300 text-gray-900'} focus:outline-none focus:ring-2 focus:ring-green-500`}
              disabled={isLoading}
            />
            <button
              onClick={handleSubmit}
              disabled={isLoading || !text.trim()}
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:bg-gray-500 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? 'Searching...' : 'Send'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
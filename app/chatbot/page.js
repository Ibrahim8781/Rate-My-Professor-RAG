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

  useEffect(() => {
    const stored = localStorage.getItem('prof_chat_history');
    if (stored) setMessages(JSON.parse(stored));
  }, []);

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
    if (isLoading || !text.trim()) return;
    const userMessage = text.trim();
    setText('');
    addMessage({ text: userMessage, sender: 'user' });
    setIsLoading(true);
    const loadingId = Date.now();
    addMessage({ text: '', sender: 'bot', id: loadingId, loading: true });

    try {
      const response = await fetch('/api/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: userMessage }),
      });
      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      const data = await response.json();

      setMessages(prev => prev.filter(m => m.id !== loadingId));
      addMessage({ text: data.llm_answer || "No answer returned", sender: 'bot' });

    } catch (error) {
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
    <div className={`flex h-screen ${isDarkTheme ? 'bg-gradient-to-br from-gray-900 via-black to-gray-800 text-white' : 'bg-gray-100 text-gray-900'}`}>
      {/* Sidebar */}
      <div className={`w-64 p-6 backdrop-blur-lg ${isDarkTheme ? 'bg-white/10' : 'bg-gray-200/70'} border-r border-gray-700`}>
        <div className="flex justify-between items-center mb-10">
          <h1 className="text-2xl font-extrabold tracking-wide">
            Prof<span className="text-green-400">Finder</span>
          </h1>
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="w-4 h-4 rounded-full bg-green-400 shadow-lg shadow-green-600/50"
          />
        </div>

        <div className="space-y-3 mb-8">
          {["Mathematics", "Computer Science", "Chemistry", "Physics", "Psychology", "Biology","Engineering","English","History","Political Science","Psychology"].map((dept) => (
            < div key = { dept } className = "rounded-lg px-3 py-2 text-sm cursor-pointer hover:scale-105 transform transition bg-white/10 hover:bg-green-500 hover:text-white" >
            { dept }
            </div>
          ))}
      </div>

      <button
        onClick={clearChat}
        className="w-full py-2 rounded-lg bg-red-500 hover:bg-red-600 text-white font-medium transition"
      >
        Clear Chat
      </button>
    </div>

      {/* Main Chat */ }
  <div className="flex-1 flex flex-col relative">
    {/* Controls */}
    <div className="absolute top-4 right-6 flex space-x-3">
      <Link href='/'>
        <motion.button
          className="bg-green-500 px-5 py-2 rounded-lg shadow-lg hover:bg-green-600 transition"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Home
        </motion.button>
      </Link>

      <motion.button
        onClick={toggleTheme}
        className={`p-3 rounded-full shadow-lg ${isDarkTheme ? 'bg-gray-800 text-yellow-400' : 'bg-gray-300 text-gray-900'}`}
        whileHover={{ scale: 1.1 }}
      >
        {isDarkTheme ? <SunIcon className="h-6 w-6" /> : <MoonIcon className="h-6 w-6" />}
      </motion.button>
    </div>

    {/* Messages */}
    <div className="flex-1 overflow-y-auto px-6 py-20 space-y-4">
      {messages.length === 0 && (
        <div className="text-center opacity-70 mt-20">
          <h2 className="text-3xl font-bold mb-4">👋 Welcome to ProfFinder</h2>
          <p className="mb-2">Ask about professors, courses, or ratings.</p>
          <h3 className="font-semibold mb-2">💡 Try asking:</h3>
          <ul className="space-y-2 text-sm opacity-80">
            <li>• Best calculus professors</li>
            <li>• Computer science teachers with top ratings</li>
            <li>• Physics professors good at explaining</li>
            <li>• English professors with high student feedback</li>
            <li>• Psychology professors with 5⭐ ratings</li>
          </ul>
        </div>
      )}
      {messages.map((m) => (
        <motion.div
          key={m.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`max-w-[75%] rounded-2xl px-4 py-3 shadow-md ${m.sender === 'user'
            ? 'ml-auto bg-green-600 text-white'
            : m.sender === 'error'
              ? 'bg-red-500 text-white'
              : isDarkTheme
                ? 'bg-white/10'
                : 'bg-gray-200'
            }`}
        >
          {m.loading ? "..." : m.text}
        </motion.div>
      ))}
    </div>

    {/* Input */}
    <div className={`p-6 border-t ${isDarkTheme ? 'border-gray-700 bg-gray-900/70' : 'bg-white/80 border-gray-300'} backdrop-blur-lg`}>
      <div className="flex items-center space-x-3">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about professors..."
          className={`flex-1 p-3 rounded-xl focus:ring-2 focus:ring-green-500 border ${isDarkTheme ? 'bg-gray-800 border-gray-700 text-white' : 'bg-white border-gray-300'}`}
          disabled={isLoading}
        />
        <button
          onClick={handleSubmit}
          disabled={isLoading || !text.trim()}
          className="px-6 py-3 rounded-xl font-semibold bg-green-500 hover:bg-green-600 text-white shadow-lg transition disabled:bg-gray-500 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Searching...' : 'Send'}
        </button>
      </div>
    </div>
  </div>
    </div >
  );
}

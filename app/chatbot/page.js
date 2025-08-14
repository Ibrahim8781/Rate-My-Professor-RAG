'use client'
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MoonIcon, SunIcon } from '@heroicons/react/outline';
import Link from 'next/link';
import { v4 as uuidv4 } from 'uuid';

export default function Chatbot() {
  const [text, setText] = useState('');
  const [messages, setMessages] = useState([]); // {id, sender, text, meta?}
  const [isDarkTheme, setIsDarkTheme] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  // Persist messages in localStorage
  useEffect(() => {
    localStorage.setItem('prof_chat_history', JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    const stored = localStorage.getItem('prof_chat_history');
    if (stored) setMessages(JSON.parse(stored));
  }, []);

  const pushMessage = (msg) => {
    setMessages(prev => [...prev, msg]);
  };

  const handleSubmit = async () => {
    if (isLoading) return; // prevent multiple submits
    if (!text.trim()) {
      alert("The message cannot be empty");
      return;
    }

    const userMsg = { id: uuidv4(), text: text, sender: 'user' };
    pushMessage(userMsg);

    const userText = text;
    setText('');
    setIsLoading(true);

    // temporary thinking message
    const thinkingId = uuidv4();
    pushMessage({ id: thinkingId, text: 'Thinking...', sender: 'bot', meta: { loading: true } });

    try {
      const response = await fetch('/api/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: userText }),
      });

      if (!response.ok) throw new Error(`Server error ${response.status}`);

      const data = await response.json();
      setMessages(prev => prev.filter(m => m.id !== thinkingId));

      // LLM answer
      const llmText = data.llm_answer || "No answer returned";
      pushMessage({ id: uuidv4(), text: llmText, sender: 'bot' });

      // --- New: cited professors first ---
      const matches = Array.isArray(data.matches) ? data.matches : [];
      const cited = Array.isArray(data.sources_used) ? data.sources_used : [];

      // build maps for quick lookup
      const byId = new Map(matches.map(m => [m.id, m]));
      const citedSet = new Set(cited);

      // Cited section
      const citedMatches = cited.map(id => byId.get(id)).filter(Boolean);
      if (citedMatches.length > 0) {
        pushMessage({ id: uuidv4(), text: 'Cited Professors:', sender: 'header' });
        citedMatches.forEach((m) => {
          pushMessage({
            id: uuidv4(),
            text: `${m.name || m.id} • ${m.subject} • ${m.stars}★\n${m.review || ''}`,
            sender: 'match',
            meta: { score: m.score }
          });
        });
      }

      // Other top matches
      const otherMatches = matches.filter(m => !citedSet.has(m.id));
      if (otherMatches.length > 0) {
        pushMessage({ id: uuidv4(), text: 'Other Matches:', sender: 'header' });
        otherMatches.forEach((m) => {
          pushMessage({
            id: uuidv4(),
            text: `${m.name || m.id} • ${m.subject} • ${m.stars}★\n${m.review || ''}`,
            sender: 'match',
            meta: { score: m.score }
          });
        });
      }
    } catch (err) {
      setMessages(prev => prev.filter(m => m.id !== thinkingId));
      pushMessage({ id: uuidv4(), text: `Error: ${err.message}`, sender: 'bot' });
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
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
            Prof<span className="text-green-500">In</span>
          </h1>
          <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className={`w-4 h-4 rounded-full ${isDarkTheme ? 'bg-gray-400' : 'bg-gray-600'}`} />
        </div>
        <div className="space-y-2">
          {["Algebra Dept", "Philosophy Dept", "Psychology Dept", "Organic Chemistry Dept", "Physics Dept"].map((dept) => (
            <div key={dept} className={`rounded p-2 ${isDarkTheme ? 'bg-green-700' : 'bg-green-500'}`}>{dept}</div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="pt-24 flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => {
            if (message.sender === 'header') {
              return <div key={message.id} className="text-sm font-bold uppercase opacity-70">{message.text}</div>;
            }

            if (message.sender === 'match') {
              return (
                <div key={message.id} className="max-w-md bg-gray-700 rounded-lg p-3">
                  <div className="font-semibold">{message.text.split('\n')[0]}</div>
                  <div className="text-sm whitespace-pre-line mt-1">{message.text.split('\n').slice(1).join('\n')}</div>
                  {message.meta?.score !== undefined && (
                    <div className="text-xs mt-2 opacity-80">
                      Score: {message.meta.score.toFixed(4)} ({(message.meta.score * 100).toFixed(1)}%)
                    </div>
                  )}
                </div>
              );
            }

            const isUser = message.sender === 'user';
            const bubbleClass = isUser ? 'ml-auto bg-green-600' : 'bg-gray-700';
            return (
              <motion.div key={message.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                className={`max-w-[60%] ${isUser ? 'ml-auto' : ''} ${bubbleClass} rounded-lg p-3 text-sm`}>
                {message.text}
              </motion.div>
            );
          })}
        </div>

        {/* Input */}
        <div className={`p-4 ${isDarkTheme ? 'bg-gray-800' : 'bg-gray-200'}`}>
          <div className="flex items-center bg-gray-700 rounded-full">
            <input
              type="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message Chatin..."
              className={`flex-1 bg-transparent p-3 rounded-l-full focus:outline-none ${isDarkTheme ? 'text-white' : 'text-white'}`}
            />
            <button
              disabled={isLoading}
              onClick={handleSubmit}
              className={`bg-green-600 text-white rounded-full p-2 m-1 ${isDarkTheme ? '' : 'bg-green-500'} ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}>
              {isLoading ? "Thinking..." : (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none"
                  viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Theme & Nav */}
        <div className="absolute top-4 right-4">
          <motion.button onClick={toggleTheme}
            className={`p-2 rounded-full ${isDarkTheme ? 'bg-gray-800 text-white' : 'bg-gray-200 text-gray-900'}`}
            initial={{ scale: 1 }} animate={{ scale: 1.1 }} transition={{ duration: 0.3 }}>
            {isDarkTheme ? (<SunIcon className="h-6 w-6" />) : (<MoonIcon className="h-6 w-6" />)}
          </motion.button>
        </div>
        <div className="absolute top-4 right-20">
          <motion.button className="bg-[#19a08e] text-white px-6 py-2 rounded-md font-semibold hover:bg-[#138f7f] shadow-md hover:shadow-lg transition-all"
            whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Link href='/'>Home</Link>
          </motion.button>
        </div>
      </div>
    </div>
  );
}

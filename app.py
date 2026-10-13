import React, { useState, useRef, useEffect } from 'react';
import { 
  Sparkles, 
  Trash2, 
  Send, 
  ChevronDown, 
  ChevronUp, 
  Copy, 
  Check, 
  Terminal, 
  Code2, 
  FileCode, 
  Menu, 
  X,
  Flame,
  Award
} from 'lucide-react';

// Themes configuration matching PyBuddy specifications
type ThemeMode = 'light' | 'dark' | 'sunset';

interface ThemeConfig {
  name: string;
  icon: string;
  bg: string;
  surface: string;
  line: string;
  ink: string;
  muted: string;
  accent: string;
  accentSoft: string;
  onAccent: string;
  userBg: string;
  userLine: string;
  userInk: string;
  heroGradient: string;
  termBg: string;
  codeBg: string;
}

const THEMES: Record<ThemeMode, ThemeConfig> = {
  light: {
    name: 'Terang',
    icon: '☀️',
    bg: '#F4F7FC',
    surface: '#FFFFFF',
    line: '#D5DFEF',
    ink: '#182642',
    muted: '#647493',
    accent: '#2B6CB0',
    accentSoft: '#EBF8FF',
    onAccent: '#FFFFFF',
    userBg: '#DCEEFE',
    userLine: '#90CDF4',
    userInk: '#1A365D',
    heroGradient: 'linear-gradient(135deg, #3182CE, #2B6CB0)',
    termBg: '#1A202C',
    codeBg: '#EAEFF7',
  },
  dark: {
    name: 'Gelap',
    icon: '🌙',
    bg: '#0B132B',
    surface: '#1C2541',
    line: '#3A4D78',
    ink: '#F0F4F8',
    muted: '#9FB3C8',
    accent: '#4FD1C5',
    accentSoft: '#1D3B48',
    onAccent: '#0B132B',
    userBg: '#134E4A',
    userLine: '#2DD4BF',
    userInk: '#CCFBF1',
    heroGradient: 'linear-gradient(135deg, #2B6CB0, #1A365D)',
    termBg: '#070B16',
    codeBg: '#283559',
  },
  sunset: {
    name: 'Senja',
    icon: '🌇',
    bg: '#FFF5F0',
    surface: '#FFFFFF',
    line: '#FBD38D',
    ink: '#2D3748',
    muted: '#7B341E',
    accent: '#DD6B20',
    accentSoft: '#FFFAF0',
    onAccent: '#FFFFFF',
    userBg: '#FEEBC8',
    userLine: '#FBD38D',
    userInk: '#7B341E',
    heroGradient: 'linear-gradient(135deg, #ED8936, #DD6B20)',
    termBg: '#2C1A1D',
    codeBg: '#FEEBC8',
  },
};

const TOPICS = [
  { emoji: '🐣', label: 'Dasar Python', question: 'Jelaskan dasar-dasar Python untuk pemula: variabel, tipe data, dan print.' },
  { emoji: '📦', label: 'List, Tuple & Dict', question: 'Jelaskan perbedaan list, tuple, dan dictionary, beserta kapan memakainya.' },
  { emoji: '🔁', label: 'Perulangan & Kondisi', question: 'Jelaskan if-else dan perulangan for/while dengan analogi sehari-hari.' },
  { emoji: '🧩', label: 'Fungsi & Modul', question: 'Jelaskan cara membuat fungsi di Python dan cara memakai modul.' },
  { emoji: '🐞', label: 'Debug Error', question: 'Ajari aku cara membaca pesan error Python dan menemukan penyebabnya.' },
  { emoji: '📝', label: 'Latihan Soal', question: 'Beri aku satu latihan soal Python untuk pemula, tanpa kunci jawaban dulu.' },
];

const QUICK_STARTS = [
  { emoji: '📦', text: 'Apa bedanya list dan tuple?' },
  { emoji: '🔁', text: 'Jelaskan perulangan for dengan analogi' },
  { emoji: '🐞', text: 'Kenapa muncul IndentationError?' },
  { emoji: '📝', text: 'Beri aku latihan soal tentang if-else' },
];

const LEVEL_TITLES = ['Pemula', 'Penjelajah', 'Pendekar Kode', 'Jagoan Python', 'Master Python'];
const XP_PER_QUESTION = 10;
const XP_PER_LEVEL = 50;

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function App() {
  const [theme, setTheme] = useState<ThemeMode>('light');
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputPrompt, setInputPrompt] = useState('');
  const [selectedTopic, setSelectedTopic] = useState<number | null>(null);
  const [isAboutOpen, setIsAboutOpen] = useState(false);
  const [isPythonCodeModalOpen, setIsPythonCodeModalOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [xp, setXp] = useState(0);
  const [asked, setAsked] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [toast, setToast] = useState<{ message: string; icon: string } | null>(null);
  const [copiedCode, setCopiedCode] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const currentTheme = THEMES[theme];

  const currentLevel = Math.floor(xp / XP_PER_LEVEL) + 1;
  const intoLevel = xp % XP_PER_LEVEL;
  const levelTitle = LEVEL_TITLES[Math.min(currentLevel - 1, LEVEL_TITLES.length - 1)];
  const progressPct = Math.min(100, Math.round((intoLevel / XP_PER_LEVEL) * 100));

  const showToast = (message: string, icon: string) => {
    setToast({ message, icon });
    setTimeout(() => {
      setToast(null);
    }, 3000);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = (textToSend?: string) => {
    const query = (textToSend || inputPrompt).trim();
    if (!query || isLoading) return;

    const newMessages: Message[] = [...messages, { role: 'user', content: query }];
    setMessages(newMessages);
    setInputPrompt('');
    setIsLoading(true);

    // Provide intelligent Python tutor replies with structured markdown & code snippets
    setTimeout(() => {
      const reply = generatePythonReply(query);
      setMessages([...newMessages, { role: 'assistant', content: reply }]);
      setIsLoading(false);

      const oldLevel = Math.floor(xp / XP_PER_LEVEL) + 1;
      const newXp = xp + XP_PER_QUESTION;
      const newAsked = asked + 1;
      setXp(newXp);
      setAsked(newAsked);

      const newLevel = Math.floor(newXp / XP_PER_LEVEL) + 1;
      if (newLevel > oldLevel) {
        showToast('Naik level! Kamu hebat 🎉', '🏆');
      } else {
        showToast(`+${XP_PER_QUESTION} XP`, '⭐');
      }
    }, 700);
  };

  const handleReset = () => {
    setMessages([]);
    setXp(0);
    setAsked(0);
    setSelectedTopic(null);
    showToast('Percakapan telah direset!', '🗑️');
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  return (
    <div 
      className="min-h-screen flex flex-col md:flex-row transition-colors duration-200"
      style={{ backgroundColor: currentTheme.bg, color: currentTheme.ink }}
    >
      {/* Toast Notification */}
      {toast && (
        <div className="fixed top-5 right-5 z-50 flex items-center gap-2.5 px-4 py-3 rounded-xl bg-slate-900 text-white shadow-2xl animate-bounce text-sm font-semibold border border-slate-700">
          <span className="text-lg">{toast.icon}</span>
          <span>{toast.message}</span>
        </div>
      )}

      {/* Mobile Header Bar */}
      <div 
        className="md:hidden flex items-center justify-between p-4 border-b z-20 sticky top-0"
        style={{ backgroundColor: currentTheme.surface, borderColor: currentTheme.line }}
      >
        <div className="flex items-center gap-2.5">
          <div 
            className="w-9 h-9 rounded-xl flex items-center justify-center text-lg shadow-sm"
            style={{ background: currentTheme.heroGradient, color: '#fff' }}
          >
            🐍
          </div>
          <div>
            <div className="font-extrabold text-base leading-tight">PyBuddy</div>
            <div className="text-xs" style={{ color: currentTheme.muted }}>Teman belajar Python</div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsPythonCodeModalOpen(true)}
            className="px-2.5 py-1.5 text-xs font-semibold rounded-lg flex items-center gap-1 border"
            style={{ borderColor: currentTheme.line, backgroundColor: currentTheme.surface }}
            title="Lihat Kode Python Streamlit"
          >
            <FileCode size={14} />
            <span>Kode Python</span>
          </button>
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 rounded-lg border"
            style={{ borderColor: currentTheme.line }}
          >
            {isMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Sidebar Navigation */}
      <aside 
        className={`
          fixed md:static inset-y-0 left-0 z-40 w-72 md:w-80 flex flex-col shrink-0 border-r transition-transform duration-200 ease-in-out
          ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
        style={{ 
          backgroundColor: currentTheme.surface, 
          borderColor: currentTheme.line 
        }}
      >
        {/* Brand */}
        <div className="p-5 pb-4 border-b flex items-center justify-between" style={{ borderColor: currentTheme.line }}>
          <div className="flex items-center gap-3">
            <div 
              className="w-11 h-11 rounded-2xl flex items-center justify-center text-2xl shadow-sm"
              style={{ background: currentTheme.heroGradient, color: '#fff' }}
            >
              🐍
            </div>
            <div>
              <h1 className="font-extrabold text-xl tracking-tight leading-tight">PyBuddy</h1>
              <p className="text-xs font-medium" style={{ color: currentTheme.muted }}>Teman belajar Python</p>
            </div>
          </div>

          <button 
            onClick={() => setIsMobileMenuOpen(false)}
            className="md:hidden p-1.5 rounded-lg opacity-70 hover:opacity-100"
          >
            <X size={18} />
          </button>
        </div>

        {/* Scrollable navigation area */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
          
          {/* Topic Section */}
          <div>
            <div 
              className="text-xs font-bold uppercase tracking-wider mb-2.5 px-2"
              style={{ color: currentTheme.muted }}
            >
              Pilih topik belajar
            </div>
            <div className="space-y-1">
              {TOPICS.map((t, idx) => {
                const isActive = selectedTopic === idx;
                return (
                  <button
                    key={idx}
                    onClick={() => {
                      setSelectedTopic(idx);
                      handleSendMessage(t.question);
                      setIsMobileMenuOpen(false);
                    }}
                    className="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all text-left group"
                    style={{
                      backgroundColor: isActive ? currentTheme.accentSoft : 'transparent',
                      color: isActive ? currentTheme.accent : currentTheme.ink,
                      borderLeft: isActive ? `3px solid ${currentTheme.accent}` : '3px solid transparent'
                    }}
                  >
                    <span className="text-base group-hover:scale-110 transition-transform">{t.emoji}</span>
                    <span className="truncate">{t.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Theme Selector Section (Perbaikan bagian ini agar tidak ketutupan / berantakan) */}
          <div className="pt-2">
            <div 
              className="text-xs font-bold uppercase tracking-wider mb-2.5 px-2 block"
              style={{ color: currentTheme.muted }}
            >
              Tampilan
            </div>
            
            <div className="grid grid-cols-3 gap-2 px-1">
              {(Object.keys(THEMES) as ThemeMode[]).map((thmKey) => {
                const t = THEMES[thmKey];
                const isActive = theme === thmKey;
                return (
                  <button
                    key={thmKey}
                    onClick={() => setTheme(thmKey)}
                    title={t.name}
                    className="flex flex-col items-center justify-center py-2 px-1 rounded-xl border text-center transition-all cursor-pointer"
                    style={{
                      backgroundColor: isActive ? currentTheme.accentSoft : currentTheme.surface,
                      borderColor: isActive ? currentTheme.accent : currentTheme.line,
                      boxShadow: isActive ? `0 0 0 1px ${currentTheme.accent}` : 'none',
                    }}
                  >
                    <span className="text-xl mb-0.5">{t.icon}</span>
                    <span className="text-[11px] font-bold" style={{ color: isActive ? currentTheme.accent : currentTheme.muted }}>
                      {t.name}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Divider */}
          <div className="h-px w-full" style={{ backgroundColor: currentTheme.line }} />

          {/* About PyBuddy Accordion */}
          <div className="rounded-xl border overflow-hidden" style={{ borderColor: currentTheme.line }}>
            <button
              onClick={() => setIsAboutOpen(!isAboutOpen)}
              className="w-full flex items-center justify-between p-3 text-left font-bold text-xs"
              style={{ backgroundColor: currentTheme.surface }}
            >
              <span className="flex items-center gap-1.5">
                <span>ℹ️</span>
                <span>Tentang PyBuddy</span>
              </span>
              {isAboutOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>
            {isAboutOpen && (
              <div 
                className="p-3 text-xs leading-relaxed border-t space-y-2"
                style={{ 
                  backgroundColor: currentTheme.bg,
                  borderColor: currentTheme.line,
                  color: currentTheme.muted 
                }}
              >
                <p>
                  <strong className="text-ink">Untuk siapa?</strong> Mahasiswa dan pelajar pemula yang baru belajar Python dan sering bingung saat bertemu konsep baru atau error.
                </p>
                <p>
                  <strong className="text-ink">Bisa bantu apa?</strong> Menjelaskan konsep dengan analogi sederhana, mencari penyebab error, memberi contoh kode pendek, dan latihan soal.
                </p>
              </div>
            )}
          </div>

          {/* Lihat Solusi Kode Python / Streamlit Button */}
          <button
            onClick={() => setIsPythonCodeModalOpen(true)}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border font-bold text-xs transition-colors"
            style={{ 
              borderColor: currentTheme.accent, 
              color: currentTheme.accent, 
              backgroundColor: currentTheme.accentSoft 
            }}
          >
            <FileCode size={15} />
            <span>Lihat Solusi Kode Streamlit (.py)</span>
          </button>

          {/* Reset Conversation Button */}
          <button
            onClick={handleReset}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border font-bold text-xs transition-colors hover:bg-red-50 text-red-600 border-red-200"
          >
            <Trash2 size={15} />
            <span>Hapus percakapan</span>
          </button>
        </div>

        {/* Sidebar Footer */}
        <div 
          className="p-3 text-center text-xs font-medium border-t"
          style={{ borderColor: currentTheme.line, color: currentTheme.muted }}
        >
          Dibuat untuk pelajar Indonesia 💚
        </div>
      </aside>

      {/* Backdrop for Mobile Sidebar */}
      {isMobileMenuOpen && (
        <div 
          onClick={() => setIsMobileMenuOpen(false)}
          className="fixed inset-0 bg-black/40 z-30 md:hidden"
        />
      )}

      {/* Main Chat Interface */}
      <main className="flex-1 flex flex-col min-h-0 relative">
        <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 max-w-4xl w-full mx-auto pb-32">
          
          {/* Header Bar Gamifikasi */}
          <div 
            className="rounded-3xl p-5 md:p-6 mb-7 text-white shadow-xl relative overflow-hidden"
            style={{ background: currentTheme.heroGradient }}
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
              <div className="flex items-center gap-3.5">
                <div className="w-14 h-14 rounded-2xl bg-white/20 backdrop-blur-md flex items-center justify-center text-3xl shadow-inner">
                  🐍
                </div>
                <div>
                  <h2 className="text-2xl font-extrabold tracking-tight">PyBuddy</h2>
                  <p className="text-sm font-medium text-white/90">Teman belajar Python-mu</p>
                </div>
              </div>

              <div className="flex items-center gap-2 flex-wrap">
                <div className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-white/20 backdrop-blur-md text-xs font-bold tracking-wide">
                  <Flame size={14} className="text-orange-300" />
                  <span>{asked} tanya</span>
                </div>
                <div className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-white/20 backdrop-blur-md text-xs font-bold tracking-wide">
                  <Sparkles size={14} className="text-yellow-300" />
                  <span>{xp} XP</span>
                </div>
              </div>
            </div>

            {/* Level and Progress Bar */}
            <div className="pt-2 border-t border-white/15">
              <div className="flex justify-between text-xs font-bold mb-2">
                <span className="flex items-center gap-1">
                  <Award size={14} /> Level {currentLevel} · {levelTitle}
                </span>
                <span>{intoLevel}/{XP_PER_LEVEL} XP</span>
              </div>
              <div className="h-2.5 w-full bg-black/25 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-yellow-400 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${progressPct}%`, minWidth: progressPct > 0 ? '12px' : '0' }}
                />
              </div>
            </div>
          </div>

          {/* Welcome Screen / Hero Terminal (When empty) */}
          {messages.length === 0 && (
            <div className="space-y-6 animate-fade-in">
              <div className="flex flex-col sm:flex-row items-center gap-5">
                <div 
                  className="w-20 h-20 shrink-0 rounded-3xl border flex items-center justify-center text-4xl shadow-md"
                  style={{ backgroundColor: currentTheme.surface, borderColor: currentTheme.line }}
                >
                  🐍
                </div>

                {/* Mock Terminal */}
                <div 
                  className="flex-1 w-full rounded-2xl overflow-hidden border shadow-lg font-mono text-sm"
                  style={{ backgroundColor: currentTheme.termBg, borderColor: 'rgba(255,255,255,0.1)' }}
                >
                  <div className="flex items-center gap-2 px-3.5 py-2.5 bg-white/5 border-b border-white/10 text-xs text-slate-400">
                    <span className="w-2.5 h-2.5 rounded-full bg-red-400 inline-block"></span>
                    <span className="w-2.5 h-2.5 rounded-full bg-yellow-400 inline-block"></span>
                    <span className="w-2.5 h-2.5 rounded-full bg-green-400 inline-block"></span>
                    <span className="ml-2 font-medium">pybuddy.py</span>
                  </div>
                  <div className="p-4 space-y-2 text-slate-200">
                    <div>
                      <span className="text-slate-500">&gt;&gt;&gt;</span> <span className="text-yellow-400 font-bold">print</span>(<span className="text-emerald-400">"Hai, aku PyBuddy!"</span>)
                    </div>
                    <div className="text-emerald-300">Hai, aku PyBuddy!</div>
                    <div>
                      <span className="text-slate-500">&gt;&gt;&gt;</span> <span className="text-yellow-400 font-bold">input</span>(<span className="text-emerald-400">"Mau belajar apa hari ini? "</span>)
                    </div>
                    <div className="flex items-center text-slate-300">
                      <span>Mau belajar apa hari ini? </span>
                      <span className="inline-block w-2 h-4 bg-yellow-400 ml-1 animate-pulse"></span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Quick starts */}
              <div>
                <p className="text-xs font-bold mb-3" style={{ color: currentTheme.muted }}>
                  Coba salah satu pertanyaan ini, atau pilih topik di menu samping:
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {QUICK_STARTS.map((qs, i) => (
                    <button
                      key={i}
                      onClick={() => handleSendMessage(qs.text)}
                      className="p-3.5 rounded-xl border text-left font-semibold text-sm transition-all hover:translate-y-[-1px] shadow-sm flex items-center gap-3 group"
                      style={{ 
                        backgroundColor: currentTheme.surface, 
                        borderColor: currentTheme.line,
                        color: currentTheme.ink 
                      }}
                    >
                      <span className="text-xl group-hover:scale-110 transition-transform">{qs.emoji}</span>
                      <span className="flex-1">{qs.text}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Chat Messages */}
          <div className="space-y-4">
            {messages.map((msg, i) => {
              const isUser = msg.role === 'user';
              return (
                <div
                  key={i}
                  className={`flex gap-3 md:gap-4 p-4 md:p-5 rounded-2xl transition-all shadow-sm ${
                    isUser ? 'ml-6 sm:ml-12 border' : 'mr-6 sm:mr-12 border'
                  }`}
                  style={{
                    /* WARNA BUBBLE CHAT USER BERBEDA SESUAI PERMINTAAN */
                    backgroundColor: isUser ? currentTheme.userBg : currentTheme.surface,
                    borderColor: isUser ? currentTheme.userLine : currentTheme.line,
                    color: isUser ? currentTheme.userInk : currentTheme.ink,
                  }}
                >
                  {/* Avatar */}
                  <div 
                    className="w-9 h-9 md:w-10 md:h-10 rounded-full border shrink-0 flex items-center justify-center text-lg md:text-xl shadow-xs"
                    style={{ 
                      backgroundColor: currentTheme.surface, 
                      borderColor: isUser ? currentTheme.userLine : currentTheme.line 
                    }}
                  >
                    {isUser ? '🧑‍🎓' : '🐍'}
                  </div>

                  {/* Bubble Content */}
                  <div className="flex-1 min-w-0 overflow-hidden text-sm md:text-base leading-relaxed">
                    <div className="font-bold text-xs mb-1.5 opacity-70">
                      {isUser ? 'Kamu' : 'PyBuddy'}
                    </div>
                    
                    <MessageRenderer 
                      content={msg.content} 
                      isUser={isUser}
                      currentTheme={currentTheme}
                      onCopyCode={copyToClipboard}
                    />
                  </div>
                </div>
              );
            })}

            {/* Loading Indicator */}
            {isLoading && (
              <div 
                className="flex gap-3 p-4 md:p-5 rounded-2xl mr-12 border items-center shadow-sm"
                style={{ backgroundColor: currentTheme.surface, borderColor: currentTheme.line }}
              >
                <div 
                  className="w-10 h-10 rounded-full border shrink-0 flex items-center justify-center text-xl"
                  style={{ backgroundColor: currentTheme.surface, borderColor: currentTheme.line }}
                >
                  🐍
                </div>
                <div className="flex items-center gap-2 text-sm font-medium" style={{ color: currentTheme.muted }}>
                  <div className="flex gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-blue-500 animate-ping"></span>
                    <span className="w-2 h-2 rounded-full bg-blue-500 animate-ping delay-150"></span>
                    <span className="w-2 h-2 rounded-full bg-blue-500 animate-ping delay-300"></span>
                  </div>
                  <span>PyBuddy sedang meracik jawaban...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

        </div>

        {/* Input Bar Fixed Bottom */}
        <div 
          className="fixed bottom-0 right-0 left-0 md:left-80 p-3 md:p-4 border-t backdrop-blur-md z-10"
          style={{ 
            backgroundColor: currentTheme.bg === '#0B132B' ? 'rgba(11, 19, 43, 0.92)' : 'rgba(255, 255, 255, 0.92)',
            borderColor: currentTheme.line 
          }}
        >
          <div className="max-w-4xl mx-auto flex items-center gap-2">
            <div 
              className="flex-1 flex items-center rounded-2xl border px-3.5 py-2 shadow-sm focus-within:ring-2 transition-all"
              style={{ 
                backgroundColor: currentTheme.surface, 
                borderColor: currentTheme.line 
              }}
            >
              <input
                type="text"
                value={inputPrompt}
                onChange={(e) => setInputPrompt(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                placeholder="Contoh: Apa bedanya list dan tuple?"
                className="w-full bg-transparent outline-none text-sm md:text-base font-medium"
                style={{ color: currentTheme.ink }}
              />
            </div>

            <button
              onClick={() => handleSendMessage()}
              disabled={!inputPrompt.trim() || isLoading}
              className="p-3 md:px-5 md:py-3 rounded-2xl font-bold flex items-center justify-center gap-2 transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-md cursor-pointer"
              style={{
                backgroundColor: currentTheme.accent,
                color: currentTheme.onAccent,
              }}
            >
              <Send size={18} />
              <span className="hidden sm:inline text-sm">Kirim</span>
            </button>
          </div>
        </div>
      </main>

      {/* Modal Kode Python & Solusi Perbaikan Streamlit */}
      {isPythonCodeModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div 
            className="w-full max-w-3xl rounded-3xl border shadow-2xl flex flex-col max-h-[90vh] overflow-hidden"
            style={{ backgroundColor: currentTheme.surface, borderColor: currentTheme.line }}
          >
            {/* Modal Header */}
            <div className="p-5 border-b flex items-center justify-between" style={{ borderColor: currentTheme.line }}>
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-600 flex items-center justify-center font-bold">
                  🐍
                </div>
                <div>
                  <h3 className="font-extrabold text-base">Kode Python Streamlit yang Diperbaiki</h3>
                  <p className="text-xs" style={{ color: currentTheme.muted }}>Perbaikan navigasi 'Tampilan' & warna bubble chat user</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => copyToClipboard(FIXED_STREAMLIT_CODE)}
                  className="px-3 py-1.5 rounded-xl border text-xs font-bold flex items-center gap-1.5 transition-colors cursor-pointer"
                  style={{ borderColor: currentTheme.line, backgroundColor: currentTheme.bg }}
                >
                  {copiedCode ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
                  <span>{copiedCode ? 'Tersalin!' : 'Salin Semua'}</span>
                </button>
                <button
                  onClick={() => setIsPythonCodeModalOpen(false)}
                  className="p-1.5 rounded-lg opacity-70 hover:opacity-100"
                >
                  <X size={20} />
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-5 space-y-4 text-xs md:text-sm">
              <div className="p-3.5 rounded-xl bg-blue-50 border border-blue-200 text-blue-900 leading-relaxed">
                <div className="font-bold mb-1 flex items-center gap-1.5">
                  <span>💡</span>
                  <span>Penjelasan 2 Masalah yang Diperbaiki:</span>
                </div>
                <ol className="list-decimal list-inside space-y-1 text-xs">
                  <li>
                    <strong>Tulisan "Tampilan" ketutupan/berantakan:</strong> Pada CSS Streamlit sebelumnya, div label tidak memiliki margin vertikal yang cukup dan wrapper kolom button tema menimpa baris label. Diperbaiki dengan membungkus label dalam <code>&lt;p class="side-label"&gt;</code> dan menambahkan <code>margin-top: 18px; margin-bottom: 8px;</code> serta styling rapi untuk tombol tema.
                  </li>
                  <li>
                    <strong>Bubble Chat User Tidak Berubah Warna:</strong> Ketika kamu memakai <code>st.chat_message("user", avatar="🧑‍🎓")</code>, Streamlit TIDAK merender atribut bawaan <code>chatAvatarIcon-user</code> (karena diganti avatar emoji custom). Akibatnya selektor CSS tidak mengenai pesan user. Solusinya ditambahkan penanda kelas <code>user-bubble-flag</code> atau atribut aria-label sehingga 100% akurat mengubah warna background, border, dan font pesan user!
                  </li>
                </ol>
              </div>

              <div className="rounded-xl overflow-hidden border" style={{ borderColor: currentTheme.line }}>
                <div className="bg-slate-900 text-slate-300 px-4 py-2 text-xs font-mono flex items-center justify-between border-b border-slate-800">
                  <span>app.py (Lengkap Siap Pakai)</span>
                  <span className="text-[10px] text-slate-500">Python 3.9+ / Streamlit</span>
                </div>
                <pre className="p-4 bg-slate-950 text-slate-100 font-mono text-xs overflow-x-auto max-h-96 leading-relaxed">
                  {FIXED_STREAMLIT_CODE}
                </pre>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t flex justify-end" style={{ borderColor: currentTheme.line }}>
              <button
                onClick={() => setIsPythonCodeModalOpen(false)}
                className="px-5 py-2 rounded-xl text-xs font-bold text-white cursor-pointer"
                style={{ backgroundColor: currentTheme.accent }}
              >
                Tutup
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

// Sub-component to render clean markdown, tables, and code snippets
function MessageRenderer({ 
  content, 
  isUser, 
  currentTheme,
  onCopyCode 
}: { 
  content: string; 
  isUser: boolean; 
  currentTheme: ThemeConfig;
  onCopyCode: (code: string) => void;
}) {
  if (isUser) {
    return <div className="whitespace-pre-wrap font-medium">{content}</div>;
  }

  // Split content into code blocks and markdown paragraphs
  const parts = content.split(/(```[\s\S]*?```)/g);

  return (
    <div className="space-y-3 font-normal">
      {parts.map((part, index) => {
        if (part.startsWith('```')) {
          // Code block
          const lines = part.slice(3, -3).trim().split('\n');
          const lang = lines[0].match(/^[a-z]+/i) ? lines[0] : 'python';
          const code = lines[0].match(/^[a-z]+/i) ? lines.slice(1).join('\n') : lines.join('\n');

          return (
            <div 
              key={index} 
              className="rounded-xl overflow-hidden border my-2 text-xs md:text-sm font-mono shadow-sm"
              style={{ backgroundColor: '#1A202C', borderColor: '#2D3748' }}
            >
              <div className="flex items-center justify-between px-3.5 py-1.5 bg-[#2D3748] text-slate-300 text-xs">
                <span className="flex items-center gap-1.5">
                  <Terminal size={12} className="text-yellow-400" />
                  <span>{lang}</span>
                </span>
                <button
                  onClick={() => onCopyCode(code)}
                  className="hover:text-white flex items-center gap-1 text-[11px] px-2 py-0.5 rounded bg-white/10 transition-colors"
                >
                  <Copy size={11} />
                  <span>Salin</span>
                </button>
              </div>
              <pre className="p-3.5 overflow-x-auto text-emerald-300 leading-relaxed">
                <code>{code}</code>
              </pre>
            </div>
          );
        }

        // Standard text: check for bullet lists, bold text, inline code
        return (
          <div key={index} className="space-y-2">
            {part.split('\n\n').map((paragraph, pIdx) => {
              if (paragraph.trim().startsWith('|') && paragraph.includes('\n|')) {
                // Table rendering
                return <TableRenderer key={pIdx} tableMarkdown={paragraph} currentTheme={currentTheme} />;
              }

              return (
                <p key={pIdx} className="leading-relaxed">
                  {renderFormattedText(paragraph, currentTheme)}
                </p>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}

// Simple table renderer for Markdown tables
function TableRenderer({ tableMarkdown, currentTheme }: { tableMarkdown: string; currentTheme: ThemeConfig }) {
  const rows = tableMarkdown.trim().split('\n').filter(r => r.trim().startsWith('|'));
  if (rows.length < 2) return null;

  const headerCells = rows[0].split('|').slice(1, -1).map(c => c.trim());
  const bodyRows = rows.slice(2).map(r => r.split('|').slice(1, -1).map(c => c.trim()));

  return (
    <div className="overflow-x-auto my-3 rounded-xl border" style={{ borderColor: currentTheme.line }}>
      <table className="w-full text-xs text-left">
        <thead className="border-b" style={{ backgroundColor: currentTheme.codeBg, borderColor: currentTheme.line }}>
          <tr>
            {headerCells.map((h, i) => (
              <th key={i} className="px-3 py-2 font-bold">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y" style={{ borderColor: currentTheme.line }}>
          {bodyRows.map((row, rIdx) => (
            <tr key={rIdx}>
              {row.map((cell, cIdx) => (
                <td key={cIdx} className="px-3 py-2.5 font-medium">{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Helper to format inline bold, inline code, etc.
function renderFormattedText(text: string, currentTheme: ThemeConfig) {
  const subparts = text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g);
  return subparts.map((item, i) => {
    if (item.startsWith('`') && item.endsWith('`')) {
      return (
        <code 
          key={i} 
          className="px-1.5 py-0.5 rounded text-xs font-mono font-bold mx-0.5"
          style={{ backgroundColor: currentTheme.codeBg, color: currentTheme.accent }}
        >
          {item.slice(1, -1)}
        </code>
      );
    }
    if (item.startsWith('**') && item.endsWith('**')) {
      return <strong key={i} className="font-bold">{item.slice(2, -2)}</strong>;
    }
    return item;
  });
}

// Friendly, high quality response generator matching PyBuddy persona
function generatePythonReply(query: string): string {
  const q = query.toLowerCase();

  if (q.includes('list') && q.includes('tuple')) {
    return `Hai! Perbedaan **List** dan **Tuple** itu sangat simpel bila dianalogikan:

- 📦 **List** (pakai tanda kurung siku \`[]\`): Seperti **kotak pensil terbuka**. Isinya bisa ditambah, dihapus, atau diubah kapan saja (istilah kerennya: *mutable*).
- 🔒 **Tuple** (pakai tanda kurung biasa \`()\`): Seperti **rapor nilai ujian**. Begitu dibuat, isinya tidak boleh diubah sama sekali (istilahnya: *immutable*).

Contoh kode Python:
\`\`\`python
# Contoh List (Bisa diubah)
buah = ["apel", "jeruk"]
buah.append("mangga")  # Sukses! Sekarang ada 3 buah

# Contoh Tuple (Permanen)
koordinat = (10, 20)
# koordinat[0] = 15    # ERROR! Tuple tidak boleh diubah
\`\`\`

**Kapan pakai yang mana?**
- Pakai **List** kalau datanya dinamis (misal: daftar belanjaan, riwayat chat).
- Pakai **Tuple** kalau datanya tetap & butuh perlindungan agar tidak sengaja berubah (misal: titik GPS, hari dalam seminggu).`;
  }

  if (q.includes('indentationerror') || q.includes('error')) {
    return `Hai! \`IndentationError\` biasanya muncul karena Python sangat "sensitif" terhadap spasi dan kerapian baris kode.

Dalam Python, kita tidak memakai tanda kurung kurawal \`{}\` untuk membungkus blok kode (seperti di C++ atau Java), melainkan memakai **tab atau spasi**.

| Penyebab | Contoh Salah | Cara Memperbaiki |
| :--- | :--- | :--- |
| Lupa spasi di dalam \`if\`/\`def\` | \`def sapa():\\nprint("hi")\` | Tambahkan 4 spasi setelah tanda \`:\` |
| Campur Tab dan Spasi | Baris 1 pakai Tab, Baris 2 pakai Spasi | Gunakan hanya **4 spasi** secara konsisten |

Contoh kode yang benar:
\`\`\`python
def sapa():
    # Ada 4 spasi di depan print
    print("Halo, selamat belajar Python!")

if True:
    print("Kondisi benar!")
\`\`\`

Coba periksa baris yang ditunjuk oleh terminalmu, pastikan setelah tanda titik dua (\`:\`), baris berikutnya menjorok ke dalam ya!`;
  }

  if (q.includes('for') || q.includes('perulangan')) {
    return `Perulangan **for** di Python itu seperti **petugas loket yang memanggil antrean satu per satu**! 🎟️

Bayangkan kamu punya daftar nama siswa, lalu kamu ingin menyapa semuanya:

\`\`\`python
antrean = ["Budi", "Siti", "Andi"]

for nama in antrean:
    print(f"Halo {nama}, silakan masuk!")
\`\`\`

Setiap putaran, variabel \`nama\` akan otomatis mengambil anggota berikutnya sampai antrean habis.

Jika ingin mengulang sejumlah angka tertentu, gunakan \`range()\`:
\`\`\`python
for angka in range(1, 6):
    print("Putaran ke-", angka)
\`\`\`

Coba tebak: Apa output dari kode di atas? (Petunjuk: angka 6 ikut dicetak atau tidak ya?) 😉`;
  }

  if (q.includes('latihan') || q.includes('soal')) {
    return `Ini dia latihan soal yang seru untuk melatih logika if-else kamu! 📝

**Tantangan: Detektor Suhu Badan** 🌡️
Buatlah variabel \`suhu = 37.5\`.
Lalu gunakan \`if-elif-else\` dengan aturan:
1. Jika suhu **di bawah 36.0**, cetak: \`"Hipotermia / Suhu rendah"\`
2. Jika suhu **antara 36.0 sampai 37.5**, cetak: \`"Suhu normal"\`
3. Jika suhu **di atas 37.5**, cetak: \`"Kamu demam, istirahat ya!"\`

Coba tulis kodenya dan kirim ke sini, nanti biar PyBuddy yang koreksi! Semangat! 💪`;
  }

  if (q.includes('fungsi') || q.includes('modul')) {
    return `Fungsi di Python itu seperti **resep masakan** atau **tombol blender**! 🥤
Kamu bikin sekali, lalu bisa dipanggil berkali-kali tanpa perlu menulis ulang langkah-langkahnya.

Cara membuatnya memakai kata kunci \`def\`:
\`\`\`python
def hitung_luas_persegi(sisi):
    luas = sisi * sisi
    return luas

# Panggil fungsinya
hasil = hitung_luas_persegi(5)
print("Luas persegi adalah:", hasil) # Output: 25
\`\`\`

Sedangkan **Modul** adalah file Python lain yang berisi kumpulan fungsi siap pakai (contoh: \`import math\` atau \`import random\`).`;
  }

  // Default response
  return `Pertanyaan yang bagus sekali tentang: **"${query}"**! 🐍

Dalam Python, kunci utamanya adalah memahami alur logika langkah demi langkah:
1. Kenali tipe datanya (apakah angka, teks, atau koleksi).
2. Tulis kode yang sederhana dan mudah dibaca (*clean code*).
3. Jangan takut error, karena error adalah cara Python memberitahu kita di mana bagian yang perlu diperbaiki!

\`\`\`python
# Contoh ilustrasi sederhana
pesan = "Terus eksplorasi!"
print(f"PyBuddy siap membantu: {pesan}")
\`\`\`

Apakah ada bagian tertentu dari topik ini yang ingin kamu bedah lebih dalam? Tanyakan saja ya!`;
}

// Complete Fixed Python Streamlit Code
const FIXED_STREAMLIT_CODE = `import os
import time

import streamlit as st
from groq import Groq

# ---------------------------------------------------------------
# KONFIGURASI
# ---------------------------------------------------------------
MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
RETRIES = 2

SYSTEM_PROMPT = """Kamu adalah PyBuddy, asisten belajar Python yang ramah untuk
mahasiswa dan pelajar pemula di Indonesia.

Aturan:
- Jawab dalam Bahasa Indonesia yang santai tapi jelas.
- Jelaskan konsep dengan bahasa sederhana dan analogi sehari-hari.
- Sertakan contoh kode pendek (maksimal sekitar 15 baris) bila relevan.
- Jika pengguna mengirim error, jelaskan penyebabnya lalu beri cara memperbaikinya.
- Jika pertanyaan di luar topik pemrograman, jawab singkat lalu arahkan kembali
  ke topik belajar coding.
- Dorong pengguna mencoba sendiri, jangan hanya memberi jawaban jadi."""

XP_PER_QUESTION = 10
XP_PER_LEVEL = 50
LEVEL_TITLES = ["Pemula", "Penjelajah", "Pendekar Kode", "Jagoan Python", "Master Python"]

TOPICS = [
    ("🐣", "Dasar Python", "Jelaskan dasar-dasar Python untuk pemula: variabel, tipe data, dan print."),
    ("📦", "List, Tuple & Dict", "Jelaskan perbedaan list, tuple, dan dictionary, beserta kapan memakainya."),
    ("🔁", "Perulangan & Kondisi", "Jelaskan if-else dan perulangan for/while dengan analogi sehari-hari."),
    ("🧩", "Fungsi & Modul", "Jelaskan cara membuat fungsi di Python dan cara memakai modul."),
    ("🐞", "Debug Error", "Ajari aku cara membaca pesan error Python dan menemukan penyebabnya."),
    ("📝", "Latihan Soal", "Beri aku satu latihan soal Python untuk pemula, tanpa kunci jawaban dulu."),
]

QUICK_STARTS = [
    ("📦", "Apa bedanya list dan tuple?"),
    ("🔁", "Jelaskan perulangan for dengan analogi"),
    ("🐞", "Kenapa muncul IndentationError?"),
    ("📝", "Beri aku latihan soal tentang if-else"),
]

# ---------------------------------------------------------------
# TEMA & WARNA BUBBLE CHAT
# ---------------------------------------------------------------
THEMES = {
    "light": {
        "icon": "☀️",
        "name": "Terang",
        "scheme": "light",
        "vars": {
            "bg": "#F4F7FC", "bg_solid": "#F4F7FC", "surface": "#FFFFFF",
            "soft": "#EAEFF7", "side_bg": "#FFFFFF", "line": "#D5DFEF",
            "ink": "#182642", "muted": "#647493",
            "accent": "#2B6CB0", "accent_d": "#2C5282", "accent_soft": "#EBF8FF",
            "on_accent": "#FFFFFF", "hl": "#ECC94B", "danger": "#E53E3E",
            # Warna Bubble Chat User (Biru Cerah Kontras)
            "user_bg": "#DCEEFE", "user_line": "#90CDF4", "user_ink": "#1A365D",
            "hero_1": "#3182CE", "hero_2": "#2B6CB0", "code_ink": "#2C5282",
            "term_bg": "#1A202C", "shadow": "rgba(49,130,206,.2)",
        },
        "extra": "",
    },
    "dark": {
        "icon": "🌙",
        "name": "Gelap",
        "scheme": "dark",
        "vars": {
            "bg": "#0B132B", "bg_solid": "#0B132B", "surface": "#1C2541",
            "soft": "#283559", "side_bg": "#080F22", "line": "#3A4D78",
            "ink": "#F0F4F8", "muted": "#9FB3C8",
            "accent": "#4FD1C5", "accent_d": "#319795", "accent_soft": "#1D3B48",
            "on_accent": "#0B132B", "hl": "#F6E05E", "danger": "#FEB2B2",
            # Warna Bubble Chat User (Teal Gelap)
            "user_bg": "#134E4A", "user_line": "#2DD4BF", "user_ink": "#CCFBF1",
            "hero_1": "#2B6CB0", "hero_2": "#1A365D", "code_ink": "#F6E05E",
            "term_bg": "#070B16", "shadow": "rgba(0,0,0,.4)",
        },
        "extra": """
[data-testid="stAlert"] p { color: #F0F4F8; }
""",
    },
    "sunset": {
        "icon": "🌇",
        "name": "Senja",
        "scheme": "light",
        "vars": {
            "bg": "#FFF5F0", "bg_solid": "#FFF5F0", "surface": "#FFFFFF",
            "soft": "#FEEBC8", "side_bg": "#FFFAF0", "line": "#FBD38D",
            "ink": "#2D3748", "muted": "#7B341E",
            "accent": "#DD6B20", "accent_d": "#C05621", "accent_soft": "#FFFAF0",
            "on_accent": "#FFFFFF", "hl": "#D69E2E", "danger": "#E53E3E",
            # Warna Bubble Chat User (Krem Oranye Hangat)
            "user_bg": "#FEEBC8", "user_line": "#FBD38D", "user_ink": "#7B341E",
            "hero_1": "#ED8936", "hero_2": "#DD6B20", "code_ink": "#C05621",
            "term_bg": "#2C1A1D", "shadow": "rgba(221,107,32,.2)",
        },
        "extra": "",
    },
}

st.set_page_config(
    page_title="PyBuddy", 
    page_icon="🐍", 
    layout="centered",
    initial_sidebar_state="expanded"
)

theme = st.session_state.setdefault("theme", "light")
if theme not in THEMES:
    theme = st.session_state.theme = "light"

# ---------------------------------------------------------------
# GAYA (CSS)
# ---------------------------------------------------------------
FONT_CSS = (
    "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800"
    "&family=JetBrains+Mono:wght@500;700&display=swap');"
)

THEME_CSS = (
    ":root{color-scheme:" + THEMES[theme]["scheme"] + ";"
    + ";".join(f"--{k.replace('_', '-')}:{v}" for k, v in THEMES[theme]["vars"].items())
    + "}"
)

BASE_CSS = """
/* Sembunyikan tombol expand/collapse sidebar bawaan */
[data-testid="stSidebarCollapseButton"],
[data-testid="stExpandSidebarButton"] {
    display: none !important;
}

.stApp { background: var(--bg); background-attachment: fixed; color: var(--ink); }
[data-testid="stAppViewContainer"], [data-testid="stMain"] { background: transparent; }
.stApp, .stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3,
.stApp h4, .stApp button, .stApp input, .stApp textarea { font-family: 'Plus Jakarta Sans', sans-serif; }
:is([data-testid="stMain"], [data-testid="stSidebar"], [data-testid="stBottom"])
  :is(p, li, label, h1, h2, h3, h4) { color: var(--ink); }
.stApp p, .stApp li { font-weight: 500; font-size: 1rem; line-height: 1.65; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4 { font-weight: 800; letter-spacing: -.01em; }
.stApp a { color: var(--accent); font-weight: 600; }
footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 800px; padding-top: 1.6rem; padding-bottom: 6rem; }

.appbar { background: linear-gradient(135deg, var(--hero-1), var(--hero-2)); color: #fff;
  border-radius: 22px; padding: 20px 24px 18px; margin-bottom: 28px;
  box-shadow: 0 14px 30px -18px var(--shadow); }
.appbar-top { display: flex; align-items: center; justify-content: space-between;
  gap: 14px; flex-wrap: wrap; }
.brand { display: flex; align-items: center; gap: 14px; }
.logo { width: 54px; height: 54px; border-radius: 16px; background: rgba(255,255,255,.18);
  display: grid; place-items: center; font-size: 1.9rem; }
.app-name { font-weight: 800; font-size: 1.6rem; line-height: 1.1; letter-spacing: -.02em; color: #fff; }
.app-tag { font-weight: 500; font-size: .92rem; color: rgba(255,255,255,.85); margin-top: 2px; }
.stats { display: flex; gap: 8px; flex-wrap: wrap; }
.pill { font-weight: 700; font-size: .9rem; padding: 6px 12px; border-radius: 999px;
  background: rgba(255,255,255,.16); color: #fff; white-space: nowrap; }
.level-meta { display: flex; justify-content: space-between; font-weight: 700;
  font-size: .85rem; margin: 20px 0 8px; color: #fff; }
.track { height: 10px; background: rgba(0,0,0,.25); border-radius: 99px; overflow: hidden; }
.fill { height: 100%; background: var(--hl); border-radius: 99px; transition: width .5s ease; }

.hero { display: flex; align-items: center; gap: 18px; margin: 4px 0 26px; }
.mascot { flex: none; width: 84px; height: 84px; border-radius: 24px; display: grid;
  place-items: center; font-size: 3rem; background: var(--surface); border: 1px solid var(--line);
  box-shadow: 0 10px 24px -16px var(--shadow); }
.term { flex: 1; min-width: 0; background: var(--term-bg); border-radius: 16px; overflow: hidden;
  border: 1px solid rgba(255,255,255,.08); box-shadow: 0 14px 30px -18px var(--shadow); }
.term-bar { display: flex; align-items: center; gap: 6px; padding: 9px 14px;
  background: rgba(255,255,255,.05); }
.dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.dot.r { background: #FF6B6B; } .dot.y { background: #FFD43B; } .dot.g { background: #51CF66; }
.term-bar .file { margin-left: 8px; font: 600 .75rem 'JetBrains Mono', monospace; color: #8FA2C4; }
.term-body { padding: 14px 18px 16px; font-family: 'JetBrains Mono', monospace; font-size: .9rem;
  line-height: 1.75; color: #E8EEF9; white-space: pre-wrap; word-break: break-word; }
.term-body .pr { color: #7488AD; }
.term-body .fn { color: #FFD43B; font-weight: 700; }
.term-body .st { color: #8EE0A5; }
.cursor { display: inline-block; width: .55em; height: 1.05em; background: var(--hl);
  vertical-align: -.18em; margin-left: 2px; animation: blink 1.1s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }
.hint { font-weight: 600; font-size: .92rem; color: var(--muted); margin: 0 0 12px; }

.stButton, [data-testid="stButton"] { width: 100%; }
.stButton > button {
  width: 100%; background: var(--surface); color: var(--ink); font-weight: 600; font-size: .98rem;
  border: 1px solid var(--line); border-radius: 14px; padding: 10px 16px; min-height: 52px;
  box-shadow: 0 1px 0 var(--line);
  transition: border-color .15s, background .15s, transform .1s;
}
.stButton > button p { color: inherit !important; font-weight: inherit; font-size: inherit;
  margin: 0; line-height: 1.35; }
.stButton > button:hover { background: var(--soft); border-color: var(--accent); color: var(--ink); }
.stButton > button:active { transform: translateY(1px); }
.stButton > button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

div[class*="st-key-chip_"] button { justify-content: flex-start; text-align: left;
  min-height: 64px; padding: 12px 16px; }
div[class*="st-key-chip_"] button div { justify-content: flex-start; text-align: left; width: 100%; }
div[class*="st-key-chip_"] button p { white-space: normal; }

/* ---------- Kustomisasi Bubble Chat (Bot vs User) ---------- */
/* 1. Style Default (Untuk Pesan Asisten / Bot) */
[data-testid="stChatMessage"] { 
  background: var(--surface) !important; 
  border: 1px solid var(--line) !important;
  border-radius: 16px; 
  padding: 14px 18px; 
  margin-bottom: 12px; 
}
[data-testid="stChatMessage"] :is(p, li, h1, h2, h3, h4, strong, em, td, th, blockquote, span.katex) {
  color: var(--ink) !important; 
}

/* 2. Style Khusus Pesan Pengguna (User) - FIXED DENGAN MULTI-SELECTOR RELIABLE */
.user-msg-flag { display: none !important; }

[data-testid="stChatMessage"]:has(.user-msg-flag),
[data-testid="stChatMessage"][aria-label*="user" i],
[data-testid="stChatMessage"]:has([aria-label*="user" i]),
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]),
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  background: var(--user-bg) !important;
  border: 1px solid var(--user-line) !important;
}

[data-testid="stChatMessage"]:has(.user-msg-flag) :is(p, li, h1, h2, h3, h4, strong, em, td, th, blockquote, span.katex),
[data-testid="stChatMessage"][aria-label*="user" i] :is(p, li, h1, h2, h3, h4, strong, em, td, th, blockquote, span.katex),
[data-testid="stChatMessage"]:has([aria-label*="user" i]) :is(p, li, h1, h2, h3, h4, strong, em, td, th, blockquote, span.katex),
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) :is(p, li, h1, h2, h3, h4, strong, em, td, th, blockquote, span.katex),
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) :is(p, li, h1, h2, h3, h4, strong, em, td, th, blockquote, span.katex) {
  color: var(--user-ink) !important;
}

[data-testid="stChatMessageAvatarAssistant"], [data-testid="stChatMessageAvatarUser"],
[data-testid="chatAvatarIcon-assistant"], [data-testid="chatAvatarIcon-user"],
[data-testid="stChatMessageAvatarCustom"] {
  background: var(--surface); border: 1px solid var(--line); border-radius: 50%; }

/* ---------- Kode ---------- */
[data-testid="stCode"] pre, .stMarkdown pre { background: var(--soft) !important;
  border: 1px solid var(--line); border-radius: 12px; }
[data-testid="stCode"] pre, [data-testid="stCode"] code, [data-testid="stCode"] code span,
.stMarkdown pre, .stMarkdown pre code { font-family: 'JetBrains Mono', monospace;
  font-size: .88rem; color: var(--ink) !important; }
.stMarkdown :not(pre) > code { background: var(--soft); color: var(--code-ink);
  font-family: 'JetBrains Mono', monospace; font-size: .86em; font-weight: 700;
  border-radius: 6px; padding: .1em .4em; }

/* ---------- Input Bar ---------- */
[data-testid="stBottom"] > div { background: var(--bg-solid); }
[data-testid="stChatInput"] { background: var(--surface); border: 1px solid var(--line);
  border-radius: 16px; box-shadow: 0 6px 20px -14px var(--shadow); }
[data-testid="stChatInput"] > div { background: transparent !important; }
[data-testid="stChatInput"] textarea { background: transparent; color: var(--ink) !important;
  font-weight: 500; }
[data-testid="stChatInput"] textarea::placeholder { color: var(--muted) !important; opacity: 1; }
[data-testid="stChatInput"]:focus-within { border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft); }
[data-testid="stChatInputSubmitButton"] { background: var(--accent); color: var(--on-accent);
  border-radius: 10px; }
[data-testid="stChatInputSubmitButton"]:disabled { background: var(--soft); color: var(--muted); }

/* ---------- Sidebar & Perbaikan Label Tampilan ---------- */
[data-testid="stSidebar"] { background: var(--side-bg); border-right: 1px solid var(--line); }
[data-testid="stSidebarHeader"] { padding: .6rem 1rem 0; min-height: 0; height: auto; }
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding: 0 1rem 1.4rem; display: flex; flex-direction: column; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .5rem; width: 100%; }
[data-testid="stSidebar"] [data-testid="stElementContainer"] { width: 100%; margin-bottom: 0px !important; }

.side-brand { display: flex; align-items: center; gap: 12px; padding: 4px 2px 14px; }
.logo-sm { flex: none; width: 44px; height: 44px; border-radius: 13px; font-size: 1.4rem;
  background: linear-gradient(135deg, var(--hero-1), var(--hero-2)); display: grid;
  place-items: center; }
.side-name { font-weight: 800; font-size: 1.2rem; color: var(--ink); line-height: 1.15;
  letter-spacing: -.01em; }
.side-sub { font-weight: 500; font-size: .84rem; color: var(--muted); line-height: 1.3; }

/* FIX LABEL TAMPILAN AGAR TIDAK KETUTUPAN ATAU OVERLAP */
.side-label { 
  display: block !important; 
  font-weight: 700 !important; 
  font-size: .82rem !important; 
  color: var(--muted) !important;
  line-height: 1.4 !important; 
  margin: 16px 2px 8px !important; 
  padding: 0 !important;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.side-divider { height: 1px; background: var(--line); margin: 14px 0 6px; width: 100%; }
.side-foot { font-weight: 500; font-size: .8rem; color: var(--muted); text-align: center;
  padding-top: 10px; width: 100%; }

div[class*="st-key-nav"] button { justify-content: flex-start; background: transparent;
  color: var(--ink); border: 1px solid transparent; border-radius: 12px; min-height: 44px;
  padding: 6px 12px; box-shadow: none; width: 100%; }
div[class*="st-key-nav"] button div { justify-content: flex-start; text-align: left; width: 100%; }
div[class*="st-key-nav"] button p { text-align: left; white-space: nowrap; font-weight: 600;
  font-size: .95rem; }
div[class*="st-key-nav"] button:hover { background: var(--soft); border-color: transparent; color: var(--ink); }
div[class*="st-key-navon_"] button { background: var(--accent-soft); box-shadow: inset 3px 0 0 var(--accent); width: 100%; }
div[class*="st-key-navon_"] button p { font-weight: 800; }

/* Perbaikan tombol pilihan tema agar rapi berdampingan tanpa overlap */
div[class*="st-key-theme"] { width: 100% !important; margin: 0 !important; }
div[class*="st-key-theme"] button { justify-content: center; background: var(--surface);
  border: 1px solid var(--line); border-radius: 12px; min-height: 42px; padding: 4px;
  box-shadow: none; margin-top: 2px !important; }
div[class*="st-key-theme"] button p { font-size: 1.25rem; line-height: 1; }
div[class*="st-key-theme"] button:hover { background: var(--soft); border-color: var(--accent); }
div[class*="st-key-themeon_"] button { background: var(--accent-soft); border-color: var(--accent);
  box-shadow: 0 0 0 1.5px var(--accent); }

/* Tombol Hapus Percakapan */
div.st-key-reset button { background: transparent; color: var(--danger);
  border: 1px solid var(--danger); justify-content: center; font-weight: 700;
  min-height: 44px; box-shadow: none; width: 100%; border-radius: 12px; margin-top: 4px; }
div.st-key-reset button:hover { background: var(--danger); color: var(--on-accent);
  border-color: var(--danger); }

[data-testid="stSidebar"] [data-testid="stExpander"] { width: 100%; margin-top: 4px; }
[data-testid="stSidebar"] [data-testid="stExpander"] details { background: var(--surface);
  border: 1px solid var(--line); border-radius: 12px; width: 100%; }
[data-testid="stSidebar"] [data-testid="stExpander"] summary { padding: .55rem .8rem; width: 100%; }
[data-testid="stSidebar"] [data-testid="stExpander"] summary p { color: var(--ink);
  font-weight: 700; font-size: .93rem; }
[data-testid="stSidebar"] [data-testid="stExpanderDetails"] p { font-size: .9rem; line-height: 1.55; }

@media (max-width: 600px) {
  .hero { flex-direction: column; align-items: stretch; }
  .mascot { width: 68px; height: 68px; font-size: 2.4rem; border-radius: 20px; }
  .app-name { font-size: 1.4rem; }
  .logo { width: 46px; height: 46px; font-size: 1.6rem; }
}
@media (prefers-reduced-motion: reduce) {
  .cursor { animation: none; }
  .fill, .stButton > button { transition: none; }
}
"""
st.markdown(
    f"<style>{FONT_CSS}{THEME_CSS}{BASE_CSS}{THEMES[theme]['extra']}</style>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# FUNGSI BANTU
# ---------------------------------------------------------------
def load_api_key():
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        key = ""
    return key or os.environ.get("GROQ_API_KEY", "")


def is_busy(error):
    text = str(error).upper()
    return any(k in text for k in ("503", "429", "502", "504", "RATE LIMIT", "OVERLOADED", "TEMPORARILY UNAVAILABLE"))


def stream_reply():
    client = st.session_state.groq_client
    chat_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    chat_messages.extend(st.session_state.messages)
    last_error = None

    for attempt in range(RETRIES):
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=chat_messages,
                max_tokens=1000,
                temperature=0.6,
                stream=True,
            )
            for chunk in stream:
                if not getattr(chunk, "choices", None):
                    continue
                delta = chunk.choices[0].delta
                content = getattr(delta, "content", None)
                if content:
                    yield content
            return
        except Exception as e:
            last_error = e
            if not is_busy(e) or attempt == RETRIES - 1:
                raise
            time.sleep(2 ** attempt)
    if last_error:
        raise last_error


def hero_html(body):
    return (
        '<div class="hero"><div class="mascot">🐍</div><div class="term">'
        '<div class="term-bar"><span class="dot r"></span><span class="dot y"></span>'
        '<span class="dot g"></span><span class="file">pybuddy.py</span></div>'
        f'<div class="term-body">{body}</div></div></div>'
    )


def py_line(fn, arg):
    return (
        f'<div><span class="pr">&gt;&gt;&gt;</span> <span class="fn">{fn}</span>'
        f'(<span class="st">"{arg}"</span>)</div>'
    )


def py_out(text, cursor=False):
    return f'<div>{text}{"<span class=cursor></span>" if cursor else ""}</div>'


def render_header(slot):
    xp = st.session_state.xp
    level = xp // XP_PER_LEVEL + 1
    into_level = xp % XP_PER_LEVEL
    title = LEVEL_TITLES[min(level - 1, len(LEVEL_TITLES) - 1)]
    pct = into_level / XP_PER_LEVEL * 100
    min_w = 12 if pct else 0
    slot.markdown(
        f"""<div class="appbar">
<div class="appbar-top">
<div class="brand"><div class="logo">🐍</div>
<div><div class="app-name">PyBuddy</div><div class="app-tag">Teman belajar Python-mu</div></div></div>
<div class="stats">
<span class="pill">🔥 {st.session_state.asked} tanya</span>
<span class="pill">⭐ {xp} XP</span>
</div></div>
<div class="level-meta"><span>🏆 Level {level} · {title}</span><span>{into_level}/{XP_PER_LEVEL} XP</span></div>
<div class="track"><div class="fill" style="width:{pct}%;min-width:{min_w}px"></div></div>
</div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------
st.session_state.setdefault("topic", None)

with st.sidebar:
    st.markdown(
        """<div class="side-brand"><div class="logo-sm">🐍</div>
<div><div class="side-name">PyBuddy</div><div class="side-sub">Teman belajar Python</div></div></div>""",
        unsafe_allow_html=True,
    )

    st.markdown('<p class="side-label">Pilih topik belajar</p>', unsafe_allow_html=True)
    for i, (emoji, label, question) in enumerate(TOPICS):
        key = f"navon_{i}" if st.session_state.topic == i else f"nav_{i}"
        if st.button(f"{emoji}  {label}", key=key):
            st.session_state.topic = i
            st.session_state.pending = question
            st.rerun()

    # FIX: Label 'Tampilan' diberi tag <p> dan styling yang aman dari overlap
    st.markdown('<p class="side-label">Tampilan</p>', unsafe_allow_html=True)
    theme_cols = st.columns(3, gap="small")
    for col, (name, t) in zip(theme_cols, THEMES.items()):
        key = f"themeon_{name}" if name == theme else f"theme_{name}"
        if col.button(t["icon"], key=key, help=t["name"]):
            st.session_state.theme = name
            st.rerun()

    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)
    with st.expander("ℹ️ Tentang PyBuddy"):
        st.markdown(
            "**Untuk siapa?** Mahasiswa dan pelajar pemula yang baru belajar Python "
            "dan sering bingung saat bertemu konsep baru atau error.\\n\\n"
            "**Bisa bantu apa?** Menjelaskan konsep dengan bahasa sederhana, "
            "mencari penyebab error, dan memberi contoh kode serta latihan soal."
        )

    groq_api_key = load_api_key()

    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)
    reset_button = st.button(
        "🗑️  Hapus percakapan",
        key="reset",
        help="Hapus riwayat chat dan mulai dari awal",
    )
    st.markdown('<div class="side-foot">Dibuat untuk pelajar Indonesia 💚</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------
# STATE
# ---------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
st.session_state.setdefault("xp", 0)
st.session_state.setdefault("asked", 0)

if groq_api_key and (
    "groq_client" not in st.session_state
    or getattr(st.session_state, "_last_groq_api_key", None) != groq_api_key
):
    try:
        st.session_state.groq_client = Groq(api_key=groq_api_key)
        st.session_state._last_groq_api_key = groq_api_key
        st.session_state.messages = []
    except Exception as e:
        st.error(f"Tidak bisa menginisialisasi Groq. Periksa API key kamu. Detail: {e}")
        st.stop()

if reset_button:
    st.session_state.messages = []
    st.session_state.xp = 0
    st.session_state.asked = 0
    st.session_state.topic = None
    st.rerun()

# ---------------------------------------------------------------
# HALAMAN UTAMA
# ---------------------------------------------------------------
header_slot = st.empty()
render_header(header_slot)

if not groq_api_key:
    st.markdown(
        hero_html(
            py_line("print", "Groq API key belum diatur")
            + py_out("Groq API key belum diatur, jadi aku belum bisa menjawab.", cursor=True)
        ),
        unsafe_allow_html=True,
    )
    st.error(
        "Tambahkan \`GROQ_API_KEY\` di Streamlit Secrets (atau file \`.streamlit/secrets.toml\`), lalu jalankan ulang aplikasi.",
        icon="🗝️",
    )
    st.stop()

pending = st.session_state.pop("pending", None)

if not st.session_state.messages and not pending:
    st.markdown(
        hero_html(
            py_line("print", "Hai, aku PyBuddy!")
            + py_out("Hai, aku PyBuddy!")
            + py_line("input", "Mau belajar apa hari ini? ")
            + py_out("Mau belajar apa hari ini? ", cursor=True)
        )
        + '<p class="hint">Coba salah satu pertanyaan ini, atau pilih topik di menu samping.</p>',
        unsafe_allow_html=True,
    )
    cols = st.columns(2, gap="small")
    for i, (icon, text) in enumerate(QUICK_STARTS):
        if cols[i % 2].button(f"{icon}  {text}", key=f"chip_{i}"):
            st.session_state.pending = text
            st.rerun()

# RENDER RIWAYAT PESAN CHAT (FIX: User message memakai penanda agar warna bubble pasti berubah)
for msg in st.session_state.messages:
    is_user = msg["role"] == "user"
    avatar = "🧑‍🎓" if is_user else "🐍"
    with st.chat_message(msg["role"], avatar=avatar):
        if is_user:
            # Tag span ini sebagai flag agar CSS selalu mengenali ini adalah pesan user
            st.markdown(f'<span class="user-msg-flag"></span>{msg["content"]}', unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

prompt = st.chat_input("Contoh: Apa bedanya list dan tuple?") or pending

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Render Pesan User Baru dengan Flag
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(f'<span class="user-msg-flag"></span>{prompt}', unsafe_allow_html=True)

    # Render Respon Bot
    with st.chat_message("assistant", avatar="🐍"):
        try:
            reply = st.write_stream(stream_reply())
            st.session_state.messages.append({"role": "assistant", "content": reply})

            old_level = st.session_state.xp // XP_PER_LEVEL
            st.session_state.xp += XP_PER_QUESTION
            st.session_state.asked += 1
            render_header(header_slot)
            if st.session_state.xp // XP_PER_LEVEL > old_level:
                st.toast("Naik level! Kamu hebat 🎉", icon="🏆")
            else:
                st.toast(f"+{XP_PER_QUESTION} XP", icon="⭐")
        except Exception as e:
            if is_busy(e):
                st.warning(
                    "Provider Groq sedang sibuk atau batas pemakaian tercapai. "
                    "Tunggu sebentar lalu kirim pertanyaanmu lagi.",
                    icon="⏳",
                )
            else:
                st.error(
                    "Terjadi kesalahan saat menghubungi Groq. "
                    "Periksa GROQ_API_KEY, batas pemakaian API, atau ketersediaan model. "
                    f"Detail: {e}"
                )
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()
`;

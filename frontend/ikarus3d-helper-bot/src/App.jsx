import React, { useState, useEffect, useRef } from 'react';
import {
  BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

// === Main App Component ===
// This component manages routing and renders the correct page.
export default function App() {
  const [page, setPage] = useState('recommend'); // 'recommend' or 'analytics'

  // This effect injects the Tailwind CSS CDN script into the document head.
  // This is a workaround to ensure styles are applied in this self-contained environment.
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://cdn.tailwindcss.com';
    script.async = true;
    document.head.appendChild(script);

    return () => {
      // Cleanup the script when the component unmounts
      document.head.removeChild(script);
    };
  }, []);


  const NavLink = ({ active, children, onClick }) => (
    <button
      onClick={onClick}
      className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
        active
          ? 'bg-slate-800 text-white'
          : 'text-slate-400 hover:bg-slate-700 hover:text-white'
      }`}
    >
      {children}
    </button>
  );

  return (
    <div className="min-h-screen bg-slate-900 text-white font-sans flex flex-col">
      <header className="bg-slate-900/80 backdrop-blur-sm border-b border-slate-700 sticky top-0 z-10">
        <nav className="container mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <div className="flex items-center space-x-2">
             <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-sky-400">
                <path d="M20 9V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v2"/>
                <path d="M2 11v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a2 2 0 0 0-4 0v2H6v-2a2 2 0 0 0-4 0Z"/>
                <path d="M4 17v2"/>
                <path d="M20 17v2"/>
              </svg>
            <h1 className="text-xl font-bold text-white">Ikarus Product Advisor</h1>
          </div>
          <div className="flex items-center space-x-2 bg-slate-700/50 p-1 rounded-lg">
            <NavLink active={page === 'recommend'} onClick={() => setPage('recommend')}>
              Recommend
            </NavLink>
            <NavLink active={page === 'analytics'} onClick={() => setPage('analytics')}>
              Analytics
            </NavLink>
          </div>
        </nav>
      </header>

      <main className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {page === 'recommend' ? <RecommendationPage /> : <AnalyticsPage />}
      </main>
      
      <footer className="text-center py-4 text-slate-500 text-sm border-t border-slate-800">
        Built for the Ikarus 3D Assignment.
      </footer>
    </div>
  );
}

// === Recommendation Page Component ===
const RecommendationPage = () => {
  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  
  const API_URL = 'http://localhost:8000/api/recommend';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;

    setError(null);
    setIsLoading(true);
    
    const userMessage = { type: 'user', content: prompt };
    setMessages(prev => [...prev, userMessage]);
    setPrompt('');

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      const aiMessage = { type: 'ai', content: data };
      setMessages(prev => [...prev, aiMessage]);

    } catch (err) {
      console.error(err);
      setError('Sorry, something went wrong. Please check if the backend is running and try again.');
      const errorMessage = { type: 'error', content: 'Sorry, something went wrong. Please check if the backend is running and try again.' };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)] max-w-4xl mx-auto w-full">
      <div className="flex-grow overflow-y-auto pr-4 -mr-4 space-y-6">
        {messages.length === 0 && <WelcomeMessage />}
        {messages.map((msg, index) => (
          <ChatMessage key={index} message={msg} />
        ))}
        {isLoading && <LoadingMessage />}
        <div ref={messagesEndRef} />
      </div>
      <div className="mt-6">
        {error && <div className="text-red-400 text-center mb-2">{error}</div>}
        <form onSubmit={handleSubmit} className="flex items-center space-x-2 bg-slate-800 p-2 rounded-xl border border-slate-700 focus-within:border-sky-500">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g., 'a modern wooden chair for my office'"
            className="w-full bg-transparent focus:outline-none px-3 py-2"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !prompt.trim()}
            className="px-5 py-2 bg-sky-500 rounded-lg font-semibold hover:bg-sky-600 disabled:bg-slate-600 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

// --- Sub-components for Recommendation Page ---

const WelcomeMessage = () => (
  <div className="text-center p-8 bg-slate-800/50 rounded-xl">
    <h2 className="text-2xl font-bold mb-2">Welcome to the Ikarus Product Advisor!</h2>
    <p className="text-slate-400">Describe the furniture you're looking for, and I'll find the best recommendations for you.</p>
  </div>
);

const ChatMessage = ({ message }) => {
  if (message.type === 'user') {
    return (
      <div className="flex justify-end">
        <p className="bg-sky-500 text-white rounded-xl px-4 py-2 max-w-lg">{message.content}</p>
      </div>
    );
  }
  
  if (message.type === 'error') {
    return (
        <div className="flex justify-start">
            <p className="bg-red-500/20 text-red-300 border border-red-500/30 rounded-xl px-4 py-3 max-w-lg">{message.content}</p>
        </div>
    );
  }
  
  if (message.type === 'ai') {
    return (
      <div className="space-y-4">
        {message.content.map(rec => (
          <RecommendationCard key={rec.product.id} recommendation={rec} />
        ))}
      </div>
    );
  }
  return null;
};

const RecommendationCard = ({ recommendation }) => {
  const { product, generated_description } = recommendation;
  
  const handleImageError = (e) => {
    e.target.src = `https://placehold.co/400x400/1e293b/94a3b8?text=Image+Not+Found`;
  };

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden flex flex-col sm:flex-row hover:border-slate-600 transition-all">
      <div className="sm:w-1/3 flex-shrink-0">
        <img 
          src={product.image_url} 
          alt={product.title} 
          onError={handleImageError}
          className="w-full h-48 sm:h-full object-cover"
        />
      </div>
      <div className="p-5 flex flex-col justify-between">
        <div>
          <h3 className="font-bold text-lg text-white">{product.title}</h3>
          <p className="text-sm text-slate-400 mt-1 mb-3">
            {product.brand && <span>{product.brand} • </span>}
            {product.category}
          </p>
          <p className="text-slate-300 mb-4">{generated_description}</p>
        </div>
        {/* <div className="text-2xl font-bold text-sky-400">
          ${product.price.toFixed(2)}
        </div> */}
        <div className="text-2xl font-bold text-sky-400">
          {product.price === "nan" ? "Price not available" : product.price}
        </div>
      </div>
    </div>
  );
};

const LoadingMessage = () => (
    <div className="flex justify-start">
        <div className="bg-slate-800 rounded-xl px-4 py-3 max-w-lg flex items-center space-x-3">
            <div className="w-2 h-2 bg-sky-500 rounded-full animate-pulse [animation-delay:-0.3s]"></div>
            <div className="w-2 h-2 bg-sky-500 rounded-full animate-pulse [animation-delay:-0.15s]"></div>
            <div className="w-2 h-2 bg-sky-500 rounded-full animate-pulse"></div>
            <span className="text-slate-400 text-sm">Finding recommendations...</span>
        </div>
    </div>
);


// === Analytics Page Component ===
const AnalyticsPage = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const API_URL = 'http://localhost:8000/api/analytics';

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(API_URL);
        if (!response.ok) {
          throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }
        const jsonData = await response.json();
        setData(jsonData);
      } catch (err) {
        console.error(err);
        setError('Could not fetch analytics data. Is the backend server running?');
      }
    };
    fetchData();
  }, []);

  if (error) {
    return <div className="text-center text-red-400 bg-red-500/10 p-8 rounded-xl">{error}</div>;
  }
  if (!data) {
    return <div className="text-center text-slate-400">Loading analytics...</div>;
  }
  
  const COLORS = ['#0ea5e9', '#38bdf8', '#7dd3fc', '#a5f3fc', '#ecfeff'];
  
  // Prepare data for recharts (e.g., limit items for readability)
  const topBrandsData = data.productsByBrand.slice(0, 10);
  const topCategoriesData = data.avgPriceByCategory.filter(d => d.price > 0).slice(0, 10);

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
        <AnalyticsCard title="Total Products" value={data.keyMetrics.totalProducts} />
        <AnalyticsCard title="Unique Brands" value={data.keyMetrics.uniqueBrands} />
        <AnalyticsCard title="Average Price" value={`$${data.keyMetrics.averagePrice.toFixed(2)}`} />
        <AnalyticsCard title="Unique Categories" value={data.keyMetrics.uniqueCategories} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <ChartContainer title="Top 10 Brands by Product Count">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topBrandsData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="brand" stroke="#9ca3af" fontSize={12} tick={{ fill: '#9ca3af' }} />
              <YAxis stroke="#9ca3af" fontSize={12} tick={{ fill: '#9ca3af' }}/>
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} cursor={{fill: '#374151'}} />
              <Bar dataKey="product_count" fill="#0ea5e9" name="Product Count" />
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
        
        <ChartContainer title="Top 10 Categories by Avg. Price">
           <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topCategoriesData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="primary_category" stroke="#9ca3af" fontSize={12} tick={{ fill: '#9ca3af' }} />
              <YAxis stroke="#9ca3af" fontSize={12} tick={{ fill: '#9ca3af' }}/>
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} cursor={{fill: '#374151'}} formatter={(value) => `$${value.toFixed(2)}`} />
              <Bar dataKey="price" fill="#0ea5e9" name="Average Price" />
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
      </div>

       <ChartContainer title="Material Distribution (Top 10)">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data.materialDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={100}
                fill="#8884d8"
                dataKey="count"
                nameKey="material"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {data.materialDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </ChartContainer>
    </div>
  );
};

// --- Sub-components for Analytics Page ---

const AnalyticsCard = ({ title, value }) => (
  <div className="bg-slate-800 p-4 sm:p-6 rounded-xl border border-slate-700">
    <h3 className="text-sm font-medium text-slate-400">{title}</h3>
    <p className="text-2xl sm:text-3xl font-bold text-white mt-1">{value}</p>
  </div>
);

const ChartContainer = ({ title, children }) => (
  <div className="bg-slate-800 p-4 sm:p-6 rounded-xl border border-slate-700">
    <h3 className="text-lg font-bold text-white mb-4">{title}</h3>
    {children}
  </div>
);
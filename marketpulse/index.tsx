import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { createRoot } from 'react-dom/client';
import { GoogleGenAI } from "@google/genai";

const API_KEY = process.env.API_KEY;

const ai = new GoogleGenAI({ apiKey: API_KEY });

// --- Mock Data ---
const allAvailableIndices = [
    { symbol: 'SPX', name: 'S&P 500 Index', price: 5430.82 },
    { symbol: 'NDX', name: 'NASDAQ 100', price: 19475.13 },
    { symbol: 'INDU', name: 'Dow Jones Industrial', price: 38589.16 },
    { symbol: 'RUT', name: 'Russell 2000', price: 2022.03 },
    { symbol: 'VIX', name: 'Volatility Index', price: 13.15 },
    { symbol: 'FTSE', name: 'FTSE 100', price: 8146.86 },
    { symbol: 'DAX', name: 'DAX PERFORMANCE-INDEX', price: 18131.97 },
    { symbol: 'N225', name: 'Nikkei 225', price: 38109.50 },
    { symbol: 'HSI', name: 'HANG SENG INDEX', price: 17915.51 },
    { symbol: 'ASX', name: 'S&P/ASX 200', price: 7715.50 },
    { symbol: 'SHCOMP', name: 'Shanghai Composite', price: 2998.14 },
    { symbol: 'GOLD', name: 'Gold Spot', price: 2302.50 },
    { symbol: 'SILVER', name: 'Silver Spot', price: 28.95 },
    { symbol: 'OIL', name: 'Crude Oil WTI', price: 80.55 },
];


const initialTickerData = [
    { symbol: 'AAPL', name: 'Apple Inc.', price: 214.29 }, { symbol: 'MSFT', name: 'Microsoft Corp.', price: 442.57 },
    { symbol: 'GOOGL', name: 'Alphabet Inc.', price: 179.63 }, { symbol: 'AMZN', name: 'Amazon.com, Inc.', price: 183.83 },
    { symbol: 'NVDA', name: 'NVIDIA Corporation', price: 129.61 }, { symbol: 'TSLA', name: 'Tesla, Inc.', price: 183.01 },
    { symbol: 'META', name: 'Meta Platforms, Inc.', price: 494.62 }, { symbol: 'JPM', name: 'JPMorgan Chase & Co.', price: 195.83 },
    { symbol: 'BTC/USD', name: 'Bitcoin', price: 65120.50 }, { symbol: 'ETH/USD', name: 'Ethereum', price: 3515.80 },
];

const mockHeadlinesPool = [
    "Tech giant 'Innovate Corp' misses quarterly earnings, stock drops 8%.",
    "EV manufacturer 'Volt Motors' announces record delivery numbers, shares soar.",
    "Commodity prices surge amid geopolitical tensions in Eastern Europe.",
    "Central Bank raises interest rates by 25 basis points to combat inflation.",
    "Pharmaceutical company 'LifeGene' receives FDA approval for breakthrough drug.",
    "Major airline alliance announces expansion, boosting travel sector stocks.",
    "Consumer confidence index falls for the third consecutive month.",
    "Renewable energy sector sees massive investment following new government policies.",
    "Global supply chain issues show signs of improvement, says shipping CEO.",
    "Social media platform 'ConnectSphere' faces scrutiny over data privacy concerns.",
    "Luxury goods market rebounds strongly in Asia, driving positive forecasts.",
    "Agricultural tech startup 'FarmWise' secures $50M in Series B funding.",
    "AAPL announces new VR headset, analysts predict strong sales.",
    "CyberGuard partners with MSFT for new cloud security initiative."
];

const initialNews = [
    { headline: "Fed hints at potential rate cuts later this year, boosting market optimism.", sentiment: null, loading: true, isAlert: false },
    { headline: "Global chip shortages expected to ease by Q4, says industry report.", sentiment: null, loading: true, isAlert: false },
    { headline: "Cybersecurity firm 'CyberGuard' stocks surge 15% after reporting record profits.", sentiment: null, loading: true, isAlert: false },
    { headline: "New regulations on energy sector cause uncertainty among investors.", sentiment: null, loading: true, isAlert: false },
    { headline: "Retail sales data for May shows unexpected decline, raising economic concerns.", sentiment: null, loading: true, isAlert: false },
];

type Sentiment = 'Bullish' | 'Bearish' | 'Neutral' | null;

interface MarketItem {
    symbol: string;
    name?: string;
    price: number;
    change?: number;
    pctChange?: number;
}
interface IndexItem extends MarketItem {
    name: string;
}
interface NewsItem {
    headline: string;
    sentiment: Sentiment;
    loading: boolean;
    isAlert?: boolean;
}

interface HistoricalPoint {
    date: Date;
    price: number;
}


const MAX_NEWS_ITEMS = 10;

// --- Helper Functions ---
const formatPrice = (price: number) => {
    return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const getSentimentFromAI = async (text: string): Promise<Sentiment> => {
    try {
        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: `Analyze the financial sentiment of this headline: "${text}". Classify it as "Bullish", "Bearish", or "Neutral". Respond with only one of these three words.`,
        });
        const sentiment = response.text.trim();
        if (sentiment === 'Bullish' || sentiment === 'Bearish' || sentiment === 'Neutral') {
            return sentiment;
        }
        return 'Neutral';
    } catch (error) {
        console.error("Error fetching sentiment:", error);
        return 'Neutral';
    }
};


// --- Components ---
const Header = () => {
    const [time, setTime] = useState(new Date());

    useEffect(() => {
        const timer = setInterval(() => setTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    return (
        <header className="panel header">
            <h1>MARKET PULSE</h1>
            <div className="market-status">
                <span>MARKET OPEN</span>
                <div className="status-dot"></div>
                <span>{time.toLocaleTimeString('en-US', { timeZone: 'America/New_York' })} ET</span>
            </div>
        </header>
    );
};

const MarketIndices = ({ indices, allStocks, onStockSelect, onCustomize }: { indices: IndexItem[], allStocks: MarketItem[], onStockSelect: (stock: MarketItem) => void, onCustomize: () => void }) => {
    const [searchQuery, setSearchQuery] = useState('');

    const filteredStocks = searchQuery
        ? allStocks.filter(stock =>
            stock.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
            stock.name?.toLowerCase().includes(searchQuery.toLowerCase())
        )
        : [];
    
    const renderStockCard = (stock: MarketItem) => {
        const isUp = (stock.change ?? 0) >= 0;
        const changeClass = isUp ? 'text-green' : 'text-red';
        const cardClass = isUp ? 'up' : 'down';
        return (
            <div key={stock.symbol} className={`index-card ${cardClass}`} onClick={() => onStockSelect(stock)} role="button" tabIndex={0}>
                <div className="index-symbol">{stock.symbol}</div>
                <div className="stock-name">{stock.name}</div>
                <div className={`index-price ${changeClass}`}>{formatPrice(stock.price)}</div>
                <div className={`index-change ${changeClass}`}>
                    {stock.change?.toFixed(2) ?? '0.00'} ({stock.pctChange?.toFixed(2) ?? '0.00'}%)
                </div>
            </div>
        );
    }

    return (
        <section className="panel main-content">
            <div className="main-content-header">
                <h2 className="panel-title">{searchQuery ? `Search Results (${filteredStocks.length})` : 'Major Indices'}</h2>
                <div className="header-controls">
                     <button className="customize-button" onClick={onCustomize}>Customize</button>
                    <div className="search-bar">
                        <input
                            type="text"
                            placeholder="Search symbols or names..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            aria-label="Search for stocks"
                        />
                    </div>
                </div>
            </div>

            {searchQuery ? (
                <div className="search-results-grid">
                    {filteredStocks.length > 0 ? (
                        filteredStocks.map(renderStockCard)
                    ) : (
                        <p className="no-results">No results found for "{searchQuery}"</p>
                    )}
                </div>
            ) : (
                <div className="indices-grid">
                    {indices.map(renderStockCard)}
                </div>
            )}
        </section>
    );
};


const NewsPanel = ({ news, setNews, alertKeywords, setAlertKeywords }: { news: NewsItem[], setNews: React.Dispatch<React.SetStateAction<NewsItem[]>>, alertKeywords: string, setAlertKeywords: (keywords: string) => void }) => {
    useEffect(() => {
        const fetchAllSentiments = async () => {
             const itemsToFetch = news.filter(item => item.sentiment === null);
            if (itemsToFetch.length === 0) return;

            const updatedNewsPromises = news.map(async (item) => {
                if (item.sentiment === null) {
                    const sentiment = await getSentimentFromAI(item.headline);
                    return { ...item, sentiment, loading: false };
                }
                return item;
            });
            const updatedNews = await Promise.all(updatedNewsPromises);
            setNews(updatedNews);
        };
        fetchAllSentiments();
    }, [news, setNews]);

    return (
        <aside className="panel news-panel">
            <h2 className="panel-title">News & Sentiment</h2>
             <div className="alert-keywords-container">
                <input
                    type="text"
                    placeholder="Alert keywords: AAPL, rates, ..."
                    value={alertKeywords}
                    onChange={(e) => setAlertKeywords(e.target.value)}
                    aria-label="Set news alert keywords"
                    className="alert-keywords-input"
                />
            </div>
            <ul className="news-list">
                {news.map((item, index) => (
                    <li key={index} className={`news-item ${item.isAlert ? 'alert' : ''}`}>
                        <p className="news-headline">{item.headline}</p>
                        <div className="news-sentiment">
                            {item.loading ? <div className="loading-spinner"></div> :
                                <span className={`sentiment-label-${item.sentiment}`}>{item.sentiment?.toUpperCase()}</span>
                            }
                        </div>
                    </li>
                ))}
            </ul>
        </aside>
    );
};

const CommandLine = () => {
    const [input, setInput] = useState('');
    const [output, setOutput] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        setLoading(true);
        setOutput(`Analyzing sentiment for: "${input}"...`);
        try {
            const response = await ai.models.generateContent({
                model: 'gemini-2.5-flash',
                contents: `Analyze the financial sentiment of: "${input}". Provide a one-sentence justification.`,
            });
            setOutput(response.text);
        } catch (error) {
            setOutput("Error: Could not analyze sentiment.");
            console.error(error);
        }
        setLoading(false);
        setInput('');
    };
    
    return (
        <section className="panel command-line">
            <div className="command-output">
                {loading && <div className="loading-spinner" style={{marginRight: '8px'}}></div>}
                {output}
            </div>
            <form onSubmit={handleSubmit} className="command-input-container">
                <span className="command-prompt">&gt;</span>
                <input
                    type="text"
                    className="command-input"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Enter a stock, headline, or topic for sentiment analysis..."
                    disabled={loading}
                />
            </form>
        </section>
    );
};


const Ticker = ({ items }: { items: MarketItem[] }) => (
    <div className="ticker-wrap">
        <div className="ticker">
            {items.concat(items).map((item, i) => {
                 const isUp = (item.change ?? 0) >= 0;
                 const changeClass = isUp ? 'text-green' : 'text-red';
                return(
                <div className="ticker-item" key={i}>
                    <span>{item.symbol}</span>
                    <span className={changeClass}> {formatPrice(item.price)} ({item.pctChange?.toFixed(2) ?? '+0.00'}%)</span>
                </div>
            )})}
        </div>
    </div>
);

const LineChart = ({ data, isUp }: { data: HistoricalPoint[], isUp: boolean }) => {
    const [tooltip, setTooltip] = useState<{ x: number; y: number; date: string; price: string; } | null>(null);
    const svgRef = useRef<SVGSVGElement>(null);

    const width = 300;
    const height = 100;
    const padding = 10;

    const prices = data.map(d => d.price);
    const maxVal = Math.max(...prices);
    const minVal = Math.min(...prices);
    const range = maxVal - minVal === 0 ? 1 : maxVal - minVal;

    const getCoords = (price: number, index: number) => {
        const x = (index / (data.length - 1)) * (width - padding * 2) + padding;
        const y = height - ((price - minVal) / range) * (height - padding * 2) - padding;
        return { x, y };
    };

    const polylinePoints = data.map((d, i) => {
        const { x, y } = getCoords(d.price, i);
        return `${x},${y}`;
    }).join(' ');

    const handleMouseMove = (event: React.MouseEvent<SVGSVGElement>) => {
        if (!svgRef.current) return;
        const svg = svgRef.current;
        const pt = svg.createSVGPoint();
        pt.x = event.clientX;
        pt.y = event.clientY;
        const cursorPoint = pt.matrixTransform(svg.getScreenCTM()?.inverse());
        
        let closestPoint: { pointData: HistoricalPoint, index: number } | null = null;
        let minDistance = Infinity;

        data.forEach((d, i) => {
            const { x } = getCoords(d.price, i);
            const distance = Math.abs(cursorPoint.x - x);
            if (distance < minDistance) {
                minDistance = distance;
                closestPoint = { pointData: d, index: i };
            }
        });

        if (closestPoint && minDistance < 10) { // Threshold for showing tooltip
            const { x, y } = getCoords(closestPoint.pointData.price, closestPoint.index);
            setTooltip({
                x,
                y,
                date: closestPoint.pointData.date.toLocaleDateString(),
                price: formatPrice(closestPoint.pointData.price),
            });
        } else {
            setTooltip(null);
        }
    };

    const handleMouseLeave = () => {
        setTooltip(null);
    };

    return (
        <svg 
            ref={svgRef} 
            viewBox={`0 0 ${width} ${height}`} 
            className="history-chart"
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
        >
            <polyline
                fill="none"
                stroke={isUp ? "var(--green-color)" : "var(--red-color)"}
                strokeWidth="2"
                points={polylinePoints}
            />
            {tooltip && (
                <g className="chart-tooltip" style={{ pointerEvents: 'none' }}>
                    <line
                        className="chart-tooltip-line"
                        x1={tooltip.x} y1={0}
                        x2={tooltip.x} y2={height}
                    />
                    <circle
                        className="chart-tooltip-point"
                        cx={tooltip.x} cy={tooltip.y}
                        r="4"
                        fill={isUp ? "var(--green-color)" : "var(--red-color)"}
                    />
                     <g transform={`translate(${tooltip.x > width / 2 ? tooltip.x - 100 : tooltip.x + 10}, 5)`}>
                        <rect className="chart-tooltip-bg" width="95" height="30" rx="3" />
                        <text className="chart-tooltip-text" x="5" y="12">
                            {tooltip.date}
                        </text>
                        <text className="chart-tooltip-text-price" x="5" y="25">
                            {tooltip.price}
                        </text>
                    </g>
                </g>
            )}
        </svg>
    );
};


const HistoricalDataModal = ({ stock, onClose }: { stock: MarketItem, onClose: () => void }) => {
    const historicalData: HistoricalPoint[] = useMemo(() => {
        const prices: number[] = [stock.price];
        for (let i = 0; i < 29; i++) {
            const prevPrice = prices[0];
            const change = prevPrice * (Math.random() - 0.5) * 0.05;
            prices.unshift(prevPrice - change);
        }

        return prices.map((price, i) => {
            const date = new Date();
            date.setDate(date.getDate() - (29 - i));
            return { date, price };
        });
    }, [stock.price]);

    const prices = historicalData.map(d => d.price);
    const high = Math.max(...prices);
    const low = Math.min(...prices);
    const startPrice = prices[0];
    const endPrice = prices[prices.length - 1];
    const change30d = endPrice - startPrice;
    const pctChange30d = (change30d / startPrice) * 100;
    const isUp = change30d >= 0;
    const changeClass = isUp ? 'text-green' : 'text-red';

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <button className="modal-close-button" onClick={onClose} aria-label="Close modal">&times;</button>
                <div className="modal-header">
                    <h3>{stock.symbol} - {stock.name}</h3>
                    <p className={`modal-price ${changeClass}`}>{formatPrice(stock.price)}</p>
                </div>
                <div className="modal-body">
                    <h4>30-Day Performance</h4>
                    <LineChart data={historicalData} isUp={isUp} />
                    <div className="stats-grid">
                        <div>
                            <span className="stat-label">30D Change</span>
                            <span className={`stat-value ${changeClass}`}>{change30d.toFixed(2)} ({pctChange30d.toFixed(2)}%)</span>
                        </div>
                         <div>
                            <span className="stat-label">30D High</span>
                            <span className="stat-value">{formatPrice(high)}</span>
                        </div>
                        <div>
                            <span className="stat-label">30D Low</span>
                            <span className="stat-value">{formatPrice(low)}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const CustomizeIndicesModal = ({ allIndices, displayedIndices, setDisplayedIndices, onClose }: { allIndices: IndexItem[], displayedIndices: IndexItem[], setDisplayedIndices: React.Dispatch<React.SetStateAction<IndexItem[]>>, onClose: () => void }) => {
    const displayedSymbols = useMemo(() => new Set(displayedIndices.map(i => i.symbol)), [displayedIndices]);
    const availableIndices = useMemo(() => allIndices.filter(i => !displayedSymbols.has(i.symbol)), [allIndices, displayedSymbols]);
    
    const dragItem = useRef<number | null>(null);
    const dragOverItem = useRef<number | null>(null);

    const handleDragStart = (e: React.DragEvent<HTMLLIElement>, index: number) => {
        dragItem.current = index;
        e.dataTransfer.effectAllowed = 'move';
    };
    
    const handleDragEnter = (index: number) => {
        dragOverItem.current = index;
    };
    
    const handleDragEnd = () => {
        if (dragItem.current === null || dragOverItem.current === null) return;
        
        const newDisplayedIndices = [...displayedIndices];
        const draggedItemContent = newDisplayedIndices.splice(dragItem.current, 1)[0];
        newDisplayedIndices.splice(dragOverItem.current, 0, draggedItemContent);
        
        dragItem.current = null;
        dragOverItem.current = null;
        
        setDisplayedIndices(newDisplayedIndices);
    };

    const addIndex = (indexToAdd: IndexItem) => {
        setDisplayedIndices(prev => [...prev, indexToAdd]);
    };

    const removeIndex = (symbolToRemove: string) => {
        setDisplayedIndices(prev => prev.filter(i => i.symbol !== symbolToRemove));
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content customize-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h3>Customize Indices</h3>
                </div>
                <div className="customize-modal-body">
                    <div className="indices-list-container">
                        <h4>Displayed Indices ({displayedIndices.length})</h4>
                        <ul className="indices-list">
                            {displayedIndices.map((item, index) => (
                                <li 
                                    key={item.symbol} 
                                    className="customize-list-item"
                                    draggable
                                    onDragStart={(e) => handleDragStart(e, index)}
                                    onDragEnter={() => handleDragEnter(index)}
                                    onDragEnd={handleDragEnd}
                                    onDragOver={(e) => e.preventDefault()}
                                >
                                    <span className="drag-handle">::</span>
                                    <span>{item.symbol} - {item.name}</span>
                                    <button onClick={() => removeIndex(item.symbol)} className="list-action-button remove-btn">-</button>
                                </li>
                            ))}
                        </ul>
                    </div>
                    <div className="indices-list-container">
                        <h4>Available Indices ({availableIndices.length})</h4>
                        <ul className="indices-list">
                           {availableIndices.map((item) => (
                                <li key={item.symbol} className="customize-list-item">
                                    <span>{item.symbol} - {item.name}</span>
                                    <button onClick={() => addIndex(item)} className="list-action-button add-btn">+</button>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
                 <div className="modal-footer">
                    <button className="done-button" onClick={onClose}>Done</button>
                </div>
            </div>
        </div>
    );
};


const App = () => {
    const [allIndices] = useState<IndexItem[]>(allAvailableIndices.map(i => ({...i, change: 0, pctChange: 0})));
    const [displayedIndices, setDisplayedIndices] = useState<IndexItem[]>(
        allIndices.slice(0, 6)
    );
    const [tickerData, setTickerData] = useState<MarketItem[]>(
        initialTickerData.map(t => ({...t, change: 0, pctChange: 0}))
    );
    const [news, setNews] = useState<NewsItem[]>(initialNews);
    const [selectedStock, setSelectedStock] = useState<MarketItem | null>(null);
    const [alertKeywords, setAlertKeywords] = useState('');
    const [isCustomizeModalOpen, setCustomizeModalOpen] = useState(false);

    const audioContextRef = useRef<AudioContext | null>(null);

    const playAlertSound = useCallback(() => {
        if (!audioContextRef.current) {
            audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
        }
        const audioContext = audioContextRef.current;
        if (audioContext.state === 'suspended') {
            audioContext.resume();
        }
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(880, audioContext.currentTime);
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.00001, audioContext.currentTime + 0.5);

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.2);
    }, []);

    // Effect for updating market data prices
    useEffect(() => {
        const updateData = () => {
            const updateItem = (item: MarketItem) => {
                const changeFactor = (Math.random() - 0.49) * 0.01; // small random change
                const change = item.price * changeFactor;
                const newPrice = item.price + change;
                const pctChange = (change / item.price) * 100;
                return { ...item, price: newPrice, change, pctChange };
            };
            setDisplayedIndices(prev => prev.map(updateItem));
            setTickerData(prev => prev.map(updateItem));
        };

        const marketDataInterval = setInterval(updateData, 2000); // Update every 2 seconds
        return () => clearInterval(marketDataInterval);
    }, []);

    // Effect for adding new news headlines
    useEffect(() => {
        const keywords = alertKeywords.toLowerCase().split(',').map(k => k.trim()).filter(Boolean);
        const addNewsItem = () => {
            setNews(currentNews => {
                const existingHeadlines = new Set(currentNews.map(n => n.headline));
                let newHeadline: string;
                do {
                    newHeadline = mockHeadlinesPool[Math.floor(Math.random() * mockHeadlinesPool.length)];
                } while (existingHeadlines.has(newHeadline));
                
                const isMatch = keywords.length > 0 && keywords.some(keyword => newHeadline.toLowerCase().includes(keyword));

                if (isMatch) {
                    playAlertSound();
                }

                const newItem: NewsItem = {
                    headline: newHeadline,
                    sentiment: null,
                    loading: true,
                    isAlert: isMatch,
                };
                return [newItem, ...currentNews].slice(0, MAX_NEWS_ITEMS);
            });
        };
        const newsInterval = setInterval(addNewsItem, 10000); // Add a new headline every 10 seconds
        return () => clearInterval(newsInterval);
    }, [alertKeywords, playAlertSound]);
    
    // Effect for handling modal closing with Escape key
    useEffect(() => {
        const handleEsc = (event: KeyboardEvent) => {
           if (event.key === 'Escape') {
            setSelectedStock(null);
            setCustomizeModalOpen(false);
           }
        };
        window.addEventListener('keydown', handleEsc);
        return () => {
            window.removeEventListener('keydown', handleEsc);
        };
    }, []);


    return (
        <>
            <Header />
            <MarketIndices 
                indices={displayedIndices} 
                allStocks={[...allIndices, ...tickerData]}
                onStockSelect={setSelectedStock} 
                onCustomize={() => setCustomizeModalOpen(true)}
            />
            <NewsPanel news={news} setNews={setNews} alertKeywords={alertKeywords} setAlertKeywords={setAlertKeywords}/>
            <CommandLine />
            <Ticker items={tickerData} />
            {selectedStock && <HistoricalDataModal stock={selectedStock} onClose={() => setSelectedStock(null)} />}
            {isCustomizeModalOpen && <CustomizeIndicesModal 
                allIndices={allIndices}
                displayedIndices={displayedIndices}
                setDisplayedIndices={setDisplayedIndices}
                onClose={() => setCustomizeModalOpen(false)}
            />}
        </>
    );
};

const root = createRoot(document.getElementById('root'));
root.render(<App />);
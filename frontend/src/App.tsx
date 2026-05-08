import { useEffect, useState } from "react";
import { analyzeText, getThreshold, setThreshold as apiSetThreshold } from "./api";
import type { AnalysisResponse } from "./types";

const SARCASTIC_EXAMPLES = [
  "رائع جداً، هذا أفضل يوم في حياتي مع هذا الفشل الذريع 🙃💔",
  "يعطيهم الصحة سونيغاز، قطعوا التريسيتي في عز السخانة، إبداع! 👏🔥",
  "الكونيكسيون طيارة، الباج تحل بعد ساعة، روعة. 🐢💻",
  "تصميم التطبيق مذهل، يعطيك صداع نصفي مجاني مع كل استخدام.",
  "حقا؟ لم أكن أعلم أن التأخير لمدة ساعتين يعتبر 'في الموعد'.",
  "خدمة عملاء ممتازة، يردون عليك بعد أسبوع ليعتذروا.",
  "زيد احكيلي، راني نتعلم من 'التجربة' العظيمة تاعك... سبحان الله كيفاش راك عايش. 🧐🍿",
  "ما شاء الله على الفلسفة... سقراط راهو يبكي في قبره من الغيرة. 😭📜",
  "واو، مطعم ممتاز، أكلت فيه ورحت المستشفى من كثرة الروعة. 🤢🏥👏",
  "ما شاء الله، الطريق نظيف جداً، كل حفرة أكبر من الثانية."
];

const NORMAL_EXAMPLES = [
  "السلام عليكم، واش راكم؟ ان شاء الله تكونوا لاباس",
  "الماكلة تاع اليوم كانت بنينة بزاف، يعطيك الصحة.",
  "يعطيك الصحة على هاد الخدمة الزينة.",
  "أتمنى أن تنجح في امتحاناتك القادمة.",
  "القهوة في هذا المقهى طعمها لذيذ حقاً.",
  "لقد استمتعت بقراءة هذا الكتاب المفيد.",
  "قضيت وقتاً ممتعاً مع عائلتي أمس.",
  "راني حاب نتعلم لغات برمجة جديدة.",
  "أنا مهتم بتعلم لغات برمجة جديدة.",
  "الرحلة كانت مريحة وممتعة للغاية."
];

interface BulkResult {
  text: string;
  result?: AnalysisResponse;
  error?: string;
  loading: boolean;
}

export default function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  
  // Bulk state
  const [bulkMode, setBulkMode] = useState(false);
  const [bulkResults, setBulkResults] = useState<BulkResult[]>([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [theme, setTheme] = useState("dark");
  const [lang, setLang] = useState("ar");

  const [threshold, setThreshold] = useState(31);
  const [sarcasticIdx, setSarcasticIdx] = useState(0);
  const [normalIdx, setNormalIdx] = useState(0);

  useEffect(() => {
    if (theme === "light") {
      document.body.classList.add("light-mode");
    } else {
      document.body.classList.remove("light-mode");
    }
  }, [theme]);

  useEffect(() => {
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  }, [lang]);

  useEffect(() => {
    const fetchThreshold = async () => {
      try {
        const val = await getThreshold();
        setThreshold(Math.round(val * 100));
      } catch (err) {
        console.error("Failed to fetch threshold:", err);
      }
    };
    fetchThreshold();
  }, []);

  const handleThresholdChange = async (newVal: number) => {
    setThreshold(newVal);
    try {
      await apiSetThreshold(newVal / 100);
    } catch (err) {
      console.error("Failed to update threshold:", err);
    }
  };

  const toggleTheme = () => setTheme(prev => (prev === "light" ? "dark" : "light"));
  const toggleLanguage = () => setLang(prev => (prev === "ar" ? "en" : "ar"));

  const loadSarcasticExample = () => {
    setText(SARCASTIC_EXAMPLES[sarcasticIdx]);
    setSarcasticIdx((prev) => (prev + 1) % SARCASTIC_EXAMPLES.length);
  };

  const loadNormalExample = () => {
    setText(NORMAL_EXAMPLES[normalIdx]);
    setNormalIdx((prev) => (prev + 1) % NORMAL_EXAMPLES.length);
  };

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    
    if (bulkMode) {
      const lines = text.split('\n').filter(line => line.trim().length > 0);
      if(lines.length === 0) return;
      
      setLoading(true);
      setError(null);
      setResult(null);
      
      const initialBulk = lines.map(line => ({ text: line, loading: true }));
      setBulkResults(initialBulk);
      
      const promises = lines.map(async (line, index) => {
        try {
          const data = await analyzeText({ text: line, languageOverride: null });
          setBulkResults(prev => {
            const newRes = [...prev];
            newRes[index] = { text: line, result: data, loading: false };
            return newRes;
          });
        } catch(err) {
          setBulkResults(prev => {
            const newRes = [...prev];
            newRes[index] = { text: line, error: (err as Error).message, loading: false };
            return newRes;
          });
        }
      });
      
      await Promise.all(promises);
      setLoading(false);

    } else {
      setLoading(true);
      setError(null);
      setResult(null);
      setBulkResults([]);

      try {
        const data = await analyzeText({ text, languageOverride: null });
        setTimeout(() => {
          setResult(data);
          setLoading(false);
        }, 300);
      } catch (err) {
        setError((err as Error).message);
        setLoading(false);
      }
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (ev) => {
      const resultText = String(ev.target?.result || "");
      setText(resultText);
      if(resultText.includes('\n')) setBulkMode(true);
    };
    reader.readAsText(file, "utf-8");
  };

  return (
    <>
      <nav>
        <a className="nav-logo" href="#hero">INFER<span>A</span></a>
        <ul className="nav-links">
          <li><a href="#analyzer">{lang === "ar" ? "تحليل" : "Analyze"}</a></li>
          <li><a href="#about">{lang === "ar" ? "حول" : "About"}</a></li>
        </ul>
        <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
          <button className="theme-btn" onClick={toggleLanguage}>
            {lang === "en" ? "العربية" : "English"}
          </button>
          <button className="theme-btn" onClick={toggleTheme}>
            {theme === "dark" ? "☀ Light" : "☾ Dark"}
          </button>
          <button className="nav-cta" onClick={() => document.querySelector('#analyzer')?.scrollIntoView({ behavior: 'smooth' })}>
            {lang === "ar" ? "ابدأ التحليل" : "Start Analysis"}
          </button>
        </div>
      </nav>

      <section id="hero">
        <div className="hero-bg-grid"></div>
        <div className="hero-bg-scanlines"></div>
        <div className="hero-left">
          <div className="hero-tag">AI-Powered Sarcasm Detection</div>
          <h1 className="hero-h1">
            <span>{lang === "ar" ? "اقرأ" : "READ"}</span><br />
            <span className="red">{lang === "ar" ? "ما بين" : "BETWEEN"}</span><br />
            <span className="stroke">{lang === "ar" ? "السطور" : "THE LINES"}</span>
          </h1>
          <p className="hero-sub" dangerouslySetInnerHTML={{
            __html: lang === "ar"
              ? "<strong>إنفيرا</strong> يفك تشفير المعنى الخفي وراء النص.<br>مدعوم بنموذج MARBERTv2، يكتشف السخرية والتهكم والتناقض النغمي بدقة متناهية."
              : "<strong>INFERA</strong> decodes the hidden meaning behind text.<br>Powered by the MARBERTv2 Transformer, it detects sarcasm, irony, and tonal contradiction with surgical precision."
          }}></p>
          <div className="hero-btns">
            <button className="btn-primary" onClick={() => document.querySelector('#analyzer')?.scrollIntoView({ behavior: 'smooth' })}>
              <span>{lang === "ar" ? "تحليل النص" : "Analyze Text"}</span> <span className="btn-arrow">→</span>
            </button>
          </div>
        </div>
        <div className="hero-right">
          <div className="mask-wrap"></div>
        </div>
      </section>

      <section id="analyzer">
        <div className="analyzer-inner">
          <div className="section-tag">Live Analyzer</div>
          <h2 className="section-h2">
            <span>{lang === "ar" ? "اكتشف" : "DETECT"}</span> <span className="red">{lang === "ar" ? "السخرية" : "SARCASM"}</span> <span className="stroke">{lang === "ar" ? "الآن" : "NOW"}</span>
          </h2>

          <div className="input-container">
            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '8px'}}>
               <span style={{ fontSize: "0.8rem", color: "var(--gray3)" }}>Mode: {bulkMode ? 'Bulk (Rows)' : 'Single'}</span>
               <button className="theme-btn" onClick={() => setBulkMode(!bulkMode)} style={{padding: '4px 8px'}}>
                 {lang === "ar" ? (bulkMode ? "تبديل لمفرد" : "تبديل لجماعي") : (bulkMode ? "Switch to Single" : "Switch to Bulk")}
               </button>
            </div>
            
            <textarea
              placeholder={lang === "ar" ? (bulkMode ? "أدخل عدة نصوص، كل نص في سطر..." : "أدخل النص العربي هنا...") : (bulkMode ? "Enter multiple texts, one per line..." : "Enter Arabic text here...")}
              maxLength={bulkMode ? 20000 : 2000}
              value={text}
              onChange={(e) => setText(e.target.value)}
              style={bulkMode ? { minHeight: "200px" } : {}}
            />
            <div className="input-actions" style={{ flexWrap: "wrap", gap: "10px" }}>
              <span className="char-count">{text.length} / {bulkMode ? 20000 : 2000}</span>
              <div style={{ display: "flex", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
                <input type="file" id="fileInputBtn" style={{ display: "none" }} accept=".txt,.csv" onChange={handleFileUpload} />
                <button className="theme-btn" onClick={() => document.getElementById("fileInputBtn")?.click()}>
                  {lang === "ar" ? "تحميل ملف" : "Upload File"}
                </button>
                <button className="theme-btn" onClick={loadSarcasticExample}>
                  {lang === "ar" ? "مثال ساخر" : "Example S"}
                </button>
                <button className="theme-btn" onClick={loadNormalExample}>
                  {lang === "ar" ? "مثال عادي" : "Example N"}
                </button>
                <button className="analyze-btn" onClick={handleAnalyze} disabled={loading}>
                  <span>{loading ? (lang === "ar" ? "جاري التحليل..." : "Analyzing...") : (lang === "ar" ? "التحقق من السخرية" : "Check Sarcasm")}</span>
                  {loading ? <div className="spinner" style={{ marginLeft: "10px" }}></div> : <span className="btn-arrow" style={{ marginLeft: "10px" }}>→</span>}
                </button>
              </div>
            </div>
          </div>

          <div style={{ width: "100%", maxWidth: "800px", marginTop: "14px", display: "flex", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
            <div style={{ display: "flex", gap: "10px", alignItems: "center", marginLeft: "auto" }}>
              <label style={{ fontSize: "0.8rem", color: "var(--gray3)" }}>Threshold</label>
              <input type="range" min="0" max="100" step="1" style={{ width: "160px" }} value={threshold} onChange={(e) => handleThresholdChange(Number(e.target.value))} />
              <span style={{ fontFamily: "var(--font-mono)", color: "var(--gray3)" }}>{threshold}%</span>
            </div>
          </div>

          {error && <div style={{ color: "var(--red)", marginTop: "15px" }}>{error}</div>}

          {/* Single Result */}
          {!bulkMode && result && (
            <div className="result-card">
              <div className={`result-badge ${result.is_sarcastic ? "sarcastic" : "not-sarcastic"}`}>
                <div className="badge-dot"></div>
                {result.is_sarcastic ? (lang === "ar" ? "تم اكتشاف سخرية" : "SARCASTIC DETECTED") : (lang === "ar" ? "غير ساخر" : "NOT SARCASTIC")}
              </div>
              
              <div className="confidence-section">
                <div className="confidence-header">
                  <span className="confidence-label">{lang === "ar" ? "درجة الثقة" : "Confidence Score"}</span>
                  <div className="confidence-val"><span>{(result.confidence * 100).toFixed(0)}</span><span>%</span></div>
                </div>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width: `${result.confidence * 100}%` }}></div>
                </div>
              </div>

              {result.is_sarcastic && (
                <div className="advanced-features" style={{ display: "grid" }}>
                  <div className="feature-box">
                    <div className="feature-label">{lang === "ar" ? "نوع السخرية" : "Sarcasm Type"}</div>
                    <div className="feature-val">{result.sarcasm_type.replace(/_/g, " ")}</div>
                  </div>
                  <div className="feature-box">
                    <div className="feature-label">{lang === "ar" ? "الهدف" : "Target"}</div>
                    <div className="feature-val">{result.target}</div>
                  </div>
                  <div className="feature-box">
                    <div className="feature-label">{lang === "ar" ? "الشدة" : "Intensity"}</div>
                    <div className="feature-val">{result.intensity}/5</div>
                    <div className="intensity-bar-wrap">
                      <div className="intensity-bar-fill" style={{ width: `${result.intensity * 20}%`, background: ["#4ade80", "#facc15", "#fb923c", "#ef4444", "#b91c1c"][result.intensity - 1] }}></div>
                    </div>
                  </div>
                  {result.explanation && result.explanation !== "The model did not cross the sarcasm threshold." && (
                    <div className="feature-box" style={{ gridColumn: "1 / -1" }}>
                      <div className="feature-label">{lang === "ar" ? "التفسير" : "Explanation"}</div>
                      <div className="feature-val" style={{ fontSize: "0.9rem", whiteSpace: "pre-wrap", color: "var(--white2)", lineHeight: "1.6" }}>
                        {result.explanation}
                      </div>
                    </div>
                  )}
                  <div className="feature-box" style={{ gridColumn: "1 / -1" }}>
                    <div className="feature-label">{lang === "ar" ? "المؤشرات والكلمات" : "Indicators & Words"}</div>
                    <div className="feature-val" style={{ fontSize: "0.9rem", whiteSpace: "pre-wrap", color: "var(--white2)", lineHeight: "1.6" }}>
                      {result.indicators && result.indicators.length > 0 
                        ? result.indicators.map((ind, i) => <div key={i} style={{ marginBottom: "6px" }}>• {ind}</div>)
                        : (lang === "ar" ? "النموذج لم يحدد كلمات معينة" : "No specific words identified by the model")}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Bulk Results */}
          {bulkMode && bulkResults.length > 0 && (
             <div style={{ marginTop: '20px', width: '100%', maxWidth: '800px' }}>
                <h3 style={{color: 'var(--white)', marginBottom: '15px'}}>{lang === 'ar' ? 'النتائج الجماعية' : 'Bulk Results'}</h3>
                <div style={{display: 'flex', flexDirection: 'column', gap: '10px'}}>
                  {bulkResults.map((br, i) => (
                    <div key={i} className="result-card" style={{padding: '15px', display: 'flex', flexDirection: 'column', gap: '10px'}}>
                      <div style={{color: 'var(--gray1)', fontSize: '0.9rem', marginBottom: '5px'}}>{br.text}</div>
                      {br.loading ? (
                         <div style={{color: 'var(--gray3)'}}>Analyzing...</div>
                      ) : br.error ? (
                         <div style={{color: 'var(--red)'}}>{br.error}</div>
                      ) : br.result && (
                         <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                            <div className={`result-badge ${br.result.is_sarcastic ? "sarcastic" : "not-sarcastic"}`} style={{margin: 0}}>
                               <div className="badge-dot"></div>
                               {br.result.is_sarcastic ? "SARCASTIC" : "NORMAL"} ({(br.result.confidence * 100).toFixed(0)}%)
                            </div>
                            {br.result.is_sarcastic && (
                               <div style={{display: 'flex', gap: '10px', fontSize: '0.8rem'}}>
                                 <span style={{color: 'var(--red)'}}>Target: {br.result.target}</span>
                                 <span style={{color: 'var(--orange)'}}>Intensity: {br.result.intensity}/5</span>
                               </div>
                            )}
                         </div>
                      )}
                    </div>
                  ))}
                </div>
             </div>
          )}

        </div>
      </section>

      <section id="about">
        <div className="about-inner">
          <div className="section-tag">About</div>
          <h2 className="section-h2"><span>{lang === "ar" ? "الذكاء" : "THE"}</span> <span className="red">{lang === "ar" ? "وراء" : "INTELLIGENCE"}</span> <span className="stroke">{lang === "ar" ? "ذلك" : "BEHIND IT"}</span></h2>
          <div className="about-grid">
            <div className="about-text">
              <p dangerouslySetInnerHTML={{
                __html: lang === "ar" 
                ? "<strong>إنفيرا</strong> هو مشروع بحثي يضم نموذجاً لكشف السخرية العربية مبنياً على محول MARBERTv2."
                : "<strong>INFERA</strong> is an AI research project featuring an Arabic Sarcasm Detection model based on a fine-tuned MARBERTv2 transformer. It achieves 88.9% accuracy."
              }}></p>
            </div>
            <div className="about-features">
              <div className="about-feat">
                <div className="feat-title">MARBERTv2 Model</div>
                <div className="feat-desc">Fine-tuned state-of-the-art transformer architecture designed for Arabic dialect understanding.</div>
              </div>
              <div className="about-feat">
                <div className="feat-title">Real-time API</div>
                <div className="feat-desc">FastAPI REST API with clean endpoints and structured JSON responses for seamless integration.</div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
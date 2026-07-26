import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  BarChart3,
  Bell,
  BrainCircuit,
  Database,
  Download,
  FileSearch,
  LineChart as LineChartIcon,
  MessageCircle,
  PlusCircle,
  Send,
  ShieldCheck,
  Sparkles,
  StickyNote,
  Upload,
  X,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const API_BASE = import.meta.env.VITE_API_BASE || "https://school-ai-campus-assistant.onrender.com";

const prompts = [
  "Aling lab supplies ang paubos na?",
  "Which courses have the most student activity?",
  "Show project scores greater than 85.",
  "Show students with low performance.",
  "Predict next month's enrollment activity.",
  "Generate a school report.",
];

const formatMoney = (value) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value || 0);

const formatChartValue = (value, chart) => (chart?.format === "money" ? formatMoney(value) : String(value ?? 0));

function Metric({ icon: Icon, label, value, accent, onClick }) {
  const handleKeyDown = (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      onClick();
    }
  };

  return (
    <div
      className="metric"
      role="button"
      tabIndex={0}
      onClick={onClick}
      onMouseDown={onClick}
      onPointerDown={(event) => {
        event.preventDefault();
        onClick();
      }}
      onKeyDown={handleKeyDown}
    >
      <div className={`metricIcon ${accent}`}>
        <Icon size={18} />
      </div>
      <div>
        <p>{label}</p>
        <strong>{value}</strong>
      </div>
    </div>
  );
}

function EvidenceTable({ rows }) {
  if (!rows?.length || typeof rows[0] !== "object") return null;
  const columns = Object.keys(rows[0]).slice(0, 6);

  return (
    <div className="tableWrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column.replaceAll("_", " ")}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, 8).map((row, index) => (
            <tr key={`${index}-${columns[0]}`}>
              {columns.map((column) => (
                <td key={column}>{String(row[column])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ResultChart({ chart }) {
  const data = useMemo(() => {
    if (!chart?.x || !chart?.y) return [];
    return chart.x.map((label, index) => ({ label, value: chart.y[index] }));
  }, [chart]);

  if (!data.length) return null;

  return (
    <div className="chartBox">
      <div className="sectionTitle">
        <LineChartIcon size={16} />
        <span>{chart.label}</span>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        {chart.type === "line" ? (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="label" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip formatter={(value) => formatChartValue(value, chart)} />
            <Line type="monotone" dataKey="value" stroke="#117865" strokeWidth={3} dot={{ r: 4 }} />
          </LineChart>
        ) : (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="label" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip formatter={(value) => formatChartValue(value, chart)} />
            <Bar dataKey="value" fill="#c45b38" radius={[4, 4, 0, 0]} />
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}

function downloadReport(markdown) {
  if (!markdown) return;
  const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "ai-school-report.md";
  link.click();
  URL.revokeObjectURL(url);
}

function App() {
  const [summary, setSummary] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [message, setMessage] = useState("Aling lab supplies ang paubos na?");
  const [activeResult, setActiveResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [chatOpen, setChatOpen] = useState(false);
  const [showPrompts, setShowPrompts] = useState(true);
  const [activeView, setActiveView] = useState("console");
  const [showDocuments, setShowDocuments] = useState(false);
  const [activeAddTab, setActiveAddTab] = useState("sql");
  const [sqlMode, setSqlMode] = useState("inventory");
  const [addStatus, setAddStatus] = useState("");
  const [notifications, setNotifications] = useState([]);
  const [selectedNotification, setSelectedNotification] = useState(null);
  const [inventoryForm, setInventoryForm] = useState({
    sku: "N-500",
    product: "Arduino Uno Kit",
    category: "Embedded Systems",
    stock_remaining: "4",
    reorder_level: "10",
    supplier: "Engineering Lab",
    note: "Extra note for the school lab supply tracker.",
  });
  const [saleForm, setSaleForm] = useState({
    date: "2026-08-01",
    product: "Capstone Prototype Review",
    category: "Computer Engineering",
    quantity: "6",
    amount: "92",
    customer_segment: "4th Year",
    note: "Added student project score sample to test school records.",
  });
  const [forecastForm, setForecastForm] = useState({
    month: "2026-08",
    revenue: "88",
    note: "Planning input for next enrollment/activity forecast demo.",
  });
  const [documentForm, setDocumentForm] = useState({
    title: "New Capstone Submission Policy",
    source_type: "DOCX",
    content: "Students with delayed capstone progress should receive adviser check-ins and lab support within seven days.",
    note: "Added to school RAG knowledge base.",
  });
  const [aiNoteForm, setAiNoteForm] = useState({
    title: "School AI Assistant Demo Note",
    source_type: "AI_NOTE",
    content: "When answering school questions, show record evidence, source snippets, workflow steps, and recommendations.",
    note: "This helps explain how the school agent makes decisions.",
  });

  async function refreshDashboardData() {
    fetch(`${API_BASE}/dashboard/summary`)
      .then((response) => response.json())
      .then(setSummary)
      .catch(() => setSummary(null));

    fetch(`${API_BASE}/documents`)
      .then((response) => response.json())
      .then(setDocuments)
      .catch(() => setDocuments([]));
  }

  useEffect(() => {
    refreshDashboardData();
  }, []);

  async function askAgent(nextMessage = message) {
    if (!nextMessage.trim()) return;
    setLoading(true);
    setError("");
    setMessage(nextMessage);
    setShowPrompts(false);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: nextMessage }),
      });
      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }
      const result = await response.json();
      setActiveResult(result);
    } catch {
      setError("Backend API is not responding yet. Please wait a moment and try again.");
    } finally {
      setLoading(false);
    }
  }

  function openView(view, question) {
    setActiveView(view);
    if (question) {
      askAgent(question);
    }
  }

  function addNotification(payload) {
    const notification = {
      id: Date.now(),
      createdAt: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      ...payload,
    };
    setNotifications((items) => [notification, ...items].slice(0, 6));
    setSelectedNotification(notification);
  }

  async function submitAddData(event) {
    event.preventDefault();
    setAddStatus("Saving...");

    const config = (() => {
      if (activeAddTab === "sql" && sqlMode === "inventory") {
        return {
          endpoint: "/data/inventory",
          payload: {
            ...inventoryForm,
            stock_remaining: Number(inventoryForm.stock_remaining),
            reorder_level: Number(inventoryForm.reorder_level),
          },
        };
      }

      if (activeAddTab === "sql" && sqlMode === "sales") {
        return {
          endpoint: "/data/sales",
          payload: {
            ...saleForm,
            quantity: Number(saleForm.quantity),
            amount: Number(saleForm.amount),
          },
        };
      }

      if (activeAddTab === "forecast") {
        return {
          endpoint: "/data/forecast-points",
          payload: {
            ...forecastForm,
            revenue: Number(forecastForm.revenue),
          },
        };
      }

      if (activeAddTab === "ai") {
        return { endpoint: "/ai/notes", payload: aiNoteForm };
      }

      return { endpoint: "/documents/text", payload: documentForm };
    })();

    try {
      const response = await fetch(`${API_BASE}${config.endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config.payload),
      });
      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.detail || "Unable to save data.");
      }

      addNotification({
        title: result.message,
        kind: result.kind,
        item: result.item,
      });
      setAddStatus("Saved. Click the notification to review the new item.");
      refreshDashboardData();
    } catch (err) {
      setAddStatus(err.message || "Unable to save data.");
    }
  }

  function updateForm(setter, key, value) {
    setter((current) => ({ ...current, [key]: value }));
  }

  function renderField(label, value, onChange, type = "text") {
    return (
      <label className="field">
        <span>{label}</span>
        <input type={type} value={value} onChange={(event) => onChange(event.target.value)} />
      </label>
    );
  }

  function renderNoteField(label, value, onChange) {
    return (
      <label className="field full">
        <span>{label}</span>
        <textarea value={value} onChange={(event) => onChange(event.target.value)} rows={3} />
      </label>
    );
  }

  function renderAddForm() {
    if (activeAddTab === "sql" && sqlMode === "inventory") {
      return (
        <>
          {renderField("SKU", inventoryForm.sku, (value) => updateForm(setInventoryForm, "sku", value))}
          {renderField("Supply item", inventoryForm.product, (value) => updateForm(setInventoryForm, "product", value))}
          {renderField("Category", inventoryForm.category, (value) => updateForm(setInventoryForm, "category", value))}
          {renderField("Stock", inventoryForm.stock_remaining, (value) => updateForm(setInventoryForm, "stock_remaining", value), "number")}
          {renderField("Reorder level", inventoryForm.reorder_level, (value) => updateForm(setInventoryForm, "reorder_level", value), "number")}
          {renderField("Supplier", inventoryForm.supplier, (value) => updateForm(setInventoryForm, "supplier", value))}
          {renderNoteField("Notes", inventoryForm.note, (value) => updateForm(setInventoryForm, "note", value))}
        </>
      );
    }

    if (activeAddTab === "sql" && sqlMode === "sales") {
      return (
        <>
          {renderField("Date", saleForm.date, (value) => updateForm(setSaleForm, "date", value), "date")}
          {renderField("Activity", saleForm.product, (value) => updateForm(setSaleForm, "product", value))}
          {renderField("Category", saleForm.category, (value) => updateForm(setSaleForm, "category", value))}
          {renderField("Quantity", saleForm.quantity, (value) => updateForm(setSaleForm, "quantity", value), "number")}
          {renderField("Score", saleForm.amount, (value) => updateForm(setSaleForm, "amount", value), "number")}
          {renderField("Year level", saleForm.customer_segment, (value) => updateForm(setSaleForm, "customer_segment", value))}
          {renderNoteField("Notes", saleForm.note, (value) => updateForm(setSaleForm, "note", value))}
        </>
      );
    }

    if (activeAddTab === "forecast") {
      return (
        <>
          {renderField("Month", forecastForm.month, (value) => updateForm(setForecastForm, "month", value), "month")}
          {renderField("Activity score input", forecastForm.revenue, (value) => updateForm(setForecastForm, "revenue", value), "number")}
          {renderNoteField("Notes", forecastForm.note, (value) => updateForm(setForecastForm, "note", value))}
        </>
      );
    }

    if (activeAddTab === "ai") {
      return (
        <>
          {renderField("AI note title", aiNoteForm.title, (value) => updateForm(setAiNoteForm, "title", value))}
          {renderNoteField("AI instruction/context", aiNoteForm.content, (value) => updateForm(setAiNoteForm, "content", value))}
          {renderNoteField("Notes", aiNoteForm.note, (value) => updateForm(setAiNoteForm, "note", value))}
        </>
      );
    }

    return (
      <>
        {renderField("Document title", documentForm.title, (value) => updateForm(setDocumentForm, "title", value))}
        {renderField("Source type", documentForm.source_type, (value) => updateForm(setDocumentForm, "source_type", value))}
        {renderNoteField("Document content", documentForm.content, (value) => updateForm(setDocumentForm, "content", value))}
        {renderNoteField("Notes", documentForm.note, (value) => updateForm(setDocumentForm, "note", value))}
      </>
    );
  }

  return (
    <main>
      <aside className="sidebar">
        <div className="brand">
          <div className="brandIcon">
            <BrainCircuit size={24} />
          </div>
          <div>
            <h1>School AI Agent</h1>
            <p>Campus data assistant</p>
          </div>
        </div>

        <nav>
          <button
            type="button"
            className={activeView === "console" ? "active" : ""}
            onClick={() => openView("console", "Generate a school report.")}
          >
            <Sparkles size={16} />
            Agent Console
          </button>
          <button
            type="button"
            className={activeView === "sql" ? "active" : ""}
            onClick={() => openView("sql", "Show project scores greater than 85.")}
          >
            <Database size={16} />
            School Records
          </button>
          <button
            type="button"
            className={activeView === "rag" ? "active" : ""}
            onClick={() => openView("rag", "What does the capstone policy say about delayed students?")}
          >
            <FileSearch size={16} />
            School Docs
          </button>
          <button
            type="button"
            className={activeView === "forecast" ? "active" : ""}
            onClick={() => openView("forecast", "Predict next month's enrollment activity.")}
          >
            <BarChart3 size={16} />
            Forecasts
          </button>
          <button
            type="button"
            className={activeView === "add" ? "active" : ""}
            onClick={() => setActiveView("add")}
          >
            <PlusCircle size={16} />
            Add School Data
          </button>
        </nav>

        <div className="sourcePanel">
          <button className="sourceToggle" type="button" onClick={() => setShowDocuments((value) => !value)}>
            <Upload size={16} />
            <span>Indexed documents</span>
            <strong>{showDocuments ? "Hide" : "Show"}</strong>
          </button>
          {showDocuments && (
            <div className="docList">
              {documents.map((doc) => (
                <div className="docItem" key={doc.id}>
                  <strong>{doc.title}</strong>
                  <span>{doc.source_type} / {doc.characters} chars</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </aside>

      <section className="workspace">
        <header>
          <div>
            <p className="eyebrow">school records + docs + forecasting</p>
            <h2>Ask questions across campus data</h2>
          </div>
          <div
            className="status"
            role="button"
            tabIndex={0}
            onClick={() => openView("console", "Generate a school report.")}
            onMouseDown={() => openView("console", "Generate a school report.")}
            onPointerDown={(event) => {
              event.preventDefault();
              openView("console", "Generate a school report.");
            }}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                openView("console", "Generate a school report.");
              }
            }}
          >
            <Activity size={15} />
            Live demo
          </div>
        </header>

        <section className="metricsGrid">
          <Metric
            icon={Database}
            label="Tracked students"
            value={summary?.total_students ?? "..."}
            accent="green"
            onClick={() => openView("console", "How many students are tracked?")}
          />
          <Metric
            icon={BarChart3}
            label="Activity records"
            value={summary?.sales_count ?? "..."}
            accent="orange"
            onClick={() => openView("sql", "Show student activity records.")}
          />
          <Metric
            icon={Activity}
            label="Low lab supplies"
            value={summary?.low_stock_count ?? "..."}
            accent="red"
            onClick={() => openView("sql", "Aling lab supplies ang paubos na?")}
          />
          <Metric
            icon={FileSearch}
            label="At-risk students"
            value={summary?.high_risk_customers ?? "..."}
            accent="blue"
            onClick={() => openView("rag", "Which students are at risk?")}
          />
        </section>

        {activeView === "add" && (
        <section className="dataStudio">
          <form className="addPanel" onSubmit={submitAddData}>
            <div className="panelHeader">
              <div>
                <div className="sectionTitle">
                  <PlusCircle size={16} />
                  <span>Add School Data</span>
                </div>
                <p>Add school records, school documents, forecast inputs, or AI notes.</p>
              </div>
            </div>

            <div className="tabRow" role="tablist" aria-label="Add data type">
              {[
                ["sql", "Records"],
                ["rag", "Docs"],
                ["forecast", "Forecast"],
                ["ai", "AI Note"],
              ].map(([key, label]) => (
                <button
                  key={key}
                  type="button"
                  className={activeAddTab === key ? "selected" : ""}
                  onClick={() => setActiveAddTab(key)}
                >
                  {label}
                </button>
              ))}
            </div>

            {activeAddTab === "sql" && (
              <label className="field full">
                <span>Record type</span>
                <select value={sqlMode} onChange={(event) => setSqlMode(event.target.value)}>
                  <option value="inventory">Lab supplies</option>
                  <option value="sales">Student activity</option>
                </select>
              </label>
            )}

            <div className="formGrid">{renderAddForm()}</div>

            <div className="formActions">
              <button className="primaryAction" type="submit">
                <PlusCircle size={17} />
                Add data
              </button>
              {addStatus && <span>{addStatus}</span>}
            </div>
          </form>

          <aside className="notificationsPanel">
            <div className="sectionTitle">
              <Bell size={16} />
              <span>Notifications</span>
            </div>

            {notifications.length ? (
              <div className="notificationList">
                {notifications.map((notification) => (
                  <button
                    key={notification.id}
                    type="button"
                    className={selectedNotification?.id === notification.id ? "notification active" : "notification"}
                    onClick={() => setSelectedNotification(notification)}
                  >
                    <strong>{notification.title}</strong>
                    <span>{notification.kind} / {notification.createdAt}</span>
                  </button>
                ))}
              </div>
            ) : (
              <p className="mutedText">No new data yet.</p>
            )}

            {selectedNotification && (
              <div className="detailBox">
                <div className="sectionTitle">
                  <StickyNote size={16} />
                  <span>Added item</span>
                </div>
                <dl>
                  {Object.entries(selectedNotification.item).map(([key, value]) => (
                    <div key={key}>
                      <dt>{key.replaceAll("_", " ")}</dt>
                      <dd>{String(value ?? "None")}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            )}
          </aside>
        </section>
        )}

        {activeView !== "add" && (
        <section className="consoleGrid">
          <div className="answerPanel">
            {activeResult ? (
              <>
                <div className="answerHeader">
                  <span>{activeResult.intent}</span>
                  <div className="confidence">
                    <ShieldCheck size={15} />
                    {Math.round((activeResult.confidence || 0.86) * 100)}% confidence
                  </div>
                </div>
                <p className="answer">{activeResult.answer}</p>

                {!!activeResult.workflow?.length && (
                  <div className="workflow">
                    <div className="sectionTitle">
                      <BrainCircuit size={16} />
                      <span>Agent workflow</span>
                    </div>
                    <ol>
                      {activeResult.workflow.map((step) => (
                        <li key={step}>{step}</li>
                      ))}
                    </ol>
                  </div>
                )}

                {activeResult.report_markdown && (
                  <button className="downloadButton" type="button" onClick={() => downloadReport(activeResult.report_markdown)}>
                    <Download size={17} />
                    Download report
                  </button>
                )}

                {activeResult.sql && (
                  <pre>
                    <code>{activeResult.sql}</code>
                  </pre>
                )}

                <ResultChart chart={activeResult.chart} />
                <EvidenceTable rows={activeResult.rows} />

                {!!activeResult.sources?.length && (
                  <div className="sources">
                    <div className="sectionTitle">
                      <FileSearch size={16} />
                      <span>Retrieved sources</span>
                    </div>
                    {activeResult.sources.map((source) => (
                      <article key={source.title}>
                        <strong>{source.title}</strong>
                        <p>{source.snippet}</p>
                      </article>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <div className="empty">
                <BrainCircuit size={40} />
                <h3>Run a sample question</h3>
                <p>The agent will choose a school record, document, report, or forecasting tool and show its evidence here.</p>
              </div>
            )}
          </div>
        </section>
        )}
      </section>

      <section className={`chatWidget ${chatOpen ? "open" : "closed"}`} aria-label="Ask the agent">
        <button className="chatBubble" type="button" onClick={() => setChatOpen(true)} title="Open chat">
          <MessageCircle size={22} />
        </button>

        <div className="chatWindow">
          <div className="chatHeader">
            <div>
              <strong>Ask the agent</strong>
              <span>{loading ? "Thinking..." : "Online"}</span>
            </div>
            <button type="button" onClick={() => setChatOpen(false)} title="Minimize chat">
              <X size={17} />
            </button>
          </div>

          {error && <div className="errorBanner">{error}</div>}

          {showPrompts ? (
            <div className="promptGrid">
              {prompts.map((prompt) => (
                <button key={prompt} type="button" onClick={() => askAgent(prompt)} disabled={loading}>
                  {prompt}
                </button>
              ))}
            </div>
          ) : (
            <div className="recommendBox">
              <span>Need recommended questions?</span>
              <button type="button" onClick={() => setShowPrompts(true)}>
                Yes
              </button>
            </div>
          )}

          <form
            onSubmit={(event) => {
              event.preventDefault();
              askAgent();
            }}
          >
            <input value={message} onChange={(event) => setMessage(event.target.value)} aria-label="Question for AI agent" />
            <button className="sendButton" type="submit" disabled={loading} title="Ask agent">
              <Send size={18} />
            </button>
          </form>

        </div>
      </section>
    </main>
  );
}

export default App;

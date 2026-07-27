import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  ArrowRight,
  BarChart3,
  Bell,
  BookOpen,
  BrainCircuit,
  CalendarDays,
  CheckCircle2,
  CircleHelp,
  Clock3,
  Database,
  Download,
  ExternalLink,
  FileSearch,
  GraduationCap,
  Home,
  LineChart as LineChartIcon,
  LockKeyhole,
  MessageCircle,
  MessageSquareWarning,
  MonitorCog,
  PlusCircle,
  School,
  Search,
  Send,
  Settings,
  ShieldCheck,
  Sparkles,
  StickyNote,
  ThumbsDown,
  ThumbsUp,
  Users,
  Upload,
  UserRound,
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

async function apiFetch(path, options = {}, retries = 2) {
  try {
    const response = await fetch(`${API_BASE}${path}`, options);
    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }
    return response;
  } catch (error) {
    if (retries <= 0) {
      throw error;
    }
    await new Promise((resolve) => setTimeout(resolve, 1500));
    return apiFetch(path, options, retries - 1);
  }
}

const promptsByRole = {
  Student: ["Enroll me for the upcoming term.", "Borrow LAB-100 Arduino Uno Kit.", "What scholarships are available?", "What are the library hours?", "How can I reset my campus WiFi password?", "Explain the capstone policy."],
  Registrar: ["Show students with low performance.", "Which students are at risk?", "What policy sources are indexed?", "Show student activity records.", "Generate a school report.", "Which questions need registrar review?"],
  Admin: ["Generate a school report.", "Predict next month's enrollment activity.", "Aling lab supplies ang paubos na?", "Show project scores greater than 85.", "How many students are tracked?", "Show system AI performance."],
};

const roleSignals = [
  { label: "Agent routing", value: "Tool selection + workflow trace" },
  { label: "Structured data", value: "SQL-style campus records" },
  { label: "Document AI", value: "Policy/source retrieval" },
  { label: "ML forecasting", value: "scikit-learn-ready forecast service" },
];

const techBadges = ["React", "FastAPI", "Google Gemini", "SQLAlchemy", "RAG retrieval", "scikit-learn", "Tagalog/English"];

const landingFeatures = [
  [MessageCircle, "AI Assistant", "Natural-language help in English, Filipino, and Taglish."],
  [FileSearch, "RAG Document Search", "Retrieved policy evidence with page-level citations."],
  [Database, "SQL Database", "Structured campus records and visible query evidence."],
  [BrainCircuit, "Multi-Agent", "Specialized Registrar, Finance, Guidance, Library, and IT agents."],
  [BarChart3, "Analytics Dashboard", "Operational metrics, forecasts, latency, and feedback."],
  [LockKeyhole, "Role-Based Experience", "Distinct student, registrar, and admin workspaces."],
  [Sparkles, "ML Inquiry Classifier", "Evaluated scikit-learn routing across seven campus service classes."],
  [MessageSquareWarning, "Human Escalation", "Feedback, tickets, staff review, approvals, and equipment returns."],
];

const roleMeta = {
  Student: { eyebrow: "Student portal", title: "Good morning, Janlyn", subtitle: "Your classes, deadlines, campus updates, and AI support in one place." },
  Registrar: { eyebrow: "Registrar operations", title: "Knowledge and student support", subtitle: "Review questions, maintain policies, and resolve escalated requests." },
  Admin: { eyebrow: "System administration", title: "CampusIQ control center", subtitle: "Monitor users, AI quality, data services, and system performance." },
};

function LandingPage({ onDemo }) {
  const [selectedRole, setSelectedRole] = useState("Student");
  return (
    <div className="landing">
      <nav className="landingNav">
        <div className="brand">
          <div className="brandIcon"><BrainCircuit size={24} /></div>
          <div><h1>CampusIQ</h1><p>Enterprise AI for higher education</p></div>
        </div>
        <div className="landingLinks">
          <a href="#architecture">Architecture</a>
          <a href="https://github.com/Janlyn1/School-AI-Campus-Assistant#readme" target="_blank" rel="noreferrer">Documentation</a>
          <a href="https://github.com/Janlyn1/School-AI-Campus-Assistant" target="_blank" rel="noreferrer">GitHub</a>
          <button type="button" onClick={() => onDemo(selectedRole)}>Try demo <ArrowRight size={16} /></button>
        </div>
      </nav>

      <section className="landingHero">
        <div className="heroCopy">
          <p className="eyebrow">Agentic AI + RAG + SQL + forecasting</p>
          <h1>One campus assistant.<br />The right agent for every question.</h1>
          <p>CampusIQ connects students and staff to structured records, school policies, analytics, and specialized AI workflows with visible evidence.</p>
          <div className="heroActions">
            <select aria-label="Choose demo role" value={selectedRole} onChange={(event) => setSelectedRole(event.target.value)}>
              <option>Student</option><option>Registrar</option><option>Admin</option>
            </select>
            <button type="button" className="heroPrimary" onClick={() => onDemo(selectedRole)}>Open {selectedRole} demo <ArrowRight size={17} /></button>
            <a href="https://github.com/Janlyn1/School-AI-Campus-Assistant" target="_blank" rel="noreferrer">View source <ExternalLink size={15} /></a>
          </div>
          <div className="heroProof"><span><CheckCircle2 size={15} /> Live FastAPI backend</span><span><CheckCircle2 size={15} /> Evidence-first answers</span><span><CheckCircle2 size={15} /> Responsive role portals</span></div>
        </div>
        <div className="heroProduct" aria-label="CampusIQ product preview">
          <div className="previewTop"><span></span><span></span><span></span><strong>CampusIQ Agent Console</strong></div>
          <div className="previewBody">
            <div className="previewRail"><BrainCircuit size={20} /><Home size={17} /><FileSearch size={17} /><BarChart3 size={17} /></div>
            <div className="previewContent">
              <p>Question routed successfully</p>
              <h3>Registrar Agent</h3>
              <div className="previewAnswer">Students with academic risk above 50% should receive an adviser review within seven days.</div>
              <div className="previewEvidence"><span>Source</span><strong>Student Support Playbook</strong><span>Retrieval</span><strong>High relevance</strong></div>
            </div>
          </div>
        </div>
      </section>

      <section className="landingSection">
        <p className="eyebrow">Platform capabilities</p>
        <h2>Built for real campus workflows</h2>
        <div className="featureGrid">
          {landingFeatures.map(([Icon, title, description]) => <article key={title}><Icon size={21} /><h3>{title}</h3><p>{description}</p></article>)}
        </div>
      </section>

      <section className="architectureSection" id="architecture">
        <div><p className="eyebrow">System architecture</p><h2>From question to grounded answer</h2><p>The deployed portfolio uses React/Vite, FastAPI, SQLAlchemy, document retrieval, and scikit-learn. Production-ready extension points are documented for LLM orchestration, PostgreSQL, and pgvector.</p></div>
        <div className="architectureFlow">
          {["Student or Staff", "React Frontend", "FastAPI Backend", "Agent Router", "SQL + RAG + ML", "Grounded Answer"].map((item, index) => <div key={item}><span>{index + 1}</span><strong>{item}</strong>{index < 5 && <ArrowRight size={16} />}</div>)}
        </div>
      </section>

      <footer><strong>CampusIQ</strong><span>Designed and developed by Janlyn Rustila</span><button type="button" onClick={() => onDemo("Student")}>Launch demo</button></footer>
    </div>
  );
}

const formatMoney = (value) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value || 0);

const formatChartValue = (value, chart) => (chart?.format === "money" ? formatMoney(value) : String(value ?? 0));
const relevanceLabel = (score) => (score >= 0.45 ? "High relevance" : score >= 0.2 ? "Moderate relevance" : "Supporting source");

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

function RequestCenter({ role, requests, onAction }) {
  const title = role === "Student" ? "My service requests" : role === "Registrar" ? "Enrollment approvals" : "Equipment borrowing";
  const description = role === "Student" ? "Track requests submitted through Ari." : role === "Registrar" ? "Confirm students who are ready to enroll." : "Approve releases and record returned school equipment.";
  return (
    <section className="requestCenter">
      <div className="panelTitle"><div><p className="eyebrow">{role} workflow</p><h3>{title}</h3><p>{description}</p></div><span className="requestCount">{requests.length} requests</span></div>
      {requests.length ? (
        <div className="requestTable">
          {requests.map((request) => (
            <article key={request.id}>
              <div className="requestIcon">{request.request_type === "enrollment" ? <GraduationCap size={19} /> : <Database size={19} />}</div>
              <div className="requestMain">
                <strong>{request.request_type === "enrollment" ? "Enrollment request" : request.product}</strong>
                <span>{role === "Student" ? `Request #${request.id}` : request.student_name}{request.sku ? ` · ${request.sku} · Qty ${request.quantity}` : ""}</span>
              </div>
              <span className={`requestStatus ${request.status}`}>{request.status.replaceAll("_", " ")}</span>
              <div className="requestActions">
                {role === "Registrar" && request.status === "pending_registrar" && <button type="button" onClick={() => onAction(request.id, "approve")}><CheckCircle2 size={15} /> Confirm enrollment</button>}
                {role === "Admin" && request.status === "pending_admin" && <button type="button" onClick={() => onAction(request.id, "approve")}><CheckCircle2 size={15} /> Approve borrow</button>}
                {role === "Admin" && request.status === "borrowed" && <button type="button" className="returnButton" onClick={() => onAction(request.id, "return")}><ArrowRight size={15} /> Mark returned</button>}
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="requestEmpty"><Clock3 size={28} /><strong>No requests yet</strong><p>{role === "Student" ? "Ask Ari to enroll or borrow a school item." : "New AI-submitted requests will appear here."}</p></div>
      )}
    </section>
  );
}

function RoleOverview({ role, summary, documents, adminMetrics, mlEvaluation, requests, onAsk, onNavigate, onAction }) {
  if (role === "Student") {
    return (
      <section className="roleOverview studentOverview">
        <div className="welcomeBand">
          <div><p className="eyebrow">Monday, July 27</p><h3>Your campus day at a glance</h3><p>You have one upcoming deadline and two new campus updates.</p></div>
          <button type="button" onClick={() => onAsk("How do I enroll?")}><Sparkles size={17} /> Ask CampusIQ</button>
        </div>
        <div className="studentGrid">
          <article><div className="cardHeading"><CalendarDays size={18} /><strong>Upcoming</strong></div><h4>Capstone consultation</h4><p>Tomorrow, 10:00 AM · Engineering Lab</p><span className="softTag">1 day left</span></article>
          <article><div className="cardHeading"><Bell size={18} /><strong>Announcements</strong></div><h4>Enrollment schedule posted</h4><p>Online registration opens August 3 for continuing students.</p><button type="button" onClick={() => onAsk("How do I enroll?")}>View details</button></article>
          <article><div className="cardHeading"><GraduationCap size={18} /><strong>My program</strong></div><h4>BS Computer Engineering</h4><p>4th Year · 18 units this term</p><button type="button" onClick={() => onAsk("What are the graduation requirements?")}>Check requirements</button></article>
        </div>
        <div className="quickServices">
          <strong>Quick services</strong>
          {[["Enrollment", School, "How do I enroll?"], ["Scholarships", GraduationCap, "What scholarships are available?"], ["Library", BookOpen, "What are the library hours?"], ["Campus IT", MonitorCog, "How can I reset my campus WiFi password?"]].map(([label, Icon, question]) => <button type="button" key={label} onClick={() => onAsk(question)}><Icon size={19} /><span>{label}</span><ArrowRight size={15} /></button>)}
        </div>
      </section>
    );
  }

  if (role === "Registrar") {
    return (
      <section className="roleOverview registrarOverview">
        <div className="opsMetrics">
          <article><span>Open tickets</span><strong>6</strong><small>2 high priority</small></article>
          <article><span>Pending enrollment</span><strong>{requests.filter((item) => item.status === "pending_registrar").length}</strong><small>Awaiting confirmation</small></article>
          <article><span>Knowledge documents</span><strong>{documents.length}</strong><small>Indexed and searchable</small></article>
          <article><span>ML routing</span><strong>Evaluated</strong><small>See model metrics in Admin</small></article>
        </div>
        <div className="operationsGrid">
          <article className="queuePanel"><div className="panelTitle"><div><h3>Enrollment request queue</h3><p>AI-submitted requests that need confirmation</p></div><button type="button" onClick={() => onNavigate("requests")}>View all</button></div>
            {requests.length ? requests.slice(0, 3).map((request) => <div className="queueRow" key={request.id}><span><strong>{request.student_name}</strong><small>Request #{request.id} · {request.status.replaceAll("_", " ")}</small></span>{request.status === "pending_registrar" && <button type="button" onClick={() => onAction(request.id, "approve")}>Confirm</button>}</div>) : <div className="miniEmpty">No pending enrollment requests.</div>}
          </article>
          <article className="knowledgeHealth"><h3>Knowledge coverage</h3><p>Current indexed sources</p><div className="healthScore"><strong>{documents.length}</strong><span> documents</span></div><ul><li><CheckCircle2 size={15} /> Page-level citations enabled</li><li><CheckCircle2 size={15} /> Policies searchable</li><li><CircleHelp size={15} /> Staff can add verified sources</li></ul><button type="button" onClick={() => onNavigate("add")}>Add school document</button></article>
        </div>
      </section>
    );
  }

  return (
    <section className="roleOverview adminOverview">
      <div className="opsMetrics adminMetrics">
        <article><span>Synthetic student records</span><strong>{summary?.total_students ?? 0}</strong><small>Demo SQL dataset</small></article>
        <article><span>Logged AI requests</span><strong>{adminMetrics?.total_interactions ?? 0}</strong><small>Persisted interactions</small></article>
        <article><span>Measured latency</span><strong>{adminMetrics?.average_latency_ms ?? 0} ms</strong><small>Average backend routing time</small></article>
        <article><span>Feedback records</span><strong>{adminMetrics?.feedback_count ?? 0}</strong><small>{adminMetrics?.open_tickets ?? 0} escalated tickets</small></article>
      </div>
      <div className="adminGrid">
        <article className="systemChart"><div className="panelTitle"><div><h3>Recent response latency</h3><p>Measured backend time for logged interactions</p></div><span className="onlineTag">{adminMetrics?.source_grounded_answers ?? 0} source-grounded</span></div>
          <ResponsiveContainer width="100%" height={220}><LineChart data={(adminMetrics?.recent || []).slice().reverse().map((item, index) => ({d: `Q${index + 1}`,v:item.latency_ms}))}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="d"/><YAxis/><Tooltip/><Line type="monotone" dataKey="v" stroke="#315b7d" strokeWidth={3}/></LineChart></ResponsiveContainer>
        </article>
        <article className="agentStatus"><h3>Actual agent usage</h3>{(adminMetrics?.agent_usage || []).slice(0, 5).map((item) => <div key={item.agent}><span className="statusDot"/><strong>{item.agent}</strong><small>{item.requests} requests</small></div>)}{!adminMetrics?.agent_usage?.length && <p className="mutedText">No interactions logged yet.</p>}<button type="button" onClick={() => onNavigate("console")}><Settings size={15}/> Open system console</button></article>
      </div>
      {mlEvaluation && <article className="mlPanel">
        <div className="panelTitle"><div><p className="eyebrow">Measured ML evaluation</p><h3>Student inquiry classifier</h3><p>{mlEvaluation.model} · {mlEvaluation.split}</p></div><span className="onlineTag">{mlEvaluation.test_size} held-out examples</span></div>
        <div className="mlMetricGrid">
          {[["Accuracy", mlEvaluation.accuracy], ["Macro precision", mlEvaluation.macro_precision], ["Macro recall", mlEvaluation.macro_recall], ["Macro F1", mlEvaluation.macro_f1]].map(([label, value]) => <div key={label}><span>{label}</span><strong>{(value * 100).toFixed(1)}%</strong></div>)}
        </div>
        <div className="confusionWrap">
          <strong>Confusion matrix</strong>
          <div className="confusionMatrix" style={{ gridTemplateColumns: `90px repeat(${mlEvaluation.labels.length}, 34px)` }}>
            <span />
            {mlEvaluation.labels.map((label) => <span className="matrixLabel top" key={`top-${label}`} title={label}>{label.slice(0, 3)}</span>)}
            {mlEvaluation.confusion_matrix.flatMap((row, rowIndex) => [
              <span className="matrixLabel" key={`label-${mlEvaluation.labels[rowIndex]}`}>{mlEvaluation.labels[rowIndex].slice(0, 10)}</span>,
              ...row.map((value, columnIndex) => <span className={rowIndex === columnIndex ? "matrixCell correct" : "matrixCell"} key={`${rowIndex}-${columnIndex}`}>{value}</span>),
            ])}
          </div>
        </div>
      </article>}
    </section>
  );
}

function App() {
  const [page, setPage] = useState("landing");
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
  const [demoRole, setDemoRole] = useState("Student");
  const [feedbackStatus, setFeedbackStatus] = useState("");
  const [lastQuestion, setLastQuestion] = useState("");
  const [requests, setRequests] = useState([]);
  const [requestStatus, setRequestStatus] = useState("");
  const [adminMetrics, setAdminMetrics] = useState(null);
  const [mlEvaluation, setMlEvaluation] = useState(null);
  const prompts = promptsByRole[demoRole];
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
    apiFetch("/dashboard/summary")
      .then((response) => response.json())
      .then(setSummary)
      .catch(() => setSummary(null));

    apiFetch("/documents")
      .then((response) => response.json())
      .then(setDocuments)
      .catch(() => setDocuments([]));

    apiFetch("/admin/metrics")
      .then((response) => response.json())
      .then(setAdminMetrics)
      .catch(() => setAdminMetrics(null));

    apiFetch("/ml/evaluation")
      .then((response) => response.json())
      .then(setMlEvaluation)
      .catch(() => setMlEvaluation(null));
  }

  async function refreshRequests(role = demoRole) {
    const params = new URLSearchParams({ role });
    if (role === "Student") params.set("student_name", "Janlyn Rustila");
    apiFetch(`/requests?${params.toString()}`)
      .then((response) => response.json())
      .then(setRequests)
      .catch(() => setRequests([]));
  }

  useEffect(() => {
    refreshDashboardData();
  }, []);

  useEffect(() => {
    if (page === "portal") refreshRequests(demoRole);
  }, [demoRole, page]);

  async function askAgent(nextMessage = message) {
    if (!nextMessage.trim()) return;
    setLoading(true);
    setError("");
    setActiveResult({
      answer: "Connecting to the school AI backend. If the Render service was asleep, this can take a few seconds.",
      intent: "waking_backend",
      confidence: 0.7,
      workflow: ["Sending question", "Waking backend if needed", "Waiting for agent response"],
    });
    setMessage(nextMessage);
    setLastQuestion(nextMessage);
    setShowPrompts(false);
    setFeedbackStatus("");

    try {
      const response = await apiFetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: nextMessage, role: demoRole, student_name: "Janlyn Rustila" }),
      }, 3);
      const result = await response.json();
      setActiveResult(result);
      if (result.intent === "inventory_write_agent" && result.rows?.[0]) {
        addNotification({
          kind: "inventory",
          title: result.answer,
          item: result.rows[0],
        });
        refreshDashboardData();
      }
      if (["enrollment_request_agent", "borrowing_request_agent"].includes(result.intent)) {
        refreshRequests(demoRole);
      }
    } catch {
      setError("AI backend is still waking up. Wait 30 seconds, then click Send again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleRequestAction(requestId, action) {
    setRequestStatus("Updating request...");
    try {
      const response = await apiFetch(`/requests/${requestId}/${action}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reviewer: demoRole === "Admin" ? "Campus Admin" : "Registrar Staff" }),
      });
      const result = await response.json();
      setRequestStatus(result.message);
      refreshRequests(demoRole);
      refreshDashboardData();
    } catch (requestError) {
      setRequestStatus(requestError.message || "Unable to update request.");
    }
  }

  async function sendFeedback(helpful, escalated = false) {
    if (!activeResult) return;
    setFeedbackStatus(escalated ? "Creating ticket..." : "Saving feedback...");
    try {
      const response = await apiFetch("/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: lastQuestion || message,
          answer: activeResult.answer,
          intent: activeResult.intent,
          helpful,
          escalated,
          note: escalated ? `Escalated by ${demoRole} demo role` : null,
        }),
      });
      const result = await response.json();
      setFeedbackStatus(result.message);
      if (escalated) addNotification({ kind: "ticket", title: result.message, item: result.item });
    } catch {
      setFeedbackStatus("Unable to save feedback while the backend is waking.");
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
      const response = await apiFetch(config.endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config.payload),
      }, 3);
      const result = await response.json();

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

  if (page === "landing") {
    return (
      <LandingPage
        onDemo={(role) => {
          setDemoRole(role);
          setActiveView("home");
          setPage("portal");
        }}
      />
    );
  }

  return (
    <main className={`portal role-${demoRole.toLowerCase()}`}>
      <aside className="sidebar">
        <div className="brand">
          <div className="brandIcon">
            <BrainCircuit size={24} />
          </div>
          <div>
            <h1>CampusIQ</h1>
            <p>Higher education AI</p>
          </div>
        </div>

        <nav>
          <button
            type="button"
            className={activeView === "home" ? "active" : ""}
            onClick={() => setActiveView("home")}
          >
            <Home size={16} />
            {demoRole === "Student" ? "My Dashboard" : demoRole === "Registrar" ? "Operations" : "Overview"}
          </button>
          <button
            type="button"
            className={activeView === "console" ? "active" : ""}
            onClick={() => {
              setActiveView("console");
              setChatOpen(true);
              if (demoRole !== "Student") askAgent("Generate a school report.");
            }}
          >
            <Sparkles size={16} />
            {demoRole === "Student" ? "Campus AI" : "Agent Console"}
          </button>
          {demoRole !== "Student" && <button
            type="button"
            className={activeView === "sql" ? "active" : ""}
            onClick={() => openView("sql", "Show project scores greater than 85.")}
          >
            <Database size={16} />
            {demoRole === "Student" ? "My Academics" : demoRole === "Registrar" ? "Student Records" : "Data Records"}
          </button>}
          {demoRole !== "Student" && <button
            type="button"
            className={activeView === "rag" ? "active" : ""}
            onClick={() => openView("rag", "What does the capstone policy say about delayed students?")}
          >
            <FileSearch size={16} />
            {demoRole === "Student" ? "Campus Resources" : demoRole === "Registrar" ? "Knowledge Base" : "AI Knowledge"}
          </button>}
          {demoRole !== "Student" && <button
            type="button"
            className={activeView === "forecast" ? "active" : ""}
            onClick={() => openView("forecast", "Predict next month's enrollment activity.")}
          >
            <BarChart3 size={16} />
            {demoRole === "Admin" ? "AI Analytics" : demoRole === "Registrar" ? "Question Analytics" : "Calendar"}
          </button>}
          <button
            type="button"
            className={activeView === "requests" ? "active" : ""}
            onClick={() => setActiveView("requests")}
          >
            <Clock3 size={16} />
            {demoRole === "Student" ? "My Requests" : demoRole === "Registrar" ? "Enrollment Requests" : "Borrowing Records"}
          </button>
          {demoRole !== "Student" && <button
            type="button"
            className={activeView === "add" ? "active" : ""}
            onClick={() => setActiveView("add")}
          >
            <PlusCircle size={16} />
            Add School Data
          </button>}
        </nav>

        {demoRole !== "Student" && <div className="sourcePanel">
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
        </div>}
        <button className="backToSite" type="button" onClick={() => setPage("landing")}><ArrowRight size={15} /> Back to project</button>
      </aside>

      <section className="workspace">
        <header>
          <div>
            <p className="eyebrow">{roleMeta[demoRole].eyebrow}</p>
            <h2>{roleMeta[demoRole].title}</h2>
            <p className="headerSubtitle">{roleMeta[demoRole].subtitle}</p>
          </div>
          <div className="headerActions">
            <label className="roleSwitcher">
              <Users size={15} />
              <span>Demo role</span>
              <select value={demoRole} onChange={(event) => { setDemoRole(event.target.value); setActiveView("home"); }}>
                <option>Student</option>
                <option>Registrar</option>
                <option>Admin</option>
              </select>
            </label>
          <button
            type="button"
            className="status"
            onClick={() => {
              setActiveView("console");
              setChatOpen(true);
              if (demoRole !== "Student") askAgent("Generate a school report.");
            }}
          >
            <Activity size={15} />
            Live demo
          </button>
          </div>
        </header>

        {activeView === "home" && (
          <RoleOverview role={demoRole} summary={summary} documents={documents} adminMetrics={adminMetrics} mlEvaluation={mlEvaluation} requests={requests} onAsk={(question) => { setActiveView("console"); setChatOpen(true); askAgent(question); }} onNavigate={setActiveView} onAction={handleRequestAction} />
        )}

        {activeView === "requests" && <RequestCenter role={demoRole} requests={requests} onAction={handleRequestAction} />}
        {requestStatus && activeView === "requests" && <div className="requestNotice">{requestStatus}</div>}

        {activeView !== "home" && activeView !== "requests" && demoRole !== "Student" && <section className="metricsGrid">
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
        </section>}

        {activeView !== "home" && activeView !== "requests" && demoRole !== "Student" && <section className="portfolioStrip" aria-label="Project role alignment">
          <div className="portfolioIntro">
            <p className="eyebrow">Agentic AI + RAG + knowledge management + analytics</p>
            <h3>CampusIQ routes each request to a specialized data tool.</h3>
            <p>
              The demo keeps the data easy to explain while showing the same pattern used in business systems:
              chat, API tools, record evidence, document sources, and forecasting.
            </p>
            <div className="techBadges">
              {techBadges.map((badge) => (
                <span key={badge}>{badge}</span>
              ))}
            </div>
          </div>

          <div className="signalGrid">
            {roleSignals.map((signal) => (
              <div className="signalItem" key={signal.label}>
                <strong>{signal.label}</strong>
                <span>{signal.value}</span>
              </div>
            ))}
          </div>
        </section>}

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

        {activeView !== "add" && activeView !== "home" && activeView !== "requests" && (
        <section className="consoleGrid">
          <div className="answerPanel">
            {activeResult ? (
              <>
                <div className="answerHeader">
                  <span>{activeResult.intent}</span>
                  <div className="confidence">
                    <ShieldCheck size={15} />
                    {activeResult.model_trace?.label || "Tool"} inquiry
                  </div>
                </div>
                <p className="answer">{activeResult.answer}</p>

                <div className="explainGrid" aria-label="AI explainability">
                  <div><span>Agent</span><strong>{activeResult.agent_name || "Campus Router"}</strong></div>
                  <div><span>Data path</span><strong>{activeResult.data_path || "Campus tools"}</strong></div>
                  <div><span>Role context</span><strong>{demoRole}</strong></div>
                  <div><span>ML classifier</span><strong>{activeResult.model_trace?.label || "Routing fallback"}</strong></div>
                  <div><span>Language model</span><strong>{activeResult.llm_provider || "Tool-grounded fallback"} · {activeResult.llm_model || "No external LLM"}</strong></div>
                  <div><span>Response time</span><strong>{activeResult.response_time_ms ?? 0} ms</strong></div>
                </div>

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
                        <div className="sourceMeta"><strong>{source.title}</strong><span>{source.source_type} · Page {source.page || 1} · {relevanceLabel(source.score || 0)}</span></div>
                        <p>{source.snippet}</p>
                      </article>
                    ))}
                  </div>
                )}

                <div className="feedbackBar">
                  <span>Was this answer useful?</span>
                  <button type="button" onClick={() => sendFeedback(true)} title="Helpful"><ThumbsUp size={16} /></button>
                  <button type="button" onClick={() => sendFeedback(false)} title="Not helpful"><ThumbsDown size={16} /></button>
                  <button className="ticketButton" type="button" onClick={() => sendFeedback(false, true)}>
                    <MessageSquareWarning size={16} /> Create ticket
                  </button>
                  {feedbackStatus && <small>{feedbackStatus}</small>}
                </div>
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
              <strong>Ari · Campus Services Assistant</strong>
              <span>{loading ? "Thinking..." : "Online"}</span>
            </div>
            <button type="button" onClick={() => setChatOpen(false)} title="Minimize chat">
              <X size={17} />
            </button>
          </div>

          {error && <div className="errorBanner">{error}</div>}

          {lastQuestion && (
            <div className="chatConversation" aria-live="polite">
              <div className="messageRow userMessage">
                <span>You</span>
                <p>{lastQuestion}</p>
              </div>
              <div className="messageRow ariMessage">
                <span>Ari</span>
                {loading ? (
                  <div className="typingDots" aria-label="Ari is thinking"><i /><i /><i /></div>
                ) : (
                  <>
                    <p>{activeResult?.answer || "I could not complete that request. Please try again."}</p>
                    <small>
                      {activeResult?.llm_provider || "Campus tools"}
                      {activeResult?.llm_status && activeResult.llm_status !== "active" ? ` · ${activeResult.llm_status.replaceAll("_", " ")}` : ""}
                    </small>
                  </>
                )}
              </div>
            </div>
          )}

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

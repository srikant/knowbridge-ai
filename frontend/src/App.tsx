import { useEffect, useRef, useState } from 'react'
import { Activity, ArrowDownToLine, ArrowRight, BookOpen, Check, ChevronDown, CircleHelp, FileText, FileUp, Files, Globe2, LayoutDashboard, LoaderCircle, MessageCircle, MoreHorizontal, Plus, Search, Send, Settings2, ShieldCheck, Sparkles, Trash2, X } from 'lucide-react'

type DocumentItem = { id: number; filename: string; content_type: string; characters: number; chunks: number; created_at: string }
type Source = { document_id: number; filename: string; chunk_index: number; excerpt: string; relevance: number }
type Message = { role: 'user' | 'assistant'; content: string; sources?: Source[]; mode?: string }
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function formatBytes(chars: number) { return chars > 1000 ? `${(chars / 1000).toFixed(1)}k chars` : `${chars} chars` }
function App() {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [question, setQuestion] = useState('')
  const [search, setSearch] = useState('')
  const [loadingDocs, setLoadingDocs] = useState(true)
  const [asking, setAsking] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [activeNav, setActiveNav] = useState('Knowledge base')
  const [showSources, setShowSources] = useState<number | null>(0)
  const [apiOnline, setApiOnline] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  async function loadDocuments() {
    setLoadingDocs(true)
    try {
      const [docsResponse, healthResponse] = await Promise.all([fetch(`${API}/api/documents`), fetch(`${API}/health`)] )
      if (!docsResponse.ok) throw new Error('Could not load documents.')
      setDocuments(await docsResponse.json())
      setApiOnline(healthResponse.ok)
      setError('')
    } catch { setApiOnline(false); setError('Cannot connect to the API. Start the FastAPI backend at localhost:8000.') }
    finally { setLoadingDocs(false) }
  }
  useEffect(() => { void loadDocuments() }, [])
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }) }, [messages, asking])

  async function uploadFiles(files: FileList | File[]) {
    if (!files.length) return
    setUploading(true); setError(''); setNotice('')
    try {
      for (const file of Array.from(files)) {
        const form = new FormData(); form.append('file', file)
        const response = await fetch(`${API}/api/documents`, { method: 'POST', body: form })
        const payload = await response.json().catch(() => ({}))
        if (!response.ok) throw new Error(payload.detail || `Could not upload ${file.name}`)
      }
      setNotice(`${files.length} document${files.length > 1 ? 's' : ''} added to your knowledge base.`)
      await loadDocuments()
    } catch (e) { setError(e instanceof Error ? e.message : 'Upload failed.') }
    finally { setUploading(false); if (fileRef.current) fileRef.current.value = '' }
  }

  async function ask(q = question) {
    const text = q.trim()
    if (!text || asking) return
    setMessages(prev => [...prev, { role: 'user', content: text }]); setQuestion(''); setAsking(true); setError(''); setNotice('')
    try {
      const response = await fetch(`${API}/api/ask`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: text }) })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.detail || 'The question could not be answered.')
      setMessages(prev => [...prev, { role: 'assistant', content: payload.answer, sources: payload.sources, mode: payload.mode }])
      setShowSources(messages.length + 1)
    } catch (e) { setMessages(prev => [...prev, { role: 'assistant', content: e instanceof Error ? e.message : 'Something went wrong. Please try again.' }]) }
    finally { setAsking(false) }
  }

  async function removeDocument(doc: DocumentItem) {
    if (!confirm(`Delete “${doc.filename}” and its indexed text?`)) return
    try { const response = await fetch(`${API}/api/documents/${doc.id}`, { method: 'DELETE' }); if (!response.ok) throw new Error('Delete failed.'); setDocuments(prev => prev.filter(d => d.id !== doc.id)); setNotice(`${doc.filename} deleted.`) }
    catch (e) { setError(e instanceof Error ? e.message : 'Delete failed.') }
  }

  const filteredDocs = documents.filter(d => d.filename.toLowerCase().includes(search.toLowerCase()))
  const prompts = ['What are the key points in my documents?', 'Summarize the main policies', 'What actions or deadlines are mentioned?']

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><Sparkles size={19}/></div><div><div className="brand-name">knowbridge<span>AI</span></div><div className="brand-subtitle">YOUR KNOWLEDGE, CONNECTED</div></div></div>
      <button className="workspace-select"><div className="workspace-avatar">W</div><div className="workspace-copy"><strong>Workspace</strong><span>Personal workspace</span></div><ChevronDown size={15}/></button>
      <div className="nav-label">WORKSPACE</div>
      <nav className="nav-list">
        {[{label:'Overview', icon:LayoutDashboard},{label:'Knowledge base',icon:Files},{label:'AI assistant',icon:MessageCircle}].map(item => <button key={item.label} className={`nav-item ${activeNav===item.label?'active':''}`} onClick={() => {setActiveNav(item.label); if(item.label==='AI assistant') document.getElementById('question-box')?.focus(); if(item.label==='Knowledge base') document.getElementById('documents')?.scrollIntoView({behavior:'smooth'})}}><item.icon size={17}/><span>{item.label}</span>{item.label==='Knowledge base'&&documents.length>0&&<span className="nav-count">{documents.length}</span>}</button>)}
      </nav>
      <div className="sidebar-spacer"/>
      <div className="plan-card"><div className="plan-icon"><ShieldCheck size={17}/></div><div><strong>Your workspace</strong><p>Files stay in your local app database.</p></div></div>
      <button className="nav-item muted" onClick={() => setNotice('Settings will be added in a future build.')}><Settings2 size={17}/>Settings</button>
      <button className="nav-item muted" onClick={() => setNotice('Help: upload a PDF, TXT, or Markdown file, then ask a question about it.')}><CircleHelp size={17}/>Help & support</button>
      <div className="profile"><div className="profile-avatar">K</div><div className="profile-copy"><strong>KnowBridge User</strong><span>Free workspace</span></div><MoreHorizontal size={18}/></div>
    </aside>

    <main className="main-area">
      <header className="topbar"><div className="breadcrumbs"><span>Workspace</span><span className="crumb-slash">/</span><strong>{activeNav}</strong></div><div className="topbar-right"><div className={`api-status ${apiOnline?'online':''}`}><span className="status-dot"/>{apiOnline?'API connected':'API offline'}</div><button className="icon-button" title="Refresh documents" onClick={() => void loadDocuments()}><Activity size={17}/></button><div className="top-avatar">K</div></div></header>
      <div className="content-wrap">
        <section className="welcome-row"><div><div className="eyebrow"><span className="eyebrow-dot"/>YOUR BUSINESS KNOWLEDGE, AT YOUR FINGERTIPS</div><h1>Good to see you again.</h1><p className="welcome-copy">Bring your documents together. Ask better questions. Find answers faster.</p></div><button className="primary-button" onClick={() => fileRef.current?.click()}><Plus size={17}/> Add documents</button></section>
        {error&&<div className="alert error-alert"><X size={17}/><span>{error}</span><button onClick={() => setError('')}><X size={15}/></button></div>}
        {notice&&<div className="alert success-alert"><Check size={17}/><span>{notice}</span><button onClick={() => setNotice('')}><X size={15}/></button></div>}

        <section className="stats-grid">
          <div className="stat-card"><div className="stat-top"><span>Documents indexed</span><div className="stat-icon purple"><Files size={17}/></div></div><div className="stat-value">{documents.length.toString().padStart(2,'0')}</div><div className="stat-foot"><span className="stat-neutral">{documents.reduce((n,d)=>n+d.chunks,0)} searchable chunks</span></div></div>
          <div className="stat-card"><div className="stat-top"><span>Knowledge coverage</span><div className="stat-icon blue"><BookOpen size={17}/></div></div><div className="stat-value">{documents.length ? 'Ready' : '—'}</div><div className="stat-foot"><span>{documents.length ? 'Your content is searchable' : 'Upload files to get started'}</span></div></div>
          <div className="stat-card"><div className="stat-top"><span>Assistant status</span><div className="stat-icon green"><Sparkles size={17}/></div></div><div className="stat-value small-value">{apiOnline?'Connected':'Waiting'}</div><div className="stat-foot"><span className={apiOnline?'green-text':'stat-neutral'}><span className="mini-dot"/>{apiOnline?'Ready for questions':'Start your API server'}</span></div></div>
        </section>

        <section className="assistant-card" id="assistant"><div className="assistant-head"><div className="assistant-title"><div className="assistant-mark"><Sparkles size={18}/></div><div><h2>Ask your knowledge base</h2><p>Answers are grounded in the documents you upload.</p></div></div><div className="beta-chip">AI ASSISTANT <span>·</span> BETA</div></div>
          {messages.length===0 ? <div className="chat-empty"><div className="chat-orb"><Sparkles size={23}/></div><h3>What would you like to know?</h3><p>Ask a question about your documents. I'll find relevant passages and show you the sources.</p><div className="prompt-grid">{prompts.map((p,i)=><button key={p} className="prompt-card" onClick={() => void ask(p)} disabled={!documents.length||asking}><span>{p}</span><ArrowRight size={16}/></button>)}</div>{!documents.length&&<div className="empty-hint"><FileUp size={15}/> Add a document first to start asking questions.</div>}</div> : <div className="conversation">{messages.map((m,i)=><div key={i} className={`message-row ${m.role}`}><div className={`message-avatar ${m.role}`}>{m.role==='assistant'?<Sparkles size={16}/>: 'K'}</div><div className="message-body"><div className="message-author">{m.role==='assistant'?'KnowBridge AI':'You'}{m.role==='assistant'&&m.mode&&<span className="mode-tag">{m.mode==='retrieval-only'?'SOURCE RETRIEVAL':'AI-GENERATED'}</span>}</div><div className="message-content">{m.content}</div>{m.sources&&m.sources.length>0&&<div className="sources-box"><button className="sources-toggle" onClick={() => setShowSources(showSources===i?null:i)}><BookOpen size={15}/>{m.sources.length} source passages<ChevronDown size={15} className={showSources===i?'rotated':''}/></button>{showSources===i&&<div className="source-list">{m.sources.map((s,j)=><div className="source-item" key={`${s.document_id}-${s.chunk_index}-${j}`}><div className="source-file-icon"><FileText size={15}/></div><div className="source-copy"><strong>{s.filename}</strong><span>Passage {s.chunk_index+1} · relevance {(s.relevance*100).toFixed(0)}%</span><p>{s.excerpt}</p></div></div>)}</div>}</div>}</div></div>)}{asking&&<div className="message-row assistant"><div className="message-avatar assistant"><Sparkles size={16}/></div><div className="message-body"><div className="message-author">KnowBridge AI</div><div className="thinking"><span/><span/><span/> Searching your knowledge base…</div></div></div>}<div ref={bottomRef}/></div>}
          <form className="composer" onSubmit={e=>{e.preventDefault();void ask()}}><div className="composer-input-wrap"><MessageCircle size={18}/><input id="question-box" value={question} onChange={e=>setQuestion(e.target.value)} placeholder={documents.length?'Ask a question about your documents…':'Upload documents to start asking questions'} disabled={!documents.length||asking}/><button type="button" className="composer-attach" title="Upload a document" onClick={()=>fileRef.current?.click()}><FileUp size={18}/></button></div><button className="send-button" type="submit" disabled={!question.trim()||asking||!documents.length}>{asking?<LoaderCircle size={17} className="spin"/>:<Send size={17}/>}</button></form><div className="composer-foot"><span><ShieldCheck size={13}/> Answers reference your uploaded sources</span><span>Always verify important information</span></div>
        </section>

        <section className="documents-section" id="documents"><div className="section-head"><div><h2>Your knowledge base</h2><p>Manage the documents powering your assistant.</p></div><button className="secondary-button" onClick={() => fileRef.current?.click()}><FileUp size={16}/> Upload files</button></div><div className="documents-panel"><div className="table-toolbar"><div className="table-count"><span className="count-dot"/>{documents.length} {documents.length===1?'document':'documents'}<span className="toolbar-divider"/>PDF, TXT, MD supported</div><label className="search-field"><Search size={15}/><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search files"/></label></div>
          {loadingDocs?<div className="table-empty"><LoaderCircle className="spin" size={22}/><span>Loading your documents…</span></div>:filteredDocs.length===0?<div className="table-empty"><div className="empty-file-icon"><Files size={22}/></div><strong>{search?'No matching documents':'Your knowledge base is ready for its first file'}</strong><span>{search?'Try another search term.':'Upload a document to make its content searchable.'}</span>{!search&&<button className="secondary-button" onClick={()=>fileRef.current?.click()}><Plus size={16}/> Add your first document</button>}</div>:<div className="document-list"><div className="document-table-header"><span>DOCUMENT</span><span>CONTENT</span><span>INDEXED</span><span/></div>{filteredDocs.map(doc=><div className="document-row" key={doc.id}><div className="document-name"><div className={`file-icon ${doc.filename.toLowerCase().endsWith('.pdf')?'pdf':doc.filename.toLowerCase().endsWith('.md')?'md':'txt'}`}><FileText size={17}/></div><div><strong>{doc.filename}</strong><span>Added {new Date(doc.created_at.replace(' ','T')+'Z').toLocaleDateString()}</span></div></div><div className="doc-content-meta">{formatBytes(doc.characters)}<span>{doc.chunks} chunks</span></div><div><span className="indexed-badge"><Check size={12}/> Indexed</span></div><div className="row-actions"><button title="Delete document" onClick={()=>void removeDocument(doc)}><Trash2 size={15}/></button></div></div>)}</div>}
        </div></section>
        <footer className="footer"><span>© 2026 KnowBridge AI</span><span><span className="footer-dot"/> {apiOnline?'All systems operational':'Waiting for backend connection'}</span><button onClick={() => setNotice('KnowBridge AI helps you find information in your own documents. AI answers can be incomplete; verify important decisions against the original source.')}><Globe2 size={13}/> About this app</button></footer>
      </div>
    </main>
    <input ref={fileRef} type="file" accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown" multiple hidden onChange={e=>e.target.files&&void uploadFiles(e.target.files)}/>
  </div>
}
export default App

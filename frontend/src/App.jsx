import { useMemo, useState } from "react";
import { startResearch } from "./services/api";
import "./App.css";

const iconPaths = {
    spark: <><path d="m12 3 1.9 5.8L20 11l-6.1 2.2L12 19l-2-5.8L4 11l6-2.2L12 3Z" /><path d="m19 14 .9 2.1L22 17l-2.1.9L19 20l-.9-2.1L16 17l2.1-.9L19 14Z" /></>,
    bot: <><rect x="4" y="7" width="16" height="13" rx="3" /><path d="M12 3v4M9 13h.01M15 13h.01M9 17h6" /><path d="M2 12v3M22 12v3" /></>,
    home: <><path d="m3 10 9-7 9 7" /><path d="M5 9v12h14V9M9 21v-7h6v7" /></>,
    search: <><circle cx="10.8" cy="10.8" r="6.8" /><path d="m16 16 5 5" /></>,
    file: <><path d="M13 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V10z" /><path d="M13 3v7h7M8 14h8M8 17h6" /></>,
    settings: <><circle cx="12" cy="12" r="3" /><path d="m19.4 15 .1.1 1.4 1.1-1.4 2.4-1.7-.7a8 8 0 0 1-1.7 1l-.3 1.8h-2.8l-.3-1.8a8 8 0 0 1-1.7-1l-1.7.7-1.4-2.4L7.3 15a8 8 0 0 1 0-2l-1.4-1.1 1.4-2.4 1.7.7a8 8 0 0 1 1.7-1l.3-1.8h2.8l.3 1.8a8 8 0 0 1 1.7 1l1.7-.7 1.4 2.4-1.4 1.1a8 8 0 0 1-.1 2Z" /></>,
    network: <><circle cx="12" cy="5" r="2.3" /><circle cx="5" cy="18" r="2.3" /><circle cx="19" cy="18" r="2.3" /><path d="m10.9 7-4.7 8.8M13.1 7l4.7 8.8M7.4 18h9.2" /></>,
    book: <><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v17H6.5A2.5 2.5 0 0 0 4 22z" /><path d="M4 5.5v14A2.5 2.5 0 0 1 6.5 17H20M8 7h8M8 10h8" /></>,
    chart: <><path d="M4 20V10M10 20V4M16 20v-7M22 20H2" /></>,
    bulb: <><path d="M9 18h6M10 22h4M8.2 14.8A7 7 0 1 1 15.8 15c-.9.7-1.3 1.5-1.4 3h-4.8c-.1-1.5-.5-2.3-1.4-3.2Z" /><path d="M12 1v2M4.9 4.9 6.3 6.3M19.1 4.9l-1.4 1.4" /></>,
    clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
    check: <><path d="m5 12 4 4L19 6" /></>,
    arrow: <><path d="M7 17 17 7M7 7h10v10" /></>,
    alert: <><path d="m12 3 10 18H2L12 3Z" /><path d="M12 9v5M12 17h.01" /></>,
    link: <><path d="M10 13a5 5 0 0 0 7.1 0l3-3A5 5 0 0 0 13 2.9l-1.7 1.7" /><path d="M14 11a5 5 0 0 0-7.1 0l-3 3A5 5 0 0 0 11 21.1l1.7-1.7" /></>,
};

function Icon({ name, size = 20 }) {
    return <svg className="icon" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{iconPaths[name]}</svg>;
}

function safeUrl(value) {
    try {
        const url = new URL(value);
        return ["https:", "http:"].includes(url.protocol) ? url.href : null;
    } catch {
        return null;
    }
}

function hostName(value) {
    try { return new URL(value).hostname.replace(/^www\./, ""); }
    catch { return "Source"; }
}

function EmptyState({ children }) {
    return <div className="empty-state">{children}</div>;
}

function App() {
    const [topic, setTopic] = useState("");
    const [maxRevisions, setMaxRevisions] = useState(2);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");

    const report = result?.report;
    const sources = useMemo(() => {
        const responseSources = result?.sources;
        if (Array.isArray(responseSources) && responseSources.length) {
            return responseSources.map((source) => typeof source === "string"
                ? { url: source, title: hostName(source), source_type: "source" }
                : source);
        }
        return (report?.sources || []).map((source) => typeof source === "string"
            ? { url: source, title: hostName(source), source_type: "source" }
            : source);
    }, [result, report]);
    const claims = useMemo(
        () => (report?.sections || []).flatMap((section) => section.claims || []),
        [report],
    );
    const findings = useMemo(() => {
        const seen = new Set();
        return claims.filter((claim) => {
            const key = claim.statement?.trim();
            if (!key || seen.has(key)) return false;
            seen.add(key);
            return true;
        }).slice(0, 4);
    }, [claims]);
    const sectionCounts = useMemo(() => (report?.sections || []).map((section) => ({
        label: section.heading || "Research section",
        count: (section.claims || []).length,
    })).slice(0, 5), [report]);
    const sectionTotal = sectionCounts.reduce((sum, section) => sum + section.count, 0);

    async function handleResearch(event) {
        event.preventDefault();
        if (!topic.trim() || loading) return;
        setLoading(true);
        setError("");
        setResult(null);
        try {
            const data = await startResearch(topic.trim(), maxRevisions);
            setResult(data);
        } catch (err) {
            const detail = err.response?.data?.detail;
            setError(typeof detail === "string" ? detail : detail?.message || "Research request failed. Check the API and provider configuration.");
        } finally {
            setLoading(false);
        }
    }

    function jumpTo(id) {
        document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function downloadMarkdown() {
        if (!report) return;
        const lines = [
            `# ${report.metadata?.title || result?.topic || "Research report"}`,
            "",
            `**Topic:** ${report.metadata?.topic || result?.topic || ""}`,
            "",
            "## Executive Summary",
            "",
            report.executive_summary || "",
            "",
        ];
        (report.sections || []).forEach((section) => {
            lines.push(`## ${section.heading || "Research section"}`, "", section.content || "", "");
            (section.claims || []).forEach((claim) => {
                lines.push(`- ${claim.statement || ""}`);
                (claim.source_urls || []).forEach((url) => lines.push(`  - Source: ${url}`));
            });
            lines.push("");
        });
        lines.push("## Conclusion", "", report.conclusion || "", "", "## Limitations", "");
        (report.limitations || []).forEach((limitation) => lines.push(`- ${limitation}`));
        const blob = new Blob([lines.join("\n")], { type: "text/markdown;charset=utf-8" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "research-report.md";
        link.click();
        URL.revokeObjectURL(link.href);
    }

    return (
        <div className="app-shell">
            <aside className="sidebar">
                <a className="brand" href="#top" onClick={() => jumpTo("top")}>
                    <span className="brand-mark"><Icon name="spark" size={25} /></span>
                    <span>Research <b>AI</b></span>
                </a>

                <div className="sidebar-bot"><Icon name="bot" size={25} /></div>
                <nav className="side-nav" aria-label="Main navigation">
                    <button className="nav-item" onClick={() => jumpTo("top")}><Icon name="home" />Home</button>
                    <button className="nav-item active" onClick={() => jumpTo("research-search")}><Icon name="search" />Research</button>
                    <button className="nav-item" onClick={() => jumpTo("documents")}><Icon name="file" />Documents</button>
                    <button className="nav-item" onClick={() => jumpTo("research-settings")}><Icon name="settings" />Settings</button>
                </nav>

                <section className="workflow-card" aria-label="Research workflow">
                    <div className="workflow-title"><Icon name="network" /><h2>Research Workflow</h2></div>
                    <ol className="workflow-steps">
                        {[
                            ["Planning & Query Analysis", "Creates research questions"],
                            ["Search & Retrieval", "Web · academic · news"],
                            ["Analysis & Synthesis", "Evidence-backed findings"],
                            ["Report Generation", "Citations and limitations"],
                        ].map(([label, caption], index) => (
                            <li className={result?.status === "completed" ? "workflow-done" : ""} key={label}>
                                <span className="step-node">{result?.status === "completed" ? <Icon name="check" size={14} /> : index + 1}</span>
                                <div><strong>{label}</strong><small>{caption}</small></div>
                            </li>
                        ))}
                    </ol>
                    <p className="workflow-footnote">Stages shown for the research pipeline. Live per-stage progress isn’t available yet.</p>
                </section>
                <div className="sidebar-footer"><span className="online-dot" />Research agents ready</div>
            </aside>

            <main className="dashboard" id="top">
                <header className="page-heading">
                    <div><div className="eyebrow">DEEP RESEARCH WORKSPACE</div><h1>Research dashboard</h1><p>Search, analyze, and organize evidence in one place.</p></div>
                    <div className="agent-pill"><Icon name="network" /><span className="online-dot" />{loading ? "3 agents working" : "3 agents ready"}</div>
                </header>

                <form className="search-bar" id="research-search" onSubmit={handleResearch}>
                    <Icon name="search" size={21} />
                    <input value={topic} onChange={(event) => setTopic(event.target.value)} placeholder="What would you like to research?" aria-label="Research topic" />
                    <label className="revision-control" id="research-settings"><span>Revisions</span><select value={maxRevisions} onChange={(event) => setMaxRevisions(Number(event.target.value))} aria-label="Maximum revisions"><option value={0}>0</option><option value={1}>1</option><option value={2}>2</option><option value={3}>3</option><option value={4}>4</option><option value={5}>5</option></select></label>
                    <button className="search-button" type="submit" disabled={loading || !topic.trim()}>{loading ? <><span className="button-spinner" />Researching</> : "Start research"}</button>
                </form>

                {error && <div className="error-banner"><Icon name="alert" /><span>{error}</span></div>}

                <div className="dashboard-grid">
                    <section className="panel summary-panel">
                        <div className="panel-heading"><span className="panel-icon"><Icon name="file" /></span><div><h2>Research summary</h2><p className="panel-subtitle">{result?.topic || "Your findings will appear here"}</p></div></div>
                        {report ? <p className="summary-copy">{report.executive_summary || "The report did not include an executive summary."}</p> : <EmptyState>Start a research request to generate an evidence-based summary.</EmptyState>}
                        <div className="metric-row">
                            <div className="metric"><span className="metric-icon"><Icon name="file" /></span><strong>{result?.sources_count ?? "—"}</strong><small>Sources</small></div>
                            <div className="metric"><span className="metric-icon"><Icon name="book" /></span><strong>{result?.evidence_count ?? "—"}</strong><small>Evidence items</small></div>
                            <div className="metric"><span className="metric-icon"><Icon name="clock" /></span><strong>{result?.revision_count ?? "—"}</strong><small>Revisions</small></div>
                        </div>
                    </section>

                    <section className="panel findings-panel">
                        <div className="panel-heading"><span className="panel-icon"><Icon name="bulb" /></span><div><h2>Key findings</h2><p className="panel-subtitle">Claims extracted from the report</p></div></div>
                        {findings.length ? <ul className="finding-list">{findings.map((claim, index) => <li key={`${claim.statement}-${index}`}><span className={`finding-symbol ${index === 3 ? "warning" : ""}`}><Icon name={index === 3 ? "alert" : "chart"} size={19} /></span><div><strong>{claim.statement}</strong><small>{claim.source_urls?.length || 0} linked source{claim.source_urls?.length === 1 ? "" : "s"}</small></div></li>)}</ul> : <EmptyState>Verified report claims will be listed after analysis.</EmptyState>}
                    </section>

                    <section className="panel trend-panel">
                        <div className="panel-heading"><span className="panel-icon"><Icon name="chart" /></span><div><h2>Claims by section</h2><p className="panel-subtitle">Cited claims in the generated report</p></div></div>
                        {sectionCounts.length ? <div className="section-bars">{sectionCounts.map((section) => <div className="section-bar-row" key={section.label}><span title={section.label}>{section.label}</span><div className="section-bar-track"><i style={{ width: `${Math.max(4, (section.count / Math.max(1, ...sectionCounts.map((item) => item.count))) * 100)}%` }} /></div><b>{section.count}</b></div>)}</div> : <EmptyState>Report sections and their cited claims will appear here.</EmptyState>}
                    </section>

                    <section className="panel sources-panel" id="documents">
                        <div className="panel-heading panel-heading-spread"><div className="heading-pair"><span className="panel-icon"><Icon name="link" /></span><div><h2>Sources</h2><p className="panel-subtitle">Research material collected for this run</p></div></div><span className="count-badge">{sources.length}</span></div>
                        {sources.length ? <div className="source-list">{sources.slice(0, 5).map((source, index) => {
                            const href = safeUrl(source.url);
                            return <div className="source-row" key={`${source.url}-${index}`}><span className={`source-file source-${(source.source_type || "web").toLowerCase()}`}>{(source.source_type || "web").slice(0, 3).toUpperCase()}</span><div className="source-info"><strong>{source.title || hostName(source.url)}</strong><small>{source.source_type || "source"} · {hostName(source.url)}</small></div>{href && <a className="external-link" href={href} target="_blank" rel="noopener noreferrer" aria-label={`Open ${source.title || source.url}`}><Icon name="arrow" size={17} /></a>}</div>;
                        })}</div> : <EmptyState>Sources from web, academic, and news search will appear here.</EmptyState>}
                    </section>

                    <section className="panel papers-panel">
                        <div className="panel-heading"><span className="panel-icon"><Icon name="book" /></span><div><h2>Evidence highlights</h2><p className="panel-subtitle">Claims cited in the report</p></div></div>
                        {claims.length ? <div className="paper-list">{claims.slice(0, 4).map((claim, index) => <article className="paper-row" key={`${claim.statement}-${index}`}><span className="paper-thumbnail"><Icon name="file" size={22} /></span><div className="paper-info"><strong>{claim.statement}</strong><small>{claim.source_urls?.length || 0} cited source{claim.source_urls?.length === 1 ? "" : "s"}</small></div></article>)}</div> : <EmptyState>Claims with citations will appear after the report is ready.</EmptyState>}
                    </section>

                    <section className="panel topics-panel">
                        <div className="panel-heading"><span className="panel-icon"><Icon name="file" /></span><div><h2>Source mix</h2><p className="panel-subtitle">Collected by source type</p></div></div>
                        {sectionCounts.length && sectionTotal ? <div className="topic-content"><div className="donut" style={{ "--segments": sectionCounts.map((section, index) => `${["#1769ed", "#31bdd5", "#8b9cf4", "#9fb6d6", "#d2dced"][index]} ${(sectionCounts.slice(0, index).reduce((sum, item) => sum + item.count, 0) / sectionTotal) * 100}% ${((sectionCounts.slice(0, index).reduce((sum, item) => sum + item.count, 0) + section.count) / sectionTotal) * 100}%`).join(", ") }}><span>{sectionTotal}<small>claims</small></span></div><ul className="legend-list">{sectionCounts.map((section, index) => <li key={section.label}><i style={{ background: ["#1769ed", "#31bdd5", "#8b9cf4", "#9fb6d6", "#d2dced"][index] }} />{section.label}<b>{Math.round(section.count / sectionTotal * 100)}%</b></li>)}</ul></div> : <EmptyState>{sectionCounts.length ? "This report has no cited claims to chart." : "Report sections will appear here after a research run."}</EmptyState>}
                    </section>

                    <section className="panel report-panel">
                        <div className="panel-heading panel-heading-spread"><div className="heading-pair"><span className="panel-icon"><Icon name="file" /></span><div><h2>Report</h2><p className="panel-subtitle">Final synthesis and exports</p></div></div>{result?.research_id && <span className={`status-chip ${result.status === "completed" ? "status-success" : ""}`}>{result.status}</span>}</div>
                        {report ? <><p className="report-preview">{report.conclusion || report.executive_summary}</p><div className="export-actions"><button type="button" onClick={downloadMarkdown}>DOWNLOAD MARKDOWN <Icon name="arrow" size={14} /></button></div></> : <EmptyState>Your complete report and download options will appear here.</EmptyState>}
                    </section>

                    <section className="panel analysis-panel">
                        <div className="panel-heading"><span className="panel-icon"><Icon name="chart" /></span><div><h2>Analysis</h2><p className="panel-subtitle">Coverage and quality signals</p></div></div>
                        <div className="analysis-body"><div className="analysis-stat"><span>Research status</span><strong className={result?.status === "completed" ? "text-success" : ""}>{result?.status || "Waiting for a search"}</strong><small>{result?.errors?.length ? `${result.errors.length} workflow note${result.errors.length === 1 ? "" : "s"}` : "Workflow response"}</small></div><div className="insight-box"><span className="insight-icon"><Icon name="spark" /></span><div><strong>Evidence traceability</strong><p>{claims.length ? `${claims.length} claims are included in the report, with ${sources.length} sources collected for this research.` : "Run a search to build a cited, evidence-backed report."}</p></div></div></div>
                    </section>
                </div>
                <footer className="page-footer"><span>Research AI</span><span>Sources and findings are generated from the current research run.</span></footer>
            </main>
        </div>
    );
}

export default App;

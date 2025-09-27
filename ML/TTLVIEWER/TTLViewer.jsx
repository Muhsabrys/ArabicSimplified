// React hooks from global React (UMD)
const { useState, useMemo, useRef, useEffect } = React;

// --- Icons ---
const Zap = (props) => <svg {...props} xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 2 16.2 11.7H7.8L12 2Z"/><path d="M10.8 13 15 22l-4.2-9H6.6l4.2-9Z"/></svg>;
const FileText = (props) => <svg {...props} xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.414A2 2 0 0 0 18.586 6L14 1.414A2 2 0 0 0 12.586 1H7a2 2 0 0 0-2 2v18a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg>;
const Code = (props) => <svg {...props} xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="m16 18 4-4-4-4"/><path d="m8 6-4 4 4 4"/><path d="M14 4l-4 16"/></svg>;
const GitGraph = (props) => <svg {...props} xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="5" cy="6" r="3"/><path d="M5 9v6"/><circle cx="5" cy="18" r="3"/><circle cx="19" cy="6" r="3"/><path d="M12 18h7"/><path d="m15 21-3-3 3-3"/></svg>;

// --- Simple TTL parser ---
const simplifiedParseTTL = (content) => {
  const lines = content.split('\n')
    .map(l => l.trim())
    .filter(l => l.length > 0 && !l.startsWith('#') && !l.startsWith('@'));

  const triples = [];
  let subj = null;

  lines.forEach(line => {
    let clean = line.endsWith('.') ? line.slice(0, -1).trim() : line.trim();
    if (clean.endsWith(';')) clean = clean.slice(0, -1).trim();
    const tokens = clean.split(/\s+/);

    if (tokens.length >= 3) {
      subj = tokens[0];
      triples.push({ id: Math.random().toString(36).substr(2, 9), s: subj, p: tokens[1], o: tokens.slice(2).join(' ') });
    } else if (subj && tokens.length >= 2) {
      triples.push({ id: Math.random().toString(36).substr(2, 9), s: subj, p: tokens[0], o: tokens.slice(1).join(' ') });
    } else {
      subj = null;
    }
  });

  return triples.slice(0, 500);
};

// --- Visualization ---
const NodeLinkVisualization = ({ triples }) => {
  const svgRef = useRef(null);

  const { nodes, links } = useMemo(() => {
    const nodeMap = new Map();
    const edges = [];
    let idx = 0;
    const getNode = (uri, type) => {
      if (!nodeMap.has(uri)) {
        nodeMap.set(uri, { id: uri, type, index: idx++ });
      }
      return nodeMap.get(uri);
    };
    triples.forEach(t => {
      const s = getNode(t.s, 'subject');
      const oMatch = t.o.match(/^<([^>]+)>/);
      if (oMatch) {
        const o = getNode(oMatch[1], 'object');
        edges.push({ source: s.id, target: o.id, label: t.p });
      }
    });
    return { nodes: Array.from(nodeMap.values()), links: edges };
  }, [triples]);

  useEffect(() => {
    if (!window.d3 || !svgRef.current || nodes.length === 0) return;
    const d3 = window.d3;
    const svg = d3.select(svgRef.current);
    const width = svgRef.current.parentElement.clientWidth;
    const height = 500;
    svg.selectAll('*').remove();

    const g = svg.append('g');

    svg.attr('viewBox', `0 0 ${width} ${height}`)
       .call(d3.zoom().on("zoom", e => g.attr("transform", e.transform)));

    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = g.append("g").selectAll("line").data(links).join("line")
      .attr("stroke", "#aaa").attr("stroke-width", 1.5);

    const linkLabel = g.append("g").selectAll("text").data(links).join("text")
      .text(d => d.label).attr("font-size", 9).attr("fill", "#bbb");

    const node = g.append("g").selectAll("circle").data(nodes).join("circle")
      .attr("r", 6)
      .attr("fill", d => d.type === 'subject' ? '#6366f1' : '#10b981')
      .call(d3.drag()
        .on("start", dragstart)
        .on("drag", dragged)
        .on("end", dragend));

    // One tooltip
    const tooltip = d3.select(svgRef.current.parentElement).selectAll(".tooltip").data([null])
      .join("div")
      .attr("class", "tooltip")
      .style("position", "absolute").style("padding", "4px 8px")
      .style("background", "#111").style("color", "#fff")
      .style("border-radius", "4px").style("display", "none");

    node.on("mouseover", (e, d) => {
      tooltip.style("display", "block").style("left", e.pageX + 5 + "px").style("top", e.pageY - 28 + "px").text(d.id);
    }).on("mouseout", () => tooltip.style("display", "none"));

    const label = g.append("g").selectAll("text").data(nodes).join("text")
      .text(d => d.id.slice(0, 20) + (d.id.length > 20 ? '...' : ''))
      .attr("font-size", 10).attr("fill", "#fff");

    simulation.on("tick", () => {
      link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
      node.attr("cx", d => d.x).attr("cy", d => d.y);
      label.attr("x", d => d.x + 8).attr("y", d => d.y);
      linkLabel.attr("x", d => (d.source.x + d.target.x) / 2)
               .attr("y", d => (d.source.y + d.target.y) / 2);
    });

    function dragstart(e, d) { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }
    function dragged(e, d) { d.fx = e.x; d.fy = e.y; }
    function dragend(e, d) { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }

    return () => simulation.stop();
  }, [nodes, links]);

  return <svg ref={svgRef} className="w-full h-[500px] bg-gray-900 rounded-lg"></svg>;
};

// --- Main App ---
const App = () => {
  const [triples, setTriples] = useState([]);
  const [activeTab, setActiveTab] = useState('triples');
  const [sparqlQuery, setSparqlQuery] = useState("SELECT ?s ?p ?o WHERE { ?s ?p ?o . } LIMIT 10");
  const [results, setResults] = useState([]);

  const handleFileUpload = (e) => {
    const file = e.target.files[0]; if (!file) return;
    const reader = new FileReader();
    reader.onload = ev => setTriples(simplifiedParseTTL(ev.target.result));
    reader.readAsText(file);
  };

  const runQuery = () => {
    if (/SELECT/i.test(sparqlQuery)) {
      setResults(triples.slice(0, 20).map(t => ({ s: t.s, p: t.p, o: t.o })));
    }
  };

  const sampleQueries = [
    { label: "All Triples", q: "SELECT ?s ?p ?o WHERE { ?s ?p ?o . } LIMIT 20" },
    { label: "All Subjects", q: "SELECT DISTINCT ?s WHERE { ?s ?p ?o . } LIMIT 20" },
    { label: "All Predicates", q: "SELECT DISTINCT ?p WHERE { ?s ?p ?o . } LIMIT 20" },
    { label: "All Objects", q: "SELECT DISTINCT ?o WHERE { ?s ?p ?o . } LIMIT 20" },
  ];

  return (
    <div className="p-4 bg-gray-900 text-white min-h-screen">
      <h1 className="text-2xl font-bold flex items-center"><Zap className="w-6 h-6 mr-2" />TTL RDF Viewer</h1>
      <input type="file" accept=".ttl" onChange={handleFileUpload} className="my-4" />
      {triples.length > 0 && (
        <div>
          <div className="flex space-x-2">
            <button onClick={() => setActiveTab('triples')}><FileText className="inline w-4 h-4" /> Triples</button>
            <button onClick={() => setActiveTab('sparql')}><Code className="inline w-4 h-4" /> SPARQL</button>
            <button onClick={() => setActiveTab('viz')}><GitGraph className="inline w-4 h-4" /> Visualization</button>
          </div>
          {activeTab === 'triples' && (
            <div className="mt-2 max-h-96 overflow-y-scroll">
              {triples.map(t => <div key={t.id} className="text-xs border-b border-gray-700 py-1">
                <span className="text-blue-300">{t.s}</span> <span className="text-yellow-300">{t.p}</span> <span className="text-green-300">{t.o}</span>
              </div>)}
            </div>
          )}
          {activeTab === 'sparql' && (
            <div className="mt-2">
              <div className="space-x-2 mb-2">
                {sampleQueries.map(btn => (
                  <button key={btn.label} onClick={() => setSparqlQuery(btn.q)} className="px-2 py-1 bg-indigo-600 rounded">{btn.label}</button>
                ))}
              </div>
              <textarea value={sparqlQuery} onChange={e => setSparqlQuery(e.target.value)} className="w-full h-32 bg-gray-800 p-2" />
              <button onClick={runQuery} className="mt-2 bg-purple-600 px-3 py-1 rounded">Execute</button>
              <div className="mt-3 text-sm text-gray-400">
                <p>💡 Example Queries:</p>
                <ul className="list-disc pl-5">
                  <li><code>SELECT ?s ?p ?o WHERE {{ ?s ?p ?o . }} LIMIT 10</code></li>
                  <li><code>SELECT DISTINCT ?s WHERE {{ ?s ?p ?o . }} LIMIT 20</code></li>
                  <li><code>SELECT DISTINCT ?p WHERE {{ ?s ?p ?o . }}</code></li>
                </ul>
              </div>
              {results.length > 0 && (
                <table className="mt-3 text-xs w-full border border-gray-700">
                  <thead><tr><th>Subject</th><th>Predicate</th><th>Object</th></tr></thead>
                  <tbody>
                    {results.map((r, i) => <tr key={i}><td>{r.s}</td><td>{r.p}</td><td>{r.o}</td></tr>)}
                  </tbody>
                </table>
              )}
            </div>
          )}
          {activeTab === 'viz' && <NodeLinkVisualization triples={triples} />}
        </div>
      )}
    </div>
  );
};

// Attach to window for index.html
window.App = App;

import { useState, useEffect } from "react";

// ── Temas ─────────────────────────────────────────────────────────────────────
const TEMAS = {
  escuro: {
    bg:"#111827", surface:"#1a2535", card:"#1f2d3f", cardAlt:"#243348",
    border:"#2e4058", borderMid:"#3a5070",
    primary:"#4e8ecb", primaryBg:"#1a3050",
    gold:"#d4a843",  goldBg:"#2a2010",
    green:"#4aaa6e", greenBg:"#0e2a1a", greenBdr:"#1e4a30",
    red:"#e05252",   redBg:"#2a0e0e",   redBdr:"#4a1e1e",
    amber:"#d4843a", amberBg:"#2a1a08",
    slate:"#7090a8",
    txt:"#dce8f5", txtMid:"#8faabf", txtMuted:"#4e6880",
    headerBg:"#0d1520", footerBg:"#0d1520",
  },
  claro: {
    bg:"#f4f0e8", surface:"#faf7f2", card:"#ffffff", cardAlt:"#f7f3ec",
    border:"#ddd5c4", borderMid:"#c8bfae",
    primary:"#1e4a7a", primaryBg:"#e8f0f8",
    gold:"#a07030",  goldBg:"#fdf5e8",
    green:"#2a6e42", greenBg:"#edf7f2", greenBdr:"#a8d5bc",
    red:"#8b2222",   redBg:"#fdf0f0",   redBdr:"#e8b8b8",
    amber:"#9a5a18", amberBg:"#fdf5e8",
    slate:"#607080",
    txt:"#1a1a1a", txtMid:"#4a3c2e", txtMuted:"#8a7a68",
    headerBg:"#1e4a7a", footerBg:"#f0ece4",
  },
};
const F = { serif:"Georgia,'Times New Roman',serif", mono:"'Courier New',Courier,monospace" };

// ── Hook de largura ────────────────────────────────────────────────────────────
function useLargura() {
  const [w, setW] = useState(typeof window !== "undefined" ? window.innerWidth : 800);
  useEffect(() => {
    const fn = () => setW(window.innerWidth);
    window.addEventListener("resize", fn);
    return () => window.removeEventListener("resize", fn);
  }, []);
  return w;
}

// ── Primitivos ────────────────────────────────────────────────────────────────
function Btn({ onClick, disabled, variant = "primary", children, T }) {
  const v = {
    primary: { bg: disabled ? T.border : T.primary, color: disabled ? T.txtMuted : "#fff", border: "none" },
    ghost:   { bg: "transparent", color: T.txtMuted, border: `1px solid ${T.border}` },
    small:   { bg: T.primary, color: "#fff", border: "none" },
  }[variant];
  return (
    <button onClick={onClick} disabled={disabled} style={{
      height: variant === "small" ? 32 : 42,
      padding: variant === "small" ? "0 14px" : "0 22px",
      borderRadius: 8, cursor: disabled ? "not-allowed" : "pointer",
      background: v.bg, color: v.color, border: v.border,
      fontFamily: F.mono, fontSize: variant === "small" ? 11 : 13,
      letterSpacing: "0.08em", fontWeight: 600,
      opacity: disabled ? 0.5 : 1, whiteSpace: "nowrap", transition: "opacity 0.2s",
    }}>{children}</button>
  );
}

const Card = ({ children, T, style }) => (
  <div style={{ background: T.card, border: `1px solid ${T.border}`, borderRadius: 12, padding: "22px 22px", ...style }}>
    {children}
  </div>
);

const Rotulo = ({ children, T }) => (
  <div style={{ fontSize: 10, fontFamily: F.mono, letterSpacing: "0.22em", textTransform: "uppercase", color: T.txtMuted, marginBottom: 16 }}>
    {children}
  </div>
);

function Tile({ active, onClick, children, T }) {
  return (
    <div onClick={onClick} style={{
      flex: 1,
      cursor: "pointer", borderRadius: 12, padding: "20px 14px", textAlign: "center",
      userSelect: "none", transition: "all 0.18s",
      background: active ? T.primary : T.card,
      border: `2px solid ${active ? T.primary : T.border}`,
      color: active ? "#fff" : T.txt,
      boxShadow: active ? `0 4px 16px ${T.primary}40` : "none",
    }}>{children}</div>
  );
}

function Passos({ passo, rotulos, T, mobile }) {
  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "flex-start", gap: 0, marginBottom: 36 }}>
      {rotulos.map((label, i) => (
        <div key={i} style={{ display: "flex", alignItems: "flex-start" }}>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6, width: mobile ? 60 : 72 }}>
            <div style={{
              width: 34, height: 34, borderRadius: "50%", flexShrink: 0,
              background: i < passo ? T.primary : "transparent",
              border: `2px solid ${i <= passo ? T.primary : T.border}`,
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 13, fontFamily: F.mono, fontWeight: 700, transition: "all 0.3s",
              color: i < passo ? "#fff" : i === passo ? T.primary : T.txtMuted,
            }}>{i < passo ? "✓" : i + 1}</div>
            {!mobile && (
              <span style={{ fontSize: 9, fontFamily: F.mono, letterSpacing: "0.1em", color: i === passo ? T.primary : T.txtMuted, textAlign: "center", lineHeight: 1.3 }}>
                {label}
              </span>
            )}
          </div>
          {i < rotulos.length - 1 && (
            <div style={{ width: mobile ? 24 : 36, height: 2, background: i < passo ? T.primary : T.border, marginTop: 16, flexShrink: 0, transition: "background 0.3s" }} />
          )}
        </div>
      ))}
    </div>
  );
}

// ── Gráficos ──────────────────────────────────────────────────────────────────
function Rosca({ v, e, d, T }) {
  const total = v + e + d;
  const R = 72, cx = 90, cy = 90, sw = 20, circ = 2 * Math.PI * R;
  const segs = [
    { pct: v / total, color: T.green, label: "Vitórias", val: v },
    { pct: e / total, color: T.slate, label: "Empates",  val: e },
    { pct: d / total, color: T.red,   label: "Derrotas", val: d },
  ];
  let off = 0;
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 20 }}>
      <svg width={180} height={180}>
        <circle cx={cx} cy={cy} r={R} fill="none" stroke={T.border} strokeWidth={sw} />
        {segs.map((s, i) => {
          const dl = Math.max(0, s.pct * circ - 2);
          const el = <circle key={i} cx={cx} cy={cy} r={R} fill="none" stroke={s.color} strokeWidth={sw}
            strokeDasharray={`${dl} ${circ}`} strokeDashoffset={-off * circ}
            transform={`rotate(-90 ${cx} ${cy})`} strokeLinecap="butt" />;
          off += s.pct; return el;
        })}
        <text x={cx} y={cy - 10} textAnchor="middle" fontSize={26} fontWeight={700} fontFamily={F.serif} fill={T.txt}>{Math.round(v / total * 100)}%</text>
        <text x={cx} y={cy + 14} textAnchor="middle" fontSize={10} fontFamily={F.mono} fill={T.txtMuted} letterSpacing="1">TX. VITÓRIA</text>
        <text x={cx} y={cy + 28} textAnchor="middle" fontSize={10} fontFamily={F.mono} fill={T.txtMuted}>{total} partidas</text>
      </svg>
      <div style={{ display: "flex", justifyContent: "center", gap: 28 }}>
        {segs.map(s => (
          <div key={s.label} style={{ textAlign: "center" }}>
            <div style={{ fontSize: 22, fontWeight: 700, color: s.color, fontFamily: F.serif }}>{s.val}</div>
            <div style={{ fontSize: 10, fontFamily: F.mono, color: T.txtMuted, letterSpacing: "0.1em", marginTop: 2 }}>{s.label.toUpperCase()}</div>
            <div style={{ fontSize: 12, fontFamily: F.mono, color: s.color, marginTop: 2 }}>{Math.round(s.val / total * 100)}%</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Radar({ dados, T }) {
  const n = dados.length, cx = 110, cy = 110, R = 80;
  const ang = i => (i / n) * 2 * Math.PI - Math.PI / 2;
  const pt  = (i, r) => [cx + r * Math.cos(ang(i)), cy + r * Math.sin(ang(i))];
  const poly = dados.map((d, i) => pt(i, R * d.valor / 100)).map(([x, y], i) => `${i ? "L" : "M"}${x},${y}`).join("") + "Z";
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
      <svg width={220} height={220}>
        {[0.25, 0.5, 0.75, 1].map(f => (
          <polygon key={f} fill="none" stroke={T.border} strokeWidth={1}
            points={dados.map((_, i) => pt(i, R * f).join(",")).join(" ")} />
        ))}
        {dados.map((_, i) => { const p = pt(i, R); return <line key={i} x1={cx} y1={cy} x2={p[0]} y2={p[1]} stroke={T.border} strokeWidth={1} />; })}
        <path d={poly} fill={`${T.primary}25`} stroke={T.primary} strokeWidth={2} />
        {dados.map((d, i) => { const p = pt(i, R * d.valor / 100); return <circle key={i} cx={p[0]} cy={p[1]} r={5} fill={T.primary} stroke={T.card} strokeWidth={2} />; })}
        {dados.map((d, i) => {
          const p = pt(i, R + 22);
          const cor = d.valor > 64 ? T.green : d.valor > 46 ? T.gold : T.red;
          return (
            <g key={i}>
              <text x={p[0]} y={p[1] - 5} textAnchor="middle" dominantBaseline="middle" fontSize={9} fontFamily={F.mono} fill={T.txtMuted} letterSpacing="0.5">{d.label}</text>
              <text x={p[0]} y={p[1] + 8} textAnchor="middle" dominantBaseline="middle" fontSize={12} fontFamily={F.mono} fontWeight={700} fill={cor}>{d.valor}</text>
            </g>
          );
        })}
      </svg>
      <div style={{ display: "flex", gap: 14, flexWrap: "wrap", justifyContent: "center" }}>
        {dados.map(d => (
          <div key={d.label} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <div style={{ width: 10, height: 10, borderRadius: 2, background: d.valor > 64 ? T.green : d.valor > 46 ? T.gold : T.red }} />
            <span style={{ fontSize: 11, fontFamily: F.mono, color: T.txtMid }}>{d.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function BarraQualidade({ label, valor, max, cor, pct, T }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
        <span style={{ fontSize: 13, fontFamily: F.serif, color: T.txtMid }}>{label}</span>
        <span style={{ fontSize: 13, fontWeight: 700, color: cor, fontFamily: F.mono }}>{valor} <span style={{ fontSize: 11, color: T.txtMuted }}>méd</span></span>
      </div>
      <div style={{ height: 18, background: T.surface, borderRadius: 6, overflow: "hidden", border: `1px solid ${T.border}`, position: "relative" }}>
        <div style={{ width: `${valor / max * 100}%`, height: "100%", background: cor, borderRadius: 6, transition: "width 1s ease", display: "flex", alignItems: "center", justifyContent: "flex-end", paddingRight: 6 }}>
          {(valor / max * 100) > 18 && <span style={{ fontSize: 10, fontFamily: F.mono, color: "#fff", fontWeight: 700 }}>{pct}%</span>}
        </div>
      </div>
    </div>
  );
}

function BarraFase({ label, sub, valor, max, cor, T }) {
  return (
    <div style={{ marginBottom: 18 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 6 }}>
        <div>
          <div style={{ fontSize: 13, fontFamily: F.serif, color: T.txt }}>{label}</div>
          <div style={{ fontSize: 10, fontFamily: F.mono, color: T.txtMuted, marginTop: 2 }}>{sub}</div>
        </div>
        <span style={{ fontSize: 22, fontWeight: 700, color: cor, fontFamily: F.serif }}>{valor}</span>
      </div>
      <div style={{ height: 20, background: T.surface, borderRadius: 6, overflow: "hidden", border: `1px solid ${T.border}` }}>
        <div style={{ width: `${valor / max * 100}%`, height: "100%", background: cor, borderRadius: 6, transition: "width 1s ease" }} />
      </div>
    </div>
  );
}

function LinhaAbertura({ nome, partidas, pct, melhor, fraca, T }) {
  const cor = pct > 55 ? T.green : pct < 43 ? T.red : T.amber;
  return (
    <div style={{ padding: "12px 0", borderBottom: `1px solid ${T.border}` }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 7 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flex: 1, minWidth: 0 }}>
          <span style={{ fontSize: 13, color: T.txt, fontFamily: F.serif }}>{nome}</span>
          {melhor && <span style={{ fontSize: 9, background: T.greenBg, color: T.green, border: `1px solid ${T.greenBdr}`, borderRadius: 10, padding: "1px 8px", fontFamily: F.mono, flexShrink: 0 }}>MELHOR</span>}
          {fraca  && <span style={{ fontSize: 9, background: T.redBg,   color: T.red,   border: `1px solid ${T.redBdr}`,   borderRadius: 10, padding: "1px 8px", fontFamily: F.mono, flexShrink: 0 }}>FRACA</span>}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12, flexShrink: 0 }}>
          <span style={{ fontSize: 11, color: T.txtMuted, fontFamily: F.mono }}>{partidas}p</span>
          <span style={{ fontSize: 16, fontWeight: 700, color: cor, fontFamily: F.mono, minWidth: 42, textAlign: "right" }}>{pct}%</span>
        </div>
      </div>
      <div style={{ height: 10, background: T.surface, borderRadius: 5, overflow: "hidden", border: `1px solid ${T.border}` }}>
        <div style={{ width: `${pct}%`, height: "100%", background: cor, borderRadius: 5, transition: "width 1s ease" }} />
      </div>
    </div>
  );
}

function CardTatica({ icon, label, n, cor, T }) {
  return (
    <div style={{ background: T.surface, borderRadius: 10, padding: "14px 16px", border: `1px solid ${T.border}`, display: "flex", alignItems: "center", gap: 12 }}>
      <span style={{ fontSize: 26, lineHeight: 1, flexShrink: 0 }}>{icon}</span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 12, color: T.txtMid, fontFamily: F.serif, marginBottom: 3 }}>{label}</div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ flex: 1, height: 6, background: T.card, borderRadius: 3, overflow: "hidden", border: `1px solid ${T.border}` }}>
            <div style={{ width: `${n / 20 * 100}%`, height: "100%", background: cor, borderRadius: 3 }} />
          </div>
          <span style={{ fontSize: 14, fontWeight: 700, color: cor, fontFamily: F.mono, flexShrink: 0 }}>{n}×</span>
        </div>
      </div>
    </div>
  );
}

// ── App principal ─────────────────────────────────────────────────────────────
const PASSOS_LABEL = ["Plataforma", "Usuário", "Perspectiva", "Tipo"];
const ABAS = ["Visão Geral", "Erros", "Aberturas", "Relatório"];
const PECAS = ["♔", "♕", "♖", "♗", "♘", "♙"];

export default function App() {
  const [escuro, setEscuro]       = useState(true);
  const [passo, setPasso]         = useState(0);
  const [plataforma, setPlat]     = useState(null);
  const [usuario, setUsuario]     = useState("");
  const [perspectiva, setPersp]   = useState(null);
  const [tipoJogo, setTipo]       = useState([]);
  const [analisando, setAnal]     = useState(false);
  const [progresso, setProgresso] = useState(0);
  const [mensagem, setMensagem]   = useState("");
  const [pronto, setPronto]       = useState(false);
  const [aba, setAba]             = useState(0);
  const largura = useLargura();
  const mobile  = largura < 640;
  const T       = escuro ? TEMAS.escuro : TEMAS.claro;

  const alternarTipo = t => setTipo(p => p.includes(t) ? p.filter(x => x !== t) : [...p, t]);
  const ok = [plataforma !== null, usuario.trim().length > 2, perspectiva !== null, tipoJogo.length > 0][passo];

  const analisar = () => {
    if (!ok) return;
    setAnal(true);
    const seq = [
      [12, "Conectando…"],
      [30, "Buscando 100 partidas…"],
      [54, "Analisando com Stockfish…"],
      [73, "Detectando padrões…"],
      [91, "Gerando relatório…"],
      [100, "Concluído!"],
    ];
    let i = 0;
    const run = () => {
      if (i >= seq.length) { setTimeout(() => { setPronto(true); setAnal(false); }, 350); return; }
      const [p, m] = seq[i++];
      setTimeout(() => { setProgresso(p); setMensagem(m); run(); }, 950);
    };
    run();
  };

  const reiniciar = () => { setPronto(false); setPasso(0); setUsuario(""); setPlat(null); setPersp(null); setTipo([]); setProgresso(0); setAnal(false); setAba(0); };

  const souEu = perspectiva === "eu";

  const radar = [
    { label: "ABERTURA",  valor: 74 },
    { label: "TÁTICAS",   valor: 62 },
    { label: "MEIO-JOGO", valor: 55 },
    { label: "FINAL",     valor: 36 },
    { label: "DEFESA",    valor: 44 },
    { label: "TEMPO",     valor: 61 },
  ];

  const padCard = mobile ? "28px 20px" : "42px 44px";

  return (
    <div style={{ minHeight: "100vh", background: T.bg, color: T.txt, fontFamily: F.serif, display: "flex", flexDirection: "column" }}>

      {/* ── Cabeçalho ── */}
      <header style={{ background: T.headerBg, height: 56, display: "flex", alignItems: "center", padding: "0 22px", flexShrink: 0, gap: 12 }}>
        <span style={{ fontSize: 22, color: "#fff" }}>♞</span>
        <span style={{ fontSize: mobile ? 11 : 13, fontWeight: 700, letterSpacing: "0.3em", fontFamily: F.mono, color: "#fff" }}>CHESS SCOUT</span>
        {!mobile && <span style={{ fontSize: 9, color: "#ffffff50", letterSpacing: "0.2em", fontFamily: F.mono }}>INTELIGÊNCIA DE JOGO</span>}
        <div style={{ flex: 1 }} />
        <button onClick={() => setEscuro(d => !d)} style={{
          display: "flex", alignItems: "center", gap: 7, padding: "6px 12px", borderRadius: 20,
          cursor: "pointer", fontFamily: F.mono, fontSize: 11,
          background: escuro ? "#ffffff18" : "#00000018",
          border: `1px solid ${escuro ? "#ffffff30" : "#ffffff50"}`,
          color: "#fff", letterSpacing: "0.06em",
        }}>
          <span>{escuro ? "☀" : "☽"}</span>
          {!mobile && <span>{escuro ? "Claro" : "Escuro"}</span>}
        </button>
      </header>

      <main style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", padding: mobile ? "32px 14px 56px" : "48px 20px 64px" }}>
        <div style={{ width: "100%", maxWidth: pronto ? 800 : 520 }}>

          {!pronto ? (
            /* ── WIZARD ── */
            <>
              <div style={{ textAlign: "center", marginBottom: 8 }}>
                <span style={{ fontSize: 10, fontFamily: F.mono, letterSpacing: "0.22em", color: T.txtMuted }}>
                  PASSO {passo + 1} DE 4
                </span>
              </div>

              <Passos passo={passo} rotulos={PASSOS_LABEL} T={T} mobile={mobile} />

              <div style={{
                background: T.card, border: `1px solid ${T.border}`, borderRadius: 18,
                padding: padCard,
                boxShadow: escuro ? "0 8px 32px #00000050" : "0 4px 20px #00000012",
              }}>

                {/* Passo 0 — Plataforma */}
                {passo === 0 && (
                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: 36, marginBottom: 12 }}>♜</div>
                    <div style={{ fontSize: 17, fontWeight: 700, marginBottom: 8 }}>Escolha a Plataforma</div>
                    <div style={{ fontSize: 11, fontFamily: F.mono, color: T.txtMuted, marginBottom: 36, letterSpacing: "0.1em" }}>Em qual plataforma este jogador tem conta?</div>
                    <div style={{ display: "flex", gap: 14, justifyContent: "center" }}>
                      {[{ k: "chesscom", icon: "♟", label: "Chess.com" }, { k: "lichess", icon: "♞", label: "Lichess" }].map(({ k, icon, label }) => (
                        <Tile key={k} active={plataforma === k} onClick={() => setPlat(k)} T={T}>
                          <div style={{ fontSize: 32, lineHeight: 1, marginBottom: 10 }}>{icon}</div>
                          <div style={{ fontSize: 13, fontWeight: 700, fontFamily: F.mono, minWidth: 96 }}>{label}</div>
                        </Tile>
                      ))}
                    </div>
                  </div>
                )}

                {/* Passo 1 — Usuário */}
                {passo === 1 && (
                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: 36, marginBottom: 12 }}>♙</div>
                    <div style={{ fontSize: 17, fontWeight: 700, marginBottom: 8 }}>Nome de Usuário</div>
                    <div style={{ fontSize: 11, fontFamily: F.mono, color: T.txtMuted, marginBottom: 36, letterSpacing: "0.1em" }}>
                      Digite o usuário no {plataforma === "chesscom" ? "Chess.com" : "Lichess"}
                    </div>
                    <input
                      autoFocus value={usuario}
                      onChange={e => setUsuario(e.target.value)}
                      onKeyDown={e => e.key === "Enter" && ok && setPasso(2)}
                      placeholder="ex: magnuscarlsen"
                      style={{
                        width: "100%", boxSizing: "border-box",
                        background: "transparent", border: "none",
                        borderBottom: `2px solid ${T.primary}`,
                        color: T.txt, fontSize: 22, fontFamily: F.serif,
                        padding: "8px 0", outline: "none", textAlign: "center",
                      }}
                    />
                  </div>
                )}

                {/* Passo 2 — Perspectiva */}
                {passo === 2 && (
                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: 36, marginBottom: 12 }}>♔</div>
                    <div style={{ fontSize: 17, fontWeight: 700, marginBottom: 8 }}>Quem é este jogador?</div>
                    <div style={{ fontSize: 11, fontFamily: F.mono, color: T.txtMuted, marginBottom: 36, letterSpacing: "0.1em" }}>
                      Sua resposta define o relatório gerado
                    </div>
                    {/* Tiles lado a lado, sem wrap, respeitando padding do card */}
                    <div style={{ display: "flex", gap: 14 }}>
                      {[
                        { k: "eu",          icon: "♔", label: "Sou eu",         sub: "Diagnóstico pessoal\ne plano de estudos" },
                        { k: "adversario",  icon: "♚", label: "Meu adversário", sub: "Guia de como\nvencê-lo" },
                      ].map(({ k, icon, label, sub }) => (
                        <Tile key={k} active={perspectiva === k} onClick={() => setPersp(k)} T={T}>
                          <div style={{ fontSize: 32, lineHeight: 1, marginBottom: 10 }}>{icon}</div>
                          <div style={{ fontSize: 13, fontWeight: 700, fontFamily: F.mono }}>{label}</div>
                          <div style={{ fontSize: 11, fontFamily: F.mono, marginTop: 6, lineHeight: 1.7, whiteSpace: "pre-line", color: perspectiva === k ? "#ffffff80" : T.txtMuted }}>{sub}</div>
                        </Tile>
                      ))}
                    </div>
                  </div>
                )}

                {/* Passo 3 — Tipo de Jogo */}
                {passo === 3 && (
                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: 36, marginBottom: 12 }}>⏱</div>
                    <div style={{ fontSize: 17, fontWeight: 700, marginBottom: 8 }}>Tipo de Partida</div>
                    <div style={{ fontSize: 11, fontFamily: F.mono, color: T.txtMuted, marginBottom: 36, letterSpacing: "0.1em" }}>Selecione um ou mais</div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                      {[
                        { k: "bullet",    icon: "⚡", label: "Bullet",   sub: "Até 3 min"     },
                        { k: "blitz",     icon: "♟", label: "Blitz",    sub: "3 – 5 min"     },
                        { k: "rapida",    icon: "♞", label: "Rápida",   sub: "10 – 30 min"   },
                        { k: "classica",  icon: "♜", label: "Clássica", sub: "Mais de 30 min" },
                      ].map(({ k, icon, label, sub }) => (
                        <Tile key={k} active={tipoJogo.includes(k)} onClick={() => alternarTipo(k)} T={T}>
                          <div style={{ fontSize: 26, lineHeight: 1, marginBottom: 8 }}>{icon}</div>
                          <div style={{ fontSize: 13, fontWeight: 700, fontFamily: F.mono }}>{label}</div>
                          <div style={{ fontSize: 11, fontFamily: F.mono, marginTop: 4, color: tipoJogo.includes(k) ? "#ffffff70" : T.txtMuted }}>{sub}</div>
                        </Tile>
                      ))}
                    </div>
                  </div>
                )}

                {/* Navegação */}
                {!analisando && (
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 44 }}>
                    <div style={{ minWidth: 80 }}>
                      {passo > 0 && <Btn variant="ghost" onClick={() => setPasso(p => p - 1)} T={T}>← Voltar</Btn>}
                    </div>
                    <div style={{ minWidth: 80, display: "flex", justifyContent: "flex-end" }}>
                      {passo < 3
                        ? <Btn variant="primary" onClick={() => ok && setPasso(p => p + 1)} disabled={!ok} T={T}>Próximo →</Btn>
                        : <Btn variant="primary" onClick={analisar} disabled={!ok} T={T}>♞ Analisar</Btn>
                      }
                    </div>
                  </div>
                )}

                {/* Progresso */}
                {analisando && (
                  <div style={{ marginTop: 40 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                      <span style={{ fontSize: 11, fontFamily: F.mono, color: T.txtMuted }}>{mensagem}</span>
                      <span style={{ fontSize: 11, fontFamily: F.mono, color: T.primary, fontWeight: 700 }}>{progresso}%</span>
                    </div>
                    <div style={{ height: 5, background: T.surface, borderRadius: 3, border: `1px solid ${T.border}`, overflow: "hidden" }}>
                      <div style={{ width: `${progresso}%`, height: "100%", background: T.primary, borderRadius: 3, transition: "width 0.7s ease" }} />
                    </div>
                    <div style={{ display: "flex", justifyContent: "center", gap: 12, marginTop: 28 }}>
                      {PECAS.map((p, i) => (
                        <span key={i} style={{ fontSize: 22, color: (progresso / 100 * 6) > i ? T.primary : T.border, transition: "color 0.4s" }}>{p}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </>

          ) : (
            /* ── RESULTADOS ── */
            <>
              {/* Card do jogador */}
              <div style={{
                background: T.card, border: `1px solid ${T.border}`, borderRadius: 14,
                padding: "18px 20px", marginBottom: 12,
                display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap",
                boxShadow: escuro ? "0 4px 20px #00000040" : "0 2px 10px #00000010",
              }}>
                <div style={{ width: 46, height: 46, borderRadius: "50%", background: T.primary, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20, color: "#fff", flexShrink: 0 }}>♞</div>
                <div style={{ flex: 1, minWidth: 100 }}>
                  <div style={{ fontSize: 17, fontWeight: 700 }}>{usuario}</div>
                  <div style={{ fontSize: 10, fontFamily: F.mono, color: T.txtMuted, letterSpacing: "0.1em", marginTop: 3 }}>
                    {plataforma === "chesscom" ? "Chess.com" : "Lichess"} · {tipoJogo.join("+").toUpperCase()} · 100 partidas
                  </div>
                </div>
                <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                  <span style={{
                    fontSize: 10, padding: "4px 12px", borderRadius: 20,
                    fontFamily: F.mono, letterSpacing: "0.1em",
                    background: souEu ? T.greenBg : T.redBg,
                    border: `1px solid ${souEu ? T.greenBdr : T.redBdr}`,
                    color: souEu ? T.green : T.red,
                  }}>
                    {souEu ? "♔ MEU DIAGNÓSTICO" : "♚ GUIA DO ADVERSÁRIO"}
                  </span>
                  <Btn variant="small" onClick={() => {}} T={T}>↓ Exportar</Btn>
                </div>
              </div>

              {/* Abas */}
              <div style={{ display: "flex", background: T.card, borderRadius: "10px 10px 0 0", border: `1px solid ${T.border}`, borderBottom: "none", overflow: "hidden" }}>
                {ABAS.map((label, i) => (
                  <button key={i} onClick={() => setAba(i)} style={{
                    flex: 1, height: 44, cursor: "pointer", border: "none",
                    background: aba === i ? T.surface : T.card,
                    borderBottom: `3px solid ${aba === i ? T.primary : "transparent"}`,
                    color: aba === i ? T.primary : T.txtMuted,
                    fontSize: mobile ? 9 : 11, letterSpacing: "0.08em", textTransform: "uppercase",
                    fontFamily: F.mono, fontWeight: aba === i ? 700 : 400, transition: "all 0.18s",
                  }}>{label}</button>
                ))}
              </div>

              <div style={{ background: T.surface, border: `1px solid ${T.border}`, borderTop: "none", borderRadius: "0 0 14px 14px", padding: mobile ? "18px 16px" : "24px 22px" }}>

                {/* ── VISÃO GERAL ── */}
                {aba === 0 && (
                  <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                      {[
                        { label: "Rating",       value: "1.842", sub: "Média Blitz",  accent: T.primary },
                        { label: "Tx. Vitória",  value: "54%",   sub: "100 partidas", accent: T.green   },
                        { label: "Blunders",     value: "2,3",   sub: "Por partida",  accent: T.red     },
                        { label: "Melhor Fase",  value: "Abertura", sub: "73% prec.", accent: T.gold    },
                      ].map(({ label, value, sub, accent }) => (
                        <div key={label} style={{ background: T.card, border: `1px solid ${T.border}`, borderTop: `3px solid ${accent}`, borderRadius: 10, padding: "16px 18px" }}>
                          <div style={{ fontSize: 10, fontFamily: F.mono, color: T.txtMuted, letterSpacing: "0.18em", marginBottom: 8 }}>{label.toUpperCase()}</div>
                          <div style={{ fontSize: 22, fontWeight: 700, color: T.txt, fontFamily: F.serif }}>{value}</div>
                          <div style={{ fontSize: 11, color: T.txtMuted, fontFamily: F.mono, marginTop: 4 }}>{sub}</div>
                        </div>
                      ))}
                    </div>

                    <Card T={T}>
                      <Rotulo T={T}>Resultado das Partidas</Rotulo>
                      <Rosca v={54} e={12} d={34} T={T} />
                    </Card>

                    <Card T={T}>
                      <Rotulo T={T}>Perfil de Habilidades</Rotulo>
                      <Radar dados={radar} T={T} />
                    </Card>

                    <Card T={T}>
                      <Rotulo T={T}>Taxa de Vitória por Cor</Rotulo>
                      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                        {[
                          ["♟ Com Brancas", 58, T.green, "64 vitórias · 12 empates · 24 derrotas"],
                          ["♙ Com Pretas",  49, T.gold,  "36 vitórias · 8 empates · 20 derrotas"],
                        ].map(([label, val, cor, sub]) => (
                          <div key={label}>
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 7 }}>
                              <div>
                                <div style={{ fontSize: 14, fontFamily: F.serif, color: T.txt }}>{label}</div>
                                <div style={{ fontSize: 10, fontFamily: F.mono, color: T.txtMuted, marginTop: 2 }}>{sub}</div>
                              </div>
                              <span style={{ fontSize: 28, fontWeight: 700, color: cor, fontFamily: F.serif }}>{val}%</span>
                            </div>
                            <div style={{ height: 16, background: T.surface, borderRadius: 6, overflow: "hidden", border: `1px solid ${T.border}` }}>
                              <div style={{ width: `${val}%`, height: "100%", background: cor, borderRadius: 6 }} />
                            </div>
                          </div>
                        ))}
                      </div>
                    </Card>
                  </div>
                )}

                {/* ── ERROS ── */}
                {aba === 1 && (
                  <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                    <Card T={T}>
                      <Rotulo T={T}>Qualidade dos Lances — Média por Partida</Rotulo>
                      {[
                        ["Excelente",  18, 25, T.green,   72],
                        ["Bom",        22, 25, "#5aaa70", 88],
                        ["Imprecisão",  8, 25, T.gold,    32],
                        ["Erro",        4, 25, T.amber,   16],
                        ["Blunder",   2.3, 25, T.red,      9],
                      ].map(([l, v, m, c, p]) => <BarraQualidade key={l} label={l} valor={v} max={m} cor={c} pct={p} T={T} />)}
                    </Card>

                    <Card T={T}>
                      <Rotulo T={T}>Blunders por Fase da Partida</Rotulo>
                      <BarraFase label="Abertura"  sub="Lances 1–15"  valor={0.3} max={2.5} cor={T.green} T={T} />
                      <BarraFase label="Meio-jogo" sub="Lances 16–35" valor={1.1} max={2.5} cor={T.gold}  T={T} />
                      <BarraFase label="Final"     sub="Lances 36+"   valor={2.1} max={2.5} cor={T.red}   T={T} />
                      <div style={{ marginTop: 18, padding: "14px 16px", background: T.redBg, borderRadius: 8, border: `1px solid ${T.redBdr}` }}>
                        <div style={{ fontSize: 10, color: T.red, fontFamily: F.mono, letterSpacing: "0.1em", marginBottom: 5 }}>⚠ CONCLUSÃO CHAVE</div>
                        <div style={{ fontSize: 13, color: T.txtMid, fontFamily: F.serif, lineHeight: 1.7 }}>
                          Blunders no final são <strong style={{ color: T.txt }}>7× maiores</strong> que na abertura. Técnica de final de jogo é a prioridade #1.
                        </div>
                      </div>
                    </Card>

                    <Card T={T}>
                      <Rotulo T={T}>Padrões Táticos Mais Ignorados</Rotulo>
                      <div style={{ display: "grid", gridTemplateColumns: mobile ? "1fr 1fr" : "repeat(3,1fr)", gap: 10 }}>
                        {[
                          { icon: "♞", label: "Garfo de Cavalo",  n: 18, cor: T.red   },
                          { icon: "♗", label: "Cravada de Bispo", n: 12, cor: T.amber },
                          { icon: "♖", label: "Última Fileira",   n: 9,  cor: T.amber },
                          { icon: "♕", label: "Espeto",           n: 7,  cor: T.gold  },
                          { icon: "♙", label: "Avanço de Peão",   n: 5,  cor: T.slate },
                          { icon: "♔", label: "Segurança do Rei", n: 4,  cor: T.slate },
                        ].map(p => <CardTatica key={p.label} {...p} T={T} />)}
                      </div>
                    </Card>
                  </div>
                )}

                {/* ── ABERTURAS ── */}
                {aba === 2 && (
                  <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                    {[
                      { titulo: "♟ Com Brancas — Taxa de Vitória", linhas: [["Ruy Lopez", 28, 64, true, false], ["Italiana", 18, 55, false, false], ["Gambito da Dama", 12, 41, false, true]] },
                      { titulo: "♙ Com Pretas — Taxa de Vitória",  linhas: [["Siciliana",  32, 68, true, false], ["Francesa", 15, 33, false, true], ["Indiana do Rei", 20, 60, false, false]] },
                    ].map(({ titulo, linhas }) => (
                      <Card key={titulo} T={T}>
                        <Rotulo T={T}>{titulo}</Rotulo>
                        {linhas.map(([nome, partidas, pct, melhor, fraca]) => (
                          <LinhaAbertura key={nome} nome={nome} partidas={partidas} pct={pct} melhor={melhor} fraca={fraca} T={T} />
                        ))}
                      </Card>
                    ))}
                  </div>
                )}

                {/* ── RELATÓRIO ── */}
                {aba === 3 && (
                  <div style={{ background: T.card, border: `1px solid ${T.border}`, borderRadius: 12, overflow: "hidden" }}>
                    <div style={{
                      padding: "14px 20px", borderBottom: `1px solid ${T.border}`,
                      background: souEu ? T.greenBg : T.redBg,
                      display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12,
                    }}>
                      <div>
                        <div style={{ fontSize: 11, fontFamily: F.mono, letterSpacing: "0.14em", color: souEu ? T.green : T.red }}>
                          {souEu ? "♔ DIAGNÓSTICO PESSOAL" : "♚ GUIA DO ADVERSÁRIO"}
                        </div>
                        <div style={{ fontSize: 10, fontFamily: F.mono, color: T.txtMuted, marginTop: 2 }}>
                          {souEu ? `Análise de ${usuario}` : `Como vencer ${usuario}`}
                        </div>
                      </div>
                      <Btn variant="small" onClick={() => {}} T={T}>↓ .md</Btn>
                    </div>

                    <div style={{ padding: mobile ? "18px 18px" : "24px 26px", maxHeight: 500, overflowY: "auto" }}>
                      {souEu ? (
                        <>
                          <div style={{ fontSize: 15, fontWeight: 700, color: T.txt, marginBottom: 4 }}>Diagnóstico do Jogador — {usuario}</div>
                          <div style={{ fontSize: 10, fontFamily: F.mono, color: T.txtMuted, marginBottom: 24, letterSpacing: "0.1em" }}>
                            100 partidas de {tipoJogo.join("+")} · {plataforma === "chesscom" ? "Chess.com" : "Lichess"}
                          </div>
                          {[
                            { titulo: "✅ Pontos Fortes", cor: T.green, itens: ["Repertório de abertura sólido com as Brancas", "Boa visão tática em posições abertas e agressivas", "Gestão de tempo consistente no Blitz"] },
                            { titulo: "⚠️ Pontos Fracos", cor: T.red,   itens: ["Técnica de final — especialmente finais de torre", "Jogo defensivo em posições fechadas e posicionais", "Blunders aumentam significativamente após o lance 35"] },
                          ].map(({ titulo, cor, itens }) => (
                            <div key={titulo} style={{ marginBottom: 20 }}>
                              <div style={{ fontSize: 11, fontFamily: F.mono, color: cor, letterSpacing: "0.1em", marginBottom: 10 }}>{titulo}</div>
                              {itens.map(it => <div key={it} style={{ paddingLeft: 14, marginBottom: 7, borderLeft: `2px solid ${cor}40`, fontSize: 13, fontFamily: F.serif, color: T.txtMid, lineHeight: 1.7 }}>{it}</div>)}
                            </div>
                          ))}
                          <div style={{ fontSize: 11, fontFamily: F.mono, color: T.primary, letterSpacing: "0.12em", marginBottom: 14 }}>📚 PLANO DE ESTUDOS</div>
                          {[
                            { label: "🔴 Alta — 30 dias",    cor: T.red,   itens: ["Técnica de final de torre e rei", "Estruturas de peões defensivas em posições fechadas"] },
                            { label: "🟡 Média — 90 dias",   cor: T.amber, itens: ["Defesa Francesa com as Pretas", "Jogo posicional e profilaxia"] },
                            { label: "🟢 Baixa — Contínuo",  cor: T.green, itens: ["Aprofundar repertório da Ruy Lopez", "Exercícios de velocidade de cálculo"] },
                          ].map(({ label, cor, itens }) => (
                            <div key={label} style={{ marginBottom: 16 }}>
                              <div style={{ fontSize: 11, fontFamily: F.mono, color: cor, marginBottom: 7 }}>{label}</div>
                              {itens.map(it => <div key={it} style={{ paddingLeft: 14, marginBottom: 5, borderLeft: `2px solid ${cor}40`, fontSize: 13, fontFamily: F.serif, color: T.txtMid, lineHeight: 1.7 }}>{it}</div>)}
                            </div>
                          ))}
                        </>
                      ) : (
                        <>
                          <div style={{ fontSize: 15, fontWeight: 700, color: T.txt, marginBottom: 4 }}>Como Vencer {usuario}</div>
                          <div style={{ fontSize: 10, fontFamily: F.mono, color: T.txtMuted, marginBottom: 24, letterSpacing: "0.1em" }}>
                            Inteligência sobre adversário · 100 partidas
                          </div>
                          {[
                            { titulo: "🎯 Preparação de Abertura", cor: T.red,     itens: ["Force a Defesa Francesa — taxa de vitória dele cai para 33%", "Evite a Siciliana — ele marca 68% nessa linha", "Com as Pretas, direcione para a Indiana do Rei"] },
                            { titulo: "⚔️ Estratégia no Meio-jogo", cor: T.amber,  itens: ["Busque posições fechadas — ele perde a paciência", "Evite complicações táticas onde ele se destaca", "Troque para finais aparentemente equilibrados"] },
                            { titulo: "🏁 Plano para o Final",       cor: T.primary,itens: ["Force finais de torre — sua fase mais fraca", "A precisão cai drasticamente após o lance 35", "Não se apresse — deixe-o cometer os erros"] },
                            { titulo: "⚠️ Fique Atento a",          cor: T.slate,  itens: ["Ataques no flanco do rei — principal arma dele", "Táticas em posições abertas — muito afiado", "Excesso de confiança em posições ganhas"] },
                          ].map(({ titulo, cor, itens }) => (
                            <div key={titulo} style={{ marginBottom: 20 }}>
                              <div style={{ fontSize: 11, fontFamily: F.mono, color: cor, letterSpacing: "0.1em", marginBottom: 10 }}>{titulo}</div>
                              {itens.map(it => <div key={it} style={{ paddingLeft: 14, marginBottom: 7, borderLeft: `2px solid ${cor}40`, fontSize: 13, fontFamily: F.serif, color: T.txtMid, lineHeight: 1.7 }}>{it}</div>)}
                            </div>
                          ))}
                          <div style={{ background: T.surface, border: `1px solid ${T.border}`, borderRadius: 8, padding: "14px 18px" }}>
                            <div style={{ fontSize: 10, fontFamily: F.mono, color: T.txtMuted, letterSpacing: "0.18em", marginBottom: 12 }}>✅ CHECKLIST PRÉ-PARTIDA</div>
                            {[
                              "Revisar as linhas principais da Defesa Francesa",
                              "Estudar técnica de final de torre e peão",
                              "Evitar simplificações precoces com as Brancas",
                              "Preparar um sistema de abertura fechado para ambas as cores",
                              "Manter a calma após o lance 30 — ele vai cometer erros",
                            ].map((it, i) => (
                              <div key={i} style={{ display: "flex", gap: 10, alignItems: "flex-start", marginBottom: 9 }}>
                                <div style={{ width: 14, height: 14, borderRadius: 3, border: `2px solid ${T.borderMid}`, flexShrink: 0, marginTop: 2 }} />
                                <span style={{ fontSize: 13, fontFamily: F.serif, color: T.txtMid, lineHeight: 1.6 }}>{it}</span>
                              </div>
                            ))}
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                )}
              </div>

              <div style={{ textAlign: "center", marginTop: 24 }}>
                <Btn variant="ghost" onClick={reiniciar} T={T}>← Analisar Outro Jogador</Btn>
              </div>
            </>
          )}
        </div>
      </main>

      <footer style={{ background: T.footerBg, borderTop: `1px solid ${T.border}`, padding: "14px 22px", textAlign: "center" }}>
        <span style={{ fontSize: 10, fontFamily: F.mono, color: T.txtMuted, letterSpacing: "0.22em" }}>
          CHESS SCOUT · STOCKFISH + PYTHON-CHESS
        </span>
      </footer>
    </div>
  );
}

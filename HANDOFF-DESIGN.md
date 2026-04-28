# Chess Scout — Handoff para Claude Code

> Protótipo: `Chess Scout - Dossie.html`
> Direção visual: **Dossiê** (relatório de inteligência clássico — tipografia editorial, papel, marginalia)
> Stack alvo: **Next.js + React + TypeScript + Tailwind** (sugerido)

---

## 1. Visão geral do produto

Aplicativo que transforma o histórico de partidas de um jogador (chess.com / lichess) em um **dossiê de inteligência** com plano operacional:

- **Self mode** — diagnóstico pessoal (perfil de habilidade, fraquezas).
- **Opponent mode** — como vencer aquele jogador específico (a tela "★ Plano de ataque" é o produto principal).

**Fluxo (4 telas + 1 ramo):**
1. `Search` — identifica alvo (username, plataforma chess.com/lichess, perspectiva self/opp, time-control multi-seleção).
2. `Loading` — análise mockada de ~4,5 s com log da engine + tabuleiro.
3. `Overview` — dashboard de stats e perfil (idêntico para self/opp; copy do CTA muda).
4. **Step IV — bifurcação por perspectiva:**
   - `perspective='self'` → `Personal` — diagnóstico pessoal, ponto-de-fuga de elo, plano de estudo de 4 semanas, momentos-chave para revisar.
   - `perspective='opp'` → `Adversary` — plano de ataque, linha decisiva, armas a evitar, brechas a explorar.

Deep-link via query params: `?screen=personal&perspective=self&lang=en`.

**Defaults da tela 01 (Search):**
- Plataforma: `chess.com`
- Perspectiva: `Sou eu` (self)
- Time-control: `Blitz` (multi-seleção, mínimo 1)

---

## 2. Estratégia responsiva — mobile-first, completa

> O usuário declarou: *"acredito que o mobile será mais usado que o desktop"*.
> Mas o produto também precisa funcionar em desktop (PDF print, dossiê grande). Por isso a estratégia é **mobile-first com upper-bounds**, não fluido infinito.

### 2.1 Tokens de breakpoint

```js
sm: 480,   // phones grandes / phablets pequenos
md: 768,   // tablet portrait + ponto de virada para 2 colunas
lg: 1024,  // tablet landscape / desktop pequeno
xl: 1280,  // desktop confortável (cap visual em ~880px de paper)
```

Mobile-first: nenhum estilo usa `max-width` query. Todos crescem com `min-width`. O `PaperCard asPage` tem `max-width: 880px` — em desktop o "papel" fica centralizado em fundo bege, exatamente como um dossiê físico.

### 2.2 Técnicas usadas no protótipo

| Técnica | Onde | Por quê |
|---|---|---|
| `clamp(min, vw, max)` em fontes/padding | TUDO | Tipografia fluida sem media queries explícitas |
| `grid-template-columns: repeat(auto-fit, minmax(N, 1fr))` | Stats, listas, two-col | Quebra automática em N colunas conforme largura |
| `aspect-ratio: 1/1` no tabuleiro | `Chessboard` | Preserva quadrado em qualquer container |
| `overflow-x: auto` + `min-width` em tabela | Tabelas de partidas | Mobile não trunca dados; desktop usa largura total |
| `clamp(14px, 2.5vw, 18px)` padding em botões | Todos os CTAs | Hit target ≥44px no mobile, denso no desktop |
| `useViewport()` hook | `tokens.jsx` | Layout condicional avançado se necessário |
| `min-height: 100dvh` | `body` | Evita o bug da barra de URL no iOS Safari |

### 2.3 Matriz de testes responsivos

Antes do go-live, validar **cada uma das 5 telas** (Search, Loading, Overview, Personal, Adversary) em:

| Viewport | Dispositivo | Pontos críticos |
|---|---|---|
| **320×568** | iPhone SE 1 (canto extremo) | Stamp na tela 04 não colide com header; tabela rola; segments wrappam |
| **375×812** | iPhone 13 mini | Hit targets ≥44px; texto ≥14px; cards de "alvos prioritários" não quebram |
| **414×896** | iPhone 14 Plus | Layout esperado em maioria do tráfego mobile |
| **768×1024** | iPad portrait | Two-col começa a aparecer; verificar `auto-fit minmax(280px)` |
| **1024×768** | iPad landscape | Paper centralizado; margens laterais bege OK |
| **1440×900** | MacBook | Cap em 880px funciona; CTAs não esticam |
| **1920×1080** | Monitor desktop | Margens generosas; sem texto em coluna >75ch |

### 2.4 Cenários a observar

- **iOS Safari `100vh` bug** — usar `100dvh` (já feito).
- **Tab backgrounded** — `setInterval` (não rAF) sobrevive; `visibilitychange` ressincroniza (já feito).
- **Print landscape** — testar `Cmd+P` em desktop; o CSS já tem `@media print { background: white }`. Validar quebra de página em folhas A4.
- **Carregamento de fonte** — `Cormorant Garamond` é o coração visual; em conexão ruim, fallback `Georgia, serif` é aceitável. Considerar `font-display: swap` (já no Google Fonts).
- **Modo escuro do sistema** — atualmente NÃO suportado; o paper bege é decisão de marca. Documentar com produto.
- **Acessibilidade** — em zoom 200% (regulatorio), o `clamp()` cresce até o cap; testar overflow horizontal.

### 2.5 Pontos de atenção específicos por tela

| Tela | Atenção |
|---|---|
| **Search** | Lista "Alvos prioritários" em mobile → cards full-width com nome cortado por `text-overflow: ellipsis`. Conferir nomes longos. |
| **Loading** | Log da engine tem `max-height` para não estourar viewport mobile. |
| **Overview** | Tabela de partidas recentes rola horizontalmente <540px. Considerar virar lista de cards <768px. |
| **Personal** | Tabela "Momentos-chave" idem. Hero "+72 elo" é grande — verificar em 320px que não estoura. |
| **Adversary** | Stamp "CONFIDENCIAL" absoluto no canto. <360px pode colidir com texto do header — opção: ocultar via `display: none` em mobile. |

---

## 3. Estrutura de arquivos

```
Chess Scout - Dossie.html        ← shell + app router (in-memory) + step branching
final/
├── tokens.jsx        ← DOSSIE_TOKENS (color, font, bp) + useViewport hook
├── i18n.jsx          ← I18N.pt, I18N.en (todas as strings, incluindo personal)
├── visuals.jsx       ← PaperTexture, Stamp, Chessboard, RadarChart,
│                       Sparkline, ResultsBar, MoveQualityBars, PhaseBars
├── ui.jsx            ← PaperCard, AppHeader, StepIndicator (perspective-aware),
│                       SectionHeading, FieldLabel, TextInput, Segment (multi),
│                       PrimaryButton, GhostButton, TwoCol, Stat, Footer
├── screen-search.jsx
├── screen-loading.jsx
├── screen-overview.jsx
├── screen-adversary.jsx   ← step IV quando perspective='opp'
└── screen-personal.jsx    ← step IV quando perspective='self'
```

**Dependência cruzada:** todos os primitivos são expostos em `window.*`. Ao migrar, transforme em **named exports** de módulos TS.

---

## 4. Design tokens — fonte única de verdade

Já estão centralizados em `final/tokens.jsx` (`DOSSIE_TOKENS`). Migrar para:

**`tokens.css` (Tailwind v4 / CSS variables):**
```css
:root {
  --color-bg: #f3ede0;
  --color-paper: #faf6ec;
  --color-paper-edge: #e7dfcc;
  --color-ink: #1c1a14;
  --color-ink-mid: #3a3528;
  --color-ink-muted: #7a6f55;
  --color-ink-faint: #a89d80;
  --color-border: #d5cab0;
  --color-border-mid: #c0b390;
  --color-red: #a8281e;
  --color-red-bg: #f3dcd6;
  --color-green: #3a6b2a;
  --color-amber: #a8702a;
  --font-serif: 'Cormorant Garamond', Georgia, serif;
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}
```

**Tailwind config (extracts):**
```ts
extend: {
  colors: { ink: '#1c1a14', paper: '#faf6ec', red: '#a8281e', /* … */ },
  fontFamily: {
    serif: ['Cormorant Garamond', 'Georgia', 'serif'],
    sans: ['Inter', 'system-ui'],
    mono: ['JetBrains Mono', 'monospace'],
  },
  screens: { sm: '480px', md: '768px', lg: '1024px', xl: '1280px' },
}
```

---

## 5. Componentes — mapeamento sugerido

| Protótipo (window.*) | TS / React component | Notas |
|---|---|---|
| `PaperCard` | `<PaperShell asPage>` | Container raiz com textura |
| `AppHeader` | `<AppHeader/>` | Sticky em mobile? confirmar com produto |
| `StepIndicator` | `<StepIndicator step={1..4}/>` | Idealmente vira ARIA `tablist` |
| `Chessboard` | `<Chessboard pieces highlights flip/>` | **Substituir por `chess.js` + `react-chessground`** em produção; o SVG do protótipo é apenas visual |
| `Sparkline`, `RadarChart`, `PhaseBars`, etc | Manter SVG ou trocar por `recharts`/`visx` | SVG inline é mais leve; recharts dá interatividade |
| `Segment`, `TextInput` | Componentes de form com react-hook-form + zod | |
| `Stamp` | Asset SVG estático | Pode virar `<img>` para evitar overhead |

---

## 6. APIs (a serem implementadas)

O protótipo usa dados mockados. Para produção:

| Endpoint | Propósito |
|---|---|
| `GET /api/players/:platform/:username` | Metadados básicos + rating atual |
| `POST /api/analysis` | Inicia job de análise. body: `{platform, username, tc}` → `{jobId}` |
| `GET /api/analysis/:jobId/stream` (SSE) | Stream de progresso (substitui o `setInterval` mock) |
| `GET /api/analysis/:jobId/report` | Relatório final (overview + adversary data) |

A tela `Loading` deve consumir SSE/WebSocket; o `setInterval` atual é só para demo. **Importante:** mantenha `visibilitychange` listener para resync ao voltar para a aba (já implementado).

---

## 7. i18n

`final/i18n.jsx` tem chaves planas em PT/EN. Migrar para **`next-intl`** ou **`react-i18next`** sem mudar a estrutura. Algumas chaves são funções (`loadingSub(user)`, `decisiveBody(pct)`) — usar interpolação ICU.

---

## 8. Acessibilidade — checklist para implementação

- [ ] `<main>` em cada tela (já há).
- [ ] `aria-label` em botões de ícone (lang toggle, back).
- [ ] `role="progressbar"` + `aria-valuenow` no progress da tela de loading.
- [ ] Foco visível em todos os botões (Tailwind `focus-visible:ring`).
- [ ] Contraste verificado: `#1c1a14` em `#faf6ec` = ratio ~17:1 ✓; `#7a6f55` em `#faf6ec` = ratio ~4.6:1 (use só para texto secundário).
- [ ] Tabuleiro precisa de `<title>` + descrição textual da posição para leitores de tela.
- [ ] Reduce motion: `@media (prefers-reduced-motion)` deve desativar a animação de progresso.

---

## 9. Performance

- Fontes: usar `next/font` em vez de Google Fonts via `<link>`.
- Imagens/SVG: tabuleiro é leve (~8KB), mas se for animado → considerar canvas.
- Code-split por rota: cada screen é uma rota Next, lazy-loadable.
- Mock data: o protótipo tem `ANALYSIS_LINES`, `recentGames`, `weapons`, `gaps`, `plan` hardcoded em cada screen — extrair para `mocks/` durante dev e remover em prod.

---

## 10. Próximos passos sugeridos

1. **Smoke test no protótipo** — abra `?screen=adversary&lang=en` em iPhone real e confirme legibilidade.
2. Validar fluxo com 5-10 usuários alvo (jogadores de blitz 1500-2200 elo).
3. Definir tier free vs paid — protótipo assume todas as features liberadas.
4. Implementar back-end de análise real (queue + Stockfish worker).
5. Decidir frame de tabuleiro: react-chessground (FOSS) vs lichess-pgn-viewer.

---

*Gerado a partir do protótipo `Chess Scout - Dossie.html`. Toda a copy do produto está em `final/i18n.jsx`.*

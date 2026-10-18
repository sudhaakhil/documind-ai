# DocuMind AI design system

## 1. Concept

**"A quiet, trustworthy research desk."** The interface stays out of the way so the documents and answers come first. Three ideas guide every decision:

1. **Grounded by default.** Every answer shows where it came from: numbered citations in the text, source chips under the answer, and the full passages in the document panel. That traceability is what makes an AI document tool feel trustworthy.
2. **One accent, used with intent.** Indigo marks what you can act on or what's active: the primary button, the send button, the active sidebar row, citation numbers. Everything else is slate on white.
3. **Calm density.** Compact type (15px base), 8px-based spacing, and only three kinds of surface: page, card, and the navy sidebar.

The dark navy sidebar against a light workspace splits *navigation* from *content* at a glance, the same pattern Linear, Notion AI and ChatGPT use.

## 2. Colour system

| Token | Hex | Used for |
|---|---|---|
| `--dm-bg` | `#F8FAFC` | Page background |
| `--dm-sidebar` | `#111827` | Sidebar |
| `--dm-primary` | `#6366F1` | Primary buttons, send button, focus ring, icons |
| `--dm-primary-strong` | `#4F46E5` | Indigo *text* on white, hover state (meets WCAG AA) |
| `--dm-secondary` | `#818CF8` | Active sidebar icon, brand "AI", logo gradient end |
| `--dm-primary-soft` | `#EEF2FF` | User bubbles, icon tiles, citation number badges |
| `--dm-card` | `#FFFFFF` | Cards, panel, inputs |
| `--dm-text` | `#0F172A` | Main text |
| `--dm-muted` | `#64748B` | Secondary text (4.8:1 on white) |
| `--dm-border` | `#E2E8F0` | Borders and dividers |
| `--dm-success` | `#10B981` | Online dot, success states |

State colours (callouts) use tinted backgrounds with dark text, never white text on saturated fills: success `#ECFDF5/#047857`, info `#EEF2FF/#3730A3`, warning `#FFFBEB/#92400E`, error `#FEF2F2/#991B1B`.

**Gradients** appear in exactly two places: the logo tile and the second half of the hero heading.

## 3. Typography

Font: **Inter** (400 / 500 / 600 / 700), loaded through Streamlit's theme config.

| Role | Size / weight | Notes |
|---|---|---|
| Hero heading | 32px / 700, -0.025em | Only on the welcome screen |
| Chat title | 16px / 600 | Top bar |
| Body / messages | 15px / 400, line-height 1.65 | |
| UI text, buttons | 14px / 500 | |
| Meta / captions | 12–13px / 400–500 | Muted colour |
| Section labels | 11–12px / 600, uppercase, +0.07em | "DOCUMENTS", "TRY ASKING" |

## 4. Layout

```
┌──────────────┬──────────────────────────────────────────────┬────────────────────────┐
│ SIDEBAR 276px│ WORKSPACE (≈70%)                             │ DOCUMENT PANEL (≈30%)  │
│ navy         │                                              │ sticky, collapsible    │
│              │ New chat                            [⋯] [▣]  │                        │
│ ◼ DocuMind AI│ ⌕ Answering from all 3 documents             │ ▢ report.pdf           │
│ Document int.│ ────────────────────────────────────────────  │   PDF · 2.4 MB         │
│              │                                              │ ────────────────────── │
│ [+ New chat] │       ( Runs locally with Ollama … )         │ Pages               12 │
│ ┆ Upload PDF┆│     Your documents. Smarter answers.         │ Passages            48 │
│              │ Upload, explore, and understand your docs.   │ Added     Oct 18, 2026 │
│ DOCUMENTS (3)│                                              │ ○ Answer from this     │
│ ▤ report.pdf │ ┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐ │   document only        │
│ ▤ thesis.pdf │ ┆  ☁  Drag and drop PDFs here   [Browse]   ┆ │                        │
│              │ └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘ │ SUMMARY                │
│ RECENT CHATS │ ✓ 3 documents are indexed and ready.         │ ✦ This report evaluates│
│ ▭ Key risks… │                                              │   a hybrid work pilot… │
│ ▭ Summarize… │ TRY ASKING                                   │                        │
│              │ ┌───────────────────┐ ┌───────────────────┐  │ CITED PASSAGES         │
│ ──────────── │ │▤ Summarize key pts│ │✱ Main conclusions │  │ p.1  p.2  p.3          │
│ ⚙ Settings ▾ │ └───────────────────┘ └───────────────────┘  │ ┌────────────────────┐ │
│  ● Ollama ok │ ┌───────────────────┐ ┌───────────────────┐  │ │1 report.pdf   p. 1 │ │
│  Chat model  │ │◷ Dates & numbers  │ │◎ Core ideas simply│  │ │▏"Remote work imp…" │ │
│  Passages    │ └───────────────────┘ └───────────────────┘  │ │ 82% match          │ │
│  Creativity  │ ┌─────────────────────────────────────── ➤┐  │ └────────────────────┘ │
│              │ │ Ask anything about your documents…       │  │ [ 🗑 Remove document ]  │
└──────────────┴──────────────────────────────────────────────┴────────────────────────┘
```

**Conversation view** replaces the welcome block:

```
                                        ┌──────────────────────────────┐
                                        │ You                          │
                                        │ What are the main findings?  │ ← indigo-tint bubble, right
                                        └──────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────┐
│ ◼ DocuMind                                                           │ ← white card, left
│ Remote work improved focus time by 23% [1] …                         │
│ ──────────────────────────────────────────────────────────────────── │
│ SOURCES  [1 ▤ report.pdf p. 1]  [2 ▤ report.pdf p. 2]                │
│ 📖 View passages                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

**Responsive behaviour**

- Panel toggle (top-right) hides the document panel; the chat then centres at a 860px reading width.
- The top bar sticks to the top and the question box to the bottom, so both stay in reach in long chats.
- Below 640px Streamlit stacks the columns: chat first, panel below (no longer sticky).
- The sidebar collapses with Streamlit's own control.

## 5. Component specifications

| Component | Where | Spec |
|---|---|---|
| **Brand** | `components.brand()` | 32px logo tile (radius 9, indigo gradient) + name 16px/650 + tagline 12px muted |
| **Primary button** | New chat, confirm actions | `#6366F1` fill, white 14px/600, radius 10, hover `#4F46E5` |
| **Nav row** | Sidebar docs & chats | Tertiary button, left-aligned, 34px tall, radius 8, ellipsis truncation. Hover `rgba(255,255,255,.06)`, active `rgba(129,140,248,.16)` + indigo icon |
| **Section label** | `section_label()` | 11px uppercase, +0.08em, optional count pill |
| **Dropzone** | Welcome | White, 1.5px dashed `#CBD5E1`, radius 14, hover border indigo. Compact dashed row in the sidebar |
| **Suggestion card** | Welcome | Secondary button as card: white, border, radius 12, shadow-sm → shadow-md on hover, indigo Material icon. Disabled until a PDF exists |
| **User message** | Chat | Right-aligned, max 82% width, `#EEF2FF` with `#E0E7FF` border, radius 14/14/4/14 |
| **AI message** | Chat | Full-width white card, border, radius 14, shadow-sm, logo + "DocuMind" header |
| **Source chip** | Under AI answer | Number badge + file icon + filename (ellipsis at 260px) + page. Not clickable; the "View passages" link next to it is the action |
| **Thinking indicator** | Live answer | Three 6px dots pulsing in `#818CF8` + status text; hidden when the first token arrives |
| **Chat input** | Bottom of workspace | White, radius 14, shadow-md; focus = indigo border + 4px ring; indigo send button |
| **Doc header** | Panel | 40px indigo-soft icon tile + filename 15px/600 + "PDF · size" |
| **Info rows** | Panel | Label/value rows (Pages, Passages, Added) split by hairlines; reads well at any panel width |
| **Summary** | Panel | Indigo-tinted box with sparkle icon; "Generate summary" button until it exists |
| **Passage card** | Panel | Number badge, filename, page pill, excerpt with 2px indigo left rule, % match |
| **Callout** | Anywhere | Tinted background + icon + optional bold title; `role="alert"` for errors |
| **Empty state** | Panel | 44px icon tile, title 15px/600, body 13px muted, max 260px wide |
| **Status line** | Settings | 8px dot with soft halo: green online, red offline |

## 6. States

| State | Treatment |
|---|---|
| Empty (no docs) | Hero + dropzone; suggestion cards and chat input disabled with a hint; panel shows its empty state |
| Loading: indexing | `st.status` card with a progress bar ("Embedding passages 33–64 of 120") |
| Loading: answering | Thinking dots ("Searching your documents" → "Reading the relevant passages"), then streamed tokens |
| Success | Toast after indexing; green "N documents indexed and ready" callout on the welcome screen |
| Error | Red callout with the fix: Ollama offline → `ollama serve`; model missing → `ollama pull <model>`; scanned PDF, encrypted PDF or corrupt file → plain explanation |
| Duplicate upload | Info callout "already in your library" (files are de-duplicated by content hash) |

## 7. Interaction rules

- Transitions are 150ms on colour, border and shadow only. No movement or scaling.
- `prefers-reduced-motion` turns off all transitions and the thinking animation.
- Every visible control does something real; there are no placeholder buttons.

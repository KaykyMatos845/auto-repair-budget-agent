import os

target = r"C:\Users\kayky.matos\Downloads\auto-repair-budget-agent\index.html"

part1 = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AutoBudget AI v2.5 — Vistoria, FIPE, Perda Total & WhatsApp</title>
  <meta name="description" content="Sistema completo de vistoria veicular com IA Gemini, Tabela FIPE, Alerta de Perda Total, Bounding Boxes nas fotos, cotação Mercado Livre e envio por WhatsApp."/>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/react@18/umd/react.development.js" crossorigin></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js" crossorigin></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <style>
    :root {
      --fh: 'Outfit', sans-serif;
      --fb: 'Plus Jakarta Sans', sans-serif;
      --bg: #06080f;
      --card: rgba(14, 20, 34, 0.92);
      --border: rgba(245, 158, 11, 0.22);
      --border-hi: rgba(245, 158, 11, 0.55);
      --text: #f1f5f9;
      --muted: #94a3b8;
      --dim: #64748b;
      --gold: #f59e0b;
      --gold-hi: #fbbf24;
      --violet: #8b5cf6;
      --emerald: #10b981;
      --rose: #f43f5e;
      --cyan: #06b6d4;
      --grad-gold: linear-gradient(135deg, #fbbf24, #d97706);
      --grad-brand: linear-gradient(135deg, #fbbf24 0%, #f43f5e 50%, #8b5cf6 100%);
      --grad-emerald: linear-gradient(135deg, #10b981, #059669);
      --grad-danger: linear-gradient(135deg, #f43f5e, #be123c);
      --shadow-gold: 0 0 28px rgba(245,158,11,0.25);
      --shadow-md: 0 10px 30px rgba(0,0,0,0.55);
      --r: 14px; --rs: 8px; --rfull: 9999px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: var(--fb);
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      background-image:
        radial-gradient(circle at 8% 8%, rgba(245,158,11,0.12) 0%, transparent 38%),
        radial-gradient(circle at 92% 15%, rgba(139,92,246,0.14) 0%, transparent 42%),
        radial-gradient(circle at 50% 88%, rgba(16,185,129,0.08) 0%, transparent 50%);
      background-attachment: fixed;
    }
    h1,h2,h3,h4 { font-family: var(--fh); letter-spacing: -0.025em; }
    .wrap { max-width: 1240px; margin: 0 auto; padding: 28px 18px; }

    .card {
      background: var(--card);
      backdrop-filter: blur(22px);
      border: 1px solid var(--border);
      border-radius: var(--r);
      box-shadow: var(--shadow-md);
      transition: border-color .25s;
    }
    .card:hover { border-color: var(--border-hi); }

    .btn-gold {
      background: var(--grad-gold);
      color: #0a0c14;
      font-weight: 800;
      padding: 12px 26px;
      border-radius: var(--rs);
      border: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 9px;
      transition: all .22s;
      letter-spacing: 0.03em;
      font-size: .87rem;
      text-transform: uppercase;
      box-shadow: var(--shadow-gold);
    }
    .btn-gold:hover { transform: translateY(-2px) scale(1.02); filter: brightness(1.12); }
    .btn-gold:disabled { opacity: 0.55; cursor: not-allowed; transform: none; }

    .btn-whatsapp {
      background: linear-gradient(135deg, #25D366, #128C7E);
      color: #fff;
      font-weight: 800;
      padding: 12px 24px;
      border-radius: var(--rs);
      border: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 9px;
      transition: all .22s;
      font-size: .87rem;
      text-transform: uppercase;
      box-shadow: 0 0 20px rgba(37,211,102,0.35);
    }
    .btn-whatsapp:hover { transform: translateY(-2px); filter: brightness(1.1); }

    .btn-ghost {
      background: rgba(255,255,255,0.05);
      color: var(--text);
      font-weight: 600;
      padding: 10px 18px;
      border-radius: var(--rs);
      border: 1px solid var(--border);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      transition: all .2s;
      font-size: .86rem;
    }
    .btn-ghost:hover { background: rgba(245,158,11,0.12); border-color: var(--gold); color: var(--gold-hi); }

    .btn-emerald {
      background: var(--grad-emerald);
      color: #fff;
      font-weight: 800;
      padding: 12px 26px;
      border-radius: var(--rs);
      border: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 9px;
      transition: all .22s;
      font-size: .87rem;
      text-transform: uppercase;
      box-shadow: 0 0 22px rgba(16,185,129,0.3);
    }
    .btn-emerald:hover { transform: translateY(-2px); filter: brightness(1.12); }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 4px 11px;
      border-radius: var(--rfull);
      font-size: .72rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: .06em;
    }
    .badge-replace { background: rgba(244,63,94,.18); color: #ff6b81; border: 1px solid rgba(244,63,94,.4); }
    .badge-repair  { background: rgba(245,158,11,.18); color: #fbbf24; border: 1px solid rgba(245,158,11,.4); }
    .badge-new     { background: rgba(139,92,246,.18); color: #c084fc; border: 1px solid rgba(139,92,246,.4); }
    .badge-used    { background: rgba(16,185,129,.18); color: #34d399;  border: 1px solid rgba(16,185,129,.4); }
    .badge-ai      { background: rgba(6,182,212,.18);  color: #22d3ee;  border: 1px solid rgba(6,182,212,.4); }

    .grad-text { background: var(--grad-brand); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

    .inp {
      width: 100%;
      padding: 10px 14px;
      background: rgba(10,14,24,0.9);
      border: 1px solid var(--border);
      border-radius: var(--rs);
      color: var(--text);
      font-size: .9rem;
      outline: none;
      transition: border-color .2s;
      font-family: var(--fb);
    }
    .inp:focus { border-color: var(--gold); }

    label { font-size: .78rem; color: var(--muted); font-weight: 700; display: block; margin-bottom: 5px; }

    .upload-zone {
      border: 2px dashed rgba(245,158,11,.35);
      border-radius: var(--r);
      padding: 36px 24px;
      text-align: center;
      background: rgba(10,14,24,.5);
      cursor: pointer;
      transition: all .25s;
    }
    .upload-zone:hover { border-color: var(--gold-hi); background: rgba(245,158,11,.07); }

    .img-box-container {
      position: relative;
      display: inline-block;
      overflow: hidden;
      border-radius: 12px;
      border: 2px solid var(--border-hi);
    }
    .bbox-overlay {
      position: absolute;
      border: 3px solid #f43f5e;
      background: rgba(244,63,94,0.25);
      border-radius: 6px;
      box-shadow: 0 0 14px rgba(244,63,94,0.7);
      pointer-events: none;
      transition: all .3s;
    }
    .bbox-label {
      position: absolute;
      top: -24px;
      left: -2px;
      background: #f43f5e;
      color: #fff;
      font-size: 10px;
      font-weight: 800;
      padding: 2px 7px;
      border-radius: 4px 4px 4px 0;
      white-space: nowrap;
      text-transform: uppercase;
    }

    @media print {
      body * { visibility: hidden; }
      #pdf-area, #pdf-area * { visibility: visible; }
      #pdf-area { position: absolute; left: 0; top: 0; width: 100%; color: #000; }
      .no-print { display: none !important; }
    }
  </style>
</head>
<body>
<div id="root"></div>
<script type="text/babel">
"""

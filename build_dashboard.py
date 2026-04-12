"""Build a self-contained interactive HTML dashboard from dashboard_data.json."""

import json
from pathlib import Path

ETF_CATALOG = [
    {"cat": "AI / 人工智慧", "color": "#7c3aed", "etfs": [
        {"t": "BAI", "n": "iShares A.I. Innovation and Tech Active ETF", "er": "0.55%", "aum": "$9.0B", "d": "主動管理，全球 AI 龍頭科技股"},
        {"t": "AIQ", "n": "Global X AI & Technology ETF", "er": "0.68%", "aum": "$7.8B", "d": "追蹤 Indxx AI 指數，廣泛 AI 曝險"},
        {"t": "BOTZ", "n": "Global X Robotics & AI ETF", "er": "0.68%", "aum": "$3.4B", "d": "應用 AI + 工業機器人自動化"},
        {"t": "XT", "n": "iShares Exponential Technologies ETF", "er": "0.46%", "aum": "$3.3B", "d": "廣泛指數科技含 AI / 奈米 / 機器人"},
        {"t": "ARTY", "n": "iShares Future AI & Tech ETF", "er": "0.47%", "aum": "$2.2B", "d": "BlackRock 被動式 AI 曝險"},
        {"t": "ARKQ", "n": "ARK Autonomous Tech & Robotics ETF", "er": "0.75%", "aum": "$2.0B", "d": "ARK 主動管理，自駕 + 機器人"},
        {"t": "ROBO", "n": "ROBO Global Robotics & Automation ETF", "er": "0.95%", "aum": "$1.6B", "d": "全球機器人自動化指數"},
        {"t": "CHAT", "n": "Roundhill Generative AI & Tech ETF", "er": "0.75%", "aum": "$1.1B", "d": "集中在生成式 AI 相關公司"},
        {"t": "IGPT", "n": "Invesco AI and Next Gen Software ETF", "er": "0.56%", "aum": "$700M", "d": "AI 驅動的次世代軟體"},
        {"t": "ROBT", "n": "First Trust Nasdaq AI & Robotics ETF", "er": "0.65%", "aum": "$655M", "d": "Nasdaq AI 指數，中小型偏重"},
        {"t": "IVES", "n": "Wedbush Dan Ives AI Revolution ETF", "er": "0.65%", "aum": "$650M", "d": "分析師精選 AI 革命主題"},
        {"t": "IRBO", "n": "iShares Robotics and AI Multisector ETF", "er": "0.47%", "aum": "$570M", "d": "92 檔持股，多產業 AI 曝險"},
        {"t": "WTAI", "n": "WisdomTree Artificial Intelligence ETF", "er": "0.45%", "aum": "$378M", "d": "AI 信號選股策略"},
        {"t": "THNQ", "n": "ROBO Global Artificial Intelligence ETF", "er": "0.68%", "aum": "$285M", "d": "全球 AI 與機器人領導者"},
        {"t": "QTUM", "n": "Defiance Machine Learning & Quantum ETF", "er": "0.40%", "aum": "$200M", "d": "機器學習 + 量子計算"},
        {"t": "AIVL", "n": "WisdomTree U.S. AI Enhanced Value Fund", "er": "0.38%", "aum": "$200M", "d": "AI 增強價值型選股"},
        {"t": "LOUP", "n": "Innovator Loup Frontier Tech ETF", "er": "0.70%", "aum": "$50M", "d": "前沿科技：AI / 自駕 / 機器人"},
    ]},
    {"cat": "半導體", "color": "#8b5cf6", "etfs": [
        {"t": "SMH", "n": "VanEck Semiconductor ETF", "er": "0.35%", "aum": "$42.5B", "d": "最大半導體 ETF，重壓 NVIDIA + TSMC"},
        {"t": "SOXX", "n": "iShares Semiconductor ETF", "er": "0.34%", "aum": "$20.7B", "d": "ICE 半導體指數，31 檔持股"},
        {"t": "XSD", "n": "SPDR S&P Semiconductor ETF", "er": "0.35%", "aum": "$1.6B", "d": "等權重，中小型半導體曝險"},
        {"t": "FTXL", "n": "First Trust Nasdaq Semiconductor ETF", "er": "0.60%", "aum": "$1.9B", "d": "Smart-beta 半導體選股"},
        {"t": "PSI", "n": "Invesco Semiconductors ETF", "er": "0.56%", "aum": "$1.3B", "d": "動態選擇半導體公司"},
        {"t": "SOXQ", "n": "Invesco PHLX Semiconductor ETF", "er": "0.19%", "aum": "$1.1B", "d": "最低費用半導體 ETF"},
        {"t": "CHPS", "n": "Xtrackers Semiconductor Select ETF", "er": "0.15%", "aum": "$42M", "d": "極低費用半導體精選"},
    ]},
    {"cat": "廣泛科技", "color": "#3b82f6", "etfs": [
        {"t": "QQQ", "n": "Invesco QQQ Trust", "er": "0.20%", "aum": "$387B", "d": "Nasdaq-100，最主流大型科技 ETF"},
        {"t": "QQQM", "n": "Invesco NASDAQ 100 ETF", "er": "0.15%", "aum": "$50B", "d": "QQQ 低費版，適合長期持有"},
        {"t": "VGT", "n": "Vanguard Information Technology ETF", "er": "0.09%", "aum": "$107B", "d": "最大純科技 ETF，300+ 持股"},
        {"t": "XLK", "n": "Technology Select Sector SPDR", "er": "0.08%", "aum": "$88B", "d": "最低費用的科技板塊 ETF"},
        {"t": "FTEC", "n": "Fidelity MSCI IT Index ETF", "er": "0.084%", "aum": "$15B", "d": "近乎 VGT 但費用更低"},
    ]},
    {"cat": "雲端 / 資安", "color": "#60a5fa", "etfs": [
        {"t": "IGV", "n": "iShares Expanded Tech-Software ETF", "er": "0.39%", "aum": "$11B", "d": "最大軟體產業 ETF"},
        {"t": "CIBR", "n": "First Trust NASDAQ Cybersecurity ETF", "er": "0.58%", "aum": "$9.8B", "d": "最大資安 ETF，約 35 檔持股"},
        {"t": "SKYY", "n": "First Trust Cloud Computing ETF", "er": "0.60%", "aum": "$2.4B", "d": "最老牌雲端運算 ETF"},
        {"t": "HACK", "n": "ETFMG Prime Cyber Security ETF", "er": "0.60%", "aum": "$1.5B", "d": "全球資安公司"},
        {"t": "BUG", "n": "Global X Cybersecurity ETF", "er": "0.50%", "aum": "$500M", "d": "全球資安領導者"},
        {"t": "WCLD", "n": "WisdomTree Cloud Computing Fund", "er": "0.45%", "aum": "$229M", "d": "雲端軟體成長股"},
        {"t": "CLOU", "n": "Global X Cloud Computing ETF", "er": "0.68%", "aum": "$211M", "d": "純雲端運算 37 檔持股"},
    ]},
    {"cat": "核能 / 鈾", "color": "#059669", "etfs": [
        {"t": "URA", "n": "Global X Uranium ETF", "er": "0.69%", "aum": "$6.9B", "d": "最大鈾 ETF，Cameco + Kazatomprom"},
        {"t": "NLR", "n": "VanEck Uranium and Nuclear ETF", "er": "0.56%", "aum": "$4.6B", "d": "核電公用事業 + 鈾礦商"},
        {"t": "URNM", "n": "Sprott Uranium Miners ETF", "er": "0.75%", "aum": "$2.2B", "d": "純鈾礦商 + 實體鈾持倉"},
        {"t": "NUKZ", "n": "Range Nuclear Renaissance Index ETF", "er": "0.85%", "aum": "$820M", "d": "核能復興動量選股"},
        {"t": "URNJ", "n": "Sprott Junior Uranium Miners ETF", "er": "0.80%", "aum": "$422M", "d": "小型鈾礦，高風險高報酬"},
        {"t": "URAN", "n": "Themes Uranium & Nuclear ETF", "er": "0.35%", "aum": "$28M", "d": "最低費用鈾 / 核能 ETF"},
    ]},
    {"cat": "清潔能源 / 電網", "color": "#10b981", "etfs": [
        {"t": "GRID", "n": "First Trust Smart Grid Infrastructure", "er": "0.56%", "aum": "$7.9B", "d": "智慧電網基礎建設，AI 資料中心用電受惠"},
        {"t": "ICLN", "n": "iShares Global Clean Energy ETF", "er": "0.39%", "aum": "$2.2B", "d": "廣泛全球清潔能源"},
        {"t": "LIT", "n": "Global X Lithium & Battery Tech ETF", "er": "0.75%", "aum": "$1.7B", "d": "鋰礦 + 電池技術"},
        {"t": "TAN", "n": "Invesco Solar ETF", "er": "0.70%", "aum": "$1.5B", "d": "純太陽能產業"},
        {"t": "QCLN", "n": "First Trust Clean Edge Green Energy", "er": "0.56%", "aum": "$570M", "d": "清潔能源含電動車概念"},
        {"t": "PBW", "n": "Invesco WilderHill Clean Energy ETF", "er": "0.64%", "aum": "$511M", "d": "太陽能 / 風能 / 儲能"},
    ]},
    {"cat": "傳統能源 / 公用事業", "color": "#34d399", "etfs": [
        {"t": "XLE", "n": "Energy Select Sector SPDR", "er": "0.08%", "aum": "$41.5B", "d": "S&P 500 能源板塊，Exxon + Chevron"},
        {"t": "XLU", "n": "Utilities Select Sector SPDR", "er": "0.08%", "aum": "$24.4B", "d": "最大公用事業 ETF，穩定配息"},
        {"t": "PAVE", "n": "Global X US Infrastructure Dev ETF", "er": "0.47%", "aum": "$11.8B", "d": "美國基礎建設開發"},
        {"t": "VDE", "n": "Vanguard Energy ETF", "er": "0.09%", "aum": "$10.6B", "d": "廣泛美國能源，低費用"},
        {"t": "VPU", "n": "Vanguard Utilities ETF", "er": "0.09%", "aum": "$8.8B", "d": "69 檔公用事業持股"},
        {"t": "COPX", "n": "Global X Copper Miners ETF", "er": "0.65%", "aum": "$3.0B", "d": "銅礦（電氣化必需金屬）"},
        {"t": "REMX", "n": "VanEck Rare Earth/Strategic Metals", "er": "0.58%", "aum": "$2.6B", "d": "稀土與戰略金屬"},
    ]},
    {"cat": "GLP-1 / 減重", "color": "#ef4444", "etfs": [
        {"t": "OZEM", "n": "Roundhill GLP-1 & Weight Loss ETF", "er": "0.59%", "aum": "$57M", "d": "全球首檔 GLP-1 ETF，NVO + LLY"},
        {"t": "THNR", "n": "Amplify Weight Loss Drug & Treatment ETF", "er": "0.59%", "aum": "$20M", "d": "減重藥物，與 OZEM 重疊 ~60%"},
    ]},
    {"cat": "製藥", "color": "#f87171", "etfs": [
        {"t": "PPH", "n": "VanEck Pharmaceutical ETF", "er": "0.36%", "aum": "$1.3B", "d": "全球製藥龍頭含 NVO / LLY"},
        {"t": "PJP", "n": "Invesco Pharmaceuticals ETF", "er": "0.55%", "aum": "$300M", "d": "動態選擇製藥公司"},
        {"t": "XPH", "n": "SPDR S&P Pharmaceuticals ETF", "er": "0.35%", "aum": "$200M", "d": "等權重美國製藥"},
        {"t": "IHE", "n": "iShares U.S. Pharmaceuticals ETF", "er": "0.39%", "aum": "$200M", "d": "美國製藥公司"},
    ]},
    {"cat": "生技", "color": "#fb923c", "etfs": [
        {"t": "IBB", "n": "iShares Biotechnology ETF", "er": "0.44%", "aum": "$8.0B", "d": "258 檔生技，市值加權"},
        {"t": "XBI", "n": "SPDR S&P Biotech ETF", "er": "0.35%", "aum": "$7.7B", "d": "等權重生技含小型股"},
        {"t": "ARKG", "n": "ARK Genomic Revolution ETF", "er": "0.75%", "aum": "$1.5B", "d": "ARK 基因體革命主動管理"},
        {"t": "FBT", "n": "First Trust NYSE Arca Biotech", "er": "0.55%", "aum": "$1.1B", "d": "30 檔生技精選"},
        {"t": "BBH", "n": "VanEck Biotech ETF", "er": "0.35%", "aum": "$365M", "d": "前 25 大生技藍籌股"},
        {"t": "IBBQ", "n": "Invesco Nasdaq Biotechnology ETF", "er": "0.19%", "aum": "$100M", "d": "最低費用生技 ETF"},
    ]},
    {"cat": "廣泛醫療", "color": "#fca5a5", "etfs": [
        {"t": "XLV", "n": "Health Care Select Sector SPDR", "er": "0.08%", "aum": "$38.8B", "d": "最大醫療 ETF 含 LLY / UNH / JNJ"},
        {"t": "VHT", "n": "Vanguard Health Care ETF", "er": "0.09%", "aum": "$16.2B", "d": "400+ 持股廣泛美國醫療"},
        {"t": "IHI", "n": "iShares U.S. Medical Devices ETF", "er": "0.39%", "aum": "$4B", "d": "美國醫療器材公司"},
        {"t": "IXJ", "n": "iShares Global Healthcare ETF", "er": "0.40%", "aum": "$3.6B", "d": "全球醫療創新企業"},
    ]},
]


def build_html(data: dict, analysis: dict | None = None) -> str:
    data_json = json.dumps(data, ensure_ascii=False)
    catalog_json = json.dumps(ETF_CATALOG, ensure_ascii=False)
    analysis_json = json.dumps(analysis or {"etfs": []}, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ETF 投資組合儀表板</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root {{
  --bg: #111119; --surface: #1a1a24; --surface2: #22222e;
  --border: #2a2a36; --text: #e2e0dc; --text2: #9ca3af;
  --text3: #6b7280; --accent: #fbbf24;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--text); font-family:'Segoe UI',system-ui,-apple-system,sans-serif; line-height:1.6; }}
.container {{ max-width:1100px; margin:0 auto; padding:24px 20px 60px; }}
h1 {{ font-size:28px; font-weight:300; margin-bottom:4px; color:#f5f5f0; }}
.subtitle {{ font-size:14px; color:var(--text2); margin-bottom:24px; }}
.tag {{ display:inline-block; padding:3px 10px; background:#2563eb22; border:1px solid #2563eb44; border-radius:4px; font-size:11px; font-weight:600; color:#60a5fa; letter-spacing:1px; text-transform:uppercase; margin-bottom:12px; }}

/* Tabs */
.tabs {{ display:flex; gap:2px; margin-bottom:20px; border-bottom:1px solid var(--border); flex-wrap:wrap; }}
.tab {{ padding:10px 16px; cursor:pointer; font-size:13px; font-weight:500; color:var(--text2); border-bottom:2px solid transparent; transition:all 0.2s; background:none; border-top:none; border-left:none; border-right:none; white-space:nowrap; }}
.tab:hover {{ color:var(--text); }}
.tab.active {{ color:var(--accent); border-bottom-color:var(--accent); }}
.tab-content {{ display:none; }}
.tab-content.active {{ display:block; }}

/* Cards */
.card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:20px; margin-bottom:16px; }}
.card h2 {{ font-size:18px; font-weight:500; margin-bottom:14px; color:#f5f5f0; }}
.card h3 {{ font-size:15px; font-weight:500; margin-bottom:10px; color:#f5f5f0; }}

/* Table */
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th {{ text-align:left; padding:8px 10px; color:var(--text3); font-weight:600; font-size:11px; text-transform:uppercase; letter-spacing:0.5px; border-bottom:1px solid var(--border); cursor:pointer; user-select:none; white-space:nowrap; }}
th:hover {{ color:var(--text); }}
th .sort-icon {{ font-size:10px; margin-left:3px; opacity:0.5; }}
td {{ padding:10px; border-bottom:1px solid var(--border); }}
tr:hover {{ background:var(--surface2); }}
.mono {{ font-family:'Cascadia Code','Fira Code',monospace; }}
.right {{ text-align:right; }}
.ticker {{ font-weight:700; font-size:14px; }}
.positive {{ color:#34d399; }}
.negative {{ color:#ef4444; }}

/* Alloc */
.alloc-header {{ display:flex; align-items:baseline; gap:16px; flex-wrap:wrap; margin-bottom:16px; }}
.alloc-input {{ display:flex; align-items:center; gap:8px; }}
.alloc-input label {{ font-size:14px; color:var(--text2); }}
.alloc-input input {{ width:120px; padding:8px 12px; background:var(--surface2); border:1px solid var(--border); border-radius:6px; color:var(--text); font-size:16px; font-weight:600; text-align:right; }}
.alloc-input input:focus {{ outline:none; border-color:var(--accent); }}

/* ETF Info Cards */
.etf-grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(320px, 1fr)); gap:12px; }}
.etf-card {{ background:var(--surface2); border:1px solid var(--border); border-radius:10px; padding:16px; transition:all 0.2s; }}
.etf-card:hover {{ border-color:var(--text3); transform:translateY(-1px); }}
.etf-card .cat {{ font-size:10px; font-weight:600; letter-spacing:0.5px; text-transform:uppercase; margin-bottom:4px; }}
.etf-card .desc {{ font-size:12px; color:var(--text2); line-height:1.5; margin-top:8px; }}
.etf-card .stats {{ display:flex; gap:16px; margin-top:10px; flex-wrap:wrap; }}
.etf-card .stat-label {{ font-size:10px; color:var(--text3); text-transform:uppercase; letter-spacing:0.3px; }}
.etf-card .stat-value {{ font-size:14px; font-weight:600; font-family:'Cascadia Code','Fira Code',monospace; }}

/* Weight slider */
.weight-row {{ display:flex; align-items:center; gap:10px; padding:6px 0; }}
.weight-row .ticker-label {{ width:55px; font-weight:700; font-size:13px; flex-shrink:0; }}
.weight-row input[type=range] {{ flex:1; accent-color:var(--accent); }}
.weight-row .weight-val {{ width:42px; text-align:right; font-family:'Cascadia Code','Fira Code',monospace; font-size:13px; }}

/* Chart */
.chart-box {{ width:100%; min-height:400px; }}

/* Pills */
.pills {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:16px; }}
.pill {{ padding:6px 14px; border-radius:20px; font-size:12px; font-weight:600; }}

/* Filter bar */
.filter-bar {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:16px; align-items:center; }}
.filter-bar input[type=text] {{ flex:1; min-width:180px; padding:8px 14px; background:var(--surface2); border:1px solid var(--border); border-radius:8px; color:var(--text); font-size:13px; }}
.filter-bar input:focus {{ outline:none; border-color:var(--accent); }}
.cat-chip {{ padding:5px 12px; border-radius:16px; font-size:11px; font-weight:600; cursor:pointer; border:1px solid var(--border); background:var(--surface2); color:var(--text2); transition:all 0.15s; white-space:nowrap; }}
.cat-chip:hover {{ border-color:var(--text3); }}
.cat-chip.active {{ background:var(--accent); color:#111; border-color:var(--accent); }}

/* Guide section */
.guide-grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(300px, 1fr)); gap:14px; }}
.guide-card {{ background:var(--surface2); border:1px solid var(--border); border-radius:10px; padding:18px; }}
.guide-card h4 {{ font-size:14px; font-weight:600; margin-bottom:10px; }}
.guide-item {{ display:flex; gap:10px; padding:8px 0; border-bottom:1px solid var(--border); }}
.guide-item:last-child {{ border-bottom:none; }}
.guide-item .label {{ font-size:12px; font-weight:600; color:var(--text); min-width:100px; flex-shrink:0; }}
.guide-item .info {{ font-size:12px; color:var(--text2); }}
.guide-tip {{ margin-top:8px; padding:10px 14px; background:#fbbf2410; border:1px solid #fbbf2425; border-radius:8px; font-size:12px; color:var(--text2); }}
.guide-tip strong {{ color:var(--accent); }}

/* AUM bar */
.aum-bar {{ display:inline-block; height:6px; border-radius:3px; margin-right:6px; vertical-align:middle; }}

@media (max-width:700px) {{
  .etf-grid, .guide-grid {{ grid-template-columns:1fr; }}
  .alloc-header {{ flex-direction:column; }}
  .tabs {{ gap:0; }}
  .tab {{ padding:8px 10px; font-size:12px; }}
}}
</style>
</head>
<body>
<div class="container">
  <div class="tag">穩健型 &middot; 長期持有 &middot; {data['generatedAt'][:10]}</div>
  <h1>ETF 主題投資組合儀表板</h1>
  <p class="subtitle">核心 + 衛星策略 &mdash; 9 檔 ETF 涵蓋 AI、電力、GLP-1 三大主題</p>

  <div class="tabs" id="tab-bar"></div>

  <!-- TAB: Allocation -->
  <div id="tab-alloc" class="tab-content active">
    <div class="card">
      <div class="alloc-header">
        <h2>投資金額配置</h2>
        <div class="alloc-input">
          <label>投入金額</label>
          <input type="number" id="totalUsd" value="30000" min="1000" step="1000" onchange="recalcAlloc()">
          <span style="font-size:14px;color:var(--text2)">USD</span>
        </div>
      </div>
      <div id="weight-sliders" style="margin-bottom:20px;"></div>
      <div id="weight-total" style="font-size:13px;color:var(--text2);margin-bottom:16px;"></div>
      <table>
        <thead><tr>
          <th>代碼</th><th>名稱</th><th class="right">權重</th>
          <th class="right">金額</th><th class="right">現價</th>
          <th class="right">股數</th><th class="right">實際</th>
        </tr></thead>
        <tbody id="alloc-tbody"></tbody>
        <tfoot id="alloc-tfoot"></tfoot>
      </table>
    </div>
  </div>

  <!-- TAB: Performance -->
  <div id="tab-perf" class="tab-content">
    <div class="card">
      <h2>過去一年績效</h2>
      <div class="pills" id="perf-pills"></div>
      <div id="chart-perf" class="chart-box"></div>
    </div>
    <div class="card">
      <h3>回撤比較</h3>
      <div id="chart-dd" class="chart-box" style="min-height:300px;"></div>
    </div>
    <div class="card">
      <h3>月度報酬</h3>
      <div id="chart-monthly" class="chart-box" style="min-height:350px;"></div>
    </div>
  </div>

  <!-- TAB: PE -->
  <div id="tab-pe" class="tab-content">
    <div class="card">
      <h2>本益比 (P/E) 趨勢</h2>
      <p style="font-size:12px;color:var(--text3);margin-bottom:14px;">基於當前 trailing P/E 與歷史價格反推。假設短期內盈餘相對穩定。</p>
      <div id="chart-pe" class="chart-box"></div>
    </div>
    <div class="card">
      <h3>本益比摘要</h3>
      <table>
        <thead><tr><th>代碼</th><th class="right">一年前</th><th class="right">現在</th><th class="right">最低</th><th class="right">最高</th><th class="right">變化</th></tr></thead>
        <tbody id="pe-tbody"></tbody>
      </table>
    </div>
  </div>

  <!-- TAB: My ETFs -->
  <div id="tab-etfs" class="tab-content">
    <div class="card">
      <h2>我的組合 ETF</h2>
      <div class="etf-grid" id="etf-grid"></div>
    </div>
  </div>

  <!-- TAB: Guide -->
  <div id="tab-guide" class="tab-content">
    <div class="card">
      <h2>ETF 選股指南</h2>
      <p style="font-size:13px;color:var(--text2);margin-bottom:20px;">投資 ETF 不能只看報酬率。以下是你應該關注的核心指標，分為三大面向。</p>
    </div>

    <div class="guide-grid">
      <div class="guide-card">
        <h4 style="color:#2563eb;">基本面指標</h4>
        <div class="guide-item"><span class="label">費用率</span><span class="info">每年從淨值扣除的管理費。核心 ETF 應 &lt;0.20%，衛星可接受 &lt;0.70%。</span></div>
        <div class="guide-item"><span class="label">追蹤誤差</span><span class="info">ETF 報酬與標的指數的偏差程度。越低代表 ETF 越忠實追蹤指數。</span></div>
        <div class="guide-item"><span class="label">本益比 (P/E)</span><span class="info">持股的平均本益比。越高代表市場對未來成長預期越高，但也越貴。</span></div>
        <div class="guide-item"><span class="label">股價淨值比 (P/B)</span><span class="info">持股價格 / 帳面價值。適合評估金融、價值型 ETF。</span></div>
        <div class="guide-item"><span class="label">殖利率</span><span class="info">年化配息 / 股價。適合追求現金流的投資人。公用事業 ETF 通常 &gt;2%。</span></div>
        <div class="guide-item"><span class="label">盈餘成長率</span><span class="info">持股的預估盈餘成長。高成長 ETF (如 SMH) 通常 &gt;15%。</span></div>
        <div class="guide-tip"><strong>重點：</strong>費用率和本益比是最直觀的兩個指標。費用率是確定的成本，本益比反映市場情緒。</div>
      </div>

      <div class="guide-card">
        <h4 style="color:#8b5cf6;">結構性指標</h4>
        <div class="guide-item"><span class="label">AUM (規模)</span><span class="info">管理資產規模。&lt;$50M 有流動性和下市風險，建議 &gt;$200M。</span></div>
        <div class="guide-item"><span class="label">日均成交量</span><span class="info">每日平均交易量。低成交量 = 買賣價差大，交易成本高。</span></div>
        <div class="guide-item"><span class="label">買賣價差</span><span class="info">買價和賣價的差距。流動性差的 ETF 可能 &gt;0.5%，每次交易都付一次。</span></div>
        <div class="guide-item"><span class="label">持股數量</span><span class="info">ETF 持有幾檔股票。越多越分散，但也越難跑贏大盤。</span></div>
        <div class="guide-item"><span class="label">前十大集中度</span><span class="info">前10大持股占比。SMH 前10佔 ~70%，風險集中。</span></div>
        <div class="guide-item"><span class="label">成立日期</span><span class="info">太新的 ETF (&lt;2年) 缺乏歷史數據驗證表現。</span></div>
        <div class="guide-tip"><strong>重點：</strong>AUM 和成交量決定了你的「隱性成本」。低 AUM 的 ETF 買賣價差可能比費用率影響更大。</div>
      </div>

      <div class="guide-card">
        <h4 style="color:#ef4444;">風險指標</h4>
        <div class="guide-item"><span class="label">最大回撤 (MDD)</span><span class="info">從高點到低點的最大跌幅。衡量最壞情況下你會虧多少。</span></div>
        <div class="guide-item"><span class="label">波動率 (Std)</span><span class="info">報酬的波動幅度。高波動 = 高風險，心理壓力大。</span></div>
        <div class="guide-item"><span class="label">Beta</span><span class="info">相對大盤的波動倍數。Beta &gt;1 漲跌都比大盤劇烈。SMH 的 Beta ~1.5。</span></div>
        <div class="guide-item"><span class="label">夏普比率</span><span class="info">(報酬 - 無風險利率) / 波動率。衡量每單位風險的報酬，越高越好。</span></div>
        <div class="guide-item"><span class="label">Sortino Ratio</span><span class="info">只看下行風險。比夏普更精確，不懲罰上行波動。</span></div>
        <div class="guide-tip"><strong>重點：</strong>夏普比率是風險調整後報酬的黃金標準。高報酬但夏普低，代表你承擔了不成比例的風險。</div>
      </div>
    </div>

    <div class="card" style="margin-top:16px;">
      <h3>費用率對長期獲利的影響</h3>
      <p style="font-size:12px;color:var(--text2);margin-bottom:12px;">假設投入 $30,000，年化報酬 10%，持有 20 年：</p>
      <div id="chart-expense" class="chart-box" style="min-height:300px;"></div>
      <div class="guide-tip" style="margin-top:12px;">
        <strong>結論：</strong>0.03% vs 0.68% 的費用率差距，20 年後少賺約 $22,000。但主題 ETF 若能提供超額報酬（如 SMH 去年 +118%），費用率差距就不那麼重要了。<br>
        <strong>真正的隱性成本是買賣價差</strong> &mdash; 低 AUM 的 OZEM 每次交易可能吃掉 0.3-0.5%，比年費影響更大。
      </div>
    </div>

    <div class="card">
      <h3>篩選建議門檻</h3>
      <table>
        <thead><tr><th>指標</th><th>建議門檻</th><th>原因</th></tr></thead>
        <tbody>
          <tr><td style="font-weight:600;">AUM</td><td class="mono">&gt; $200M</td><td style="color:var(--text2);">避免流動性風險和下市風險</td></tr>
          <tr><td style="font-weight:600;">費用率（核心）</td><td class="mono">&lt; 0.20%</td><td style="color:var(--text2);">長期複利成本必須極低</td></tr>
          <tr><td style="font-weight:600;">費用率（衛星）</td><td class="mono">&lt; 0.70%</td><td style="color:var(--text2);">主題溢價可接受但有上限</td></tr>
          <tr><td style="font-weight:600;">日均成交量</td><td class="mono">&gt; 10 萬股</td><td style="color:var(--text2);">確保買賣價差夠小</td></tr>
          <tr><td style="font-weight:600;">前十大集中度</td><td class="mono">&lt; 60%</td><td style="color:var(--text2);">除非你刻意集中押注</td></tr>
          <tr><td style="font-weight:600;">成立年限</td><td class="mono">&gt; 2 年</td><td style="color:var(--text2);">有足夠歷史資料驗證</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- TAB: Explore -->
  <div id="tab-explore" class="tab-content">
    <div class="card">
      <h2>ETF 完整分析</h2>
      <p style="font-size:12px;color:var(--text2);margin-bottom:14px;">共 <span id="etf-count"></span> 檔 ETF，含即時指標分析。點擊類別篩選，點擊欄位標題排序。紅色標記 = 未達建議門檻。</p>
      <div class="filter-bar">
        <input type="text" id="etf-search" placeholder="搜尋代碼或名稱..." oninput="renderCatalog()">
      </div>
      <div class="filter-bar" id="cat-chips"></div>
      <div class="pills" style="margin-top:8px;">
        <div class="pill" style="background:#34d39918;border:1px solid #34d39933;font-size:11px;"><span style="color:#34d399;">&#9679;</span> <span style="color:var(--text2);">達標</span></div>
        <div class="pill" style="background:#ef444418;border:1px solid #ef444433;font-size:11px;"><span style="color:#ef4444;">&#9679;</span> <span style="color:var(--text2);">警示</span></div>
        <div class="pill" style="background:var(--surface2);border:1px solid var(--border);font-size:11px;cursor:pointer;" onclick="toggleView()"><span id="view-label">切換卡片檢視</span></div>
      </div>
    </div>
    <div id="catalog-container"></div>
    <div id="etf-detail-modal" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.7);z-index:999;overflow-y:auto;padding:40px 20px;" onclick="if(event.target===this)closeDetail()">
      <div id="etf-detail-content" style="max-width:700px;margin:0 auto;background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:28px;"></div>
    </div>
  </div>
</div>

<script>
const DATA = {data_json};
const CATALOG = {catalog_json};
const ANALYSIS = {analysis_json};

const TABS = [
  {{id:'tab-alloc', label:'配置計算'}},
  {{id:'tab-perf', label:'績效分析'}},
  {{id:'tab-pe', label:'本益比'}},
  {{id:'tab-etfs', label:'我的 ETF'}},
  {{id:'tab-guide', label:'選股指南'}},
  {{id:'tab-explore', label:'ETF 探索'}},
];

const allItems = DATA.portfolio.flatMap(g => g.items);
let weights = {{}};
allItems.forEach(it => weights[it.ticker] = it.weight);

// ---- Tabs ----
function initTabs() {{
  const bar = document.getElementById('tab-bar');
  bar.innerHTML = TABS.map((t,i) =>
    `<button class="tab ${{i===0?'active':''}}" onclick="switchTab('${{t.id}}')">${{t.label}}</button>`
  ).join('');
}}

function switchTab(id) {{
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  const idx = TABS.findIndex(t => t.id === id);
  document.querySelectorAll('.tab')[idx].classList.add('active');
  if (id === 'tab-perf' && !window._p1) {{ renderPerf(); window._p1 = true; }}
  if (id === 'tab-pe' && !window._p2) {{ renderPE(); window._p2 = true; }}
  if (id === 'tab-etfs' && !window._p3) {{ renderETFs(); window._p3 = true; }}
  if (id === 'tab-guide' && !window._p4) {{ renderExpenseChart(); window._p4 = true; }}
  if (id === 'tab-explore' && !window._p5) {{ initCatalog(); window._p5 = true; }}
}}

// ---- Allocation ----
function buildSliders() {{
  const c = document.getElementById('weight-sliders');
  let h = '';
  DATA.portfolio.forEach(g => {{
    h += `<div style="font-size:10px;font-weight:600;color:${{g.color}};letter-spacing:0.8px;text-transform:uppercase;margin:10px 0 4px;padding-left:2px;">${{g.categoryZh}}</div>`;
    g.items.forEach(it => {{
      h += `<div class="weight-row">
        <span class="ticker-label" style="color:${{it.color}}">${{it.ticker}}</span>
        <input type="range" min="0" max="50" value="${{it.weight}}" id="slider-${{it.ticker}}" oninput="onSlider('${{it.ticker}}',this.value)">
        <span class="weight-val" id="wval-${{it.ticker}}">${{it.weight}}%</span>
      </div>`;
    }});
  }});
  c.innerHTML = h;
}}

function onSlider(t, v) {{ weights[t]=parseInt(v); document.getElementById('wval-'+t).textContent=v+'%'; recalcAlloc(); }}

function recalcAlloc() {{
  const total = parseFloat(document.getElementById('totalUsd').value)||30000;
  const tbody = document.getElementById('alloc-tbody');
  const tfoot = document.getElementById('alloc-tfoot');
  const sumW = Object.values(weights).reduce((a,b)=>a+b,0);
  document.getElementById('weight-total').innerHTML = `權重合計: <strong style="color:${{sumW===100?'#34d399':'#ef4444'}}">${{sumW}}%</strong> ${{sumW!==100?'(建議 100%)':''}}`;

  let rows='', totalActual=0;
  DATA.portfolio.forEach(g => {{
    g.items.forEach(it => {{
      const w=weights[it.ticker], amt=total*w/100, pr=DATA.currentPrices[it.ticker];
      const sh=Math.floor(amt/pr), act=sh*pr;
      totalActual+=act;
      rows+=`<tr>
        <td class="ticker" style="color:${{it.color}}">${{it.ticker}}</td>
        <td style="font-size:12px;">${{it.nameZh}}</td>
        <td class="right mono">${{w}}%</td>
        <td class="right mono">$${{amt.toLocaleString('en-US',{{minimumFractionDigits:0}})}}</td>
        <td class="right mono">$${{pr.toFixed(2)}}</td>
        <td class="right mono">${{sh}}</td>
        <td class="right mono">$${{act.toLocaleString('en-US',{{minimumFractionDigits:0}})}}</td>
      </tr>`;
    }});
  }});
  const rem=total-totalActual;
  rows+=`<tr style="background:var(--surface2);"><td colspan="3" style="font-weight:600;">餘額現金</td><td colspan="4" class="right mono" style="font-weight:600;color:var(--accent);">$${{rem.toLocaleString('en-US',{{minimumFractionDigits:0}})}}</td></tr>`;
  tbody.innerHTML=rows;
  tfoot.innerHTML=`<tr style="border-top:2px solid var(--border);"><td colspan="3" style="font-weight:700;">合計</td><td class="right mono" style="font-weight:700;">$${{total.toLocaleString('en-US')}}</td><td></td><td></td><td class="right mono" style="font-weight:700;">$${{totalActual.toLocaleString('en-US',{{minimumFractionDigits:0}})}}</td></tr>`;
}}

// ---- Performance ----
function renderPerf() {{
  const ph=DATA.priceHistory, ps=DATA.portfolioSeries;
  const traces=[];
  allItems.forEach(it => {{
    const cl=ph[it.ticker].closes, base=cl[0];
    traces.push({{x:ph[it.ticker].dates, y:cl.map(c=>(c/base)*100), name:`${{it.ticker}} (${{weights[it.ticker]}}%)`, line:{{color:it.color,width:1.5}}, hovertemplate:`${{it.ticker}}: %{{y:.1f}}<extra></extra>`}});
  }});
  traces.push({{x:ps.dates, y:ps.values, name:'加權組合', line:{{color:'#fbbf24',width:3}}, hovertemplate:'組合: %{{y:.2f}}<extra></extra>'}});
  const lo = {{title:'累積報酬 (基準=100)',template:'plotly_dark',height:450,hovermode:'x unified',legend:{{orientation:'h',y:1.12,font:{{size:10}}}},margin:{{t:60,b:40,l:50,r:20}},paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)'}};
  Plotly.newPlot('chart-perf',traces,lo,{{responsive:true}});

  const portN=ps.values; let pk=portN[0];
  const portDD=portN.map(v=>{{pk=Math.max(pk,v);return((v-pk)/pk)*100;}});
  const vC=ph['VOO'].closes, vB=vC[0], vN=vC.map(c=>(c/vB)*100); let vP=vN[0];
  const vDD=vN.map(v=>{{vP=Math.max(vP,v);return((v-vP)/vP)*100;}});
  Plotly.newPlot('chart-dd',[
    {{x:ps.dates,y:portDD,name:'組合',fill:'tozeroy',line:{{color:'#fbbf24',width:1}},hovertemplate:'組合: %{{y:.2f}}%<extra></extra>'}},
    {{x:ph['VOO'].dates,y:vDD,name:'VOO',fill:'tozeroy',line:{{color:'#6b7280',width:1,dash:'dot'}},hovertemplate:'VOO: %{{y:.2f}}%<extra></extra>'}}
  ],{{title:'回撤 (%)',template:'plotly_dark',height:300,hovermode:'x unified',legend:{{orientation:'h',y:1.15,font:{{size:10}}}},margin:{{t:50,b:40,l:50,r:20}},paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)'}},{{responsive:true}});

  const mC=['#fbbf24','#2563eb','#8b5cf6','#10b981','#ef4444'], mT=['VOO','QQQM','SMH','GRID','OZEM'];
  const mTraces=mT.map((t,i)=>{{const mr=DATA.monthlyReturns[t];return mr?{{x:mr.months,y:mr.returns,name:t,type:'bar',marker:{{color:mC[i]}},hovertemplate:`${{t}}: %{{y:+.2f}}%<extra></extra>`}}:null;}}).filter(Boolean);
  Plotly.newPlot('chart-monthly',mTraces,{{title:'月度報酬 (%)',template:'plotly_dark',barmode:'group',height:350,hovermode:'x unified',legend:{{orientation:'h',y:1.12,font:{{size:10}}}},margin:{{t:50,b:40,l:50,r:20}},paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)'}},{{responsive:true}});

  const pR=ps.values[ps.values.length-1]-100, pM=Math.min(...portDD);
  const vR=vN[vN.length-1]-100, vM=Math.min(...vDD);
  document.getElementById('perf-pills').innerHTML=`
    <div class="pill" style="background:#fbbf2418;border:1px solid #fbbf2433;"><span style="color:#fbbf24">${{pR>=0?'+':''}}${{pR.toFixed(2)}}%</span> <span style="color:var(--text2);margin-left:4px;">組合報酬</span></div>
    <div class="pill" style="background:#6b728018;border:1px solid #6b728033;"><span style="color:#9ca3af">${{vR>=0?'+':''}}${{vR.toFixed(2)}}%</span> <span style="color:var(--text2);margin-left:4px;">VOO 基準</span></div>
    <div class="pill" style="background:#ef444418;border:1px solid #ef444433;"><span style="color:#ef4444">${{pM.toFixed(2)}}%</span> <span style="color:var(--text2);margin-left:4px;">最大回撤</span></div>`;
}}

// ---- PE ----
function renderPE() {{
  const traces=[], summary=[];
  allItems.forEach(it => {{
    const pe=DATA.peRatios[it.ticker]; if(!pe) return;
    const ph=DATA.priceHistory[it.ticker], cp=ph.closes[ph.closes.length-1];
    const est=ph.closes.map(c=>c*pe/cp);
    traces.push({{x:ph.dates,y:est,name:it.ticker,line:{{color:it.color,width:1.5}},hovertemplate:`${{it.ticker}}: %{{y:.1f}}x<extra></extra>`}});
    summary.push({{t:it.ticker,c:it.color,s:est[0],e:est[est.length-1],lo:Math.min(...est),hi:Math.max(...est)}});
  }});
  Plotly.newPlot('chart-pe',traces,{{title:'估計 Trailing P/E (一年)',template:'plotly_dark',height:450,hovermode:'x unified',legend:{{orientation:'h',y:1.12,font:{{size:10}}}},margin:{{t:60,b:40,l:50,r:20}},paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',yaxis:{{title:'P/E 倍數'}}}},{{responsive:true}});
  document.getElementById('pe-tbody').innerHTML=summary.map(p=>{{
    const ch=((p.e-p.s)/p.s*100),cls=ch>=0?'positive':'negative';
    return`<tr><td class="ticker" style="color:${{p.c}}">${{p.t}}</td><td class="right mono">${{p.s.toFixed(1)}}x</td><td class="right mono">${{p.e.toFixed(1)}}x</td><td class="right mono">${{p.lo.toFixed(1)}}x</td><td class="right mono">${{p.hi.toFixed(1)}}x</td><td class="right mono ${{cls}}">${{ch>=0?'+':''}}${{ch.toFixed(1)}}%</td></tr>`;
  }}).join('');
}}

// ---- My ETFs ----
function renderETFs() {{
  const grid=document.getElementById('etf-grid');
  let h='';
  DATA.portfolio.forEach(g => {{
    g.items.forEach(it => {{
      const pr=DATA.currentPrices[it.ticker], pe=DATA.peRatios[it.ticker];
      const cl=DATA.priceHistory[it.ticker].closes, ret=((cl[cl.length-1]-cl[0])/cl[0]*100);
      h+=`<div class="etf-card">
        <div class="cat" style="color:${{g.color}}">${{g.categoryZh}}</div>
        <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px;">
          <span class="ticker" style="color:${{it.color}};font-size:20px;">${{it.ticker}}</span>
          <span class="mono" style="font-size:18px;font-weight:700;">$${{pr.toFixed(2)}}</span>
        </div>
        <div style="font-size:12px;color:var(--text2);">${{it.nameZh}}</div>
        <div class="desc">${{it.desc}}</div>
        <div class="stats">
          <div><div class="stat-label">權重</div><div class="stat-value" style="color:${{it.color}}">${{it.weight}}%</div></div>
          <div><div class="stat-label">費用率</div><div class="stat-value">${{it.expense}}</div></div>
          <div><div class="stat-label">P/E</div><div class="stat-value">${{pe?pe.toFixed(1)+'x':'N/A'}}</div></div>
          <div><div class="stat-label">一年報酬</div><div class="stat-value ${{ret>=0?'positive':'negative'}}">${{ret>=0?'+':''}}${{ret.toFixed(1)}}%</div></div>
        </div>
      </div>`;
    }});
  }});
  grid.innerHTML=h;
}}

// ---- Expense Chart ----
function renderExpenseChart() {{
  const base=30000, rate=0.10, years=20;
  const ers=[{{l:'0.03% (VOO)',v:0.0003,c:'#2563eb'}},{{l:'0.15% (QQQM)',v:0.0015,c:'#3b82f6'}},{{l:'0.35% (SMH)',v:0.0035,c:'#8b5cf6'}},{{l:'0.56% (GRID)',v:0.0056,c:'#10b981'}},{{l:'0.68% (AIQ)',v:0.0068,c:'#a78bfa'}}];
  const traces=ers.map(e=>{{
    const ys=[]; for(let y=0;y<=years;y++) ys.push(Math.round(base*Math.pow(1+rate-e.v,y)));
    return{{x:Array.from({{length:years+1}},(_,i)=>i),y:ys,name:e.l,line:{{color:e.c,width:2}},hovertemplate:`${{e.l}}: $%{{y:,.0f}}<extra></extra>`}};
  }});
  Plotly.newPlot('chart-expense',traces,{{
    title:'費用率對 $30,000 投資的 20 年影響 (年化 10%)',template:'plotly_dark',
    height:300,hovermode:'x unified',
    legend:{{orientation:'h',y:1.15,font:{{size:10}}}},
    margin:{{t:60,b:40,l:60,r:20}},
    paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',
    xaxis:{{title:'年'}},yaxis:{{title:'USD',tickformat:'$,.0f'}}
  }},{{responsive:true}});
}}

// ---- Catalog (Analysis-powered) ----
let activeCats = new Set();
let sortKey = 'sharpe';
let sortAsc = false;
let viewMode = 'table'; // 'table' or 'card'

const analysisMap = {{}};
(ANALYSIS.etfs||[]).forEach(e => analysisMap[e.ticker] = e);

function parseAUM(s) {{
  if(!s) return 0;
  const m = s.replace('$','').replace(/,/g,'');
  if(m.endsWith('B')) return parseFloat(m)*1e9;
  if(m.endsWith('M')) return parseFloat(m)*1e6;
  return parseFloat(m)||0;
}}
function parseER(s) {{ return parseFloat((s||'').replace('%',''))||0; }}
function fmt(v,d=1) {{ return v!=null ? v.toFixed(d) : '-'; }}
function fmtPct(v,d=1) {{ return v!=null ? (v>=0?'+':'')+v.toFixed(d)+'%' : '-'; }}
function fmtVol(v) {{
  if(!v) return '-';
  if(v>=1e6) return (v/1e6).toFixed(1)+'M';
  if(v>=1e3) return (v/1e3).toFixed(0)+'K';
  return v.toString();
}}
function clsPct(v) {{ return v!=null ? (v>=0?'positive':'negative') : ''; }}

function toggleView() {{
  viewMode = viewMode==='table'?'card':'table';
  document.getElementById('view-label').textContent = viewMode==='table'?'切換卡片檢視':'切換表格檢視';
  renderCatalog();
}}

function initCatalog() {{
  const cats = [...new Set(CATALOG.map(c=>c.cat))];
  const chips = document.getElementById('cat-chips');
  chips.innerHTML = `<span class="cat-chip active" onclick="toggleCat('all')">全部</span>` +
    cats.map(c=>`<span class="cat-chip" data-cat="${{c}}" onclick="toggleCat('${{c}}')">${{c}}</span>`).join('');
  document.getElementById('etf-count').textContent = ANALYSIS.etfs.length;
  renderCatalog();
}}

function toggleCat(cat) {{
  if(cat==='all') {{
    activeCats.clear();
    document.querySelectorAll('.cat-chip').forEach(el=>el.classList.remove('active'));
    document.querySelector('.cat-chip').classList.add('active');
  }} else {{
    document.querySelector('.cat-chip:first-child').classList.remove('active');
    const chip=document.querySelector(`.cat-chip[data-cat="${{cat}}"]`);
    if(activeCats.has(cat)) {{ activeCats.delete(cat); chip.classList.remove('active'); }}
    else {{ activeCats.add(cat); chip.classList.add('active'); }}
    if(activeCats.size===0) document.querySelector('.cat-chip:first-child').classList.add('active');
  }}
  renderCatalog();
}}

function sortCatalog(key) {{
  if(sortKey===key) sortAsc=!sortAsc; else {{ sortKey=key; sortAsc=(key==='ticker'); }}
  renderCatalog();
}}

function showDetail(ticker) {{
  const e = analysisMap[ticker]; if(!e) return;
  const modal = document.getElementById('etf-detail-modal');
  const content = document.getElementById('etf-detail-content');
  const erNum = parseER(e.expenseRatio);
  const aumNum = parseAUM(e.aumText);

  // Sparkline SVG
  const sp = e.sparkline||[];
  let sparkSvg = '';
  if(sp.length>2) {{
    const mn=Math.min(...sp), mx=Math.max(...sp), rng=mx-mn||1;
    const pts=sp.map((v,i)=>`${{(i/(sp.length-1))*200}},${{40-(v-mn)/rng*36}}`).join(' ');
    sparkSvg=`<svg viewBox="0 0 200 44" style="width:100%;height:50px;margin:10px 0;"><polyline points="${{pts}}" fill="none" stroke="${{e.catColor}}" stroke-width="1.5"/></svg>`;
  }}

  const warn = (ok, txt) => `<span style="color:${{ok?'#34d399':'#ef4444'}}">&#9679;</span> ${{txt}}`;

  content.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;">
      <div>
        <span class="cat" style="color:${{e.catColor}};font-size:10px;font-weight:600;letter-spacing:0.5px;text-transform:uppercase;">${{e.cat}}</span>
        <div style="margin-top:4px;"><span style="font-size:28px;font-weight:700;color:${{e.catColor}};">${{e.ticker}}</span> <span style="font-size:14px;color:var(--text2);margin-left:8px;">${{e.name}}</span></div>
      </div>
      <span style="font-size:24px;font-weight:700;font-family:monospace;">$${{e.price}}</span>
    </div>
    <div style="font-size:13px;color:var(--text2);margin:8px 0;">${{e.desc}}</div>
    ${{sparkSvg}}
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:12px;margin:16px 0;">
      <div class="guide-card" style="padding:12px;">
        <div class="stat-label">一年報酬</div>
        <div class="stat-value ${{clsPct(e.ret1y)}}" style="font-size:18px;">${{fmtPct(e.ret1y)}}</div>
      </div>
      <div class="guide-card" style="padding:12px;">
        <div class="stat-label">六個月</div>
        <div class="stat-value ${{clsPct(e.ret6m)}}" style="font-size:18px;">${{fmtPct(e.ret6m)}}</div>
      </div>
      <div class="guide-card" style="padding:12px;">
        <div class="stat-label">三個月</div>
        <div class="stat-value ${{clsPct(e.ret3m)}}" style="font-size:18px;">${{fmtPct(e.ret3m)}}</div>
      </div>
      <div class="guide-card" style="padding:12px;">
        <div class="stat-label">夏普比率</div>
        <div class="stat-value" style="font-size:18px;color:${{e.sharpe>=1?'#34d399':e.sharpe>=0.5?'var(--text)':'#ef4444'}}">${{fmt(e.sharpe,2)}}</div>
      </div>
    </div>
    <h4 style="font-size:14px;margin:16px 0 10px;color:#f5f5f0;">基本面</h4>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">
      <div style="font-size:12px;">${{warn(erNum<=0.5, '費用率: '+e.expenseRatio)}}</div>
      <div style="font-size:12px;">P/E: <span class="mono">${{e.pe ? fmt(e.pe)+'x' : 'N/A'}}</span></div>
      <div style="font-size:12px;">P/B: <span class="mono">${{e.pb ? fmt(e.pb,2)+'x' : 'N/A'}}</span></div>
      <div style="font-size:12px;">殖利率: <span class="mono">${{e.divYield ? fmt(e.divYield)+'%' : 'N/A'}}</span></div>
    </div>
    <h4 style="font-size:14px;margin:16px 0 10px;color:#f5f5f0;">結構性</h4>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">
      <div style="font-size:12px;">${{warn(aumNum>=2e8, 'AUM: '+e.aumText)}}</div>
      <div style="font-size:12px;">${{warn(e.avgVolume>=100000, '日均量: '+fmtVol(e.avgVolume))}}</div>
    </div>
    <h4 style="font-size:14px;margin:16px 0 10px;color:#f5f5f0;">風險</h4>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">
      <div style="font-size:12px;">最大回撤: <span class="mono negative">${{fmt(e.maxDD)}}%</span></div>
      <div style="font-size:12px;">波動率: <span class="mono">${{fmt(e.volatility)}}%</span></div>
      <div style="font-size:12px;">Beta: <span class="mono">${{e.beta ? fmt(e.beta,2) : 'N/A'}}</span></div>
    </div>
    <button onclick="closeDetail()" style="margin-top:20px;padding:8px 20px;background:var(--surface2);border:1px solid var(--border);border-radius:8px;color:var(--text);cursor:pointer;font-size:13px;">關閉</button>
  `;
  modal.style.display='block';
}}
function closeDetail() {{ document.getElementById('etf-detail-modal').style.display='none'; }}

function renderCatalog() {{
  const q = (document.getElementById('etf-search')?.value||'').toLowerCase();
  let flat = ANALYSIS.etfs.filter(e => {{
    if(activeCats.size>0 && !activeCats.has(e.cat)) return false;
    if(q && !e.ticker.toLowerCase().includes(q) && !e.name.toLowerCase().includes(q) && !(e.desc||'').toLowerCase().includes(q)) return false;
    return true;
  }}).map(e => ({{...e, er_num:parseER(e.expenseRatio), aum_num:parseAUM(e.aumText)}}));

  flat.sort((a,b) => {{
    let va=a[sortKey]??-999, vb=b[sortKey]??-999;
    if(typeof va==='string') {{ va=va.toLowerCase(); vb=vb.toLowerCase(); }}
    return sortAsc ? (va<vb?-1:va>vb?1:0) : (va>vb?-1:va<vb?1:0);
  }});

  const arrow = (key) => sortKey===key ? (sortAsc?'&#9650;':'&#9660;') : '';
  let html = '';

  if(viewMode==='table') {{
    html = `<div class="card" style="overflow-x:auto;"><table>
      <thead><tr>
        <th onclick="sortCatalog('ticker')">代碼${{arrow('ticker')}}</th>
        <th>類別</th>
        <th class="right" onclick="sortCatalog('price')">現價${{arrow('price')}}</th>
        <th class="right" onclick="sortCatalog('ret1y')">1Y報酬${{arrow('ret1y')}}</th>
        <th class="right" onclick="sortCatalog('ret6m')">6M${{arrow('ret6m')}}</th>
        <th class="right" onclick="sortCatalog('sharpe')">夏普${{arrow('sharpe')}}</th>
        <th class="right" onclick="sortCatalog('maxDD')">回撤${{arrow('maxDD')}}</th>
        <th class="right" onclick="sortCatalog('volatility')">波動${{arrow('volatility')}}</th>
        <th class="right" onclick="sortCatalog('er_num')">費用${{arrow('er_num')}}</th>
        <th class="right" onclick="sortCatalog('pe')">P/E${{arrow('pe')}}</th>
      </tr></thead><tbody>`;
    flat.forEach(e => {{
      const erOk=e.er_num<=0.5, aumOk=e.aum_num>=2e8;
      html += `<tr style="cursor:pointer;" onclick="showDetail('${{e.ticker}}')">
        <td><span class="ticker" style="color:${{e.catColor}}">${{e.ticker}}</span>
          ${{!aumOk?'<span style=\"font-size:9px;color:#ef4444;margin-left:3px;\">低AUM</span>':''}}</td>
        <td style="font-size:11px;color:${{e.catColor}};white-space:nowrap;">${{e.cat}}</td>
        <td class="right mono">$${{e.price}}</td>
        <td class="right mono ${{clsPct(e.ret1y)}}">${{fmtPct(e.ret1y)}}</td>
        <td class="right mono ${{clsPct(e.ret6m)}}">${{fmtPct(e.ret6m)}}</td>
        <td class="right mono" style="color:${{e.sharpe>=1?'#34d399':e.sharpe>=0.5?'var(--text)':'#ef4444'}}">${{fmt(e.sharpe,2)}}</td>
        <td class="right mono negative">${{fmt(e.maxDD)}}%</td>
        <td class="right mono">${{fmt(e.volatility)}}%</td>
        <td class="right mono" style="color:${{erOk?'var(--text)':'#ef4444'}}">${{e.expenseRatio}}</td>
        <td class="right mono">${{e.pe ? fmt(e.pe)+'x' : '-'}}</td>
      </tr>`;
    }});
    html += '</tbody></table></div>';
  }} else {{
    html = '<div class="etf-grid">';
    flat.forEach(e => {{
      html += `<div class="etf-card" style="cursor:pointer;" onclick="showDetail('${{e.ticker}}')">
        <div class="cat" style="color:${{e.catColor}}">${{e.cat}}</div>
        <div style="display:flex;justify-content:space-between;align-items:baseline;">
          <span class="ticker" style="color:${{e.catColor}};font-size:18px;">${{e.ticker}}</span>
          <span class="mono" style="font-size:16px;font-weight:700;">$${{e.price}}</span>
        </div>
        <div style="font-size:11px;color:var(--text2);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${{e.name}}</div>
        <div class="stats" style="margin-top:10px;">
          <div><div class="stat-label">1Y 報酬</div><div class="stat-value ${{clsPct(e.ret1y)}}">${{fmtPct(e.ret1y)}}</div></div>
          <div><div class="stat-label">夏普</div><div class="stat-value" style="color:${{e.sharpe>=1?'#34d399':e.sharpe>=0.5?'var(--text)':'#ef4444'}}">${{fmt(e.sharpe,2)}}</div></div>
          <div><div class="stat-label">回撤</div><div class="stat-value negative">${{fmt(e.maxDD)}}%</div></div>
          <div><div class="stat-label">費用</div><div class="stat-value">${{e.expenseRatio}}</div></div>
        </div>
      </div>`;
    }});
    html += '</div>';
  }}

  document.getElementById('catalog-container').innerHTML = html;
  const countEl = document.getElementById('etf-count');
  if(countEl) countEl.textContent = flat.length;
}}

// ---- Init ----
initTabs();
buildSliders();
recalcAlloc();
</script>
</body>
</html>"""


def main() -> None:
    root = Path(__file__).parent
    data_path = root / "charts" / "dashboard_data.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))

    analysis_path = root / "charts" / "etf_analysis.json"
    analysis = None
    if analysis_path.exists():
        analysis = json.loads(analysis_path.read_text(encoding="utf-8"))

    html = build_html(data, analysis)

    out_path = root / "charts" / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"Dashboard saved to {out_path}")


if __name__ == "__main__":
    main()

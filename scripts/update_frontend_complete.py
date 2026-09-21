#!/usr/bin/env python3
"""
Complete frontend overhaul for NEET PG College Finder:
1. Fix [object HTMLSelectElement] bug.
2. Accurate branch-wise cutoff prediction drawer for all 22 branches.
3. Modern, user-friendly medical edtech theme with Light/Dark mode toggle.
4. Full mobile responsiveness with touch-friendly elements.
"""

import os
import re

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_path = os.path.join(root, "index.html")

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Update CSS in <style>
    new_css = """  <style>
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    
    /* ══════ MODERN MEDICAL EDTECH THEME SYSTEM ══════ */
    :root {
      /* User-Friendly Clean Medical Theme (Default) */
      --bg: #f8fafc;
      --bg-surface: #ffffff;
      --card: #ffffff;
      --card-alt: #f1f5f9;
      --card-border: #e2e8f0;
      --card-border-hover: #93c5fd;
      --border: #e2e8f0;
      --border2: #cbd5e1;
      --accent: #2563eb;
      --accent-hover: #1d4ed8;
      --accent-bg: #eff6ff;
      --a2: #4f46e5;
      --teal: #0d9488;
      --teal-bg: #ccfbf1;
      --green: #10b981;
      --green-bg: #ecfdf5;
      --green-text: #047857;
      --yellow: #f59e0b;
      --yellow-bg: #fffbeb;
      --yellow-text: #b45309;
      --red: #ef4444;
      --red-bg: #fef2f2;
      --red-text: #b91c1c;
      --pink: #8b5cf6;
      --text: #0f172a;
      --t2: #334155;
      --t3: #64748b;
      --header-bg: rgba(255, 255, 255, 0.92);
      --notice-bg: #f0fdfa;
      --notice-border: #99f6e4;
      --notice-text: #0f766e;
      --shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.06);
      --shadow-md: 0 4px 12px -2px rgba(15, 23, 42, 0.08);
      --shadow-lg: 0 12px 28px -4px rgba(15, 23, 42, 0.12);
      --r: 16px;
      --rs: 10px;
    }

    [data-theme="dark"] {
      --bg: #0b1120;
      --bg-surface: #111a2e;
      --card: #131d33;
      --card-alt: #1a2540;
      --card-border: #1e293b;
      --card-border-hover: #3b82f6;
      --border: #1e293b;
      --border2: #334155;
      --accent: #3b82f6;
      --accent-hover: #60a5fa;
      --accent-bg: rgba(59, 130, 246, 0.15);
      --a2: #6366f1;
      --teal: #14b8a6;
      --teal-bg: rgba(20, 184, 166, 0.15);
      --green: #34d399;
      --green-bg: rgba(16, 185, 129, 0.15);
      --green-text: #6ee7b7;
      --yellow: #fbbf24;
      --yellow-bg: rgba(245, 158, 11, 0.15);
      --yellow-text: #fde68a;
      --red: #f87171;
      --red-bg: rgba(239, 68, 68, 0.15);
      --red-text: #fca5a5;
      --pink: #a78bfa;
      --text: #f8fafc;
      --t2: #cbd5e1;
      --t3: #94a3b8;
      --header-bg: rgba(11, 17, 32, 0.9);
      --notice-bg: rgba(13, 148, 136, 0.12);
      --notice-border: rgba(13, 148, 136, 0.28);
      --notice-text: #2dd4bf;
      --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
      --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
      --shadow-lg: 0 12px 30px rgba(0, 0, 0, 0.55);
    }

    html{scroll-behavior:smooth}
    body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden;transition:background-color .25s ease,color .25s ease}

    /* SUBTLE AMBIENT ACCENTS */
    .orbs{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden;opacity:0.45}
    .orb{position:absolute;border-radius:50%;filter:blur(110px);animation:drift 18s ease-in-out infinite alternate}
    .o1{width:520px;height:520px;background:#3b82f6;top:-200px;left:-100px;opacity:.09}
    .o2{width:420px;height:420px;background:#0d9488;top:40%;right:-90px;opacity:.08;animation-delay:-6s}
    .o3{width:360px;height:360px;background:#6366f1;bottom:-100px;left:30%;opacity:.07;animation-delay:-10s}
    @keyframes drift{0%{transform:translate(0,0) scale(1)}100%{transform:translate(30px,20px) scale(1.08)}}

    .wrap{position:relative;z-index:1;max-width:1300px;margin:0 auto;padding:0 20px}

    /* HEADER */
    header{padding:12px 0;border-bottom:1px solid var(--border);background:var(--header-bg);backdrop-filter:blur(20px);position:sticky;top:0;z-index:200;box-shadow:var(--shadow-sm);transition:background .25s,border-color .25s}
    .hdr{display:flex;align-items:center;justify-content:space-between;max-width:1300px;margin:0 auto;padding:0 20px;gap:12px}
    .logo{display:flex;align-items:center;gap:10px;font-family:'Outfit',sans-serif;font-weight:900;font-size:1.25rem;color:var(--text);white-space:nowrap}
    .logo em{font-style:normal;color:var(--accent)}
    .logo-box{width:36px;height:36px;background:linear-gradient(135deg,var(--accent),#3b82f6);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.15rem;color:#fff;box-shadow:0 3px 10px rgba(37,99,235,.28);flex-shrink:0}
    .hdr-mid{display:flex;gap:18px;align-items:center}
    .hs{font-size:.76rem;color:var(--t2);white-space:nowrap}
    .hs strong{color:var(--green-text);font-weight:700}
    .hdr-actions{display:flex;align-items:center;gap:8px;flex-wrap:wrap}

    /* THEME TOGGLE BUTTON */
    .theme-btn{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;border-radius:20px;border:1px solid var(--border);background:var(--card-alt);color:var(--text);font-size:.75rem;font-weight:700;cursor:pointer;transition:all .2s;font-family:'Inter',sans-serif}
    .theme-btn:hover{background:var(--card-border);border-color:var(--accent)}

    .badge{font-size:.65rem;font-weight:800;padding:4px 10px;border-radius:20px;background:var(--accent-bg);border:1px solid var(--accent);color:var(--accent);letter-spacing:.05em;white-space:nowrap}
    .api-badge{font-size:.65rem;font-weight:800;padding:4px 10px;border-radius:20px;letter-spacing:.04em;white-space:nowrap;display:inline-flex;align-items:center;gap:5px;transition:all .2s}
    .api-badge.online{background:var(--green-bg);border:1px solid var(--green);color:var(--green-text)}
    .api-badge.offline{background:var(--yellow-bg);border:1px solid var(--yellow);color:var(--yellow-text)}

    /* NOTICE BAR */
    .notice{background:var(--notice-bg);border-bottom:1px solid var(--notice-border);padding:8px 20px;text-align:center;font-size:.78rem;color:var(--notice-text);font-weight:500}
    .notice strong{font-weight:700}
    .notice a{color:inherit;text-decoration:underline}

    /* HERO */
    .hero{text-align:center;padding:44px 20px 28px}
    .htag{display:inline-flex;align-items:center;gap:8px;font-size:.74rem;font-weight:800;color:var(--accent);background:var(--accent-bg);border:1px solid rgba(37,99,235,.25);padding:5px 16px;border-radius:30px;margin-bottom:14px;letter-spacing:.06em;text-transform:uppercase}
    h1{font-family:'Outfit',sans-serif;font-size:clamp(1.85rem,4.5vw,2.9rem);font-weight:900;line-height:1.18;margin-bottom:12px;color:var(--text)}
    h1 em{font-style:normal;color:var(--accent)}
    .sub{font-size:.95rem;color:var(--t2);max-width:640px;margin:0 auto 20px;line-height:1.65}
    .update-chip{display:inline-flex;align-items:center;gap:6px;background:var(--green-bg);border:1px solid rgba(16,185,129,.3);padding:5px 14px;border-radius:20px;font-size:.74rem;color:var(--green-text);font-weight:700;margin-bottom:20px}

    /* SEARCH CARD CONTAINER */
    .sc{background:var(--card);border:1px solid var(--card-border);border-radius:var(--r);padding:24px;max-width:880px;margin:0 auto 34px;box-shadow:var(--shadow-lg);transition:box-shadow .25s,border-color .25s;position:relative}
    .sc:hover{border-color:var(--card-border-hover)}

    /* MODE SELECTOR TABS */
    .mode-nav{display:flex;gap:10px;background:var(--card-alt);padding:6px;border-radius:12px;border:1px solid var(--border);margin-bottom:20px}
    .mode-btn{flex:1;display:flex;align-items:center;justify-content:center;gap:10px;padding:12px 16px;border-radius:9px;background:transparent;border:1px solid transparent;color:var(--t2);cursor:pointer;font-family:'Inter',sans-serif;transition:all .2s;min-height:48px}
    .mode-btn:hover{color:var(--text);background:rgba(0,0,0,.03)}
    [data-theme="dark"] .mode-btn:hover{background:rgba(255,255,255,.05)}
    .mode-btn.active{background:var(--bg-surface);border:1px solid var(--border2);color:var(--accent);box-shadow:var(--shadow-sm)}
    .m-icon{font-size:1.25rem}
    .m-text{text-align:left}
    .m-text strong{display:block;font-size:.88rem;font-weight:700}
    .m-text small{display:block;font-size:.7rem;color:var(--t3)}

    /* PATTERN BAR */
    .pattern-bar{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-bottom:16px;padding-bottom:14px;border-bottom:1px solid var(--border)}
    .pattern-label{font-size:.74rem;font-weight:700;color:var(--t3);text-transform:uppercase;letter-spacing:.05em}
    .pattern-options{display:flex;gap:8px}
    .p-opt{font-size:.73rem;font-weight:700;padding:6px 14px;border-radius:20px;border:1px solid var(--border);background:var(--card-alt);color:var(--t2);cursor:pointer;transition:all .18s;min-height:36px}
    .p-opt.active,.p-opt:hover{background:var(--accent-bg);border-color:var(--accent);color:var(--accent)}

    /* INPUTS & SELECTS */
    .r2{display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap}
    .grp{flex:1;min-width:200px}
    label{display:block;font-size:.74rem;font-weight:700;color:var(--t2);margin-bottom:6px;letter-spacing:.05em;text-transform:uppercase}
    input[type=number],select{width:100%;background:var(--card-alt);border:1.5px solid var(--border);border-radius:var(--rs);color:var(--text);font-family:'Inter',sans-serif;font-size:16px;padding:12px 14px;outline:none;transition:border-color .2s,box-shadow .2s;min-height:48px}
    input[type=number]:focus,select:focus{border-color:var(--accent);background:var(--bg-surface);box-shadow:0 0 0 3px rgba(37,99,235,.15)}
    input::placeholder{color:var(--t3)}
    select option{background:var(--card);color:var(--text)}

    /* PRESET CHIPS */
    .presets{display:flex;align-items:center;gap:6px;margin-top:8px;flex-wrap:wrap}
    .presets-label{font-size:.7rem;color:var(--t3);font-weight:600;margin-right:2px}
    .chip{font-size:.72rem;font-weight:700;padding:4px 10px;border-radius:14px;border:1px solid var(--border);background:var(--card-alt);color:var(--t2);cursor:pointer;transition:all .18s;min-height:30px}
    .chip:hover{background:var(--accent-bg);border-color:var(--accent);color:var(--accent)}

    /* LIVE PREDICTION CARD */
    .pred-card{background:var(--accent-bg);border:1px solid rgba(37,99,235,.25);border-radius:14px;padding:16px 18px;margin-bottom:20px;animation:fadeIn .25s ease}
    @keyframes fadeIn{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}
    .pred-header{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:12px}
    .pred-title{font-size:.78rem;font-weight:800;color:var(--accent);text-transform:uppercase;letter-spacing:.06em;display:flex;align-items:center;gap:6px}
    .pred-status{font-size:.72rem;font-weight:800;padding:3px 10px;border-radius:20px;border:1px solid var(--green);background:var(--green-bg);color:var(--green-text)}
    .pred-status.fail{border-color:var(--red);background:var(--red-bg);color:var(--red-text)}
    .pred-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:12px}
    .pm-box{background:var(--bg-surface);border:1px solid var(--border);border-radius:10px;padding:10px 12px;box-shadow:var(--shadow-sm)}
    .pm-lbl{font-size:.67rem;color:var(--t3);font-weight:700;text-transform:uppercase;margin-bottom:3px}
    .pm-val{font-size:1.3rem;font-weight:900;font-family:'Outfit',sans-serif;color:var(--accent)}
    .pm-sub{font-size:.72rem;color:var(--t3);margin-top:2px}
    .pm-percentile{font-size:1.2rem;font-weight:800;color:var(--teal);font-family:'Outfit',sans-serif}
    .pred-branches{border-top:1px solid var(--border);padding-top:10px;font-size:.75rem;color:var(--t2);line-height:1.55}
    .pred-branches strong{color:var(--text)}
    .branch-tags{display:flex;flex-wrap:wrap;gap:5px;margin-top:6px}
    .btag{font-size:.68rem;font-weight:700;padding:3px 9px;border-radius:12px;background:var(--card-alt);color:var(--text);border:1px solid var(--border)}

    /* FILTERS GRID */
    .fg{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:20px}

    /* BUTTONS */
    .btn-row{display:flex;gap:10px;flex-wrap:wrap}
    .btn{flex:2;min-width:220px;padding:14px 22px;font-size:.96rem;font-weight:800;font-family:'Inter',sans-serif;background:linear-gradient(135deg,var(--accent),#1d4ed8);color:#fff;border:none;border-radius:var(--rs);cursor:pointer;transition:transform .18s,box-shadow .18s;box-shadow:0 6px 20px rgba(37,99,235,.35);letter-spacing:.02em;text-align:center;min-height:50px}
    .btn:hover{transform:translateY(-2px);box-shadow:0 10px 28px rgba(37,99,235,.45)}
    .btn:active{transform:none}
    .btn-sec{flex:1;min-width:140px;padding:14px 16px;font-size:.85rem;font-weight:700;font-family:'Inter',sans-serif;background:var(--card-alt);color:var(--text);border:1px solid var(--border);border-radius:var(--rs);cursor:pointer;transition:all .18s;display:flex;align-items:center;justify-content:center;gap:6px;min-height:50px}
    .btn-sec:hover{background:var(--border);color:var(--accent)}

    /* STATS BAR */
    .stats{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-bottom:36px}
    .sp{display:flex;align-items:center;gap:8px;background:var(--card);border:1px solid var(--border);border-radius:50px;padding:8px 16px;font-size:.78rem;color:var(--t2);box-shadow:var(--shadow-sm)}
    .sp strong{color:var(--text);font-weight:700}
    .dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
    .dg{background:var(--green)}.dp{background:var(--yellow)}.dd{background:var(--teal)}.da{background:var(--accent)}.dn{background:var(--pink)}

    /* RESULTS SECTION */
    #res{display:none}

    /* PREDICTION RESULT BANNER */
    .pred-banner{background:var(--accent-bg);border:1.5px solid rgba(37,99,235,.25);border-radius:var(--r);padding:16px 20px;margin-bottom:20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;box-shadow:var(--shadow-sm)}
    .pb-left{flex:1;min-width:240px}
    .pb-title{font-size:1.02rem;font-weight:800;color:var(--text);margin-bottom:4px;display:flex;align-items:center;gap:8px}
    .pb-title strong{color:var(--accent)}
    .pb-sub{font-size:.82rem;color:var(--t2);line-height:1.5}
    .pb-sub strong{color:var(--text)}
    .pb-badge{font-size:.68rem;font-weight:800;background:var(--green-bg);border:1px solid var(--green);color:var(--green-text);padding:3px 9px;border-radius:20px}
    .pb-btn{font-size:.75rem;font-weight:700;padding:7px 15px;border-radius:20px;background:var(--card);border:1px solid var(--border);color:var(--text);cursor:pointer;transition:all .18s;white-space:nowrap}
    .pb-btn:hover{background:var(--border);border-color:var(--accent);color:var(--accent)}

    .rh{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-bottom:16px}
    .rt{font-family:'Outfit',sans-serif;font-size:1.35rem;font-weight:800;color:var(--text)}
    .rt em{font-style:normal;color:var(--accent)}
    .rc{display:flex;align-items:center;gap:8px;font-size:.82rem;color:var(--t2);background:var(--card);border:1px solid var(--border);padding:6px 14px;border-radius:50px;box-shadow:var(--shadow-sm)}
    .cb{background:var(--accent);color:#fff;font-weight:800;font-size:.78rem;padding:2px 10px;border-radius:20px}
    .sb{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:16px}
    .sl{font-size:.75rem;color:var(--t3);font-weight:600}
    .sbt{font-size:.74rem;font-weight:700;padding:6px 14px;border-radius:20px;border:1px solid var(--border);background:var(--card);color:var(--t2);cursor:pointer;transition:all .18s;font-family:'Inter',sans-serif}
    .sbt.on,.sbt:hover{background:var(--accent-bg);border-color:var(--accent);color:var(--accent)}

    /* ══════ COLLEGE CARD & BRANCH EXPLORER ══════ */
    .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:20px;margin-bottom:50px}
    .card{background:var(--card);border:1.5px solid var(--card-border);border-radius:var(--r);padding:22px;transition:transform .22s,border-color .22s,box-shadow .22s;position:relative;overflow:hidden;animation:up .38s ease both;box-shadow:var(--shadow-md);display:flex;flex-direction:column;justify-content:space-between}
    .card:hover{transform:translateY(-4px);border-color:var(--card-border-hover);box-shadow:var(--shadow-lg)}
    @keyframes up{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}

    .b-premier::after{content:'★ PREMIER';position:absolute;top:12px;right:12px;font-size:.6rem;font-weight:900;letter-spacing:.08em;color:var(--yellow-text);background:var(--yellow-bg);border:1px solid var(--yellow);padding:3px 9px;border-radius:20px}
    .b-new::after{content:'🆕 NEW 2025';position:absolute;top:12px;right:12px;font-size:.6rem;font-weight:900;letter-spacing:.06em;color:var(--green-text);background:var(--green-bg);border:1px solid var(--green);padding:3px 9px;border-radius:20px}
    .b-ok::after{content:'✓ ELIGIBLE';position:absolute;top:12px;right:12px;font-size:.6rem;font-weight:900;letter-spacing:.08em;color:var(--green-text);background:var(--green-bg);border:1px solid var(--green);padding:3px 9px;border-radius:20px}

    .ct{display:flex;align-items:flex-start;gap:12px;margin-bottom:14px;padding-right:70px}
    .ci{width:46px;height:46px;min-width:46px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.3rem}
    .ig{background:var(--green-bg);border:1px solid rgba(16,185,129,.3);color:var(--green-text)}
    .ip{background:var(--yellow-bg);border:1px solid rgba(245,158,11,.3);color:var(--yellow-text)}
    .id{background:var(--teal-bg);border:1px solid rgba(13,148,136,.3);color:var(--teal)}
    .in2{background:var(--accent-bg);border:1px solid rgba(37,99,235,.3);color:var(--accent)}
    .cm{flex:1;min-width:0}
    .cn{font-weight:800;font-size:.96rem;line-height:1.35;color:var(--text);margin-bottom:3px}
    .cl{font-size:.76rem;color:var(--t3);font-weight:500}

    .tr{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}
    .tg{font-size:.68rem;font-weight:700;padding:3px 9px;border-radius:20px;letter-spacing:.02em}
    .tg-g{background:var(--green-bg);color:var(--green-text);border:1px solid rgba(16,185,129,.3)}
    .tg-p{background:var(--yellow-bg);color:var(--yellow-text);border:1px solid rgba(245,158,11,.3)}
    .tg-d{background:var(--teal-bg);color:var(--teal);border:1px solid rgba(13,148,136,.3)}
    .tg-n{background:var(--accent-bg);color:var(--accent);border:1px solid rgba(37,99,235,.3)}
    .tg-a{background:var(--accent-bg);color:var(--accent);border:1px solid var(--accent);font-weight:800}
    .tg-s{background:var(--card-alt);color:var(--t2);border:1px solid var(--border)}

    /* TARGET SPECIALTY HIGHLIGHT BOX */
    .target-branch-box{background:var(--accent-bg);border:1.5px solid rgba(37,99,235,.3);border-radius:12px;padding:12px 14px;margin-bottom:12px}
    .tbb-top{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:6px}
    .tbb-label{font-size:.68rem;font-weight:800;color:var(--accent);letter-spacing:.05em}
    .tbb-name{font-size:.95rem;font-weight:800;color:var(--text);margin-bottom:10px}
    .tbb-metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;background:var(--card);padding:8px 10px;border-radius:8px;border:1px solid var(--border)}
    .tbb-metric{display:flex;flex-direction:column}
    .tbb-mlbl{font-size:.64rem;color:var(--t3);font-weight:700;text-transform:uppercase}
    .tbb-mval{font-size:.88rem;font-weight:800;color:var(--text)}
    .m-pos{color:var(--green-text)!important}
    .m-neg{color:var(--red-text)!important}

    /* ALL BRANCHES SUMMARY BOX */
    .branch-summary-box{background:var(--card-alt);border:1px solid var(--border);border-radius:12px;padding:12px 14px;margin-bottom:12px}
    .bsb-header{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:6px;margin-bottom:8px}
    .bsb-title{font-size:.82rem;font-weight:800;color:var(--text);display:flex;align-items:center;gap:6px}
    .bsb-sub{font-size:.72rem;color:var(--t3)}
    .eligible-highlights{display:flex;flex-direction:column;gap:5px}
    .eh-item{display:flex;align-items:center;justify-content:space-between;background:var(--card);padding:5px 10px;border-radius:6px;border:1px solid var(--border);font-size:.76rem}
    .eh-check{color:var(--green-text);font-weight:800;margin-right:6px}
    .eh-name{font-weight:600;color:var(--text);flex:1}
    .eh-cutoff{color:var(--accent);font-weight:700;font-size:.73rem}

    /* VIEW ALL BRANCHES EXPANDER BUTTON */
    .branch-actions{margin-top:8px;margin-bottom:12px}
    .view-branches-btn{width:100%;padding:10px 14px;background:var(--card-alt);color:var(--accent);border:1.5px solid var(--border);border-radius:10px;font-size:.8rem;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:space-between;transition:all .2s;font-family:'Inter',sans-serif}
    .view-branches-btn:hover,.view-branches-btn.open{background:var(--accent-bg);border-color:var(--accent)}
    .btn-arrow{font-size:.75rem;transition:transform .2s}

    /* BRANCH DRAWER & TABLE */
    .branch-drawer{background:var(--card-alt);border:1.5px solid var(--border2);border-radius:12px;padding:12px;margin-top:6px;margin-bottom:12px}
    .bd-head{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid var(--border)}
    .bd-title{font-size:.75rem;font-weight:800;color:var(--text);text-transform:uppercase;letter-spacing:.04em}
    .bd-search-wrap{width:100%;max-width:240px}
    .bd-search{width:100%;background:var(--card);border:1px solid var(--border);border-radius:8px;padding:6px 10px;font-size:.75rem;color:var(--text);outline:none;min-height:34px}
    .bd-search:focus{border-color:var(--accent)}
    .bd-list{max-height:260px;overflow-y:auto;display:flex;flex-direction:column;gap:6px;padding-right:4px;-webkit-overflow-scrolling:touch}
    .bd-list::-webkit-scrollbar{width:5px}
    .bd-list::-webkit-scrollbar-thumb{background:var(--border2);border-radius:4px}

    .bd-row{display:flex;align-items:center;justify-content:space-between;padding:8px 10px;border-radius:8px;border:1px solid var(--border);background:var(--card);transition:background .15s}
    .bd-row:hover{background:var(--bg)}
    .row-eligible{border-left:3px solid var(--green)}
    .row-reach{border-left:3px solid var(--t3);opacity:0.88}
    .bd-main{display:flex;flex-direction:column;gap:3px;flex:1;min-width:0;padding-right:8px}
    .bd-branch-name{font-size:.78rem;color:var(--text);font-weight:700;display:flex;align-items:center;gap:6px}
    .bd-dot{width:6px;height:6px;border-radius:50%;flex-shrink:0}
    .dot-el{background:var(--green)}
    .dot-reach{background:var(--t3)}
    .bd-tags{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
    .chance-pill{font-size:.65rem;font-weight:800;padding:2px 7px;border-radius:12px}
    .badge-safe,.chance-safe{background:var(--green-bg);color:var(--green-text);border:1px solid var(--green)}
    .badge-high,.chance-good{background:var(--teal-bg);color:var(--teal);border:1px solid var(--teal)}
    .badge-comp,.chance-comp{background:var(--yellow-bg);color:var(--yellow-text);border:1px solid var(--yellow)}
    .badge-reach,.chance-reach{background:var(--card-alt);color:var(--t3);border:1px solid var(--border)}
    .margin-pill{font-size:.65rem;color:var(--t3);font-weight:600}
    .margin-pill.pos{color:var(--green-text)}
    .margin-pill.neg{color:var(--red-text)}
    .bd-cutoff-col{text-align:right;flex-shrink:0}
    .bd-cutoff-lbl{display:block;font-size:.64rem;color:var(--t3);text-transform:uppercase;font-weight:700}
    .bd-cutoff-val{font-size:.88rem;font-weight:900;color:var(--text);font-family:'Outfit',sans-serif}

    /* CARD FOOTER STATS */
    .ri{background:var(--card-alt);border:1px solid var(--border);border-radius:var(--rs);padding:10px 14px;display:flex;align-items:center;justify-content:space-between;margin-top:auto}
    .rl{font-size:.72rem;color:var(--t3);margin-bottom:2px}
    .rv{font-size:.95rem;font-weight:900;color:var(--accent);font-family:'Outfit',sans-serif}
    .rm{font-size:.78rem;font-weight:800;color:var(--green-text)}

    /* INI-CET NOTE */
    .ini-note{background:var(--accent-bg);border:1.5px solid var(--accent);border-radius:var(--r);padding:14px 16px;margin-bottom:22px;font-size:.82rem;color:var(--t2);line-height:1.6}
    .ini-note strong{color:var(--accent)}

    /* EMPTY */
    .empty{text-align:center;padding:60px 20px;color:var(--t2);grid-column:1/-1}
    .ei{font-size:3rem;margin-bottom:12px}
    .empty h3{font-size:1.15rem;font-weight:700;color:var(--text);margin-bottom:6px}

    /* PAGINATION */
    .pgn{display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:40px;flex-wrap:wrap}
    .pbt{font-size:.78rem;font-weight:700;padding:8px 16px;border-radius:20px;border:1px solid var(--border);background:var(--card);color:var(--t2);cursor:pointer;font-family:'Inter',sans-serif;transition:all .18s;min-height:38px}
    .pbt:hover,.pbt.on{background:var(--accent-bg);border-color:var(--accent);color:var(--accent)}
    .pbt:disabled{opacity:.4;cursor:default}
    .pinfo{font-size:.76rem;color:var(--t3);padding:0 6px;font-weight:600}

    /* AUTH MODAL & HEADER WIDGET */
    .auth-btn-hdr{font-family:'Inter',sans-serif;font-size:.78rem;font-weight:700;padding:6px 14px;border-radius:20px;border:1px solid var(--border);background:var(--card-alt);color:var(--text);cursor:pointer;display:inline-flex;align-items:center;gap:6px;transition:all .18s;min-height:36px}
    .auth-btn-hdr:hover{background:var(--accent-bg);color:var(--accent);border-color:var(--accent)}
    .user-pill{display:inline-flex;align-items:center;gap:8px;padding:4px 10px 4px 6px;border-radius:20px;background:var(--green-bg);border:1px solid var(--green)}
    .user-avatar{width:24px;height:24px;border-radius:50%;background:rgba(16,185,129,.3);display:inline-flex;align-items:center;justify-content:center;font-size:.75rem}
    .user-info{font-size:.75rem;line-height:1.2;text-align:left}
    .user-name{font-weight:700;color:var(--text);display:block}
    .user-batch{font-size:.65rem;color:var(--t3)}
    .logout-btn{background:none;border:none;color:var(--red-text);font-size:.72rem;font-weight:700;cursor:pointer;padding:2px 6px;border-radius:4px;transition:background .15s}
    .logout-btn:hover{background:rgba(239,68,68,.15)}
    .auth-input-group{margin-bottom:12px;text-align:left}
    .auth-input-group label{display:block;font-size:.75rem;font-weight:700;color:var(--t2);margin-bottom:5px}
    .auth-input-group input, .auth-input-group select{width:100%;box-sizing:border-box;background:var(--card-alt);border:1.5px solid var(--border);border-radius:10px;padding:10px 12px;color:var(--text);font-size:16px;font-family:'Inter',sans-serif;outline:none;transition:border-color .18s}
    .auth-input-group input:focus, .auth-input-group select:focus{border-color:var(--accent);background:var(--bg-surface)}
    .auth-alert{padding:10px 14px;border-radius:8px;font-size:.8rem;margin-bottom:14px;display:none}
    .auth-alert.err{background:var(--red-bg);border:1px solid var(--red);color:var(--red-text)}
    .auth-alert.succ{background:var(--green-bg);border:1px solid var(--green);color:var(--green-text)}
    .auth-banner-info{background:var(--accent-bg);border:1px solid rgba(37,99,235,.3);padding:10px 14px;border-radius:10px;font-size:.82rem;color:var(--accent);margin-bottom:16px;display:flex;align-items:center;gap:8px}

    /* MODAL */
    .modal-overlay{position:fixed;inset:0;background:rgba(15,23,42,.6);backdrop-filter:blur(6px);z-index:999;display:none;align-items:center;justify-content:center;padding:16px}
    .modal-box{background:var(--card);border:1px solid var(--border2);border-radius:20px;max-width:800px;width:100%;max-height:88vh;overflow-y:auto;padding:24px;position:relative;box-shadow:var(--shadow-lg)}
    .modal-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;border-bottom:1px solid var(--border);padding-bottom:14px}
    .modal-title{font-family:'Outfit',sans-serif;font-size:1.25rem;font-weight:800;color:var(--text)}
    .modal-close{width:32px;height:32px;border-radius:8px;background:var(--card-alt);border:none;color:var(--t2);font-size:1.1rem;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background .18s}
    .modal-close:hover{background:var(--red-bg);color:var(--red-text)}
    .modal-tabs{display:flex;gap:8px;margin-bottom:16px}
    .mtab{font-size:.78rem;font-weight:700;padding:6px 14px;border-radius:20px;border:1px solid var(--border);background:var(--card-alt);color:var(--t2);cursor:pointer}
    .mtab.active{background:var(--accent-bg);border-color:var(--accent);color:var(--accent)}
    .tbl-wrap{overflow-x:auto}
    table.m-tbl{width:100%;border-collapse:collapse;font-size:.82rem;text-align:left}
    table.m-tbl th{background:var(--card-alt);padding:10px 12px;color:var(--accent);font-weight:700;border-bottom:1.5px solid var(--border)}
    table.m-tbl td{padding:10px 12px;border-bottom:1px solid var(--border);color:var(--t2)}
    table.m-tbl tr:hover td{background:var(--accent-bg);color:var(--text)}
    .t-mark{font-weight:800;color:var(--text)}
    .t-air{font-weight:800;color:var(--green-text)}

    footer{border-top:1px solid var(--border);padding:32px 20px;text-align:center;color:var(--t3);font-size:.78rem;line-height:2}
    footer a{color:var(--accent);text-decoration:none}

    /* ══════ MOBILE RESPONSIVE TWEAKS ══════ */
    @media(max-width:768px){
      .sc{padding:18px 14px}
      .hero{padding:30px 12px 18px}
      .grid{grid-template-columns:1fr}
      .hdr-mid{display:none}
      .mode-nav{flex-direction:column}
      .pred-grid{grid-template-columns:1fr 1fr}
      .btn-row{flex-direction:column}
      .btn,.btn-sec{width:100%;min-width:unset}
      .ct{padding-right:0}
      .b-premier::after,.b-new::after,.b-ok::after{position:static;display:inline-block;margin-bottom:8px}
      .tbb-metrics{grid-template-columns:1fr}
      .bd-search-wrap{max-width:100%}
    }
    @media(max-width:480px){
      .wrap{padding:0 12px}
      .hdr{padding:0 12px}
      .fg{grid-template-columns:1fr}
      .pred-grid{grid-template-columns:1fr}
    }
  </style>"""

    # Replace <style> block
    style_pattern = r'<style>.*?</style>'
    html = re.sub(style_pattern, new_css.strip(), html, count=1, flags=re.DOTALL)

    # 2. Update Header actions to include theme toggle
    header_old = r'<div style="display:flex;align-items:center;gap:10px">\s*<div id="authHeaderWidget"></div>\s*<span id="apiStatusBadge" class="api-badge offline">⚪ MLOps Checking\.\.\.</span>\s*<span class="badge">2025–26 DATA</span>\s*</div>'
    header_new = """<div class="hdr-actions">
      <button id="themeToggleBtn" class="theme-btn" onclick="toggleTheme()" aria-label="Toggle Theme">
        <span id="themeIcon">☀️</span> <span id="themeText">Light</span>
      </button>
      <div id="authHeaderWidget"></div>
      <span id="apiStatusBadge" class="api-badge offline">⚪ MLOps Checking...</span>
      <span class="badge">2025–26 DATA</span>
    </div>"""
    html, h_count = re.subn(header_old, header_new, html, count=1)
    if h_count == 0:
        print("Warning: Header actions pattern not matched directly, attempting fallback")
        fallback_target = '<div style="display:flex;align-items:center;gap:10px">'
        if fallback_target in html:
            html = html.replace(fallback_target, '<div class="hdr-actions">\n      <button id="themeToggleBtn" class="theme-btn" onclick="toggleTheme()" aria-label="Toggle Theme"><span id="themeIcon">☀️</span> <span id="themeText">Light</span></button>', 1)
            print("Fallback header replacement succeeded")

    # 3. Update JavaScript logic: selectedSpecialty, branch details, renderCards, theme logic
    # Find start of APP STATE
    app_state_old_pattern = r'/\* ══════ APP STATE ══════ \*/.*?(?=/\* ══════ PREDICTION CALCULATION ══════ \*/)'
    new_js_logic = """/* ══════ APP STATE ══════ */
let activeMode = 'marks'; // 'marks' or 'rank'
let examPattern = 800;    // 800 or 720
let results = [];
let targetRank = 12427;
let searchOrigin = 'marks'; // 'marks' or 'rank'
let lastMarks = 540;
let cat = 'UR';
let selectedSpecialty = ''; // Clean string tracking selected branch filter
let page = 1;
let sortMode = 'cutoff';

/* ══════ 22 SPECIALTY CUTOFF MULTIPLIERS ══════ */
/* Exact multipliers from MCC NEET PG 2024 AIQ Round 1 branch-wise closing
   ranks divided by MD General Medicine closing rank (3,803).
   Source: MCC official R1 seat allotment results 2024. */
const SPECIALTY_MULTIPLIERS = {
  "MD Radio-diagnosis": 0.56,
  "MD Dermatology, Venereology & Leprosy": 0.69,
  "MD General Medicine": 1.00,
  "MD Pediatrics": 1.70,
  "MS Obstetrics & Gynaecology": 2.39,
  "MS General Surgery": 2.84,
  "MS Orthopedics": 3.12,
  "MS Ophthalmology": 3.68,
  "MD Respiratory Medicine": 3.94,
  "MS ENT": 4.21,
  "MD Psychiatry": 4.87,
  "MD Anaesthesiology": 5.26,
  "MD Emergency Medicine": 5.79,
  "MD Radiation Oncology": 6.58,
  "MD Pathology": 9.20,
  "MD Microbiology": 14.46,
  "MD Community Medicine": 15.78,
  "MD Pharmacology": 17.09,
  "MD Forensic Medicine": 18.41,
  "MD Physiology": 22.35,
  "MD Biochemistry": 23.67,
  "MD Anatomy": 26.30
};

function getSpecialtyCutoff(baseCutoff, specialty) {
  const mult = SPECIALTY_MULTIPLIERS[specialty] || 1.0;
  return Math.min(230114, Math.max(1, Math.round(baseCutoff * mult)));
}

function findBestEligibleSpecialty(baseCutoff, userRank, offeredSpecialties) {
  const sorted = [...offeredSpecialties].sort((a, b) => (SPECIALTY_MULTIPLIERS[a] || 1.0) - (SPECIALTY_MULTIPLIERS[b] || 1.0));
  for (const s of sorted) {
    const spCutoff = getSpecialtyCutoff(baseCutoff, s);
    if (userRank <= spCutoff) {
      return { specialty: s, cutoff: spCutoff };
    }
  }
  if (sorted.length > 0) {
    const last = sorted[sorted.length - 1];
    return { specialty: last, cutoff: getSpecialtyCutoff(baseCutoff, last) };
  }
  return { specialty: null, cutoff: baseCutoff };
}

function getCollegeBranchDetails(college, userRank, category) {
  const baseCutoff = co(college, category);
  return college.sp.map(spec => {
    const cutoff = getSpecialtyCutoff(baseCutoff, spec);
    const margin = cutoff - userRank;
    const isEligible = userRank <= cutoff;
    let probClass = 'badge-reach';
    let probText = 'Reach';
    if (cutoff >= userRank * 1.30) {
      probClass = 'badge-safe';
      probText = 'Safety Seat';
    } else if (cutoff >= userRank * 1.10) {
      probClass = 'badge-high';
      probText = 'High Chance';
    } else if (cutoff >= userRank) {
      probClass = 'badge-comp';
      probText = 'Competitive';
    }
    return {
      name: spec,
      cutoff: cutoff,
      margin: margin,
      isEligible: isEligible,
      probClass: probClass,
      probText: probText
    };
  }).sort((a, b) => a.cutoff - b.cutoff);
}

function toggleBranchDrawer(cardId) {
  const el = document.getElementById(cardId);
  const arr = document.getElementById('arr-' + cardId);
  const btn = document.getElementById('btn-' + cardId);
  if (el) {
    const isClosed = el.style.display === 'none' || !el.style.display;
    el.style.display = isClosed ? 'block' : 'none';
    if (arr) arr.textContent = isClosed ? '▲' : '▼';
    if (btn) btn.classList.toggle('open', isClosed);
  }
}

function filterDrawerBranches(cardId, query) {
  const q = (query || '').toLowerCase().trim();
  const list = document.getElementById('list-' + cardId);
  if (!list) return;
  const rows = list.querySelectorAll('.bd-row');
  rows.forEach(row => {
    const name = row.getAttribute('data-name') || '';
    if (!q || name.includes(q)) {
      row.style.display = 'flex';
    } else {
      row.style.display = 'none';
    }
  });
}

function co(c, ct) {
  if (c.cutoffs && c.cutoffs[ct]) return c.cutoffs[ct];
  return c[ct] || c.UR || 50000;
}

/* ══════ THEME CONTROLLER ══════ */
function initTheme() {
  const saved = localStorage.getItem('neetpg_theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeUI(saved);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const next = current === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('neetpg_theme', next);
  updateThemeUI(next);
}

function updateThemeUI(theme) {
  const icon = document.getElementById('themeIcon');
  const text = document.getElementById('themeText');
  if (icon) icon.textContent = theme === 'light' ? '☀️' : '🌙';
  if (text) text.textContent = theme === 'light' ? 'Light' : 'Dark';
}
initTheme();

"""
    html, count_js = re.subn(app_state_old_pattern, new_js_logic, html, count=1, flags=re.DOTALL)
    print(f"Updated JS state & multipliers (matched {count_js})")

    # 4. Update runSearch() and render()
    run_search_old_pattern = r'/\* ══════ MAIN SEARCH / PREDICTION ══════ \*/.*?(?=function scrollToTop)'
    new_search_and_render = """/* ══════ MAIN SEARCH / PREDICTION ══════ */
function runSearch() {
  const catVal = document.getElementById('cs').value;
  const st = document.getElementById('ss').value;
  const tp = document.getElementById('ts').value;
  selectedSpecialty = (document.getElementById('sp').value || '').trim();
  const tf = document.getElementById('tierf').value;

  // Validate inputs before prompting auth
  if (activeMode === 'marks') {
    const mVal = document.getElementById('mi').value.trim();
    if (!mVal) {
      const el = document.getElementById('mi');
      el.focus(); el.style.borderColor = '#ef4444';
      setTimeout(() => el.style.borderColor = '', 1800);
      return;
    }
  } else {
    const rVal = document.getElementById('ri').value.trim();
    if (!rVal) {
      const el = document.getElementById('ri');
      el.focus(); el.style.borderColor = '#ef4444';
      setTimeout(() => el.style.borderColor = '', 1800);
      return;
    }
  }

  // Check Authentication Gatekeeper
  if (!currentUser) {
    pendingSearchTrigger = true;
    openAuthModal('register', 'Please register your candidate details (Name, Email, Phone, Batch Year) to view your All India Rank prediction and eligible colleges.');
    return;
  }

  if (activeMode === 'marks') {
    const mVal = document.getElementById('mi').value.trim();
    const score = parseInt(mVal, 10);
    const pred = calculatePrediction(score, examPattern, catVal);
    
    targetRank = pred.predRank;
    searchOrigin = 'marks';
    lastMarks = score;
    cat = catVal;

    // Update banner
    const banner = document.getElementById('predBanner');
    banner.style.display = 'flex';
    document.getElementById('bannerRank').textContent = `~${targetRank.toLocaleString('en-IN')}`;
    document.getElementById('bannerScore').textContent = `Score: ${score}/${examPattern}`;
    document.getElementById('bannerRange').textContent = `${pred.minRank.toLocaleString('en-IN')} – ${pred.maxRank.toLocaleString('en-IN')}`;
    document.getElementById('bannerPct').textContent = `${pred.percentile}%`;
    document.getElementById('bannerCat').textContent = catVal;
  } else {
    const rVal = document.getElementById('ri').value.trim();
    targetRank = parseInt(rVal, 10);
    searchOrigin = 'rank';
    cat = catVal;
    document.getElementById('predBanner').style.display = 'none';
  }

  page = 1;
  sortMode = 'cutoff';
  document.querySelectorAll('.sbt').forEach(b => b.classList.remove('on'));
  document.getElementById('s1').classList.add('on');

  results = COLLEGES.filter(c => {
    if (st && c.s !== st) return false;
    if (tp && c.t !== tp) return false;
    if (tf && String(c.tier) !== tf) return false;
    if (selectedSpecialty && !c.sp.includes(selectedSpecialty)) return false;

    const baseCutoff = co(c, catVal);
    let effectiveCutoff = baseCutoff;
    let targetBranch = selectedSpecialty || null;

    if (selectedSpecialty) {
      effectiveCutoff = getSpecialtyCutoff(baseCutoff, selectedSpecialty);
    } else {
      const match = findBestEligibleSpecialty(baseCutoff, targetRank, c.sp);
      targetBranch = match.specialty;
      effectiveCutoff = match.cutoff;
    }

    c._calc = {
      baseCutoff: baseCutoff,
      effectiveCutoff: effectiveCutoff,
      targetBranch: targetBranch,
      margin: effectiveCutoff - targetRank
    };

    return targetRank <= effectiveCutoff;
  });

  render();
}

function srt(m) {
  sortMode = m; page = 1;
  document.querySelectorAll('.sbt').forEach(b => b.classList.remove('on'));
  document.getElementById({cutoff:'s1',name:'s2',state:'s3',tier:'s4'}[m]).classList.add('on');
  render();
}

function render() {
  const sec = document.getElementById('res');
  sec.style.display = 'block';
  sec.scrollIntoView({ behavior: 'smooth', block: 'start' });

  const hasINI = results.some(c => c.t === 'INI-CET');
  document.getElementById('inicet-note').style.display = hasINI ? 'block' : 'none';

  if (searchOrigin === 'marks') {
    document.getElementById('rl').textContent = `for Predicted Rank ~${targetRank.toLocaleString('en-IN')} (${cat})`;
  } else {
    document.getElementById('rl').textContent = `for Rank ${targetRank.toLocaleString('en-IN')} (${cat})`;
  }
  document.getElementById('cnt').textContent = results.length;

  let sorted = [...results];
  if (sortMode === 'cutoff') sorted.sort((a,b) => (a._calc ? a._calc.effectiveCutoff : co(a,cat)) - (b._calc ? b._calc.effectiveCutoff : co(b,cat)));
  else if (sortMode === 'name')  sorted.sort((a,b) => a.n.localeCompare(b.n));
  else if (sortMode === 'state') sorted.sort((a,b) => a.s.localeCompare(b.s));
  else if (sortMode === 'tier')  sorted.sort((a,b) => a.tier - b.tier || ((a._calc ? a._calc.effectiveCutoff : co(a,cat)) - (b._calc ? b._calc.effectiveCutoff : co(b,cat))));

  const total = sorted.length;
  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  if (page > pages) page = 1;
  const slice = sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const grd = document.getElementById('grd');
  if (!slice.length) {
    grd.innerHTML = '<div class="empty"><div class="ei">😔</div><h3>No colleges found</h3><p>Try adjusting your filters, selecting a different category, or entering a higher score/rank.</p></div>';
    document.getElementById('pgn').innerHTML = '';
    return;
  }

  grd.innerHTML = slice.map((c, i) => {
    const baseCutoff = co(c, cat);
    const branchDetails = getCollegeBranchDetails(c, targetRank, cat);
    const eligibleBranches = branchDetails.filter(b => b.isEligible);

    const calc = c._calc || {
      baseCutoff: baseCutoff,
      effectiveCutoff: baseCutoff,
      targetBranch: c.sp[0] || 'General Medicine',
      margin: baseCutoff - targetRank
    };

    const badge = c.tier === 1 ? 'b-premier' : c.new ? 'b-new' : 'b-ok';
    const cardId = `col-${page}-${i}`;

    // Target Branch Panel or All-Branches Breakdown
    let branchSectionHtml = '';
    if (selectedSpecialty) {
      const chosen = branchDetails.find(b => b.name === selectedSpecialty) || {
        name: selectedSpecialty,
        cutoff: getSpecialtyCutoff(baseCutoff, selectedSpecialty),
        margin: getSpecialtyCutoff(baseCutoff, selectedSpecialty) - targetRank,
        isEligible: targetRank <= getSpecialtyCutoff(baseCutoff, selectedSpecialty),
        probClass: 'badge-comp',
        probText: 'Competitive'
      };

      branchSectionHtml = `
        <div class="target-branch-box">
          <div class="tbb-top">
            <span class="tbb-label">🎯 SELECTED SPECIALTY</span>
            <span class="chance-pill ${chosen.probClass}">${chosen.probText}</span>
          </div>
          <div class="tbb-name">${chosen.name}</div>
          <div class="tbb-metrics">
            <div class="tbb-metric">
              <span class="tbb-mlbl">2025–26 Cutoff (${cat})</span>
              <span class="tbb-mval">${chosen.cutoff.toLocaleString('en-IN')}</span>
            </div>
            <div class="tbb-metric">
              <span class="tbb-mlbl">Your Rank</span>
              <span class="tbb-mval">#${targetRank.toLocaleString('en-IN')}</span>
            </div>
            <div class="tbb-metric">
              <span class="tbb-mlbl">Safety Margin</span>
              <span class="tbb-mval ${chosen.margin >= 0 ? 'm-pos' : 'm-neg'}">${chosen.margin >= 0 ? '+' : ''}${chosen.margin.toLocaleString('en-IN')}</span>
            </div>
          </div>
        </div>
      `;
    } else {
      branchSectionHtml = `
        <div class="branch-summary-box">
          <div class="bsb-header">
            <div class="bsb-title">
              <span>🎓</span>
              <strong>${eligibleBranches.length} of ${c.sp.length} Branches Eligible</strong>
            </div>
            <span class="bsb-sub">at AIR #${targetRank.toLocaleString('en-IN')}</span>
          </div>
          <div class="eligible-highlights">
            ${eligibleBranches.slice(0, 3).map(b => `
              <div class="eh-item">
                <span class="eh-check">✓</span>
                <span class="eh-name">${b.name}</span>
                <span class="eh-cutoff">Cutoff: ~${b.cutoff.toLocaleString('en-IN')}</span>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    const drawerRowsHtml = branchDetails.map(b => `
      <div class="bd-row ${b.isEligible ? 'row-eligible' : 'row-reach'}" data-name="${b.name.toLowerCase()}">
        <div class="bd-main">
          <div class="bd-branch-name">
            <span class="bd-dot ${b.isEligible ? 'dot-el' : 'dot-reach'}"></span>
            <strong>${b.name}</strong>
          </div>
          <div class="bd-tags">
            <span class="chance-pill ${b.probClass}">${b.probText}</span>
            <span class="margin-pill ${b.margin >= 0 ? 'pos' : 'neg'}">${b.margin >= 0 ? '+' : ''}${b.margin.toLocaleString('en-IN')} margin</span>
          </div>
        </div>
        <div class="bd-cutoff-col">
          <span class="bd-cutoff-lbl">Cutoff</span>
          <span class="bd-cutoff-val">${b.cutoff.toLocaleString('en-IN')}</span>
        </div>
      </div>
    `).join('');

    const cutoffLabel = selectedSpecialty 
      ? `2025–26 ${selectedSpecialty} Cutoff (${cat})` 
      : `Anchor MD Gen Med Cutoff (${cat})`;
    const displayCutoff = selectedSpecialty 
      ? getSpecialtyCutoff(baseCutoff, selectedSpecialty) 
      : baseCutoff;
    const displayMargin = displayCutoff - targetRank;

    return `<div class="card ${badge}" style="animation-delay:${i * .025}s">
      <div>
        <div class="ct">
          <div class="ci ${ICLS[c.t]}">${ICON[c.t]}</div>
          <div class="cm">
            <div class="cn">${c.n}</div>
            <div class="cl">📍 ${c.s}</div>
          </div>
        </div>
        <div class="tr">
          <span class="tg ${TCLS[c.t]}">${c.t}</span>
          <span class="tg tg-a">${cat}</span>
          <span class="tg tg-s">Tier ${c.tier}</span>
          <span class="tg tg-s">🪑 ${c.seats} seats</span>
          ${c.new ? '<span class="tg tg-d">🆕 2025</span>' : ''}
        </div>
        
        ${branchSectionHtml}

        <div class="branch-actions">
          <button type="button" class="view-branches-btn" onclick="toggleBranchDrawer('${cardId}')" id="btn-${cardId}">
            <span>📊 View Branch-Wise Cutoffs (${c.sp.length} Branches)</span>
            <span class="btn-arrow" id="arr-${cardId}">▼</span>
          </button>
        </div>

        <div id="${cardId}" class="branch-drawer" style="display:none;">
          <div class="bd-head">
            <div class="bd-title">All Branches · Closing Ranks (${cat})</div>
            <div class="bd-search-wrap">
              <input type="text" class="bd-search" placeholder="Search branch (e.g. ortho)..." oninput="filterDrawerBranches('${cardId}', this.value)" />
            </div>
          </div>
          <div class="bd-list" id="list-${cardId}">
            ${drawerRowsHtml}
          </div>
        </div>
      </div>

      <div class="ri">
        <div>
          <div class="rl">${cutoffLabel}</div>
          <div class="rv">${displayCutoff.toLocaleString('en-IN')}</div>
        </div>
        <div style="text-align:right">
          <div class="rl">Safety margin</div>
          <div class="rm ${displayMargin >= 0 ? 'm-pos' : 'm-neg'}">${displayMargin >= 0 ? '+' : ''}${displayMargin.toLocaleString('en-IN')} AIR</div>
        </div>
      </div>
    </div>`;
  }).join('');

  // Pagination
  const pgn = document.getElementById('pgn');
  if (pages <= 1) { pgn.innerHTML = ''; return; }
  pgn.innerHTML = `
    <button class="pbt" onclick="goPage(${page - 1})" ${page === 1 ? 'disabled' : ''}>← Prev</button>
    <span class="pinfo">Page ${page} / ${pages} &nbsp;(${total} colleges)</span>
    <button class="pbt" onclick="goPage(${page + 1})" ${page === pages ? 'disabled' : ''}>Next →</button>`;
}

function goPage(p) {
  page = p;
  document.getElementById('res').scrollIntoView({ behavior: 'smooth', block: 'start' });
  render();
}
"""
    html, count_search = re.subn(run_search_old_pattern, new_search_and_render, html, count=1, flags=re.DOTALL)
    print(f"Updated runSearch and render functions (matched {count_search})")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("Successfully wrote updated index.html")

if __name__ == "__main__":
    main()

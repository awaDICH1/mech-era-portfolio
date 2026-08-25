#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机械纪元创作项目部 - 静态官网构建脚本
扫描 completed/、progress/、team/ 目录下的 .html 文件，生成 index.html
"""

import os
import re
import json
import time
import datetime
import random
import html as html_mod

# ============================================================
# 配置
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMPLETED_DIR = os.path.join(BASE_DIR, "completed")
PROGRESS_DIR = os.path.join(BASE_DIR, "progress")
TEAM_DIR = os.path.join(BASE_DIR, "team")
OUTPUT_FILE = os.path.join(BASE_DIR, "index.html")

# 动态标语池
SLOGANS = [
    "WARNING: ARTILLERY LOADING",
    "STATUS: NOMINAL",
    "SYSTEM: ONLINE",
    "REACTOR: 98.7% OUTPUT",
    "ALL UNITS STAND BY",
    "MECH ERA :: PRODUCTION ACTIVE",
    "SCANNING: NEW INTELLIGENCE DETECTED",
    "PROTOCOL: IRON WILL ENGAGED",
    "NEURAL LINK: STABLE",
    "ARSENAL: FULLY LOADED",
    "DEPLOYMENT SEQUENCE: INITIATED",
    "COMBAT READINESS: 100%",
]


# ============================================================
# 返回按钮 HTML 模板
# ============================================================
BACK_BUTTON_HTML = '''
<!-- MECH ERA :: BACK TO HOME :: AUTO-INJECTED -->
<a id="back-to-home" href="../index.html" style="
    position: fixed;
    top: 20px;
    left: 20px;
    z-index: 9999;
    display: inline-block;
    padding: 10px 18px;
    background: rgba(10, 10, 15, 0.9);
    border: 1px solid #00f0ff;
    border-radius: 2px;
    color: #00f0ff;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    letter-spacing: 1.5px;
    text-decoration: none;
    text-shadow: 0 0 8px rgba(0, 240, 255, 0.6);
    box-shadow: 0 0 12px rgba(0, 240, 255, 0.3), inset 0 0 10px rgba(0, 240, 255, 0.05);
    transition: all 0.3s ease;
    white-space: nowrap;
" onmouseover="this.style.background='rgba(0, 240, 255, 0.1)'; this.style.boxShadow='0 0 20px rgba(0, 240, 255, 0.6), inset 0 0 15px rgba(0, 240, 255, 0.1)';" onmouseout="this.style.background='rgba(10, 10, 15, 0.9)'; this.style.boxShadow='0 0 12px rgba(0, 240, 255, 0.3), inset 0 0 10px rgba(0, 240, 255, 0.05)';">
    ⍟ 返回指挥中心
</a>
'''

# 用于检测是否已注入的正则
BACK_BUTTON_PATTERN = re.compile(r'id=["\']back-to-home["\']', re.IGNORECASE)


# ============================================================
# 工具函数
# ============================================================
def inject_back_button(filepath, display_label):
    """向 HTML 文件注入返回主页按钮。
    返回 (状态码, 消息): 0=已注入, 1=已跳过(已存在), 2=失败(无body标签)
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return 2, f"读取失败: {e}"

    # 检查是否已注入
    if BACK_BUTTON_PATTERN.search(content):
        return 1, "已跳过（已存在返回按钮）"

    # 查找 <body ...> 标签（支持带属性的 body 标签）
    body_match = re.search(r'<body[^>]*>', content, re.IGNORECASE)
    if not body_match:
        return 2, "未找到 <body> 标签"

    # 在 body 开始标签后插入返回按钮
    insert_pos = body_match.end()
    new_content = content[:insert_pos] + BACK_BUTTON_HTML + content[insert_pos:]

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return 0, "已注入返回按钮"
    except Exception as e:
        return 2, f"写入失败: {e}"


def human_size(size_bytes):
    """将字节数转换为人类可读格式"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def format_time(timestamp):
    """格式化时间戳为可读字符串"""
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M")


def scan_projects(folder_path, label):
    """扫描指定目录下的所有 .html 文件，返回项目列表"""
    projects = []
    if not os.path.isdir(folder_path):
        print(f"  [!] 目录不存在: {folder_path}")
        return projects

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".html"):
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                name_no_ext = os.path.splitext(filename)[0]
                projects.append({
                    "name": name_no_ext,
                    "filename": filename,
                    "size": stat.st_size,
                    "size_human": human_size(stat.st_size),
                    "mtime": stat.st_mtime,
                    "mtime_str": format_time(stat.st_mtime),
                    "timestamp": int(stat.st_mtime),
                    "rel_path": f"./{label}/{html_mod.escape(filename)}",
                })

    # 按修改时间倒序排列（最新的在前）
    projects.sort(key=lambda x: x["mtime"], reverse=True)
    return projects


def scan_team(folder_path, label="team"):
    """扫描 team 目录下的 .html 文件，提取 title 和 meta description 作为成员信息"""
    members = []
    if not os.path.isdir(folder_path):
        print(f"  [!] 目录不存在: {folder_path}")
        return members

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".html"):
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                name_no_ext = os.path.splitext(filename)[0]

                # 读取文件内容提取 title 和 meta description
                title = name_no_ext
                desc = ""
                role = "团队成员"
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
                    if title_match and title_match.group(1).strip():
                        title = title_match.group(1).strip()
                    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
                    if desc_match:
                        desc = desc_match.group(1).strip()
                    role_match = re.search(r'<meta\s+name=["\']role["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
                    if role_match:
                        role = role_match.group(1).strip()
                except Exception:
                    pass

                members.append({
                    "name": name_no_ext,
                    "title": title,
                    "role": role,
                    "desc": desc,
                    "filename": filename,
                    "size": stat.st_size,
                    "size_human": human_size(stat.st_size),
                    "mtime": stat.st_mtime,
                    "mtime_str": format_time(stat.st_mtime),
                    "timestamp": int(stat.st_mtime),
                    "rel_path": f"./{label}/{html_mod.escape(filename)}",
                })

    members.sort(key=lambda x: x["mtime"], reverse=True)
    return members


def update_team_stats(folder_path, project_count):
    """更新 team 目录下 HTML 文件中的自动统计数据（项目数、从业年限）"""
    if not os.path.isdir(folder_path):
        return
    today = datetime.date.today()

    # 项目总数
    pattern_count = re.compile(
        r'(<div\s+class="stat-value"[^>]*data-auto="project-count"[^>]*>)(.*?)(</div>)',
        re.IGNORECASE | re.DOTALL
    )
    # 从业年限（根据 data-start 日期自动计算）
    pattern_years = re.compile(
        r'(<div\s+class="stat-value"[^>]*data-auto="years"[^>]*data-start="([0-9]{4}-[0-9]{2}-[0-9]{2})"[^>]*>)(.*?)(</div>)',
        re.IGNORECASE | re.DOTALL
    )

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(".html"):
            continue
        filepath = os.path.join(folder_path, filename)
        if not os.path.isfile(filepath):
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            new_content = pattern_count.sub(
                lambda m: f'{m.group(1)}{project_count}{m.group(3)}',
                content
            )

            def calc_years(m):
                try:
                    start = datetime.date.fromisoformat(m.group(2))
                    years = today.year - start.year
                    if (today.month, today.day) < (start.month, start.day):
                        years -= 1
                    return f'{m.group(1)}{years}{m.group(4)}'
                except Exception:
                    return m.group(0)

            new_content = pattern_years.sub(calc_years, new_content)

            if new_content != content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)
        except Exception:
            pass


# ============================================================
# HTML 生成
# ============================================================
def generate_html(completed_projects, progress_projects, team_members):
    """生成完整的 index.html 内容"""
    build_time = int(time.time())
    build_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    random_slogan = random.choice(SLOGANS)

    # 生成已完成项目卡片
    completed_cards = ""
    for p in completed_projects:
        link = f'{p["rel_path"]}?v={p["timestamp"]}'
        completed_cards += f'''
            <a class="card card-cyan" href="{link}">
                <div class="card-corner tl"></div>
                <div class="card-corner tr"></div>
                <div class="card-corner bl"></div>
                <div class="card-corner br"></div>
                <div class="card-icon">◈</div>
                <h3 class="card-title">{html_mod.escape(p["name"])}</h3>
                <div class="card-meta">
                    <span class="meta-item">
                        <span class="meta-label">SIZE</span>
                        <span class="meta-value">{p["size_human"]}</span>
                    </span>
                    <span class="meta-item">
                        <span class="meta-label">UPDATED</span>
                        <span class="meta-value">{p["mtime_str"]}</span>
                    </span>
                </div>
                <div class="card-status completed">
                    <span class="status-dot"></span>
                    COMPLETED
                </div>
            </a>
        '''

    if not completed_projects:
        completed_cards = '''
            <div class="empty-state">
                <div class="empty-icon">∅</div>
                <p>暂无已完成项目</p>
                <p class="empty-sub">将 .html 文件放入 completed/ 目录</p>
            </div>
        '''

    # 生成进行中项目卡片
    progress_cards = ""
    for p in progress_projects:
        link = f'{p["rel_path"]}?v={p["timestamp"]}'
        progress_cards += f'''
            <a class="card card-orange" href="{link}">
                <div class="card-corner tl"></div>
                <div class="card-corner tr"></div>
                <div class="card-corner bl"></div>
                <div class="card-corner br"></div>
                <div class="card-icon">⚙</div>
                <h3 class="card-title">{html_mod.escape(p["name"])}</h3>
                <div class="card-meta">
                    <span class="meta-item">
                        <span class="meta-label">SIZE</span>
                        <span class="meta-value">{p["size_human"]}</span>
                    </span>
                    <span class="meta-item">
                        <span class="meta-label">UPDATED</span>
                        <span class="meta-value">{p["mtime_str"]}</span>
                    </span>
                </div>
                <div class="card-status progress">
                    <span class="status-dot pulse"></span>
                    IN PROGRESS
                </div>
            </a>
        '''

    if not progress_projects:
        progress_cards = '''
            <div class="empty-state">
                <div class="empty-icon">∅</div>
                <p>暂无进行中项目</p>
                <p class="empty-sub">将 .html 文件放入 progress/ 目录</p>
            </div>
        '''

    # 生成团队成员卡片
    team_cards = ""
    for m in team_members:
        link = f'{m["rel_path"]}?v={m["timestamp"]}'
        desc_html = f'<div class="member-desc">{html_mod.escape(m["desc"])}</div>' if m["desc"] else ""
        team_cards += f'''
            <a class="member-card" href="{link}">
                <div class="member-corner tl"></div>
                <div class="member-corner tr"></div>
                <div class="member-corner bl"></div>
                <div class="member-corner br"></div>
                <div class="member-avatar">⬡</div>
                <div class="member-codename">{html_mod.escape(m["title"])}</div>
                <div class="member-role">{html_mod.escape(m["role"])}</div>
                {desc_html}
                <div class="member-meta">
                    <span class="meta-label">SIZE</span>
                    <span class="meta-value">{m["size_human"]}</span>
                </div>
            </a>
        '''

    if not team_members:
        team_cards = '''
            <div class="empty-state">
                <div class="empty-icon">∅</div>
                <p>暂无团队成员</p>
                <p class="empty-sub">将 .html 文件放入 team/ 目录</p>
            </div>
        '''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>// MECH ERA :: 创作项目部 //</title>
<style>
/* ================================================================
   重置与基础
   ================================================================ */
*, *::before, *::after {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

:root {{
    --bg-deep: #0a0a0f;
    --bg-panel: rgba(10, 15, 25, 0.7);
    --neon-cyan: #00f0ff;
    --neon-cyan-dim: #00a0b0;
    --neon-gold: #d4a843;
    --neon-orange: #ff6b00;
    --neon-orange-dim: #aa4400;
    --text-primary: #e0e8f0;
    --text-secondary: #8899aa;
    --text-dim: #445566;
    --border-cyan: rgba(0, 240, 255, 0.3);
    --border-orange: rgba(255, 107, 0, 0.3);
}}

html, body {{
    width: 100%;
    min-height: 100vh;
    background-color: var(--bg-deep);
    color: var(--text-primary);
    font-family: "Consolas", "Courier New", "Microsoft YaHei", monospace;
    overflow-x: hidden;
}}

body {{
    position: relative;
    padding-bottom: 80px;
}}

/* ================================================================
   背景动效 - 扫描线网格 + 点阵
   ================================================================ */
.bg-grid {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}}

/* 主网格线 */
.bg-grid::before {{
    content: "";
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background-image:
        linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px);
    background-size: 60px 60px;
    animation: gridMove 20s linear infinite;
    transform: perspective(500px) rotateX(60deg);
    transform-origin: center center;
}}

/* 扫描线 */
.bg-grid::after {{
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg,
        transparent 0%,
        rgba(0, 240, 255, 0.1) 20%,
        rgba(0, 240, 255, 0.6) 50%,
        rgba(0, 240, 255, 0.1) 80%,
        transparent 100%);
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.5);
    animation: scanLine 4s ease-in-out infinite;
}}

/* 闪烁点阵 */
.bg-dots {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
    background-image: radial-gradient(rgba(0, 240, 255, 0.15) 1px, transparent 1px);
    background-size: 4px 4px;
    animation: dotFlicker 3s ease-in-out infinite alternate;
}}

@keyframes gridMove {{
    0% {{ background-position: 0 0; }}
    100% {{ background-position: 60px 60px; }}
}}

@keyframes scanLine {{
    0% {{ top: -2px; opacity: 0; }}
    10% {{ opacity: 1; }}
    90% {{ opacity: 1; }}
    100% {{ top: 100%; opacity: 0; }}
}}

@keyframes dotFlicker {{
    0% {{ opacity: 0.3; }}
    50% {{ opacity: 0.6; }}
    100% {{ opacity: 0.4; }}
}}

/* ================================================================
   头部
   ================================================================ */
header {{
    position: relative;
    z-index: 10;
    text-align: center;
    padding: 60px 20px 40px;
}}

.main-title {{
    font-size: clamp(1.8rem, 5vw, 3.2rem);
    font-weight: 900;
    letter-spacing: 4px;
    color: var(--neon-cyan);
    text-shadow:
        0 0 10px rgba(0, 240, 255, 0.5),
        0 0 20px rgba(0, 240, 255, 0.3),
        0 0 40px rgba(0, 240, 255, 0.1);
    margin-bottom: 16px;
    animation: titleGlow 3s ease-in-out infinite alternate;
}}

@keyframes titleGlow {{
    0% {{
        text-shadow:
            0 0 10px rgba(0, 240, 255, 0.5),
            0 0 20px rgba(0, 240, 255, 0.3);
    }}
    100% {{
        text-shadow:
            0 0 15px rgba(0, 240, 255, 0.8),
            0 0 30px rgba(0, 240, 255, 0.5),
            0 0 60px rgba(0, 240, 255, 0.2);
    }}
}}

.subtitle {{
    font-size: clamp(0.85rem, 2vw, 1.1rem);
    letter-spacing: 3px;
    color: var(--neon-gold);
    text-shadow: 0 0 8px rgba(212, 168, 67, 0.4);
    min-height: 1.5em;
}}

.subtitle .blink {{
    display: inline-block;
    width: 8px;
    height: 14px;
    background: var(--neon-gold);
    margin-left: 4px;
    vertical-align: middle;
    animation: blinkCursor 1s step-end infinite;
}}

@keyframes blinkCursor {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0; }}
}}

.divider {{
    width: 80%;
    max-width: 700px;
    height: 1px;
    margin: 30px auto 0;
    background: linear-gradient(90deg,
        transparent 0%,
        var(--neon-cyan) 30%,
        var(--neon-gold) 50%,
        var(--neon-cyan) 70%,
        transparent 100%);
    box-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
}}

/* ================================================================
   主体布局
   ================================================================ */
main {{
    position: relative;
    z-index: 10;
    max-width: 1400px;
    margin: 0 auto;
    padding: 30px 20px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
}}

@media (max-width: 900px) {{
    main {{
        grid-template-columns: 1fr;
    }}
}}

/* ================================================================
   板块
   ================================================================ */
.section {{
    position: relative;
    background: var(--bg-panel);
    border-radius: 4px;
    padding: 24px;
    backdrop-filter: blur(8px);
}}

.section::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 4px;
    pointer-events: none;
}}

.section-cyan {{
    border: 1px solid var(--border-cyan);
    box-shadow:
        0 0 15px rgba(0, 240, 255, 0.1),
        inset 0 0 30px rgba(0, 240, 255, 0.03);
}}

.section-cyan::before {{
    border: 1px solid rgba(0, 240, 255, 0.1);
}}

.section-orange {{
    border: 1px solid var(--border-orange);
    box-shadow:
        0 0 15px rgba(255, 107, 0, 0.1),
        inset 0 0 30px rgba(255, 107, 0, 0.03);
}}

.section-orange::before {{
    border: 1px solid rgba(255, 107, 0, 0.1);
}}

.section-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    padding-bottom: 14px;
    border-bottom: 1px dashed;
}}

.section-cyan .section-header {{
    border-bottom-color: rgba(0, 240, 255, 0.2);
}}

.section-orange .section-header {{
    border-bottom-color: rgba(255, 107, 0, 0.2);
}}

.section-title {{
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: 2px;
    display: flex;
    align-items: center;
    gap: 10px;
}}

.section-cyan .section-title {{
    color: var(--neon-cyan);
    text-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
}}

.section-orange .section-title {{
    color: var(--neon-orange);
    text-shadow: 0 0 8px rgba(255, 107, 0, 0.4);
}}

.section-title .bracket {{
    opacity: 0.6;
}}

.section-count {{
    font-size: 0.85rem;
    padding: 3px 10px;
    border-radius: 2px;
    letter-spacing: 1px;
}}

.section-cyan .section-count {{
    background: rgba(0, 240, 255, 0.1);
    color: var(--neon-cyan);
    border: 1px solid var(--border-cyan);
}}

.section-orange .section-count {{
    background: rgba(255, 107, 0, 0.1);
    color: var(--neon-orange);
    border: 1px solid var(--border-orange);
}}

/* ================================================================
   卡片网格
   ================================================================ */
.card-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 16px;
}}

/* ================================================================
   卡片
   ================================================================ */
.card {{
    position: relative;
    display: block;
    text-decoration: none;
    color: var(--text-primary);
    background: rgba(15, 20, 30, 0.8);
    border: 1px solid;
    border-radius: 3px;
    padding: 20px 16px 16px;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    transform-style: preserve-3d;
    perspective: 1000px;
    overflow: hidden;
}}

.card-cyan {{
    border-color: rgba(0, 240, 255, 0.2);
}}

.card-orange {{
    border-color: rgba(255, 107, 0, 0.2);
}}

.card:hover {{
    transform: translateY(-6px) translateZ(10px);
}}

.card-cyan:hover {{
    border-color: var(--neon-cyan);
    box-shadow:
        0 8px 30px rgba(0, 240, 255, 0.2),
        0 0 20px rgba(0, 240, 255, 0.15),
        inset 0 0 20px rgba(0, 240, 255, 0.05);
}}

.card-orange:hover {{
    border-color: var(--neon-orange);
    box-shadow:
        0 8px 30px rgba(255, 107, 0, 0.2),
        0 0 20px rgba(255, 107, 0, 0.15),
        inset 0 0 20px rgba(255, 107, 0, 0.05);
}}

/* 卡片四角装饰 */
.card-corner {{
    position: absolute;
    width: 12px;
    height: 12px;
    border: 2px solid;
    transition: all 0.3s ease;
    opacity: 0.5;
}}

.card-cyan .card-corner {{ border-color: var(--neon-cyan); }}
.card-orange .card-corner {{ border-color: var(--neon-orange); }}

.card-corner.tl {{ top: 6px; left: 6px; border-right: none; border-bottom: none; }}
.card-corner.tr {{ top: 6px; right: 6px; border-left: none; border-bottom: none; }}
.card-corner.bl {{ bottom: 6px; left: 6px; border-right: none; border-top: none; }}
.card-corner.br {{ bottom: 6px; right: 6px; border-left: none; border-top: none; }}

.card:hover .card-corner {{
    opacity: 1;
    width: 16px;
    height: 16px;
}}

.card-icon {{
    font-size: 1.8rem;
    margin-bottom: 10px;
    transition: all 0.3s ease;
}}

.card-cyan .card-icon {{ color: var(--neon-cyan); text-shadow: 0 0 10px rgba(0, 240, 255, 0.5); }}
.card-orange .card-icon {{ color: var(--neon-orange); text-shadow: 0 0 10px rgba(255, 107, 0, 0.5); }}

.card:hover .card-icon {{
    transform: scale(1.1);
}}

.card-title {{
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 14px;
    letter-spacing: 0.5px;
    word-break: break-all;
    line-height: 1.4;
    min-height: 2.8em;
}}

.card-meta {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 14px;
}}

.meta-item {{
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
}}

.meta-label {{
    color: var(--text-dim);
    letter-spacing: 1px;
}}

.meta-value {{
    color: var(--text-secondary);
    font-family: "Consolas", monospace;
}}

.card-status {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.7rem;
    letter-spacing: 1.5px;
    padding-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
}}

.status-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
}}

.card-status.completed {{
    color: var(--neon-cyan);
}}
.card-status.completed .status-dot {{
    background: var(--neon-cyan);
    box-shadow: 0 0 6px var(--neon-cyan);
}}

.card-status.progress {{
    color: var(--neon-orange);
}}
.card-status.progress .status-dot {{
    background: var(--neon-orange);
    box-shadow: 0 0 6px var(--neon-orange);
}}

.pulse {{
    animation: pulse 1.5s ease-in-out infinite;
}}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.5; transform: scale(1.3); }}
}}

/* ================================================================
   空状态
   ================================================================ */
.empty-state {{
    text-align: center;
    padding: 40px 20px;
    color: var(--text-dim);
}}

.empty-icon {{
    font-size: 2.5rem;
    margin-bottom: 12px;
    opacity: 0.4;
}}

.empty-state p {{
    font-size: 0.9rem;
    letter-spacing: 1px;
}}

.empty-sub {{
    font-size: 0.75rem !important;
    margin-top: 6px;
    opacity: 0.6;
}}

/* ================================================================
   团队介绍板块
   ================================================================ */
.team-section {{
    position: relative;
    z-index: 10;
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 20px 10px;
}}

.team-panel {{
    position: relative;
    background: var(--bg-panel);
    border: 1px solid rgba(212, 168, 67, 0.25);
    border-radius: 4px;
    padding: 24px;
    backdrop-filter: blur(8px);
    box-shadow:
        0 0 15px rgba(212, 168, 67, 0.08),
        inset 0 0 30px rgba(212, 168, 67, 0.02);
}}

.team-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    padding-bottom: 14px;
    border-bottom: 1px dashed rgba(212, 168, 67, 0.2);
}}

.team-title {{
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: 2px;
    color: var(--neon-gold);
    text-shadow: 0 0 8px rgba(212, 168, 67, 0.4);
    display: flex;
    align-items: center;
    gap: 10px;
}}

.team-title .bracket {{
    opacity: 0.6;
}}

.team-tagline {{
    font-size: 0.75rem;
    color: var(--text-dim);
    letter-spacing: 1px;
}}

.member-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
}}

.member-card {{
    position: relative;
    display: block;
    text-decoration: none;
    color: var(--text-primary);
    background: rgba(15, 20, 30, 0.8);
    border: 1px solid rgba(212, 168, 67, 0.15);
    border-radius: 3px;
    padding: 24px 16px 18px;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    overflow: hidden;
}}

.member-card:hover {{
    transform: translateY(-4px);
    border-color: var(--neon-gold);
    box-shadow:
        0 8px 30px rgba(212, 168, 67, 0.15),
        0 0 15px rgba(212, 168, 67, 0.1),
        inset 0 0 20px rgba(212, 168, 67, 0.03);
}}

.member-corner {{
    position: absolute;
    width: 10px;
    height: 10px;
    border: 2px solid var(--neon-gold);
    transition: all 0.3s ease;
    opacity: 0.4;
}}

.member-corner.tl {{ top: 5px; left: 5px; border-right: none; border-bottom: none; }}
.member-corner.tr {{ top: 5px; right: 5px; border-left: none; border-bottom: none; }}
.member-corner.bl {{ bottom: 5px; left: 5px; border-right: none; border-top: none; }}
.member-corner.br {{ bottom: 5px; right: 5px; border-left: none; border-top: none; }}

.member-card:hover .member-corner {{
    opacity: 1;
    width: 14px;
    height: 14px;
}}

.member-avatar {{
    font-size: 2.2rem;
    color: var(--neon-gold);
    text-shadow: 0 0 12px rgba(212, 168, 67, 0.5);
    margin-bottom: 12px;
    transition: all 0.3s ease;
}}

.member-card:hover .member-avatar {{
    transform: scale(1.15);
    text-shadow: 0 0 20px rgba(212, 168, 67, 0.8);
}}

.member-codename {{
    font-size: 1rem;
    font-weight: 700;
    color: var(--neon-cyan);
    letter-spacing: 1.5px;
    margin-bottom: 4px;
    text-shadow: 0 0 6px rgba(0, 240, 255, 0.3);
}}

.member-role {{
    font-size: 0.75rem;
    color: var(--neon-gold);
    letter-spacing: 1px;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}}

.member-desc {{
    font-size: 0.72rem;
    color: var(--text-secondary);
    line-height: 1.6;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
}}

.member-meta {{
    display: flex;
    justify-content: space-between;
    font-size: 0.68rem;
    padding-top: 8px;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
}}

/* ================================================================
   页脚
   ================================================================ */
footer {{
    position: relative;
    z-index: 10;
    text-align: center;
    padding: 30px 20px;
    color: var(--text-dim);
    font-size: 0.75rem;
    letter-spacing: 1.5px;
}}

footer .build-info {{
    margin-top: 6px;
    color: var(--neon-cyan-dim);
    font-family: "Consolas", monospace;
}}

/* ================================================================
   滚动条
   ================================================================ */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background: var(--bg-deep);
}}

::-webkit-scrollbar-thumb {{
    background: rgba(0, 240, 255, 0.2);
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: rgba(0, 240, 255, 0.4);
}}
</style>
</head>
<body>

<!-- 背景层 -->
<div class="bg-grid"></div>
<div class="bg-dots"></div>

<!-- 头部 -->
<header>
    <h1 class="main-title">// MECH ERA :: 创作项目部 //</h1>
    <div class="subtitle" id="slogan">{random_slogan}<span class="blink"></span></div>
    <div class="divider"></div>
</header>

<!-- 团队介绍板块 -->
<div class="team-section">
    <div class="team-panel">
        <div class="team-header">
            <div class="team-title">
                <span class="bracket">[</span>
                团队介绍
                <span class="bracket">]</span>
            </div>
            <div class="team-tagline">{len(team_members)} MEMBERS · 点击查看详情</div>
        </div>
        <div class="member-grid">
            {team_cards}
        </div>
    </div>
</div>

<!-- 主体 -->
<main>
    <!-- 项目总览 -->
    <section class="section section-cyan">
        <div class="section-header">
            <div class="section-title">
                <span class="bracket">[</span>
                项目总览
                <span class="bracket">]</span>
            </div>
            <div class="section-count">{len(completed_projects)} UNITS</div>
        </div>
        <div class="card-grid">
            {completed_cards}
        </div>
    </section>

    <!-- 项目进展追踪 -->
    <section class="section section-orange">
        <div class="section-header">
            <div class="section-title">
                <span class="bracket">[</span>
                项目进展追踪
                <span class="bracket">]</span>
            </div>
            <div class="section-count">{len(progress_projects)} UNITS</div>
        </div>
        <div class="card-grid">
            {progress_cards}
        </div>
    </section>
</main>

<!-- 页脚 -->
<footer>
    <div>// MECHANICAL ERA CREATION DEPARTMENT //</div>
    <div class="build-info">BUILD_TIME: {build_time_str} | HASH: {build_time:x}</div>
</footer>

<script>
/* ================================================================
   动态标语切换
   ================================================================ */
(function() {{
    var slogans = {json.dumps(SLOGANS, ensure_ascii=False)};
    var sloganEl = document.getElementById("slogan");
    var currentIndex = slogans.indexOf("{random_slogan}");
    if (currentIndex === -1) currentIndex = 0;

    function typewriter(text, callback) {{
        var i = 0;
        sloganEl.innerHTML = '<span class="blink"></span>';
        function type() {{
            if (i < text.length) {{
                var blink = sloganEl.querySelector(".blink");
                if (blink) {{
                    blink.remove();
                }}
                sloganEl.innerHTML = sloganEl.innerHTML.replace('<span class="blink"></span>', '') + text.charAt(i) + '<span class="blink"></span>';
                i++;
                setTimeout(type, 40 + Math.random() * 30);
            }} else if (callback) {{
                callback();
            }}
        }}
        type();
    }}

    function nextSlogan() {{
        currentIndex = (currentIndex + 1) % slogans.length;
        setTimeout(function() {{
            typewriter(slogans[currentIndex], function() {{
                setTimeout(nextSlogan, 4000);
            }});
        }}, 1000);
    }}

    setTimeout(nextSlogan, 4000);
}})();

/* ================================================================
   卡片 3D 倾斜动效
   ================================================================ */
(function() {{
    var cards = document.querySelectorAll(".card");
    cards.forEach(function(card) {{
        card.addEventListener("mousemove", function(e) {{
            var rect = card.getBoundingClientRect();
            var x = e.clientX - rect.left;
            var y = e.clientY - rect.top;
            var centerX = rect.width / 2;
            var centerY = rect.height / 2;
            var rotateX = (y - centerY) / centerY * -5;
            var rotateY = (x - centerX) / centerX * 5;
            card.style.transform = "translateY(-6px) translateZ(10px) rotateX(" + rotateX + "deg) rotateY(" + rotateY + "deg)";
        }});
        card.addEventListener("mouseleave", function() {{
            card.style.transform = "translateY(0) translateZ(0) rotateX(0) rotateY(0)";
        }});
    }});
}})();
</script>

</body>
</html>
'''
    return html


# ============================================================
# 主流程
# ============================================================
def main():
    print("=" * 60)
    print("  // MECH ERA :: 创作项目部 :: BUILD SYSTEM //")
    print("=" * 60)
    print()

    # 1. 扫描目录
    print(">>> 正在扫描项目目录...")
    print(f"  已完成目录: {COMPLETED_DIR}")
    print(f"  进行中目录: {PROGRESS_DIR}")
    print(f"  团队目录: {TEAM_DIR}")
    print()

    completed_projects = scan_projects(COMPLETED_DIR, "completed")
    progress_projects = scan_projects(PROGRESS_DIR, "progress")
    team_members = scan_team(TEAM_DIR, "team")

    project_total = len(completed_projects) + len(progress_projects)
    print(f">>> 扫描完成：发现 {len(completed_projects)} 个已完成项目，{len(progress_projects)} 个进行中项目，{len(team_members)} 个团队成员。")
    print()

    # 2. 更新团队成员页面中的自动统计数据
    update_team_stats(TEAM_DIR, project_total)

    # 3. 向子页面注入返回按钮
    print(">>> 正在向子页面注入返回指挥中心按钮...")
    injected_count = 0
    skipped_count = 0
    fail_count = 0

    for p in completed_projects:
        filepath = os.path.join(COMPLETED_DIR, p["filename"])
        status, msg = inject_back_button(filepath, "已完成")
        status_icon = "✓" if status == 0 else ("=" if status == 1 else "✗")
        print(f"  {status_icon} 已完成/{p['filename']} —— {msg}")
        if status == 0:
            injected_count += 1
        elif status == 1:
            skipped_count += 1
        else:
            fail_count += 1

    for p in progress_projects:
        filepath = os.path.join(PROGRESS_DIR, p["filename"])
        status, msg = inject_back_button(filepath, "进行中")
        status_icon = "✓" if status == 0 else ("=" if status == 1 else "✗")
        print(f"  {status_icon} 进行中/{p['filename']} —— {msg}")
        if status == 0:
            injected_count += 1
        elif status == 1:
            skipped_count += 1
        else:
            fail_count += 1

    for m in team_members:
        filepath = os.path.join(TEAM_DIR, m["filename"])
        status, msg = inject_back_button(filepath, "团队")
        status_icon = "✓" if status == 0 else ("=" if status == 1 else "✗")
        print(f"  {status_icon} 团队/{m['filename']} —— {msg}")
        if status == 0:
            injected_count += 1
        elif status == 1:
            skipped_count += 1
        else:
            fail_count += 1

    print()
    print(f">>> 子页面处理完成：新注入 {injected_count} 个，跳过 {skipped_count} 个，失败 {fail_count} 个。")
    print()

    # 4. 重新扫描（注入后文件修改时间会变，更新一下数据）
    completed_projects = scan_projects(COMPLETED_DIR, "completed")
    progress_projects = scan_projects(PROGRESS_DIR, "progress")
    team_members = scan_team(TEAM_DIR, "team")

    # 5. 生成 index.html
    print(">>> 正在生成 index.html...")
    html_content = generate_html(completed_projects, progress_projects, team_members)

    # 6. 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    file_size = os.path.getsize(OUTPUT_FILE)
    print(f">>> index.html 已生成，大小: {human_size(file_size)}")
    print(f">>> 输出路径: {OUTPUT_FILE}")
    print()
    print(">>> index.html 已生成，准备部署！")
    print("=" * 60)


if __name__ == "__main__":
    main()

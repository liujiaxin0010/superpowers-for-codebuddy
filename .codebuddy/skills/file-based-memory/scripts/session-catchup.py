#!/usr/bin/env python3
"""
会话恢复脚本 - 检测上一次会话中未同步到持久化文件的上下文。
用法: python3 session-catchup.py [项目路径]
"""

import json
import sys
import os
from pathlib import Path

PLANNING_FILES = ['findings.md', 'progress.md']
PLANNING_DIRS = ['docs']


def get_project_dir(project_path: str) -> Path:
    sanitized = project_path.replace('/', '-')
    if not sanitized.startswith('-'):
        sanitized = '-' + sanitized
    sanitized = sanitized.replace('_', '-')
    return Path.home() / '.codebuddy' / 'projects' / sanitized


def get_sessions_sorted(project_dir: Path):
    sessions = list(project_dir.glob('*.jsonl'))
    main_sessions = [s for s in sessions if not s.name.startswith('agent-')]
    return sorted(main_sessions, key=lambda p: p.stat().st_mtime, reverse=True)


def parse_session_messages(session_file: Path):
    messages = []
    with open(session_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            try:
                data = json.loads(line)
                data['_line_num'] = line_num
                messages.append(data)
            except json.JSONDecodeError:
                pass
    return messages


def find_last_planning_update(messages):
    last_line = -1
    last_file = None
    for msg in messages:
        if msg.get('type') != 'assistant':
            continue
        content = msg.get('message', {}).get('content', [])
        if not isinstance(content, list):
            continue
        for item in content:
            if item.get('type') != 'tool_use':
                continue
            if item.get('name') not in ('Write', 'Edit'):
                continue
            file_path = item.get('input', {}).get('file_path', '')
            for pf in PLANNING_FILES:
                if file_path.endswith(pf):
                    last_line = msg['_line_num']
                    last_file = pf
    return last_line, last_file


def extract_messages_after(messages, after_line):
    result = []
    for msg in messages:
        if msg['_line_num'] <= after_line:
            continue
        msg_type = msg.get('type')
        if msg_type == 'user' and not msg.get('isMeta', False):
            content = msg.get('message', {}).get('content', '')
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        content = item.get('text', '')
                        break
                else:
                    content = ''
            if content and isinstance(content, str):
                if content.startswith(('<local-command', '<command-', '<task-notification')):
                    continue
                if len(content) > 20:
                    result.append({'role': 'user', 'content': content[:300]})
        elif msg_type == 'assistant':
            msg_content = msg.get('message', {}).get('content', '')
            text = ''
            tools = []
            if isinstance(msg_content, str):
                text = msg_content
            elif isinstance(msg_content, list):
                for item in msg_content:
                    if item.get('type') == 'text':
                        text = item.get('text', '')
                    elif item.get('type') == 'tool_use':
                        name = item.get('name', '')
                        inp = item.get('input', )
                        if name in ('Edit', 'Write'):
                            tools.append(f"{name}: {inp.get('file_path', '?')}")
                        elif name == 'Bash':
                            tools.append(f"Bash: {inp.get('command', '')[:80]}")
                        else:
                            tools.append(name)
            if text or tools:
                result.append({'role': 'assistant', 'content': text[:600], 'tools': tools})
    return result


def main():
    project_path = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    has_files = False
    for d in PLANNING_DIRS:
        for pf in PLANNING_FILES:
            if Path(project_path, d, pf).exists():
                has_files = True
                break
    if not has_files:
        return

    project_dir = get_project_dir(project_path)
    if not project_dir.exists():
        return

    sessions = get_sessions_sorted(project_dir)
    target = None
    for s in sessions:
        if s.stat().st_size > 5000:
            target = s
            break
    if not target:
        return

    messages = parse_session_messages(target)
    last_line, last_file = find_last_planning_update(messages)
    if last_line < 0:
        return

    after = extract_messages_after(messages, last_line)
    if not after:
        return

    print(f"\n[file-based-memory] 检测到未同步的会话上下文")
    print(f"上次更新: {last_file} (消息 #{last_line})")
    print(f"未同步消息: {len(after)} 条")
    print("\n--- 未同步内容 ---")
    for msg in after[-15:]:
        if msg['role'] == 'user':
            print(f"USER: {msg['content']}")
        else:
            if msg.get('content'):
                print(f"AI: {msg['content'][:300]}")
            if msg.get('tools'):
                print(f"  工具: {', '.join(msg['tools'][:4])}")
    print("\n--- 建议操作 ---")
    print("1. 运行 git diff --stat 或 svn status")
    print("2. 读取 docs/findings.md 和 docs/progress.md")
    print("3. 根据上下文更新持久化文件")
    print("4. 继续任务")


if __name__ == '__main__':
    main()

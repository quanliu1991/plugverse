#!/usr/bin/env python3
"""
标记 TASKS.md 中的任务为已完成

用法:
    python mark-complete.py 1.1.1    # 标记 1.1.1 节的所有任务为完成
    python mark-complete.py 1.1      # 标记 1.1 节的所有任务为完成
    python mark-complete.py 1        # 标记 Phase 1 的所有任务为完成
"""

import re
import sys
from pathlib import Path
from datetime import datetime


def mark_section_complete(tasks_file: str, section_id: str):
    """标记指定 section 的任务为完成"""
    
    with open(tasks_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    in_target_section = False
    section_depth = section_id.count('.')
    
    for line in lines:
        # 检测是否进入目标 section
        header_match = re.match(r'^(#+)\s+(\d+(?:\.\d+)*)\s+(.+?)\s*([⬜🔄✅⏸️])?\s*$', line)
        
        if header_match:
            hash_count = len(header_match.group(1))
            current_id = header_match.group(2)
            
            # 检查是否匹配目标 section
            if current_id == section_id:
                in_target_section = True
                # 更新 section 标题状态
                line = re.sub(r'\s*[⬜🔄]\s*$', ' ✅', line)
                line = re.sub(r'\s*✅\s*$', ' ✅', line)
            elif current_id.startswith(section_id + '.'):
                # 子 section 也标记
                pass
            else:
                # 检查是否退出目标 section
                if in_target_section:
                    # 检查是否是同级或更高级的 section
                    current_depth = current_id.count('.')
                    if current_depth <= section_depth:
                        in_target_section = False
        
        # 如果在目标 section 中，标记任务
        if in_target_section:
            # 标记任务 (- [ ] -> - [x])
            line = re.sub(r'^-\s+\[\s+\]\s*([⬜🔄])\s*', r'- [x] ✅ ', line)
            line = re.sub(r'^-\s+\[\s+\]\s*', r'- [x] ', line)
        
        new_lines.append(line)
    
    # 写回文件
    with open(tasks_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f"✅ 已标记 Section {section_id} 的所有任务为完成")


def main():
    if len(sys.argv) < 2:
        print("用法：python mark-complete.py <section_id>")
        print("示例:")
        print("  python mark-complete.py 1.1.1    # 标记 1.1.1 节")
        print("  python mark-complete.py 1.1      # 标记 1.1 节")
        print("  python mark-complete.py 1        # 标记 Phase 1")
        return
    
    section_id = sys.argv[1]
    tasks_file = "TASKS.md"
    
    if not Path(tasks_file).exists():
        print(f"❌ 错误：找不到 {tasks_file}")
        return
    
    # 备份原文件
    backup_file = f"{tasks_file}.bak"
    with open(tasks_file, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"📄 备份已保存到：{backup_file}")
    
    # 标记完成
    mark_section_complete(tasks_file, section_id)
    
    print("\n💡 提示:")
    print("  - 运行 'python progress.py' 查看更新后的进度")
    print("  - 如果要撤销，运行：cp TASKS.md.bak TASKS.md")


if __name__ == "__main__":
    main()

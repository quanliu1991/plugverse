#!/usr/bin/env python3
"""
PlugVerse 任务进度追踪器

实时查看 TASKS.md 中的任务完成情况
"""

import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def parse_tasks_md(file_path: str) -> dict:
    """解析 TASKS.md 文件，提取任务信息"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    phases = []
    current_phase = None
    current_section = None
    current_subsection = None
    
    lines = content.split('\n')
    
    for line in lines:
        line_stripped = line.strip()
        
        # 跳过空行和注释
        if not line_stripped or line_stripped.startswith('>'):
            continue
        
        # 检测 Phase 标题 (## 🏗️ Phase 1 - 核心框架搭建)
        if line_stripped.startswith('##') and 'Phase' in line_stripped and not line_stripped.startswith('###'):
            # 提取 Phase 编号
            phase_match = re.search(r'(Phase\s+\d+)', line_stripped)
            if phase_match:
                phase_id = phase_match.group(1)
                # 提取 Phase 名称
                name_match = re.search(r'Phase\s+\d+\s*[-–]\s*(.+?)(?:\s*[⬜🔄✅⏸️])?\s*$', line_stripped)
                phase_name = name_match.group(1).strip() if name_match else "Unknown"
                
                current_phase = {
                    'id': phase_id,
                    'name': phase_name,
                    'sections': [],
                    'tasks': []
                }
                phases.append(current_phase)
                current_section = None
                current_subsection = None
                continue
        
        # 检测 Section 标题 (### 1.1 项目初始化)
        if line_stripped.startswith('###') and re.match(r'^###\s+\d+\.\d+', line_stripped):
            if current_phase:
                section_match = re.match(r'^###\s+(\d+\.\d+)\s+(.+?)(?:\s*[⬜🔄✅⏸️])?\s*$', line_stripped)
                if section_match:
                    section_id = section_match.group(1)
                    section_name = section_match.group(2).strip()
                    current_section = {
                        'id': section_id,
                        'name': section_name,
                        'subsections': [],
                        'tasks': []
                    }
                    current_phase['sections'].append(current_section)
                    current_subsection = None
                    continue
        
        # 检测 Subsection 标题 (#### 1.1.1 创建项目结构)
        if line_stripped.startswith('####') and re.match(r'^####\s+\d+\.\d+\.\d+', line_stripped):
            if current_section:
                subsection_match = re.match(r'^####\s+(\d+\.\d+\.\d+)\s+(.+?)\s*$', line_stripped)
                if subsection_match:
                    subsection_id = subsection_match.group(1)
                    subsection_name = subsection_match.group(2).strip()
                    current_subsection = {
                        'id': subsection_id,
                        'name': subsection_name,
                        'tasks': []
                    }
                    current_section['subsections'].append(current_subsection)
                    continue
        
        # 检测任务 (- [ ] 或 - [x])
        task_match = re.match(r'^-\s+\[([ x])\]\s*([⬜🔄✅⏸️🚫])?\s*(.+?)\s*$', line_stripped)
        if task_match:
            is_completed = task_match.group(1) == 'x'
            task_name = task_match.group(3).strip()
            
            # 移除行内代码标记
            task_name = re.sub(r'`([^`]+)`', r'\1', task_name)
            
            task = {
                'name': task_name,
                'completed': is_completed
            }
            
            # 添加到最近的容器
            if current_subsection:
                current_subsection['tasks'].append(task)
            elif current_section:
                current_section['tasks'].append(task)
            elif current_phase:
                current_phase['tasks'].append(task)
    
    return {'phases': phases}


def calculate_stats(data: dict) -> dict:
    """计算统计数据"""
    
    stats = {
        'total': 0,
        'completed': 0,
        'pending': 0,
        'by_phase': {}
    }
    
    for phase in data['phases']:
        phase_stats = {'total': 0, 'completed': 0, 'sections': {}}
        
        # 统计 section
        for section in phase['sections']:
            section_stats = {'total': 0, 'completed': 0, 'subsections': {}}
            
            # 统计 subsection
            for subsection in section['subsections']:
                sub_stats = {
                    'total': len(subsection['tasks']),
                    'completed': sum(1 for t in subsection['tasks'] if t['completed'])
                }
                section_stats['subsections'][subsection['id']] = sub_stats
                section_stats['total'] += sub_stats['total']
                section_stats['completed'] += sub_stats['completed']
            
            # 统计 section 直接的任务
            section_direct_tasks = len(section['tasks'])
            section_direct_completed = sum(1 for t in section['tasks'] if t['completed'])
            section_stats['total'] += section_direct_tasks
            section_stats['completed'] += section_direct_completed
            
            phase_stats['sections'][section['id']] = section_stats
            phase_stats['total'] += section_stats['total']
            phase_stats['completed'] += section_stats['completed']
        
        # 统计 phase 直接的任务
        phase_direct_tasks = len(phase['tasks'])
        phase_direct_completed = sum(1 for t in phase['tasks'] if t['completed'])
        phase_stats['total'] += phase_direct_tasks
        phase_stats['completed'] += phase_direct_completed
        
        stats['by_phase'][phase['id']] = phase_stats
        stats['total'] += phase_stats['total']
        stats['completed'] += phase_stats['completed']
    
    stats['pending'] = stats['total'] - stats['completed']
    stats['percent'] = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
    
    return stats


def print_progress_bar(completed: int, total: int, width: int = 40) -> str:
    """生成进度条"""
    percent = (completed / total * 100) if total > 0 else 0
    filled = int(width * completed / total) if total > 0 else 0
    empty = width - filled
    
    bar = '█' * filled + '░' * empty
    return f"[{bar}] {percent:.1f}%"


def display_dashboard(data: dict, stats: dict):
    """显示进度仪表板"""
    
    print("\n" + "=" * 70)
    print("🎯 PlugVerse 任务进度仪表板")
    print("=" * 70)
    print(f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 总体进度
    print("\n📊 总体进度")
    print("-" * 70)
    print(f"总任务数：{stats['total']}")
    print(f"已完成：{stats['completed']} ✅")
    print(f"未完成：{stats['pending']} ⬜")
    print(f"完成率：{print_progress_bar(stats['completed'], stats['total'])}")
    
    # 按阶段统计
    print("\n📈 按阶段进度")
    print("-" * 70)
    
    phase_names = {
        'Phase 1': '🏗️ 核心框架',
        'Phase 2': '🔌 首个插件',
        'Phase 3': '🎨 前端 UI',
        'Phase 4': '🌟 插件生态'
    }
    
    for phase_id, name in phase_names.items():
        if phase_id in stats['by_phase']:
            phase_stats = stats['by_phase'][phase_id]
            bar = print_progress_bar(phase_stats['completed'], phase_stats['total'], 30)
            status = "✅" if phase_stats['completed'] == phase_stats['total'] > 0 else "🔄" if phase_stats['completed'] > 0 else "⬜"
            print(f"{name:20s} {bar:35s} ({phase_stats['completed']:2d}/{phase_stats['total']}) {status}")
    
    # 收集所有任务
    all_tasks = []
    for phase in data['phases']:
        for section in phase['sections']:
            for subsection in section['subsections']:
                for task in subsection['tasks']:
                    all_tasks.append({
                        'phase': phase['id'],
                        'section': section['id'],
                        'subsection': subsection['id'],
                        'name': task['name'],
                        'completed': task['completed']
                    })
    
    # 最近完成的任务
    print("\n✨ 最近完成的任务")
    print("-" * 70)
    
    completed_tasks = [t for t in all_tasks if t['completed']][-5:]
    if completed_tasks:
        for i, task in enumerate(completed_tasks, 1):
            print(f"  {i}. ✅ {task['name'][:60]}")
    else:
        print("  暂无完成的任务")
    
    # 待办任务
    print("\n📋 待办任务（最近 10 个）")
    print("-" * 70)
    
    pending_tasks = [t for t in all_tasks if not t['completed']][:10]
    if pending_tasks:
        for i, task in enumerate(pending_tasks, 1):
            print(f"  {i:2d}. ⬜ [{task['phase']}.{task['section']}] {task['name'][:50]}")
    else:
        print("  🎉 所有任务已完成！")
    
    # 进度提示
    print("\n💡 进度提示")
    print("-" * 70)
    
    if stats['percent'] == 100:
        print("  🎊 恭喜！所有任务已完成！")
    elif stats['percent'] >= 75:
        print("  🚀 项目接近尾声，继续加油！")
    elif stats['percent'] >= 50:
        print("  💪 进度过半，保持势头！")
    elif stats['percent'] >= 25:
        print("  🌱 良好开端，持续推进！")
    else:
        print("  🏁 新的征程，从第一步开始！")
    
    print("\n" + "=" * 70)


def save_report(data: dict, stats: dict, output_file: str = "PROGRESS-REPORT.md"):
    """保存进度报告到文件"""
    
    report = f"""# PlugVerse 任务进度报告

**更新时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 总体统计

- **总任务数:** {stats['total']}
- **已完成:** {stats['completed']} ✅
- **未完成:** {stats['pending']} ⬜
- **完成率:** {stats['percent']:.1f}%

## 📈 按阶段进度

"""
    
    phase_names = {
        'Phase 1': '🏗️ 核心框架',
        'Phase 2': '🔌 首个插件',
        'Phase 3': '🎨 前端 UI',
        'Phase 4': '🌟 插件生态'
    }
    
    for phase_id, name in phase_names.items():
        if phase_id in stats['by_phase']:
            phase_stats = stats['by_phase'][phase_id]
            percent = (phase_stats['completed'] / phase_stats['total'] * 100) if phase_stats['total'] > 0 else 0
            report += f"### {name}\n"
            report += f"- 进度：{phase_stats['completed']}/{phase_stats['total']} ({percent:.1f}%)\n"
            report += f"- 进度条：{print_progress_bar(phase_stats['completed'], phase_stats['total'])}\n\n"
    
    # 收集所有任务
    all_tasks = []
    for phase in data['phases']:
        for section in phase['sections']:
            for subsection in section['subsections']:
                for task in subsection['tasks']:
                    all_tasks.append({
                        'phase': phase['id'],
                        'section': section['id'],
                        'subsection': subsection['id'],
                        'name': task['name'],
                        'completed': task['completed']
                    })
    
    report += "## ✅ 已完成的任务\n\n"
    completed_tasks = [t for t in all_tasks if t['completed']]
    for task in completed_tasks[-10:]:
        report += f"- [x] {task['name']}\n"
    
    if not completed_tasks:
        report += "*暂无完成的任务*\n\n"
    
    report += "\n## ⬜ 待办任务\n\n"
    pending_tasks = [t for t in all_tasks if not t['completed']][:20]
    for task in pending_tasks:
        report += f"- [ ] {task['name']}\n"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 详细报告已保存到：{output_file}")


def main():
    """主函数"""
    
    tasks_file = "TASKS.md"
    
    if not Path(tasks_file).exists():
        print(f"❌ 错误：找不到 {tasks_file}")
        return
    
    print(f"📖 解析 {tasks_file}...")
    data = parse_tasks_md(tasks_file)
    
    print(f"📊 计算统计数据...")
    stats = calculate_stats(data)
    
    # 显示仪表板
    display_dashboard(data, stats)
    
    # 保存报告
    save_report(data, stats)
    
    # 显示快速命令
    print("\n🔧 快捷命令:")
    print("-" * 70)
    print("  python progress.py          # 查看进度仪表板")
    print("  python progress.py --json   # 输出 JSON 格式")
    print("  python progress.py --watch  # 实时监控模式（每 5 秒刷新）")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    if '--json' in sys.argv:
        # JSON 输出模式
        tasks_file = "TASKS.md"
        if Path(tasks_file).exists():
            data = parse_tasks_md(tasks_file)
            stats = calculate_stats(data)
            print(json.dumps({'stats': stats, 'data': data}, indent=2, ensure_ascii=False))
    else:
        main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Error Logger - Tự động ghi lỗi từ Odoo vào BAO_CAO_LOI.txt
Chạy script này khi muốn monitor lỗi
"""

import subprocess
import re
import sys
from datetime import datetime
from pathlib import Path

# File báo cáo
BAO_CAO_FILE = Path('/home/quang/TTDN-15-01-N1/BAO_CAO_LOI.txt')

# Regex pattern để detect lỗi
ERROR_PATTERNS = [
    r'ERROR',
    r'CRITICAL',
    r'Traceback',
    r'Exception',
    r'AttributeError',
    r'ValueError',
    r'TypeError',
    r'ImportError',
    r'ModuleNotFoundError',
    r'KeyError',
    r'FileNotFoundError',
    r'ConnectionError',
    r'DatabaseError',
    r'OperationalError',
]

def get_error_type(line):
    """Phân loại loại lỗi"""
    if 'CRITICAL' in line:
        return 'CRITICAL'
    elif 'ERROR' in line:
        return 'ERROR'
    elif 'Traceback' in line or 'Exception' in line:
        return 'EXCEPTION'
    elif 'WARNING' in line or 'WARN' in line:
        return 'WARNING'
    return 'ERROR'

def is_error_line(line):
    """Kiểm tra dòng có phải lỗi không"""
    for pattern in ERROR_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    return False

def save_error_to_file(error_block):
    """Lưu lỗi vào file báo cáo"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(BAO_CAO_FILE, 'a', encoding='utf-8') as f:
            f.write(f'\n[Lỗi #{get_error_count() + 1}]\n')
            f.write(f'Thời gian: {timestamp}\n')
            f.write(f'Loại: {get_error_type(error_block)}\n')
            f.write(f'\nThông báo lỗi:\n')
            f.write('---\n')
            f.write(error_block)
            f.write('\n---\n')
            f.write('\n')
        
        print(f'✅ Đã lưu lỗi lúc {timestamp}')
    except Exception as e:
        print(f'❌ Lỗi khi lưu báo cáo: {e}')

def get_error_count():
    """Lấy số lỗi đã ghi"""
    try:
        with open(BAO_CAO_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            count = content.count('[Lỗi #')
            return count
    except:
        return 0

def monitor_docker_logs():
    """Monitor Docker logs real-time"""
    print('🔍 Bắt đầu monitor lỗi từ Odoo...')
    print('📝 Lỗi sẽ tự động được lưu vào BAO_CAO_LOI.txt')
    print('⏹️  Nhấn Ctrl+C để dừng\n')
    
    try:
        # Chạy command lấy logs từ Docker
        cmd = ['sudo', 'docker', 'compose', 'logs', '-f', '--tail=50', 'odoo_app']
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd='/home/quang/TTDN-15-01-N1'
        )
        
        error_buffer = ''
        
        for line in process.stdout:
            line = line.strip()
            
            # In ra terminal để user thấy
            print(line)
            
            # Kiểm tra nếu là dòng lỗi
            if is_error_line(line):
                error_buffer += line + '\n'
            elif error_buffer and line and not line.startswith('['):
                # Tiếp tục ghi chi tiết lỗi
                error_buffer += line + '\n'
            elif error_buffer and (line.startswith('[') or not line):
                # Kết thúc block lỗi - lưu vào file
                if error_buffer.strip():
                    save_error_to_file(error_buffer)
                error_buffer = ''
        
        process.wait()
        
    except KeyboardInterrupt:
        print('\n\n⏹️  Đã dừng monitor')
        if error_buffer.strip():
            save_error_to_file(error_buffer)
    except FileNotFoundError:
        print('❌ Lỗi: docker-compose không tìm được')
        print('💡 Cài đặt: sudo apt install docker-compose -y')
    except Exception as e:
        print(f'❌ Lỗi: {e}')

def monitor_file_logs():
    """Monitor từ log file Odoo (alternative)"""
    print('🔍 Bắt đầu monitor từ Odoo log file...')
    log_file = Path('/home/quang/TTDN-15-01-N1/odoo.log')
    
    if not log_file.exists():
        print(f'⚠️  File log không tìm được: {log_file}')
        print('💡 Thử monitor Docker logs thay vì...\n')
        monitor_docker_logs()
        return
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            # Đi tới cuối file
            f.seek(0, 2)
            
            print(f'📝 Monitoring: {log_file}')
            print('⏹️  Nhấn Ctrl+C để dừng\n')
            
            error_buffer = ''
            
            while True:
                line = f.readline()
                
                if not line:
                    import time
                    time.sleep(0.5)
                    continue
                
                line = line.strip()
                print(line)
                
                if is_error_line(line):
                    error_buffer += line + '\n'
                elif error_buffer and line and not line.startswith('['):
                    error_buffer += line + '\n'
                elif error_buffer and (line.startswith('[') or not line):
                    if error_buffer.strip():
                        save_error_to_file(error_buffer)
                    error_buffer = ''
    
    except KeyboardInterrupt:
        print('\n\n⏹️  Đã dừng monitor')
        if error_buffer.strip():
            save_error_to_file(error_buffer)
    except Exception as e:
        print(f'❌ Lỗi: {e}')

if __name__ == '__main__':
    # Kiểm tra option
    if len(sys.argv) > 1 and sys.argv[1] == 'file':
        monitor_file_logs()
    else:
        # Mặc định monitor Docker logs
        monitor_docker_logs()

#!/usr/bin/env python3
# categorize_logs.py
# 简单脚本：按事件重组日志，筛选 ERROR/Exception/Traceback，排除 404 NOT_FOUND + InfusionPatientDrug，然后按关键字分类并输出文件与 summary

import os
import re
import sys
import argparse
from datetime import datetime

timestamp_re = re.compile(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")
level_re = re.compile(r"^\s*(?:INFO|WARN|ERROR|DEBUG|FATAL|TRACE)\b", re.IGNORECASE)
error_check = re.compile(r"ERROR|Exception|Traceback", re.IGNORECASE)
exclude_404 = re.compile(r"404\s+NOT[_ ]?FOUND", re.IGNORECASE)
exclude_ipd = re.compile(r"InfusionPatientDrug", re.IGNORECASE)

categories = [
    ("infusion-patient-drug", re.compile(r"InfusionPatientDrug", re.IGNORECASE)),
    ("resource-not-found", re.compile(r"ResourceNotFoundException|404\s+NOT[_ ]?FOUND|not found:", re.IGNORECASE)),
    ("auth-security", re.compile(r"AccessDeniedException|AuthenticationException|ExceptionTranslationFilter|SessionManagementFilter|AccessDenied|Authentication|403\s+FORBIDDEN", re.IGNORECASE)),
    ("database-sql", re.compile(r"SQLException|DataAccessException|SQLSyntaxErrorException|deadlock|constraint violation|could not prepare statement|JDBC", re.IGNORECASE)),
    ("null-illegal", re.compile(r"NullPointerException|IllegalArgumentException|IllegalStateException", re.IGNORECASE)),
    ("container-tomcat", re.compile(r"ErrorReportValve|CoyoteAdapter|Http11Processor|RemoteIpValve|Tomcat", re.IGNORECASE)),
    ("timeout-network", re.compile(r"Timeout|ConnectTimeout|SocketTimeoutException|ReadTimeoutException|Connection refused", re.IGNORECASE)),
    ("spring-bean", re.compile(r"BeanCreationException|NoSuchBeanDefinitionException|org\\.springframework", re.IGNORECASE)),
]


def ensure_dir(p):
    os.makedirs(p, exist_ok=True)


def classify_and_write(block, hdr, outdir, counts, combined_path):
    # 排除规则
    if exclude_404.search(block) and exclude_ipd.search(block):
        return
    # 依序匹配分类
    for name, pat in categories:
        if pat.search(block):
            p = os.path.join(outdir, f"{name}.txt")
            with open(p, "a", encoding="utf-8") as fh:
                fh.write(hdr)
                fh.write(block)
                fh.write("\n")
            counts[name] = counts.get(name, 0) + 1
            with open(combined_path, "a", encoding="utf-8") as cf:
                cf.write(hdr)
                cf.write(block)
                cf.write("\n")
            return
    # 未匹配 -> other
    p = os.path.join(outdir, "other.txt")
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(hdr)
        fh.write(block)
        fh.write("\n")
    counts["other"] = counts.get("other", 0) + 1
    with open(combined_path, "a", encoding="utf-8") as cf:
        cf.write(hdr)
        cf.write(block)
        cf.write("\n")


def process_files(paths, outdir):
    ensure_dir(outdir)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    combined_path = os.path.join(outdir, f"combined-{timestamp}.txt")
    counts = {}
    for path in paths:
        if not os.path.isfile(path):
            print(f"找不到檔案: {path}", file=sys.stderr)
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            current_lines = []
            start_line = 1
            line_no = 0
            for line in f:
                line_no += 1
                is_boundary = bool(timestamp_re.match(line) or level_re.match(line))
                if is_boundary and current_lines:
                    block = ''.join(current_lines)
                    if error_check.search(block):
                        hdr = f"---- FILE: {path} START_LINE: {start_line} ----\n"
                        classify_and_write(block, hdr, outdir, counts, combined_path)
                    current_lines = [line]
                    start_line = line_no
                else:
                    if not current_lines:
                        start_line = line_no
                        current_lines = [line]
                    else:
                        current_lines.append(line)
            # 處理最後一個 block
            if current_lines:
                block = ''.join(current_lines)
                if error_check.search(block):
                    hdr = f"---- FILE: {path} START_LINE: {start_line} ----\n"
                    classify_and_write(block, hdr, outdir, counts, combined_path)
    # 寫入 summary
    summary_path = os.path.join(outdir, f"summary-{timestamp}.txt")
    with open(summary_path, "w", encoding="utf-8") as s:
        s.write(f"分類匯總 - {timestamp}\n輸出目錄: {outdir}\n\n")
        for k in sorted(counts.keys()):
            s.write(f"{k}: {counts[k]}\n")
        s.write('\n生成檔案列表:\n')
        for fn in sorted(os.listdir(outdir)):
            fp = os.path.join(outdir, fn)
            s.write(f"{fn} - {os.path.getsize(fp)} bytes\n")
    print('完成，輸出目錄:', outdir)
    print('摘要:', summary_path)


def main():
    parser = argparse.ArgumentParser(description='按錯誤類別分類日誌事件並輸出到目錄')
    parser.add_argument('paths', nargs='+', help='要分析的日誌檔案路徑')
    parser.add_argument('-o', '--outdir', help='輸出目錄（預設放在第一個日誌相同目錄）')
    args = parser.parse_args()
    if args.outdir:
        outdir = args.outdir
    else:
        first_dir = os.path.dirname(os.path.abspath(args.paths[0])) or os.getcwd()
        outdir = os.path.join(first_dir, 'categorized-' + datetime.now().strftime('%Y%m%dT%H%M%S'))
    process_files(args.paths, outdir)


if __name__ == '__main__':
    main()

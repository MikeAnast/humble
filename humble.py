#! /usr/bin/env python3

# humble (HTTP Headers Analyzer)
#
# MIT License
#
# Copyright (c) 2020-2023 Rafa 'Bluesman' Faura (rafael.fcucalon@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# ADVICE:
# Use the information provided by this humble program wisely. There is *far*
# more merit in teaching, learning and helping others than in harming,
# attacking or taking advantage. Don't just be a 'script kiddie': if this
# really interests you, learn, research and become a Security Analyst!.

# GREETINGS:
# María Antonia, Fernando, Joanna, Eduardo, Ana, Iván, Luis Joaquín, Juan
# Carlos, David, Carlos, Juán, Alejandro, Pablo, Íñigo, Naiara, Ricardo,
# Gabriel, Miguel Angel, David (x2), Sergio, Marta, Alba, Montse & Eloy.

from fpdf import FPDF
from time import time
from datetime import datetime
from os import linesep, path, remove
from colorama import Fore, Style, init
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import sys
import requests
import tldextract

A_FILE = 'analysis_h.txt'
BOLD_S = ("[0.", "HTTP R", "[1.", "[2.", "[3.", "[4.", "[5.", "[Cabeceras")
BRI_R = Style.BRIGHT + Fore.RED
CAN_S = ': https://caniuse.com/?search='
CLI_E = [400, 401, 402, 403, 405, 406, 409, 410, 411, 412, 413, 414, 415, 416,
         417, 421, 422, 423, 424, 425, 426, 428, 429, 431, 451]
GIT_U = "https://github.com/rfc-st/humble"
INS_S = 'http:'
# https://data.iana.org/TLD/tlds-alpha-by-domain.txt
NON_RU_TLDS = ['CYMRU', 'GURU', 'PRU']
RU_DESC = '[bcnt]'
PRG_N = 'humble (HTTP Headers Analyzer) - '
REF_S = 'Ref: '
SEC_S = "https://"
URL_S = ' URL  : '

version = '\r\n' + '(v. 2023-05-13)' + '\r\n'
now = datetime.now().strftime("%Y/%m/%d - %H:%M:%S")


class PDF(FPDF):

    def header(self):
        self.set_font('Courier', 'B', 10)
        self.set_y(15)
        pdf.set_text_color(0, 0, 0)
        self.cell(0, 5, get_detail('[pdf_t]'), new_x="CENTER", new_y="NEXT",
                  align='C')
        self.ln(1)
        self.cell(0, 5, f"({GIT_U})", align='C')
        if self.page_no() == 1:
            self.ln(9)
        else:
            self.ln(13)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        pdf.set_text_color(0, 0, 0)
        self.cell(0, 10, get_detail('[pdf_p]') + str(self.page_no()) +
                  get_detail('[pdf_po') + '{nb}', align='C')


def pdf_metadata():
    title = get_detail('[pdf_m]', replace=True) + URL
    git_urlc = f"{GIT_U} {version.strip()}"
    pdf.set_author(git_urlc)
    pdf.set_creation_date = now
    pdf.set_creator(git_urlc)
    pdf.set_keywords(get_detail('[pdf_k]', replace=True))
    pdf.set_lang(get_detail('[pdf_l]'))
    pdf.set_subject(get_detail('[pdf_s]', replace=True))
    pdf.set_title(title)
    pdf.set_producer(git_urlc)


def pdf_sections():
    section_dict = {'[0.': '[0section_s]', '[HTTP R': '[0headers_s]',
                    '[1.': '[1missing_s]', '[2.': '[2fingerprint_s]',
                    '[3.': '[3depinsecure_s]', '[4.': '[4empty_s]',
                    '[5.': '[5compat_s]', '[Cabeceras': '[0headers_s]'}
    if match := next((i for i in section_dict if x.startswith(i)), None):
        pdf.start_section(get_detail(section_dict[match]))


def pdf_links(pdfstring):
    links = {URL_S: URL, REF_S: x.partition(REF_S)[2].strip(),
             CAN_S: x.partition(': ')[2].strip()}
    link_h = links.get(pdfstring)
    if pdfstring in (URL_S, REF_S):
        prefix = ' Ref: ' if pdfstring == REF_S else pdfstring
        pdf.write(h=3, txt=prefix)
    else:
        pdf.write(h=3, txt=x[:x.index(": ")+2])
    pdf.set_text_color(0, 0, 255)
    pdf.cell(w=2000, h=3, txt=x[x.index(": ")+2:], align="L", link=link_h)


def get_language():
    return 'details_es.txt' if args.lang == 'es' else 'details.txt'


def get_details_lines():
    details_file = 'details_es.txt' if args.lang == 'es' else 'details.txt'
    with open(details_file, encoding='utf8') as rf:
        return rf.readlines()


def save_extract_totals(t_cnt):
    with open(A_FILE, 'a+', encoding='utf8') as a_history, \
         open(A_FILE, 'r', encoding='utf8') as c_history:
        a_history.write(f"{now} ; {URL} ; {m_cnt} ; {f_cnt} ; {i_cnt[0]} ; \
{e_cnt} ; {t_cnt}\n")
        url_ln = [line for line in c_history if URL in line]
        if not url_ln:
            return ("First",) * 5
        date_var = max(line.split(" ; ")[0] for line in url_ln)
        for line in url_ln:
            if date_var in line:
                _, _, mh_cnt, fh_cnt, ih_cnt, eh_cnt, \
                    th_cnt = line.strip().split(' ; ')
                break
        return mh_cnt, fh_cnt, ih_cnt, eh_cnt, th_cnt


def compare_totals(mh_cnt, m_cnt, fh_cnt, f_cnt, ih_cnt, i_cnt, eh_cnt, e_cnt,
                   th_cnt, t_cnt):
    if mh_cnt == "First":
        return [get_detail('[first_one]', replace=True)] * 5
    mhr_cnt = m_cnt - int(mh_cnt)
    fhr_cnt = f_cnt - int(fh_cnt)
    ihr_cnt = i_cnt[0] - int(ih_cnt)
    ehr_cnt = e_cnt - int(eh_cnt)
    thr_cnt = t_cnt - int(th_cnt)
    return [f'+{n}' if n > 0 else str(n) for n in [mhr_cnt, fhr_cnt, ihr_cnt,
                                                   ehr_cnt, thr_cnt]]


def file_exists(filepath):
    if not path.exists(filepath):
        print("")
        print(get_detail('[no_analysis]'))
        print("")
        sys.exit()


def url_analytics():
    file_exists(A_FILE)
    with open(A_FILE, 'r', encoding='utf8') as c_history:
        analysis_stats = extract_metrics(c_history)
    print("")
    print(f"{get_detail('[stats_analysis]', replace=True)}{URL}")
    print("")
    for key, value in analysis_stats.items():
        if not value or not key.startswith(' '):
            key = f"{Style.BRIGHT}{key}{Style.RESET_ALL}"
            print(f"{key}{value}")
        else:
            print(f"{key}: {value}")


def extract_first_metrics(url_ln):
    first_a = min(f"{line.split(' ; ')[0]}" for line in url_ln)
    latest_a = max(f"{line.split(' ; ')[0]}" for line in url_ln)
    date_w = [(line.split(" ; ")[0],
               int(line.strip().split(" ; ")[-1])) for line in url_ln]
    best_d, best_w = min(date_w, key=lambda x: x[1])
    worst_d, worst_w = max(date_w, key=lambda x: x[1])
    return (first_a, latest_a, best_d, best_w, worst_d, worst_w)


def extract_second_metrics(url_ln, index, total_a):
    metric_c = len([line for line in url_ln if int(line.split(' ; ')[index])
                    == 0])
    return f"{metric_c / total_a * 100:.0f}% ({metric_c}\
{get_detail('[pdf_po]', replace=True)}{total_a})"


def extract_third_metrics(url_ln):
    fields = [line.strip().split(';') for line in url_ln]
    total_miss, total_fng, total_dep, total_ety = \
        [sum(int(f[i]) for f in fields) for i in range(2, 6)]
    num_a = len(url_ln)
    avg_miss, avg_fng, avg_dep, avg_ety = \
        [t // num_a for t in (total_miss, total_fng, total_dep, total_ety)]
    return (avg_miss, avg_fng, avg_dep, avg_ety)


def extract_year_metrics(url_ln):
    year_cnt = {}
    for line in url_ln:
        year = int(line.split(' ; ')[0][:4])
        if year not in year_cnt:
            year_cnt[year] = (1, int(line.split(' ; ')[-1]))
        else:
            year_cnt[year] = (year_cnt[year][0] + 1,
                              year_cnt[year][1] + int(line.split(' ; ')[-1]))
    years_str = [f" {year}: {year_cnt[year][0]} {get_detail('[analysis_y]')}"
                 for year in sorted(year_cnt.keys())]
    avg_w_y = (sum(count[1] for count in year_cnt.values()) // len(year_cnt))
    return "".join(years_str), avg_w_y


def extract_additional_metrics(url_ln):
    avg_w = int(sum(int(line.split(' ; ')[-1]) for line in url_ln) /
                len(url_ln))
    year_a, avg_w_y = extract_year_metrics(url_ln)
    return (avg_w, year_a, avg_w_y)


def extract_metrics(c_history):
    url_ln = [line for line in c_history if URL in line]
    if not url_ln:
        print("")
        print(get_detail('[no_analysis]'))
        print("")
        sys.exit()
    total_a = len(url_ln)
    first_m = extract_first_metrics(url_ln)
    second_m = [extract_second_metrics(url_ln, i, total_a) for i in
                range(2, 6)]
    third_m = extract_third_metrics(url_ln)
    additional_m = extract_additional_metrics(url_ln)
    return print_metrics(total_a, first_m, second_m, third_m, additional_m)


def print_metrics(total_a, first_m, second_m, third_m, additional_m):
    basic_m = {'[main]': "", '[total_analysis]': total_a,
               '[first_analysis_a]': first_m[0], '[latest_analysis]':
               first_m[1], '[best_analysis]': f"{first_m[2]} \
{get_detail('[total_warnings]', replace=True)}{first_m[3]})",
               '[worst_analysis]': f"{first_m[4]} \
{get_detail('[total_warnings]', replace=True)}{first_m[5]})\n"}
    error_m = {'[analysis_y]': "", '[no_missing]': second_m[0],
               '[no_fingerprint]': second_m[1], '[no_ins_deprecated]':
               second_m[2], '[no_empty]': second_m[3] + "\n"}
    warning_m = {'[averages]': "", '[average_warnings]': f"{additional_m[0]}",
                 '[average_warnings_year]': f"{additional_m[2]}"}
    averages_m = {'[average_miss]': f"{third_m[0]}", '[average_fng]':
                  f"{third_m[1]}", '[average_dep]': f"{third_m[2]}",
                  '[average_ety]': f"{third_m[3]}\n"}
    analysis_year_m = {'[analysis_year]': f"\n{additional_m[1]}"}
    totals_m = basic_m | error_m | warning_m | averages_m | analysis_year_m
    return {get_detail(key, replace=True): value for key, value in
            totals_m.items()}


def analysis_time():
    print(".:")
    print("")
    print_detail_l('[analysis_time]')
    print(round(end - start, 2), end="")
    print_detail_l('[analysis_time_sec]')
    t_cnt = m_cnt + f_cnt + i_cnt[0] + e_cnt
    mh_cnt, fh_cnt, ih_cnt, eh_cnt, th_cnt = save_extract_totals(t_cnt)
    mhr_cnt, fhr_cnt, ihr_cnt, ehr_cnt,\
        thr_cnt = compare_totals(mh_cnt, m_cnt, fh_cnt, f_cnt, ih_cnt, i_cnt,
                                 eh_cnt, e_cnt, th_cnt, t_cnt)
    print("")
    analysis_detail(mhr_cnt, fhr_cnt, ihr_cnt, ehr_cnt, t_cnt, thr_cnt)


def clean_output():
    # Kudos to Aniket Navlur!!!: https://stackoverflow.com/a/52590238
    sys.stdout.write('\x1b[1A\x1b[2K\x1b[1A\x1b[2K\x1b[1A\x1b[2K')


def print_path(filename):
    clean_output()
    print("")
    print_detail_l('[report]')
    print(path.abspath(filename))


def print_ok():
    print_detail('[ok]')


def print_header(header):
    if not args.output:
        print(f"{BRI_R} {header}")
    else:
        print(f" {header}")


def print_header_fng(header):
    prefix, _, suffix = [x.strip() for x in header.partition(' [')]
    if args.output:
        print(f" {header}")
    elif '[' in header:
        print(f"{BRI_R} {prefix}{Style.NORMAL}{Fore.RESET} [{suffix}")
    else:
        print(f"{BRI_R} {header}")


def print_summary():
    if not args.output:
        clean_output()
        print("")
        banner = '''  _                     _     _
 | |__  _   _ _ __ ___ | |__ | | ___
 | '_ \\| | | | '_ ` _ \\| '_ \\| |/ _ \\
 | | | | |_| | | | | | | |_) | |  __/
 |_| |_|\\__,_|_| |_| |_|_.__/|_|\\___|
'''
        print(banner)
        print(f" ({GIT_U})")
    elif args.output != 'pdf':
        print("")
        print_detail('[humble]', 2)
    print(linesep.join(['']*2))
    print_detail_r('[0section]')
    print_detail_l('[info]')
    print(f" {now}")
    print(f' URL  : {URL}')
    if status_code in CLI_E:
        id_mode = f"[http_{status_code}]"
        print(f"{get_detail(id_mode, replace=True)}")


def print_headers():
    if args.ret:
        print(linesep.join(['']*2))
        print_detail_r('[0headers]')
        for key, value in sorted(headers.items()):
            if not args.output:
                print(f" {Fore.CYAN}{key}:", value)
            else:
                print(f" {key}:", value)
    print('\n')


def print_details(short_d, long_d, id_mode, i_cnt):
    print_detail_r(short_d, is_red=True)
    if not args.brief:
        print_detail(long_d, 2) if id_mode == 'd' else print_detail(long_d, 3)
    i_cnt[0] += 1
    return i_cnt


def print_detail(id_mode, num_lines=1):
    idx = details_f.index(id_mode + '\n')
    print(details_f[idx+1], end='')
    for i in range(1, num_lines+1):
        if idx+i+1 < len(details_f):
            print(details_f[idx+i+1], end='')


def print_detail_l(id_mode):
    for i, line in enumerate(details_f):
        if line.startswith(id_mode):
            print(details_f[i+1].replace('\n', ''), end='')


def print_detail_r(id_mode, is_red=False):
    style_str = BRI_R if is_red else Style.BRIGHT
    for i, line in enumerate(details_f):
        if line.startswith(id_mode):
            if not args.output:
                print(style_str + details_f[i+1], end='')
            else:
                print(details_f[i+1], end='')
            if not is_red:
                print("")


def get_detail(id_mode, replace=False):
    for i, line in enumerate(details_f):
        if line.startswith(id_mode):
            return (details_f[i+1].replace('\n', '')) if replace else \
                details_f[i+1]


def python_ver():
    if sys.version_info < (3, 9):
        print("")
        print_detail('[python]', 2)
        sys.exit()


def print_guides():
    print("")
    print_detail('[guides]')
    with open('guides.txt', 'r', encoding='utf8') as gd:
        for line in gd:
            if line.startswith('['):
                print(f"{Style.BRIGHT}{line}", end='')
            else:
                print(f"{line}", end='')


def ua_ru_analysis(suffix, country):
    print("")
    if suffix == "UA" or country == 'Ukraine':
        detail = '[analysis_ua_output]' if args.output else '[analysis_ua]'
    elif suffix == "RU" and suffix not in NON_RU_TLDS or country == 'Russia':
        detail = RU_DESC
    print_detail(detail, 2) if detail == RU_DESC else print_detail(detail)
    if detail == RU_DESC:
        sys.exit()


def fingerprint_headers(headers, l_fng, l_fng_ex):
    f_cnt = 0
    matching_headers = sorted([header for header in headers if any(elem.lower()
                               in headers for elem in l_fng)])
    l_fng = [x.title() for x in l_fng]
    matching_headers = [x.title() for x in matching_headers]
    for key in matching_headers:
        if key in l_fng:
            if not args.brief:
                index_fng = l_fng.index(key)
                print_header_fng(l_fng_ex[index_fng])
                print(f" {headers[key]}")
                print("")
            else:
                print_header(key)
            f_cnt += 1
    return f_cnt


def analysis_detail(mhr_cnt, fhr_cnt, ihr_cnt, ehr_cnt, t_cnt, thr_cnt):
    print(" ")
    print(f"{(print_detail_l('[miss_cnt]') or '')[:-1]}{m_cnt} ({mhr_cnt})")
    print(f"{(print_detail_l('[finger_cnt]') or '')[:-1]}{f_cnt} ({fhr_cnt})")
    print(f"{(print_detail_l('[ins_cnt]') or '')[:-1]}{i_cnt[0]} ({ihr_cnt})")
    print(f"{(print_detail_l('[empty_cnt]') or '')[:-1]}{e_cnt} ({ehr_cnt})")
    print("")
    print(f"{(print_detail_l('[total_cnt]') or '')[:-1]}{t_cnt} ({thr_cnt})")
    print(""), print(".:"), print("")


def detail_exceptions(id_exception, exception_v):
    clean_output()
    print("")
    print_detail(id_exception)
    raise SystemExit from exception_v


def request_exceptions():
    headers = {}
    status_c = None
    try:
        # Yes: Server certificates should be verified during SSL/TLS
        # connections. Despite this, I think 'verify=False' would benefit
        # analysis of URLs with self-signed certificates, associated with
        # development environments, etc.
        r = requests.get(URL, verify=False, headers=c_headers, timeout=15)
        status_c = r.status_code
        headers = r.headers
        r.raise_for_status()
    except requests.exceptions.HTTPError as err_http:
        if err_http.response.status_code == 407:
            detail_exceptions('[e_proxy]', err_http)
        if str(err_http.response.status_code).startswith('5'):
            detail_exceptions('[e_serror]', err_http)
    except tuple(exception_d.keys()) as e:
        ex = exception_d.get(type(e))
        if ex and (not callable(ex) or ex(e)):
            detail_exceptions(ex, e)
    except requests.exceptions.RequestException as err:
        raise SystemExit from err
    return headers, status_c


init(autoreset=True)

parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                        description=PRG_N + GIT_U)
parser.add_argument("-a", dest='URL_A', action="store_true", help="Show \
statistics of the analysis performed on the specified URL.")
parser.add_argument("-b", dest='brief', action="store_true", help="Show a \
brief analysis; if omitted, a detailed analysis will be shown.")
parser.add_argument("-g", dest='guides', action="store_true", help="Show \
guidelines on securing most used web servers/services.")
parser.add_argument("-l", dest='lang', choices=['es'], help="Displays the \
analysis in the indicated language; if omitted, English will be used.")
parser.add_argument("-o", dest='output', choices=['html', 'pdf', 'txt'],
                    help="Save analysis to file (URL_yyyymmdd.ext).")
parser.add_argument("-r", dest='ret', action="store_true", help="Show HTTP \
response headers and a detailed analysis.")
parser.add_argument('-u', type=str, dest='URL', help="URL to analyze, with \
schema. E.g., https://google.com")
parser.add_argument("-v", "--version", action='version', version=version,
                    help="show version")

args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])

if any([args.brief, args.lang, args.output, args.ret]) and args.URL is None:
    parser.error("The '-u' option is required.")

URL = args.URL

details_file = get_language()
details_f = get_details_lines()

python_ver()

if args.guides:
    print_guides()
    sys.exit()

if args.URL_A:
    url_analytics()
    sys.exit()

start = time()

# https://github.com/rfc-st/humble/blob/master/CODE_OF_CONDUCT.md#update-20220326
sffx = tldextract.extract(URL).suffix[-2:].upper()
cnty = requests.get('https://ipapi.co/country_name/').text.strip()
if (sffx in ("UA", 'RU') and sffx not in NON_RU_TLDS) or cnty in ('Ukraine',
                                                                  'Russia'):
    ua_ru_analysis(sffx, cnty)
else:
    if not args.URL_A:
        detail = '[analysis_output]' if args.output else '[analysis]'
        print("")
        print_detail(detail)

# Regarding 'dh key too small' errors: https://stackoverflow.com/a/41041028
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
try:
    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS \
        += ':HIGH:!DH:!aNULL'
except AttributeError:
    pass

exception_d = {
    requests.exceptions.ConnectionError: '[e_404]',
    requests.exceptions.InvalidSchema: '[e_schema]',
    requests.exceptions.InvalidURL: '[e_invalid]',
    requests.exceptions.MissingSchema: '[e_schema]',
    requests.exceptions.SSLError: None,
    requests.exceptions.Timeout: '[e_timeout]',
}
requests.packages.urllib3.disable_warnings()

c_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}

headers, status_code = request_exceptions()

# Export analysis
date_now = datetime.now().strftime("%Y%m%d")
extension = "t.txt" if args.output in ['pdf', 'html'] else ".txt"

if args.output:
    orig_stdout = sys.stdout
    name_s = tldextract.extract(URL)
    name_e = f"{name_s.domain}_headers_{date_now}{extension}"
    f = open(name_e, 'w', encoding='utf8')
    sys.stdout = f

print_summary()
print_headers()

# Report - 1. Missing HTTP Security Headers
m_cnt = 0

print_detail_r('[1missing]')

l_miss = ['Cache-Control', 'Clear-Site-Data', 'Content-Type',
          'Cross-Origin-Embedder-Policy', 'Cross-Origin-Opener-Policy',
          'Cross-Origin-Resource-Policy', 'Content-Security-Policy', 'NEL',
          'Permissions-Policy', 'Referrer-Policy', 'Strict-Transport-Security',
          'X-Content-Type-Options']

l_detail = ['[mcache]', '[mcsd]', '[mctype]', '[mcoe]', '[mcop]', '[mcor]',
            '[mcsp]', '[mnel]', '[mpermission]', '[mreferrer]', '[msts]',
            '[mxcto]', '[mxfo]']

missing_headers_lower = {k.lower(): v for k, v in headers.items()}

for i, key in enumerate(l_miss):
    if key.lower() not in missing_headers_lower:
        print_header(key)
        if not args.brief:
            print_detail(l_detail[i], 2)
        m_cnt += 1

if not (headers.get('X-Frame-Options') or 'frame-ancestors' in
        headers.get('Content-Security-Policy', '')):
    print_header('X-Frame-Options')
    if not args.brief:
        print_detail("[mxfo]", 2)
    m_cnt += 1

if not any(elem.lower() in headers for elem in l_miss):
    print_header('X-Frame-Options')
    if not args.brief:
        print_detail("[mxfo]", 2)
    m_cnt += 1

l_miss.append('X-Frame-Options')

if args.brief and m_cnt != 0:
    print("")

if m_cnt == 0:
    print_ok()

print("")

# Report - 2. Fingerprinting through headers/values

# Certain content of the file 'fingerprint.txt' has been made possible by:
#
# OWASP Secure Headers Project
# https://github.com/OWASP/www-project-secure-headers/blob/master/LICENSE.txt
print_detail_r('[2fingerprint]')

if not args.brief:
    print_detail("[afgp]")

l_fng = []
l_fng_ex = []

with open('fingerprint.txt', 'r', encoding='utf8') as fn:
    for line in fn:
        l_fng.append(line.partition(' [')[0].strip())
        l_fng_ex.append(line.strip())

f_cnt = fingerprint_headers(headers, l_fng, l_fng_ex)

if args.brief and f_cnt != 0:
    print("")

if f_cnt == 0:
    print_ok()

print("")

# Report - 3. Deprecated HTTP Headers/Protocols and Insecure values
i_cnt = [0]

print_detail_r('[3depinsecure]')

if not args.brief:
    print_detail("[aisc]")

l_ins = ['Access-Control-Allow-Methods', 'Access-Control-Allow-Origin',
         'Allow', 'Content-Type', 'Etag', 'Expect-CT', 'Feature-Policy',
         'Onion-Location', 'Public-Key-Pins', 'Set-Cookie', 'Server-Timing',
         'Timing-Allow-Origin', 'X-Content-Security-Policy',
         'X-Content-Security-Policy-Report-Only', 'X-DNS-Prefetch-Control',
         'X-Download-Options', 'X-Pad', 'X-Permitted-Cross-Domain-Policies',
         'X-Pingback', 'X-Runtime', 'X-Webkit-CSP',
         'X-Webkit-CSP-Report-Only', 'X-XSS-Protection']

l_methods = ['PUT', 'HEAD', 'OPTIONS', 'CONNECT', 'TRACE', 'TRACK', 'DELETE',
             'DEBUG', 'PATCH', '*']

l_cache = ['no-cache', 'no-store', 'must-revalidate']

l_csp_directives = ['base-uri', 'child-src', 'connect-src', 'default-src',
                    'font-src', 'form-action', 'frame-ancestors', 'frame-src',
                    'img-src', 'manifest-src', 'media-src', 'navigate-to',
                    'object-src', 'prefetch-src', 'report-to',
                    'require-trusted-types-for', 'sandbox', 'script-src',
                    'script-src-elem', 'script-src-attr', 'style-src',
                    'style-src-elem', 'style-src-attr', 'trusted-types',
                    'upgrade-insecure-requests', 'worker-src']

l_csp_deprecated = ['block-all-mixed-content', 'plugin-types', 'referrer',
                    'report-uri', 'require-sri-for']

l_csp_equal = ['nonce', 'sha', 'style-src-elem', 'report-to', 'report-uri']

l_legacy = ['application/javascript', 'application/ecmascript',
            'application/x-ecmascript', 'application/x-javascript',
            'text/ecmascript', 'text/javascript1.0', 'text/javascript1.1',
            'text/javascript1.2', 'text/javascript1.3', 'text/javascript1.4',
            'text/javascript1.5', 'text/jscript', 'text/livescript',
            'text/x-ecmascript', 'text/x-javascript']

# https://github.com/w3c/webappsec-permissions-policy/blob/main/features.md
# https://csplite.com/fp/
l_per_feat = ['accelerometer', 'ambient-light-sensor', 'autoplay', 'battery',
              'bluetooth', 'browsing-topics', 'camera', 'ch-ua', 'ch-ua-arch',
              'ch-ua-bitness', 'ch-ua-full-version', 'ch-ua-full-version-list',
              'ch-ua-mobile', 'ch-ua-model', 'ch-ua-platform',
              'ch-ua-platform-version', 'ch-ua-wow64', 'clipboard-read',
              'clipboard-write', 'conversion-measurement',
              'cross-origin-isolated', 'display-capture', 'document-access',
              'document-write', 'encrypted-media',
              'execution-while-not-rendered',
              'execution-while-out-of-viewport',
              'focus-without-user-activation', 'font-display-late-swap',
              'fullscreen', 'gamepad', 'geolocation', 'gyroscope', 'hid',
              'idle-detection', 'interest-cohort', 'keyboard-map',
              'layout-animations', 'lazyload', 'legacy-image-formats',
              'loading-frame-default-eager', 'local-fonts', 'magnetometer',
              'microphone', 'midi', 'navigation-override', 'oversized-images',
              'payment', 'picture-in-picture', 'publickey-credentials-get',
              'screen-wake-lock', 'serial', 'shared-autofill', 'speaker',
              'speaker-selection', 'sync-script', 'sync-xhr',
              'trust-token-redemption', 'unload', 'unoptimized-images',
              'unoptimized-lossless-images',
              'unoptimized-lossless-images-strict',
              'unoptimized-lossy-images', 'unsized-media', 'usb',
              'vertical-scroll', 'vibrate', 'wake-lock', 'web-share',
              'window-placement', 'xr-spatial-tracking']

l_ref = ['strict-origin', 'strict-origin-when-cross-origin',
         'no-referrer-when-downgrade', 'no-referrer']

# https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag
# https://www.bing.com/webmasters/help/which-robots-metatags-does-bing-support-5198d240
l_robots = ['all', 'indexifembedded', 'max-image-preview', 'max-snippet',
            'max-video-preview', 'noarchive', 'noodp', 'nofollow',
            'noimageindex', 'noindex', 'none', 'nositelinkssearchbox',
            'nosnippet', 'notranslate', 'noydir', 'unavailable_after']

if 'Accept-CH-Lifetime' in headers:
    print_details('[ixacl_h]', '[ixacld]', 'd', i_cnt)

if 'Access-Control-Allow-Methods' in headers:
    methods = headers["Access-Control-Allow-Methods"]
    if any(method in methods for method in l_methods):
        print_detail_r('[imethods_h]', is_red=True)
        if not args.brief:
            match_method = [x for x in l_methods if x in methods]
            match_method_str = ', '.join(match_method)
            print_detail_l("[imethods_s]")
            print(match_method_str)
            print_detail("[imethods]")
        i_cnt[0] += 1

accesso_header = headers.get("Access-Control-Allow-Origin", '').lower()
if accesso_header:
    if (accesso_header in ['*', 'null']) and (not any(val in accesso_header for
                                                      val in ['.*', '*.'])):
        print_details('[iaccess_h]', '[iaccess]', 'd', i_cnt)

if 'Allow' in headers:
    methods = headers["Allow"]
    if any(method in methods for method in l_methods):
        print_detail_r('[imethods_hh]', is_red=True)
        if not args.brief:
            match_method = [x for x in l_methods if x in methods]
            match_method_str = ', '.join(match_method)
            print_detail_l("[imethods_s]")
            print(match_method_str)
            print_detail("[imethods]")
        i_cnt[0] += 1

cache_header = headers.get("Cache-Control", '').lower()
if cache_header and not all(elem in cache_header for elem in l_cache):
    print_details('[icache_h]', '[icache]', 'd', i_cnt)

if ('Clear-Site-Data' in headers) and (URL.startswith(INS_S)):
    print_details('[icsd_h]', '[icsd]', 'd', i_cnt)

if 'Content-DPR' in headers:
    print_details('[ixcdpr_h]', '[ixcdprd]', 'd', i_cnt)

if 'Content-Security-Policy' in headers:
    csp_h = headers['Content-Security-Policy'].lower()
    if any(elem in csp_h for elem in ['unsafe-eval', 'unsafe-inline']):
        print_details('[icsp_h]', '[icsp]', 'm', i_cnt)
    elif not any(elem in csp_h for elem in l_csp_directives):
        print_details('[icsi_h]', '[icsi]', 'd', i_cnt)
    if any(elem in csp_h for elem in l_csp_deprecated):
        print_detail_r('[icsi_d]', is_red=True)
        if not args.brief:
            matches_csp = [x for x in l_csp_deprecated if x in csp_h]
            print_detail_l("[icsi_d_s]")
            print(', '.join(matches_csp))
            print_detail("[icsi_d_r]")
        i_cnt[0] += 1
    if ('=' in csp_h) and not (any(elem in csp_h for elem in l_csp_equal)):
        print_details('[icsn_h]', '[icsn]', 'd', i_cnt)
    if (INS_S in csp_h) and (URL.startswith('https')):
        print_details('[icsh_h]', '[icsh]', 'd', i_cnt)
    if ' * ' in csp_h:
        print_details('[icsw_h]', '[icsw]', 'd', i_cnt)

ctype_header = headers.get('Content-Type', '').lower()
if ctype_header:
    if any(elem in ctype_header for elem in l_legacy):
        print_details('[ictlg_h]', '[ictlg]', 'm', i_cnt)
    if 'html' not in ctype_header:
        print_details('[ictlhtml_h]', '[ictlhtml]', 'd', i_cnt)

if 'Etag' in headers:
    print_details('[ieta_h]', '[ieta]', 'd', i_cnt)

if 'Expect-CT' in headers:
    print_details('[iexct_h]', '[iexct]', 'm', i_cnt)

if 'Feature-Policy' in headers:
    print_details('[iffea_h]', '[iffea]', 'd', i_cnt)

if URL.startswith(INS_S):
    print_details('[ihttp_h]', '[ihttp]', 'd', i_cnt)

if 'Large-Allocation' in headers:
    print_details('[ixlalloc_h]', '[ixallocd]', 'd', i_cnt)

perm_header = headers.get('Permissions-Policy', '').lower()
if perm_header:
    if not any(elem in perm_header for elem in l_per_feat):
        print_details('[ifpoln_h]', '[ifpoln]', 'm', i_cnt)
    if '*' in perm_header:
        print_details('[ifpol_h]', '[ifpol]', 'd', i_cnt)
    if 'none' in perm_header:
        print_details('[ifpoli_h]', '[ifpoli]', 'd', i_cnt)
    if 'document-domain' in perm_header:
        print_detail_r('[ifpold_h]', is_red=True)
        if not args.brief:
            print_detail_l('[ifpold_s]')
            print('document-domain')
            print_detail('[ifpold]')
        i_cnt[0] += 1

if 'Onion-Location' in headers:
    print_details('[ionloc_h]', '[ionloc]', 'm', i_cnt)

if 'Pragma' in headers:
    print_details('[iprag_h]', '[iprag]', 'd', i_cnt)

if 'Public-Key-Pins' in headers:
    print_details('[ipkp_h]', '[ipkp]', 'd', i_cnt)

referrer_header = headers.get('Referrer-Policy', '').lower()
if referrer_header:
    if not any(elem in referrer_header for elem in l_ref):
        print_details('[iref_h]', '[iref]', 'm', i_cnt)
    if 'unsafe-url' in referrer_header:
        print_details('[irefi_h]', '[irefi]', 'd', i_cnt)

if 'Server-Timing' in headers:
    print_details('[itim_h]', '[itim]', 'd', i_cnt)

ck_header = headers.get("Set-Cookie", '').lower()
if ck_header:
    if not (URL.startswith(INS_S)) and not all(elem in ck_header for elem in
                                               ('secure', 'httponly')):
        print_details("[iset_h]", "[iset]", "d", i_cnt)
    if (URL.startswith(INS_S)) and ('secure' in ck_header):
        print_details("[iseti_h]", "[iseti]", "d", i_cnt)
    if "samesite=none" in ck_header and "secure" not in ck_header:
        print_details("[iseti_m]", "[isetm]", "d", i_cnt)

sts_header = headers.get('Strict-Transport-Security', '').lower()
if (sts_header) and not (URL.startswith(INS_S)):
    age = int(''.join(filter(str.isdigit, sts_header)))
    if not all(elem in sts_header for elem in ('includesubdomains',
       'max-age')) or (age is None or age < 31536000):
        print_details('[ists_h]', '[ists]', 'm', i_cnt)
    if ',' in sts_header:
        print_details('[istsd_h]', '[istsd]', 'd', i_cnt)

if (sts_header) and (URL.startswith(INS_S)):
    print_details('[ihsts_h]', '[ihsts]', 'd', i_cnt)

if headers.get('Timing-Allow-Origin', '') == '*':
    print_details('[itao_h]', '[itao]', 'd', i_cnt)

if 'Tk' in headers:
    print_details('[ixtk_h]', '[ixtkd]', 'd', i_cnt)

if 'Warning' in headers:
    print_details('[ixwar_h]', '[ixward]', 'd', i_cnt)

wwwa_header = headers.get('WWW-Authenticate', '').lower()
if (wwwa_header) and (URL.startswith(INS_S)) and ('basic' in wwwa_header):
    print_details('[ihbas_h]', '[ihbas]', 'd', i_cnt)

if 'X-Content-Security-Policy' in headers:
    print_details('[ixcsp_h]', '[ixcsp]', 'd', i_cnt)

if 'X-Content-Security-Policy-Report-Only' in headers:
    print_details('[ixcspr_h]', '[ixcspr]', 'd', i_cnt)

if 'X-Content-Type-Options' in headers:
    if ',' in headers['X-Content-Type-Options']:
        print_details('[ictpd_h]', '[ictpd]', 'd', i_cnt)
    elif 'nosniff' not in headers['X-Content-Type-Options']:
        print_details('[ictp_h]', '[ictp]', 'd', i_cnt)

if headers.get('X-DNS-Prefetch-Control', '') == 'on':
    print_details('[ixdp_h]', '[ixdp]', 'd', i_cnt)

if 'X-Download-Options' in headers:
    print_details('[ixdow_h]', '[ixdow]', 'm', i_cnt)

xfo_header = headers.get('X-Frame-Options', '').lower()
if xfo_header:
    if ',' in xfo_header:
        print_details('[ixfo_h]', '[ixfo]', 'm', i_cnt)
    if 'allow-from' in xfo_header:
        print_details('[ixfod_h]', '[ixfod]', 'm', i_cnt)
    if xfo_header not in ['deny', 'sameorigin']:
        print_details('[ixfoi_h]', '[ixfodi]', 'm', i_cnt)

if 'X-Pad' in headers:
    print_details('[ixpad_h]', '[ixpad]', 'd', i_cnt)

if headers.get('X-Permitted-Cross-Domain-Policies', '') == 'all':
    print_details('[ixcd_h]', '[ixcd]', 'm', i_cnt)

if headers.get('X-Pingback', '').endswith('xmlrpc.php'):
    print_details('[ixpb_h]', '[ixpb]', 'd', i_cnt)

robots_header = headers.get('X-Robots-Tag', '').lower()
if robots_header:
    if not any(elem in robots_header for elem in l_robots):
        print_details('[ixrobv_h]', '[ixrobv]', 'm', i_cnt)
    if 'all' in robots_header:
        print_details('[ixrob_h]', '[ixrob]', 'm', i_cnt)

if 'X-Runtime' in headers:
    print_details('[ixrun_h]', '[ixrun]', 'd', i_cnt)

if 'X-UA-Compatible' in headers:
    print_details('[ixuacom_h]', '[ixuacom]', 'm', i_cnt)

if 'X-Webkit-CSP' in headers:
    print_details('[ixwcsp_h]', '[ixcsp]', 'd', i_cnt)

if 'X-Webkit-CSP-Report-Only' in headers:
    print_details('[ixwcspr_h]', '[ixcspr]', 'd', i_cnt)

if 'X-XSS-Protection' in headers:
    if '0' not in headers["X-XSS-Protection"]:
        print_details('[ixxp_h]', '[ixxp]', 'd', i_cnt)
    if ',' in headers['X-XSS-Protection']:
        print_details('[ixxpd_h]', '[ixxpd]', 'd', i_cnt)

if args.brief and i_cnt[0] != 0:
    print("")

if i_cnt[0] == 0:
    print_ok()

print("")

# Report - 4. Empty HTTP Response Headers Values
e_cnt = 0
empty_s_headers = sorted(headers)
print_detail_r('[4empty]')

if not args.brief:
    print_detail("[aemp]")

for key in empty_s_headers:
    if not headers[key]:
        print_header(key)
        e_cnt += 1

print("") if e_cnt != 0 else print_ok()

print("")

# Report - 5. Browser Compatibility for Enabled HTTP Security Headers
print_detail_r('[5compat]')

l_sec = ['Cache-Control', 'Clear-Site-Data', 'Content-Type',
         'Content-Security-Policy', 'Cross-Origin-Embedder-Policy',
         'Cross-Origin-Opener-Policy', 'Cross-Origin-Resource-Policy', 'NEL',
         'Permissions-Policy', 'Referrer-Policy', 'Strict-Transport-Security',
         'X-Content-Type-Options', 'X-Frame-Options']

header_matches = [header for header in l_sec if header in headers]

if header_matches:
    for key in header_matches:
        output_string = "  " if args.output == 'html' else " "
        key_string = Fore.CYAN + key + Fore.RESET if not args.output else key
        print(f"{output_string}{key_string}{CAN_S}\
{key.replace('Content-Security-Policy', 'contentsecuritypolicy2')}")
else:
    print_detail_r("[bcompat_n]", is_red=True) if not args.output else\
                                  print_detail_l("[bcompat_n]")

print(linesep.join(['']*2))
end = time()
analysis_time()

# Export analysis
if args.output == 'txt':
    sys.stdout = orig_stdout
    print_path(name_e)
    f.close()
elif args.output == 'pdf':
    sys.stdout = orig_stdout
    f.close()
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf_metadata()
    pdf.set_display_mode(zoom='real')
    pdf.add_page()

    # PDF Body
    pdf.set_font("Courier", size=9)
    f = open(name_e, "r", encoding='utf8')
    links_strings = (URL_S, REF_S, CAN_S)

    for x in f:
        if '[' in x:
            pdf_sections()
        pdf.set_font(style='B' if any(s in x for s in BOLD_S) else '')
        for string in links_strings:
            if string in x:
                pdf_links(string)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(197, 2.6, txt=x, align='L')

    name_p = f"{name_e[:-5]}.pdf"
    pdf.output(name_p)
    print_path(name_p)
    f.close()
    remove(name_e)
elif args.output == 'html':
    sys.stdout = orig_stdout
    f.close()

    # HTML Template
    title = get_detail('[pdf_s]')
    header = f'<!DOCTYPE HTML><html lang="en"><head><meta charset="utf-8">\
<title>{title}</title><style>pre {{overflow-x: auto; white-space: \
pre-wrap;white-space: -moz-pre-wrap; white-space: -pre-wrap;white-space: \
-o-pre-wrap; word-wrap: break-word; font-size: medium;}} a {{color: blue; \
text-decoration: none;}} .ok {{color: green;}} .header {{color: #660033;}} \
.ko {{color: red;}} </style></head>'
    body = '<body><pre>'
    footer = '</pre></body></html>'

    name_p = f"{name_e[:-5]}.html"
    l_miss.extend(['Pragma', 'WWW-Authenticate', 'X-Frame-Options',
                   'X-Robots-Tag', 'X-UA-compatible'])
    l_final = sorted(l_miss + l_ins)
    l_fng_final = sorted(l_fng)

    with open(name_e, 'r', encoding='utf8') as input_file,\
            open(name_p, 'w', encoding='utf8') as output:
        output.write(str(header))
        output.write(str(body))

        sub_d = {'ahref_f': '</a>', 'ahref_s': '<a href="', 'close_t': '">',
                 'span_ko': '<span class="ko">', 'span_h':
                 '<span class="header">', 'span_f': '</span>'}

        for ln in input_file:
            if 'rfc-st' in ln:
                output.write(f"{ln[:2]}{sub_d['ahref_s']}{ln[2:-2]}\
                             {sub_d['close_t']}{ln[2:]}{sub_d['ahref_f']}")
            elif ' URL  : ' in ln:
                output.write(f"{ln[:7]}{sub_d['ahref_s']}{ln[7:]}\
                             {sub_d['close_t']}{ln[7:]}{sub_d['ahref_f']}")
            elif any(s in ln for s in BOLD_S):
                output.write(f'<strong>{ln}</strong>')
            elif get_detail('[ok]') in ln:
                output.write(f'<span class="ok">{ln}{sub_d["span_f"]}')
            elif get_detail('[bcompat_n]') in ln:
                output.write(f"{sub_d['span_ko']}{ln}{sub_d['span_f']}")
            elif ' Ref: ' in ln:
                output.write(f"{ln[:6]}{sub_d['ahref_s']}{ln[6:]}\
                             {sub_d['close_t']}{ln[6:]}{sub_d['ahref_f']}")
            elif 'caniuse' in ln:
                ln = f"{sub_d['span_h']}{ln[1:ln.index(': ')]}: \
{sub_d['span_f']}{sub_d['ahref_s']}{ln[ln.index(SEC_S):]}{sub_d['close_t']}\
{ln[ln.index(SEC_S):]}{sub_d['ahref_f']}"
                output.write(ln)
            else:
                for i in headers:
                    if (str(i + ": ") in ln) and ('Date:   ' not in ln):
                        ln = ln.replace(ln[0: ln.index(":")], sub_d['span_h'] +
                                        ln[0: ln.index(":")] + sub_d['span_f'])
                for i in l_fng_final:
                    if i in ln and not args.brief:
                        try:
                            idx = ln.index(' [')
                        except ValueError:
                            continue
                        ln = f"{sub_d['span_ko']}{ln[:idx]}{sub_d['span_f']}\
{ln[idx:]}"
                    elif i in ln and args.brief:
                        ln = f"{sub_d['span_ko']}{ln}{sub_d['span_f']}"
                for i in l_final:
                    if (i in ln) and ('"' not in ln) or ('HTTP (' in ln):
                        ln = ln.replace(ln, sub_d['span_ko'] +
                                        ln + sub_d['span_f'])
                output.write(ln)
        output.write(footer)

    print_path(name_p)
    remove(name_e)

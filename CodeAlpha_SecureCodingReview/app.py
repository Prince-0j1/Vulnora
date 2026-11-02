from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from pathlib import Path
from werkzeug.utils import secure_filename
from datetime import datetime
import re, io, json, os, zipfile
app=Flask(__name__); app.secret_key=os.environ.get('FLASK_SECRET','local-review-change-me'); app.config['MAX_CONTENT_LENGTH']=2*1024*1024
ROOT=Path(__file__).resolve().parent; UPLOAD=ROOT/'uploads'; UPLOAD.mkdir(exist_ok=True)
ALLOWED={'.py','.php','.js','.html','.sql'}
RULES=[
('SQL injection risk','high',re.compile(r"(?:execute|query|cursor\.execute)\s*\(\s*(?:f[\"']|[\"'][^\"']{0,120}[\"']\s*\+|[\"'][^\"']*%\s*\()",re.I),'String interpolation/concatenation may build a SQL query. Use parameterized queries/prepared statements.'),
('SQL query built with interpolation','high',re.compile(r"(?i)\b(?:query|sql)\s*=.*(?:f[\"']|\s(?:\+|\.)\s*\$?\w+)"),'SQL statements built with user-controlled strings can be injectable. Use parameterized queries/prepared statements.') ,
('Possible hardcoded secret','high',re.compile(r"(?i)\b\w*(?:password|passwd|secret_key|api_key|token)\s*=\s*[\"'][^\"']{5,}[\"']"),'Move secrets to environment variables or a secret manager; rotate any real credential found in source.'),
('Weak password hash','high',re.compile(r"(?i)\b(?:md5|sha1)\s*\([^\n]*(?:password|passwd|credential)"),'Use a password hashing function designed for passwords (Argon2id, bcrypt, or scrypt), with a maintained library.'),
('Dynamic code execution','high',re.compile(r"\b(?:eval|exec)\s*\("),'Avoid evaluating untrusted input as code. Replace with explicit parsing/dispatch.'),
('Shell command injection risk','high',re.compile(r"(?i)\b(?:os\.system|popen|subprocess\.Popen|subprocess\.run)\s*\([^\n]*(?:shell\s*=\s*True|\+\s*\w+|f[\"'])"),'Avoid shell=True and command-string construction. Pass an argument list and validate inputs.'),
('Potential XSS output','medium',re.compile(r"(?i)(?:innerHTML\s*=|document\.write\s*\(|echo\s+\$_(?:GET|POST|REQUEST))"),'Escape untrusted output for its context; use safe DOM APIs or framework auto-escaping.'),
('CSRF protection may be missing','medium',re.compile(r"(?i)method\s*=\s*[\"']post[\"']"),'Review state-changing forms/endpoints and ensure CSRF tokens or equivalent framework protections are used.'),
('TLS certificate verification disabled','high',re.compile(r"(?i)verify\s*=\s*False"),'Keep TLS certificate verification enabled. Fix trust-store/certificate issues instead of disabling validation.'),
('Insecure randomness','medium',re.compile(r"(?i)\brandom\.(?:random|randint|choice)\s*\("),'Use a cryptographically secure source such as Python secrets for tokens, reset links, or security-sensitive identifiers.'),
('Potentially unsafe file upload handling','medium',re.compile(r"(?i)(?:save\s*\(\s*request\.files|move_uploaded_file\s*\(\s*\$_FILES)"),'Validate content and extension, generate server-side filenames, limit size, store outside web root, and prevent execution.'),
]
def scan_source(filename, source):
    findings=[]; lines=source.splitlines()
    for title,severity,pattern,fix in RULES:
        for i,line in enumerate(lines,1):
            if pattern.search(line): findings.append({'title':title,'severity':severity,'line':i,'snippet':line.strip()[:240],'fix':fix})
    # simple manual checks with targeted contexts
    if re.search(r"(?i)SELECT\s+.+\s+FROM\s+\w+\s+WHERE\s+.+\$_(?:GET|POST|REQUEST)",source):
        findings.append({'title':'User input may reach SQL query','severity':'high','line':1,'snippet':'SQL statement and request input appear in the same file.','fix':'Use prepared statements with bound parameters. Manually verify the query construction and call sites.'})
    # de-duplicate findings
    seen=set(); unique=[]
    for f in findings:
        key=(f['title'],f['line'])
        if key not in seen: seen.add(key); unique.append(f)
    unique.sort(key=lambda f:({'high':0,'medium':1,'low':2}.get(f['severity'],3),f['line']))
    return unique
@app.route('/',methods=['GET'])
def index(): return render_template('index.html',title='CodeShield Review',subtitle='Static source inspection • vulnerability triage • remediation guidance',logo='⌘',allowed=', '.join(sorted(ALLOWED)))
@app.post('/scan')
def scan():
    uploaded=request.files.get('source_file')
    if not uploaded or not uploaded.filename: flash('Choose a source file first.','error'); return redirect(url_for('index'))
    name=secure_filename(uploaded.filename); ext=Path(name).suffix.lower()
    if ext not in ALLOWED: flash('Unsupported file type. Allowed: '+', '.join(sorted(ALLOWED)), 'error'); return redirect(url_for('index'))
    raw=uploaded.read()
    if len(raw)>app.config['MAX_CONTENT_LENGTH']: flash('File exceeds 2 MB limit.','error'); return redirect(url_for('index'))
    try: source=raw.decode('utf-8-sig')
    except UnicodeDecodeError: flash('File must be UTF-8 text source code.','error'); return redirect(url_for('index'))
    findings=scan_source(name,source); report={'filename':name,'scanned_at':datetime.now().isoformat(timespec='seconds'),'lines':len(source.splitlines()),'findings':findings,'summary':{s:sum(f['severity']==s for f in findings) for s in ['high','medium','low']}}
    report_path=ROOT/'last_report.json'; report_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    return render_template('results.html',title='CodeShield Review',subtitle='Scan results • inspect every finding before remediation',logo='⌘',report=report)
@app.get('/download-report')
def download_report():
    p=ROOT/'last_report.json'
    if not p.exists(): flash('Run a scan before downloading a report.','error'); return redirect(url_for('index'))
    return send_file(p,as_attachment=True,download_name='codeshield_review_report.json',mimetype='application/json')
@app.get('/sample/<name>')
def sample(name):
    p=ROOT/'samples'/name
    if not p.exists() or p.suffix.lower() not in ALLOWED: return 'Sample not found',404
    return send_file(p,as_attachment=True,download_name=p.name)
if __name__=='__main__': app.run(host='127.0.0.1',port=5003,debug=False,threaded=True)

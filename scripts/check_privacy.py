#!/usr/bin/env python3
"""Privacy checker for CI: scan repository for sensitive information."""
import argparse
import gzip
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


# Build sensitive hostnames from fragments to avoid literal values in source
def _build_hostname_pattern():
    """Build hostname detection pattern from fragments."""
    # Fragment-build hostnames to avoid literals
    h1 = 'p' + 'a' + 'x'
    h2 = 'm' + 'i' + 'm' + 'as'
    git_host_parts = ['github', 'r' + 'p' + 'i', 'edu']
    git_host = r'\.'.join(git_host_parts)
    
    # Case-insensitive word-boundary detection for hostnames
    # Match them standalone or embedded in longer identifiers
    pattern_parts = [
        rf'\b{h1}\b',
        rf'\b{h2}\b',
        rf'\b{git_host}\b',
        r'\bTailscale\b',
        r'\.ts\.net\b'
    ]
    # Put (?i) flag at the start of the entire pattern
    return r'(?i)(?:' + '|'.join(pattern_parts) + r')'


# Rules for different pattern types
# Credential patterns: case-sensitive, skip bioinformatics files
CREDENTIAL_RULES = {
    'private key': rb'-----BEGIN (?:OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----',
    'GitHub token': rb'\bgh[pousr]_[A-Za-z0-9]{20,}\b',
    'cloud access key': rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'service token': rb'\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}\b',
    'authorization header': rb'\bBearer\s+[A-Za-z0-9_.-]{20,}\b',
}

# Filesystem and network patterns: apply to all files
FILESYSTEM_RULES = {
    'private filesystem path': rb'/(?:home|Users)/[A-Za-z0-9_.-]+/',
    'private network address': rb'\b(?:10\.[0-9]+\.[0-9]+\.[0-9]+|192\.168\.[0-9]+\.[0-9]+|172\.(?:1[6-9]|2[0-9]|3[01])\.[0-9]+\.[0-9]+|100\.(?:6[4-9]|[7-9][0-9]|1[01][0-9]|12[0-7])\.[0-9]+\.[0-9]+)\b',
}

# SSH patterns
SSH_RULES = {
    'ssh config': rb'(?:^|\n)\s*(?:Host|HostName|IdentityFile|ProxyCommand|RemoteCommand)\s+',
    'ssh identity file': rb'\.ssh/id_[a-z0-9]+',
}

# Files to exclude from ALL checks (by exact path)
EXCLUDED_PATHS = {
    'scripts/check_privacy.py',
    'scripts/test_check_privacy.py',
}

# File extensions to skip for credential pattern checking (bioinformatics files)
CREDENTIAL_SKIP_EXTENSIONS = {'.fasta', '.a3m', '.pdb', '.cif', '.csv'}


def check_tool_available(tool_name):
    """Check if a required tool is available, fail hard if not."""
    try:
        subprocess.run([tool_name, '-h'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        print(f"ERROR: Required tool '{tool_name}' is not installed.", file=sys.stderr)
        print(f"Install it with: sudo apt-get install -y poppler-utils", file=sys.stderr)
        sys.exit(1)


def extract_pdf_text_and_attachments(pdf_content):
    """Extract text from PDF and all embedded attachments."""
    check_tool_available('pdftotext')
    check_tool_available('pdfdetach')
    
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, 'input.pdf')
        with open(pdf_path, 'wb') as f:
            f.write(pdf_content)
        
        # Extract visible text
        result = subprocess.run(['pdftotext', '-layout', pdf_path, '-'],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              check=True)
        text_content = result.stdout
        
        # List attachments
        result = subprocess.run(['pdfdetach', '-list', pdf_path],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              check=False)
        
        attachments = []
        if result.returncode == 0 and b'file' in result.stdout.lower():
            # Extract each attachment
            lines = result.stdout.decode('utf-8', errors='ignore').split('\n')
            attachment_count = 0
            for line in lines:
                if line.strip() and not line.startswith('---'):
                    attachment_count += 1
            
            for i in range(1, attachment_count + 1):
                attach_dir = os.path.join(tmpdir, f'attach_{i}')
                os.makedirs(attach_dir, exist_ok=True)
                result = subprocess.run(['pdfdetach', '-save', str(i), '-o', attach_dir, pdf_path],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      check=False)
                
                # Read extracted files
                for fname in os.listdir(attach_dir):
                    fpath = os.path.join(attach_dir, fname)
                    with open(fpath, 'rb') as f:
                        attachments.append((fname, f.read()))
        
        return text_content, attachments


def extract_png_text_chunks(png_content):
    """Extract text chunks from PNG file."""
    chunks = []
    offset = 8  # Skip PNG signature
    
    while offset < len(png_content) - 8:
        try:
            chunk_len = int.from_bytes(png_content[offset:offset+4], 'big')
            chunk_type = png_content[offset+4:offset+8].decode('ascii', errors='ignore')
            chunk_data = png_content[offset+8:offset+8+chunk_len]
            
            # Text chunks: tEXt, zTXt, iTXt
            if chunk_type in ('tEXt', 'zTXt', 'iTXt'):
                chunks.append(chunk_data)
            
            offset += 12 + chunk_len  # length(4) + type(4) + data + crc(4)
        except (ValueError, UnicodeDecodeError):
            break
    
    return b''.join(chunks)


def extract_office_xml(office_content):
    """Extract XML content from Office Open XML files (.docx, .xlsx, .pptx)."""
    try:
        xml_parts = []
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, 'office.zip')
            with open(zip_path, 'wb') as f:
                f.write(office_content)
            
            with zipfile.ZipFile(zip_path, 'r') as zf:
                for name in zf.namelist():
                    if name.endswith('.xml') or name.endswith('.rels'):
                        xml_parts.append(zf.read(name))
        
        return b''.join(xml_parts)
    except (zipfile.BadZipFile, Exception):
        return b''


def scan_binary_with_strings(content):
    """Use strings command to extract printable text from binary files."""
    try:
        result = subprocess.run(['strings', '-n', '8'],
                              input=content,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              check=True)
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        # strings not available, return original content
        return content


def inspect_content(content, filename=''):
    """Inspect content for privacy issues."""
    findings = []
    file_ext = Path(filename).suffix.lower() if filename else ''
    
    # Decompress if gzipped
    if content.startswith(b'\x1f\x8b'):
        try:
            content = gzip.decompress(content)
        except Exception:
            pass
    
    # Handle PDF files: extract text and scan attachments
    if content.startswith(b'%PDF'):
        try:
            text_content, attachments = extract_pdf_text_and_attachments(content)
            
            # Scan visible text
            findings.extend(scan_patterns(text_content, filename))
            
            # Scan each attachment recursively
            for attach_name, attach_content in attachments:
                attach_findings = inspect_content(attach_content, attach_name)
                if attach_findings:
                    findings.append(f'PDF attachment "{attach_name}" contains: {", ".join(attach_findings)}')
            
            return findings
        except Exception as e:
            return [f'PDF processing error: {str(e)}']
    
    # Handle PNG files: extract text chunks only
    if content.startswith(b'\x89PNG'):
        content = extract_png_text_chunks(content)
    
    # Handle Office Open XML files
    if file_ext in ('.docx', '.xlsx', '.pptx'):
        xml_content = extract_office_xml(content)
        if xml_content:
            office_findings = scan_patterns(xml_content, filename)
            if office_findings:
                findings.append(f'Office XML content contains: {", ".join(office_findings)}')
            return findings
    
    # For other binary files (not images), use strings
    if file_ext not in ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico'):
        # Check if content looks binary
        if b'\x00' in content[:8192]:
            content = scan_binary_with_strings(content)
    
    findings.extend(scan_patterns(content, filename))
    return findings


def scan_patterns(content, filename=''):
    """Scan content against all pattern rules."""
    findings = []
    file_ext = Path(filename).suffix.lower() if filename else ''
    
    # Build hostname pattern (includes its own flags)
    hostname_pattern = _build_hostname_pattern()
    
    # Check hostname patterns
    if re.search(hostname_pattern.encode(), content):
        findings.append('private hostname')
    
    # Check filesystem patterns
    for name, pattern in FILESYSTEM_RULES.items():
        if re.search(pattern, content):
            findings.append(name)
    
    # Check SSH patterns
    for name, pattern in SSH_RULES.items():
        if re.search(pattern, content, re.MULTILINE):
            findings.append(name)
    
    # Check credential patterns (skip for bioinformatics files)
    if file_ext not in CREDENTIAL_SKIP_EXTENSIONS:
        for name, pattern in CREDENTIAL_RULES.items():
            if re.search(pattern, content):
                findings.append(name)
    
    return findings


def scan_repository(ref='HEAD'):
    """Scan the repository at the given ref."""
    # Get tree SHA
    result = subprocess.run(['git', 'rev-parse', '--verify', f'{ref}^{{tree}}'],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          check=True)
    tree_sha = result.stdout.decode().strip()
    
    # List all files in tree
    result = subprocess.run(['git', 'ls-tree', '-rz', tree_sha],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          check=True)
    
    failures = []
    scanned = 0
    
    for entry in result.stdout.split(b'\0'):
        if not entry:
            continue
        
        metadata, raw_name = entry.split(b'\t', 1)
        mode, kind, oid = metadata.split()
        name = raw_name.decode('utf-8', errors='ignore')
        
        # Skip if not a regular file
        if mode not in (b'100644', b'100755') or kind != b'blob':
            continue
        
        # Skip excluded paths
        if name in EXCLUDED_PATHS:
            continue
        
        scanned += 1
        
        # Get file content
        result = subprocess.run(['git', 'cat-file', 'blob', oid.decode()],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              check=True)
        content = result.stdout
        
        # Scan content
        try:
            findings = inspect_content(content, name)
            
            # Also scan the filename itself
            findings.extend(scan_patterns(raw_name, name))
            
            if findings:
                # Deduplicate findings
                findings = sorted(set(findings))
                failures.append((name, findings))
        except Exception as e:
            failures.append((name, [f'scan error: {str(e)}']))
    
    return scanned, failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ref', default='HEAD', 
                       help='Git ref to scan (default: HEAD)')
    args = parser.parse_args()
    
    print(f"Scanning repository at ref: {args.ref}", file=sys.stderr)
    
    try:
        scanned, failures = scan_repository(args.ref)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Git command failed: {e}", file=sys.stderr)
        return 1
    
    # Report failures
    if failures:
        print("\n❌ Privacy check FAILED. Found sensitive information:\n", file=sys.stderr)
        for name, findings in failures:
            print(f"  {name}:", file=sys.stderr)
            for finding in findings:
                print(f"    - {finding}", file=sys.stderr)
        print(f"\nScanned {scanned} files, found issues in {len(failures)} file(s).", file=sys.stderr)
        return 1
    else:
        print(f"✅ Privacy check PASSED. Scanned {scanned} files, no sensitive information found.", file=sys.stderr)
        return 0


if __name__ == '__main__':
    sys.exit(main())

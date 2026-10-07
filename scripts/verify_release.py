"""Verify the unpacked release against its SHA-256 file manifest."""
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    count=0
    for line in (ROOT/'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        expected,name=line.split('  ',1)
        path=(ROOT/name).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise SystemExit(f'Missing or invalid path: {name}')
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=expected:
            raise SystemExit(f'Content mismatch: {name}')
        count+=1
    print(f'Verified {count} release files. The manifest is an integrity record, not an external signature.')

if __name__=='__main__': main()

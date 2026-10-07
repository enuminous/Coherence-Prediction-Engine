"""Package the existing evidence without rerunning or replacing experiments."""
import hashlib
import sys
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def included(path):
    relative=path.relative_to(ROOT)
    allowed={'cpe','data','docs','protocols','references','runs','scripts','tests','validation'}
    return path.is_file() and '__pycache__' not in relative.parts and path.suffix!='.pyc' and (
        len(relative.parts)==1 or relative.parts[0] in allowed) and path.name!='SHA256SUMS.txt'

def main():
    destination=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT.parent/'Coherence-Prediction-Engine.zip'
    if destination.exists(): raise SystemExit('Refusing to replace an existing ZIP; choose a new filename.')
    if destination.resolve().is_relative_to(ROOT): raise SystemExit('Choose an output outside the source folder.')
    files=sorted(p for p in ROOT.rglob('*') if included(p))
    manifest=ROOT/'SHA256SUMS.txt'
    manifest.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in files),encoding='utf-8')
    with zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in sorted(files+[manifest]):
            name='coherence-prediction-engine/'+path.relative_to(ROOT).as_posix()
            info=zipfile.ZipInfo(name,date_time=(2026,10,7,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644<<16
            archive.writestr(info,path.read_bytes())
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None: raise SystemExit('ZIP integrity failure')
    print(destination)
    print(f'{len(files)+1} files; {destination.stat().st_size:,} bytes')
    print('SHA256 '+hashlib.sha256(destination.read_bytes()).hexdigest())

if __name__=='__main__': main()

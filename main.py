import sys
from pathlib import Path

HINTS = ('cache','tmp','temp','log','build','dist','node_modules','__pycache__')
EXTS = ('.log','.tmp','.cache','.pyc','.zip','.dmg','.pkg')

def risk(p):
    parts = [x.lower() for x in p.parts]
    if p.name.lower() == '.ds_store' or any(h in parts for h in HINTS) or p.suffix.lower() in EXTS:
        return 'high'
    return 'mid' if p.stat().st_size > 100 * 1024 * 1024 else 'low'

def scan(root):
    out = []
    for p in Path(root).rglob('*'):
        try:
            if p.is_file() and p.stat().st_size > 1024 * 1024:
                out.append((risk(p), p.stat().st_size, p))
        except OSError:
            pass
    return sorted(out, key=lambda x: (x[0] == 'high', x[1]), reverse=True)[:15]

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    items = scan(root)
    if not items:
        print('No large candidate files found.'); return
    print('AI-suggested cleanup candidates:')
    for i, (r, n, p) in enumerate(items, 1):
        print(f'{i:2}. risk={r} size={n/1024/1024:.1f}MB {p}')
    raw = input('Select numbers (comma-separated, empty=cancel): ').strip()
    if not raw:
        print('Cancelled.'); return
    chosen = []
    for part in raw.split(','):
        try:
            i = int(part.strip()) - 1
            if 0 <= i < len(items): chosen.append(items[i][2])
        except ValueError:
            pass
    if not chosen:
        print('No valid selection.'); return
    print('Selected:', *chosen, sep='\n  ')
    if '--delete' not in sys.argv:
        print('Dry run. Add --delete and confirm to remove.'); return
    if input(f'Delete {len(chosen)} files? Type YES: ').strip() != 'YES':
        print('Cancelled.'); return
    for p in chosen:
        try:
            p.unlink(); print('Deleted:', p)
        except OSError as e:
            print('Skip:', p, e)

if __name__ == '__main__':
    main()
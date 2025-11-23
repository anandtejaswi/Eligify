import sys, os, json
ROOT = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from lib.pdf_parser import extract_text_with_info, extract_marksheet_fields

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'tenth_certificate.pdf'
    if not os.path.exists(path):
        print(json.dumps({"error": f"File not found: {path}"}))
        return

    info = extract_text_with_info(path, method='auto', dpi=300)
    fields = extract_marksheet_fields(path, method='auto', dpi=300)

    out = {
        "debug": info,
        "fields": fields,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()

from lib.pdf_parser import extract_text_from_pdf, extract_marksheet_fields

pdf_path = "12th_marksheet.pdf"

text_auto = extract_text_from_pdf(pdf_path, method="auto")
print(text_auto)

print("\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
text_text = extract_text_from_pdf(pdf_path, method="text")
print(text_text)

print("\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
text_ocr = extract_text_from_pdf(pdf_path, method="ocr", dpi=300)
print(text_ocr)

print("\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
print("[STRUCTURED] Marksheet key–value extraction")
fields = extract_marksheet_fields(pdf_path, method="auto")
if isinstance(fields, dict) and "error" in fields:
    print("Error:", fields.get("error"))
else:
    print("name:", fields.get("name"))
    print("father_name:", fields.get("father_name"))
    print("roll_number:", fields.get("roll_number"))
    print("registration_number:", fields.get("registration_number"))
    print("dob:", fields.get("dob"))
    print("exam:", fields.get("exam"))
    print("year:", fields.get("year"))
    print("university:", fields.get("university"))
    print("college:", fields.get("college"))
    print("percentage:", fields.get("percentage"))
    print("cgpa:", fields.get("cgpa"))
    print("subjects:")
    for s in fields.get("subjects", []) or []:
        print(" -", s.get("name"), "| marks:", s.get("marks"), "| grade:", s.get("grade"))
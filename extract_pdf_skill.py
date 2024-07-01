from unstructured.partition.pdf import partition_pdf
import PyPDF2

def extract_text_from_pdf(pdf_file):
    with open(pdf_file, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
        return text

text = extract_text_from_pdf("bank-statement-1.pdf")
print("text : ", text)

# below does not work
# pdf_text = partition_pdf(text)
# print("pdf_text : ", pdf_text)
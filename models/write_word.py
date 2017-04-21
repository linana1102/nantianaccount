from docx import Document

document = Document()
table1 = document.add_table(rows=1, cols=1)
table2 = document.add_table(rows=3, cols=6)
table3 = document.add_table(rows=1, cols=4)
table4 = document.add_table(rows=1, cols=1)
table5 = document.add_table(rows=4, cols=4)
table6 = document.add_table(rows=1, cols=1)
table7 = document.add_table(rows=1, cols=1)
table8 = document.add_table(rows=1, cols=1)
table9 = document.add_table(rows=1, cols=1)
document.add_page_break()
document.save('demo.docx')

# -*- coding: utf-8 -*-
from docx import Document
import win32com.client as win32

app='Word'
word= win32.gencache.EnsureDispatch('%s.Application' % app)
doc=word.Documents.Add()
word.Visible=False

#Title begin
sel =word.Selection
sel.Font.Name = u"微软雅黑"
sel.Font.Size = 8
sel.Font.Bold = False
sel.Font.Italic = False
sel.Font.Underline = False
sel.ParagraphFormat.Alignment = 1

myRange = doc.Range(0,0)
myRange.InsertBefore(u'标题1  测试表格') # 使用样式
#Title end
#Table Start
sel.SetRange(10,10)
tab = doc.Tables.Add(sel.Range, 9, 3)
tab.Columns(1).SetWidth(10.35*20.35, 0)
tab.Rows.Alignment = 1
tab.Style = u"网格型"
tabnow = doc.Tables(1)
cell1 = tabnow.Cell(1,1)
cell2 = tabnow.Cell(3,1)

#myrange = doc.Range(cell1.Range.Start, cell2.Range.End)

sel.SetRange(cell1.Range.Start, cell2.Range.End)
sel.Cells.Merge()

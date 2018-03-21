# -*- coding: utf-8 -*-
'''
Created : 2017-05-19
@author: Eric Lapouyade
'''

from docxtpl import DocxTemplate

tpl=DocxTemplate(r'C:/Users/nantian/Desktop/resume_template.docx')

context = {
    'name': 'linana',
    'gender':'female',
    'birthday':'19920520',
    'items' : [
        {'desc' : 'Python interpreters', 'qty' : 2, 'price' : 'FREE' },
        {'desc' : 'Django projects', 'qty' : 5403, 'price' : 'FREE' },
        {'desc' : 'Guido', 'qty' : 1, 'price' : '100,000,000.00' },
    ],
    'in_europe' : True,
    'is_paid': False,
    'company_name' : 'The World Wide company',
    'total_price' : '100,000,000.00'
}

tpl.render(context)
print dir(tpl.docx)



# tpl.save('C:/Users/nantian/Desktop/
#
#
# _template.docx')
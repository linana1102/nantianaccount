from StringIO import StringIO

for i in range(2):
    s = StringIO()
    s.write(str(i)+'aaaaaaaaaaaaaaaaa')
    print s.getvalue()
    s.close()
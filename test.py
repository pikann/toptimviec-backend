s="adfjkwdahkzsfjefoaijtoajwltokafgkajfkwjef"
print({k:v for k,v in sorted({x:s.count(x) for x in s}.items(), key=lambda a: a[0])})
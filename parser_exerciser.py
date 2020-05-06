
from wabbit.parse import parse_source

#     print 1;
#     print 2.5;
#
# From there, expand it to handle expressions:
#
#     print 2 + 3 * -4;
#
# Then, expand it to include variable names
#
#     var x = 3;
#     print 2 + x;

print('prelim', 1)
s = 'print 1;'
print(s)
print(parse_source(s))
print()

print('prelim 2')
s = 'print 2.5;'
print(s)
print(parse_source(s))
print()

print('prelim 3a')
s = '1 + 2;'
print(s)
print(parse_source(s))
print()

print('prelim 3')
s = 'print 4 * 2 + 3 * 4 / 701 - 1;'
print(s)
print(parse_source(s))
print()

print('prelim 4')
s = 'var x = 3;'
print(s)
print(parse_source(s))
print()

print('prelim 5')
s = 'print 2 + x;'
print(s)
print(parse_source(s))
print()

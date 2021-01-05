import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('string')
parser.add_argument('regex')

args = parser.parse_args()

print('the string to analyze: ', args.string, '\n')
print('reg expresion to check for:', args.regex, '\n')

compiled = re.compile(args.regex)
match = compiled.match(args.string)

if match:
    print('matched this: ' , match.group(), '\n')
else:
    print('sorry, no match.')

    

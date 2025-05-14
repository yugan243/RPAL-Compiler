import re

class Lexer:
    def __init__(self, input_text):
        self.input = input_text.replace('\n', ' ').replace('\t', ' ')
        self.pos = 0
        self.tokens = []
        self.token_specs = [
            ('INTEGER', r'\d+'),
            ('IDENTIFIER', r'[a-zA-Z][a-zA-Z0-9]*'),
            ('OPERATOR', r'\+|\-|\*|\/|eq|\|'),
            ('KEYWORD', r'\blet\b|\bin\b|\bwhere\b|\brec\b|\bfunction_form\b|\bgamma\b|\btau\b'),
            ('PUNCTUATION', r'\(|\)|,|\.'),
            ('ARROW', r'->'),
            ('WHITESPACE', r'\s+'),
        ]
        self.token_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in self.token_specs)

    def tokenize(self):
        for match in re.finditer(self.token_regex, self.input):
            kind = match.lastgroup
            value = match.group()
            if kind == 'WHITESPACE':
                continue
            self.tokens.append((kind, value))
        return self.tokens

    def next_token(self):
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        return None
class Token:
    def __init__(self, type, value=None, line=0, column=0):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __str__(self):
        if self.value:
            return f"{self.type}:{self.value}"
        return self.type

class LexicalAnalyzer:
    def __init__(self, input_text):
        self.input_text = input_text
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.current_char = None
        self.advance()
    
    def advance(self):
        """Move to the next character in the input"""
        if self.position < len(self.input_text):
            self.current_char = self.input_text[self.position]
            self.position += 1
            self.column += 1
        else:
            self.current_char = None
    
    def peek(self, n=1):
        """Look ahead n characters without advancing"""
        peek_pos = self.position + n - 1
        if peek_pos < len(self.input_text):
            return self.input_text[peek_pos]
        return None
    
    def skip_whitespace(self):
        """Skip whitespace characters"""
        while self.current_char and self.current_char.isspace():
            if self.current_char == '\n':
                self.line += 1
                self.column = 1
            self.advance()
    
    def skip_comment(self):
        """Skip comments starting with //"""
        while self.current_char and self.current_char != '\n':
            self.advance()
    
    def handle_multi_line_comment(self):
        """Skip multi-line comments enclosed in /* ... */"""
        while self.current_char:
            if self.current_char == '*' and self.peek() == '/':
                self.advance()  # consume '*'
                self.advance()  # consume '/'
                return
            if self.current_char == '\n':
                self.line += 1
                self.column = 1
            self.advance()
        # If we get here, the comment was not properly closed
        raise Exception("Unclosed multi-line comment")
    
    def read_identifier(self):
        """Read an identifier or keyword"""
        start_column = self.column
        id_str = ''
        
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            id_str += self.current_char
            self.advance()
        
        # Check for keywords
        keywords = {
            'let': 'let', 'in': 'in', 'fn': 'fn', 'where': 'where',
            'aug': 'aug', 'or': 'or', 'not': 'not', 'gr': 'gr',
            'ge': 'ge', 'ls': 'ls', 'le': 'le', 'eq': 'eq',
            'ne': 'ne', 'true': 'true', 'false': 'false',
            'nil': 'nil', 'dummy': 'dummy', 'rec': 'rec',
            'within': 'within', 'and': 'and'
        }
        
        if id_str in keywords:
            return Token(keywords[id_str], None, self.line, start_column)
        else:
            return Token('ID', id_str, self.line, start_column)
    
    def read_integer(self):
        """Read an integer literal"""
        start_column = self.column
        num_str = ''
        
        while self.current_char and self.current_char.isdigit():
            num_str += self.current_char
            self.advance()
        
        return Token('INT', int(num_str), self.line, start_column)
    
    def read_string(self):
        """Read a string literal enclosed in double quotes"""
        start_column = self.column
        self.advance()  # consume opening quote
        string_value = ''
        
        while self.current_char and self.current_char != '"':
            if self.current_char == '\\':
                self.advance()
                if self.current_char == 'n':
                    string_value += '\n'
                elif self.current_char == 't':
                    string_value += '\t'
                elif self.current_char == '\\':
                    string_value += '\\'
                elif self.current_char == '"':
                    string_value += '"'
                else:
                    string_value += self.current_char
            else:
                string_value += self.current_char
            self.advance()
        
        if self.current_char != '"':
            raise Exception(f"Unclosed string literal at line {self.line}, column {start_column}")
        
        self.advance()  # consume closing quote
        return Token('STR', string_value, self.line, start_column)
    
    def tokenize(self):
        """Convert input text into a list of tokens"""
        while self.current_char:
            # Skip whitespace
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Skip comments
            if self.current_char == '/' and self.peek() == '/':
                self.advance()  # consume first '/'
                self.advance()  # consume second '/'
                self.skip_comment()
                continue
            
            if self.current_char == '/' and self.peek() == '*':
                self.advance()  # consume '/'
                self.advance()  # consume '*'
                self.handle_multi_line_comment()
                continue
            
            # Identifiers and keywords
            if self.current_char.isalpha() or self.current_char == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Integer literals
            if self.current_char.isdigit():
                self.tokens.append(self.read_integer())
                continue
            
            # String literals
            if self.current_char == '"':
                self.tokens.append(self.read_string())
                continue
            
            # Operators and punctuation
            if self.current_char == '+':
                self.tokens.append(Token('+', None, self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == '-':
                if self.peek() == '>':
                    self.tokens.append(Token('->', None, self.line, self.column))
                    self.advance()  # consume '-'
                    self.advance()  # consume '>'
                else:
                    self.tokens.append(Token('-', None, self.line, self.column))
                    self.advance()
                continue
            
            if self.current_char == '*':
                self.tokens.append(Token('*', None, self.line, self.column))
                self.advance()
                continue

            if self.current_char == '>':
                self.tokens.append(Token('>', None, self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == '/':
                self.tokens.append(Token('/', None, self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == '=':
                self.tokens.append(Token('=', None, self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == '(':
                self.tokens.append(Token('(', None, self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == ')':
                self.tokens.append(Token(')', None, self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == ';':
                self.tokens.append(Token(';', None, self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == ',':
                self.tokens.append(Token(',', None, self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == '.':
                self.tokens.append(Token('.', None, self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == ':':
                self.tokens.append(Token(':', None, self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == '&':
                self.tokens.append(Token('&', None, self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == '@':
                self.tokens.append(Token('@', None, self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == '|':
                self.tokens.append(Token('|', None, self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == '\\':
                self.tokens.append(Token('\\', None, self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == '[':
                self.tokens.append(Token('[', None, self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == ']':
                self.tokens.append(Token(']', None, self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == '{':
                self.tokens.append(Token('{', None, self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == '}':
                self.tokens.append(Token('}', None, self.line, self.column))
                self.advance()
                continue
            
            # Unknown character
            raise Exception(f"Unknown character '{self.current_char}' at line {self.line}, column {self.column}")
        
        # Add EOF token
        self.tokens.append(Token('EOF', None, self.line, self.column))
        return self.tokens

def tokenize_file(filename):
    with open(filename, 'r') as file:
        input_text = file.read()
    
    lexer = LexicalAnalyzer(input_text)
    return lexer.tokenize()

# Test the lexical analyzer
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python lexical_analyzer.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    tokens = tokenize_file(filename)
    
    for token in tokens:
        print(token)
class Token:
    def __init__(self, type, value =None, line=0, column=0):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    #for debugging purposes
    def __repr__(self):
        return f"Token({self.type},{self.value})"
  
    def __str__(self):
        return f"<{self.type}:{self.value}>" if self.value else f"<{self.type}>"
   
class LexicalAnalyzer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 0
        self.tokens = []
        self.current_char = self.text[self.pos]
        self.current_token = None
        self.advance()

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        #Move to the next character in the text

        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
            self.column += 1
    
    def peek(self,n=1):
        peek_pos = self.position + n - 1
        if peek_pos < len(self.input_text):
            return self.input_text[peek_pos]
        return None

    def skip_whitespace(self):
        while self.current_char  and self.current_char.isspace():
            if self.current_char == '\n':
                self.line += 1
                self.column = 0
            self.advance()

    def skip_comment(self):
        while self.current_char and self.current_char != '\n':
            self.advance()

    def skip_multiline_comment(self):
        while self.current_char and (self.current_char != '*' or self.peek() != '/'):
            if self.current_char == '\n':
                self.line += 1
                self.column = 0
            self.advance()
        if self.current_char == '*':
            self.advance()
        if self.current_char == '/':
            self.advance()
        
        if self.current_char == None:
            raise Exception('Unterminated multiline comment')
        self.advance()


    def identifier(self):
        start_column = self.column
        id_str = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
              id_str += self.current_char
              self.advance()
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
        start_column = self.column
        int_str = ''
        while self.current_char and self.current_char.isdigit():
            int_str += self.current_char
            self.advance()
        return Token('INT', int(int_str), self.line, start_column)
    
    def read_float(self):
        start_column = self.column
        float_str = ''
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            float_str += self.current_char
            self.advance()
        return Token('FLOAT', float(float_str), self.line, start_column)
    
    #Read a string literal enclosed in double quotes
    def read_string(self):
        start_column = self.column
        string_str = ''
        self.advance()
        while self.current_char and self.current_char != '"':
            if self.current_char == '\\':
                self.advance()
                if self.current_char == 'n':
                    string_str += '\n'
                elif self.current_char == 't':
                    string_str += '\t'
                elif self.current_char == '"':
                    string_str += '"'
                elif self.current_char == '\\':
                    string_str += '\\'
                else:
                    string_str += self.current_char
            else:
                string_str += self.current_char
            self.advance()

            if self.current_char != '"':
                raise Exception(f"Unclosed string literal at line {self.line}, column {start_column}")
            self.advance()  # consume closing quote
        return Token('STR', string_str, self.line, start_column)
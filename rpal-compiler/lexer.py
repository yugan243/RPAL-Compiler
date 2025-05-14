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
        

       
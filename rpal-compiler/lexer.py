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
        self.column = 1
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
            if self.current_char == '\n':
                self.line += 1
                self.column = 0
    
    

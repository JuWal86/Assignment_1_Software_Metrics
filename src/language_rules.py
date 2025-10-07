LANGUAGE_RULES = {
    "python": {
        "single_line_comment": "#",
        "multi_line_start": '"""',    
        "multi_line_end": '"""',
        "multi_line_start_alt": "'''",
        "multi_line_end_alt": "'''",
        "statement_end": None,       
        "preprocessor": None
    },
    "c": {
        "single_line_comment": "//",
        "multi_line_start": "/*",
        "multi_line_end": "*/",
        "statement_end": ";",
        "preprocessor": "#"           
    },
    "cpp": {
        "single_line_comment": "//",
        "multi_line_start": "/*",
        "multi_line_end": "*/",
        "statement_end": ";",
        "preprocessor": "#"
    },
    "java": {
        "single_line_comment": "//",
        "multi_line_start": "/*",
        "multi_line_end": "*/",
        "statement_end": ";",
        "preprocessor": None
    },
    "go": {
        "single_line_comment": "//",
        "multi_line_start": "/*",
        "multi_line_end": "*/",
        "statement_end": ";",          
        "preprocessor": None
    },
    "rust": {
        "single_line_comment": "//",  
        "multi_line_start": "/*",     
        "multi_line_end": "*/",
        "statement_end": ";",
        "preprocessor": None
    }
}

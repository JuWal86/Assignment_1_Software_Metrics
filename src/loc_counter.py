import os
import re
from language_rules import LANGUAGE_RULES

CONTROL_KEYWORDS = [
    "if", "elif", "else if", "for", "while", "case", "catch", "except",
    "&&", "||", "?", "switch", "do"
]

def analyze_file(file_path):
    lang = detect_language(file_path)
    if lang not in LANGUAGE_RULES:
        return [], []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    ploc = count_physical_loc(code)
    lloc = count_logical_loc(code, lang)
    cc_results = count_cyclomatic_complexity(code, lang)

    # --- Extract function definitions (language-aware) ---
    if lang == "python":
        funcs = re.findall(r"def\s+([A-Za-z_]\w*)\s*\([^)]*\)\s*:", code)
    else:
        funcs = re.findall(r"\b([A-Za-z_]\w*)\s*\([^)]*\)\s*\{", code)

    keywords_to_ignore = {
        "if", "for", "while", "switch", "return", "sizeof",
        "catch", "try", "else", "elif", "do"
    }
    funcs = [f for f in funcs if f not in keywords_to_ignore]

    rows = []
    for func in funcs:
        rows.append({
            "file": file_path,
            "language": lang,
            "function": func,
            "signature": func + "()",
            "ploc_file": ploc,
            "lloc_file": lloc,
            "cyclomatic": cc_results.get(func, 1)
        })

    return rows, funcs


def detect_language(file_path):
   ext = os.path.splitext(file_path)[1]
   for extension, lang in {
       ".py": "python",
       ".c": "c",
       ".h": "c",
       ".cpp": "cpp",
       ".hpp": "cpp",
       ".java": "java",
       ".go": "go",
       ".rs": "rust",
   }.items():
       if ext == extension:
           return lang
   return "unknown"

def count_physical_loc(code):
   lines = code.splitlines()
   return sum(1 for line in lines if line.strip())

def count_logical_loc(code, lang):
    """
    Logical LOC counter
    """
    if lang not in LANGUAGE_RULES:
        return 0

    rule = LANGUAGE_RULES[lang]
    count = 0
    inside_multiline = False
    ml_start = rule.get("multi_line_start")
    ml_end   = rule.get("multi_line_end")
    ml_start_alt = rule.get("multi_line_start_alt")
    ml_end_alt   = rule.get("multi_line_end_alt")
    preproc = rule.get("preprocessor")

    logical_statements = [
        "for","if","elif","while","switch","case","else","do","void","return",
        "def","class","import","from","try","continue","break","package"
    ]

    for raw_line in code.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        # Skip preprocessor 
        if preproc and line.startswith(preproc):
            continue

        # Handle multiline comments/strings
        if inside_multiline:
            # Close if multi-line end appears
            if (ml_end and ml_end in line) or (ml_end_alt and ml_end_alt in line):
                inside_multiline = False
            continue

        # Detect start-end on the same line
        if ((ml_start and ml_start in line and ml_end and line.count(ml_start) >= 1 and line.count(ml_end) >= 1 and line.find(ml_start) != -1 and line.find(ml_end) != -1 and line.find(ml_start) < line.find(ml_end)) or
            (ml_start_alt and ml_start_alt in line and ml_end_alt and line.count(ml_start_alt) >= 1 and line.count(ml_end_alt) >= 1 and line.find(ml_start_alt) < line.find(ml_end_alt))):
            # whole comment/string on one line -> skip it entirely
            continue

        # Detect start of multiline
        if (ml_start and ml_start in line) or (ml_start_alt and ml_start_alt in line):
            inside_multiline = True
            continue

        # Single-line comments
        if rule.get("single_line_comment") and line.startswith(rule["single_line_comment"]):
            continue

        # Logical statements handling
        if "(" in line and ")" in line:
            count += 1
            continue
        if "=" in line:
            count += 1
            continue
        if rule.get("statement_end") and rule["statement_end"] in line:
            count += 1
            continue

        for kw in logical_statements:
            if re.search(rf"\b{kw}\b", line):
                count += 1
                break

    return count

def count_cyclomatic_complexity(code, lang):
    """
    McCabe complexity per function.
    CC = 1 + number of decision points (if, elif/else if, for, while, case, catch/except, &&, ||, ?)
    """
    cc_results = {}
    current_func = None
    cc = 1
    inside_function = False

    # Python scope tracking
    base_indent = None

    # C/Java/... scope tracking
    brace_depth = 0
    entered_body = False  # becomes True after we've seen the first '{' of the body

    lines = code.splitlines()
    for raw in lines:
        original = raw  # keep indentation
        line = raw.strip()

        if lang not in LANGUAGE_RULES:
            return {}

        # Skip blanks and single-line comments
        if not line or line.startswith(LANGUAGE_RULES[lang]["single_line_comment"]):
            continue

        # Detect function definition (language-aware) 
        if lang == "python":
            func_def = re.search(r"^def\s+([A-Za-z_]\w*)\s*\([^)]*\)\s*:", original)
        else:
            # Detect signature, body may start here or on a following line with '{'
            func_def = re.search(r"\b([A-Za-z_]\w*)\s*\([^)]*\)\s*(\{)?\s*$", line)

        # ---------- Handle new function definition ----------
        if func_def:
            if lang == "python":
                new_name = func_def.group(1)
                new_indent = len(original) - len(original.lstrip())

                if not inside_function:
                    current_func = new_name
                    cc = 1
                    inside_function = True
                    base_indent = new_indent
                    continue
                else:
                    # Close previous function if a new def appears at same-or-lower indent
                    if new_indent <= base_indent:
                        cc_results[current_func] = cc
                        current_func = new_name
                        cc = 1
                        base_indent = new_indent
                        continue
                    # Treat nested def as a new function too
                    cc_results[current_func] = cc
                    current_func = new_name
                    cc = 1
                    base_indent = new_indent
                    continue
            else:
                new_name = func_def.group(1)
                has_open_brace = (func_def.lastindex and func_def.group(2) == "{")

                if not inside_function:
                    current_func = new_name
                    cc = 1
                    inside_function = True
                    brace_depth = 1 if has_open_brace else 0
                    entered_body = bool(has_open_brace)
                    continue
                else:
                    # If previous body is closed, finalize and start new
                    if entered_body and brace_depth == 0:
                        cc_results[current_func] = cc
                        current_func = new_name
                        cc = 1
                        brace_depth = 1 if has_open_brace else 0
                        entered_body = bool(has_open_brace)
                        continue
                    # Otherwise wait for the '{' to actually enter body
                    pass

        # Count decision points while inside function
        if inside_function:
            if lang == "python":
                # Count decisions 
                tmp = line

                # Python: 'elif' and 'if' are distinct statement, else not taken into account
                cc += len(re.findall(r'\belif\b', tmp))
                cc += len(re.findall(r'\bif\b', tmp))
                cc += len(re.findall(r'\bfor\b', tmp))
                cc += len(re.findall(r'\bwhile\b', tmp))
                cc += len(re.findall(r'\bexcept\b', tmp))  

                # End-of-function: indentation back to (or above) def level
                if line and not line.startswith("#"):
                    cur_indent = len(original) - len(original.lstrip())
                    if cur_indent <= base_indent and not line.startswith("def"):
                        cc_results[current_func] = cc
                        current_func = None
                        inside_function = False
                        base_indent = None

            else:
                # C-like: count braces to know when we're in the body
                opens = original.count("{")
                closes = original.count("}")
                if opens:
                    entered_body = True
                    brace_depth += opens
                if closes:
                    brace_depth -= closes

                if entered_body:
                    tmp = line

                    # First count 'else if' as one decision to avoid double counting "if"
                    ei = len(re.findall(r'\belse\s+if\b', tmp))
                    cc += ei
                    tmp = re.sub(r'\belse\s+if\b', 'ELSE_IF', tmp)

                    # Now count remaining decisions
                    cc += len(re.findall(r'\bif\b', tmp))
                    cc += len(re.findall(r'\bfor\b', tmp))
                    cc += len(re.findall(r'\bwhile\b', tmp))
                    cc += len(re.findall(r'\bcase\b', tmp))
                    cc += len(re.findall(r'\bcatch\b', tmp))
                    cc += tmp.count('&&')
                    cc += tmp.count('||')
                    cc += tmp.count('?')  

                # Close function only after body entered and depth returns to 0
                if entered_body and brace_depth == 0:
                    cc_results[current_func] = cc
                    current_func = None
                    inside_function = False
                    entered_body = False
                    brace_depth = 0

    # End-of-function while inside a function
    if inside_function and current_func is not None:
        cc_results[current_func] = cc

    return cc_results



def compute_fan_in_out(source_files):
    """
    Fan-in and fan-out computation
    Only function calls are taken into account
    """

    # Pass 1: Collect all function names across all files 
    all_functions = set()
    for file_path in source_files:
        lang = detect_language(file_path)
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()
        except Exception as e:
            print(f"⚠️ Skipping {file_path}: {e}")
            continue

        if lang == "python":
            defs = re.findall(r"def\s+([A-Za-z_]\w*)\s*\([^)]*\)\s*:", code)
        else:
            defs = re.findall(r"\b([A-Za-z_]\w*)\s*\([^)]*\)\s*\{", code)
        all_functions.update(defs)

    # Filter out keywords that are not actual functions
    keywords_to_ignore = {"if", "for", "while", "switch", "return", "sizeof", "catch", "try", "else", "elif", "do"}
    all_functions = {f for f in all_functions if f not in keywords_to_ignore}

    #  Initialize results
    fan_in = {f: 0 for f in all_functions}
    fan_out = {f: 0 for f in all_functions}
    calls_map = {f: set() for f in all_functions}
    callers_map = {f: set() for f in all_functions}

    # Pass 2: Re-open each file and analyze calls 
    for file_path in source_files:
        lang = detect_language(file_path)
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()
        except Exception as e:
            print(f"⚠️ Skipping {file_path}: {e}")
            continue

        # Regex for function definitions depending on language
        if lang == "python":
            func_pattern = re.compile(r"def\s+([A-Za-z_]\w*)\s*\([^)]*\)\s*:", re.MULTILINE)
        else:
            func_pattern = re.compile(r"([A-Za-z_]\w*)\s*\([^)]*\)\s*\{", re.MULTILINE)

        for match in func_pattern.finditer(code):
            caller = match.group(1)
            if caller not in all_functions:
                continue

            # Extract the function body
            if lang == "python":
                start_idx = match.end()
                body_match = re.search(r"(?=^def\s+[A-Za-z_]\w*\s*\()", code[start_idx:], re.MULTILINE)
                func_body = code[start_idx:start_idx + body_match.start()] if body_match else code[start_idx:]
            else:
                start_idx = match.end()
                brace_count = 1
                idx = start_idx
                while idx < len(code) and brace_count > 0:
                    if code[idx] == '{':
                        brace_count += 1
                    elif code[idx] == '}':
                        brace_count -= 1
                    idx += 1
                func_body = code[start_idx:idx]

            # Extract all possible calls in one pass
            calls_found = set(re.findall(r"\b([A-Za-z_]\w*)\s*\(", func_body))

            # Filter only user-defined functions and exclude self-calls
            real_calls = calls_found & all_functions - {caller}

            # Update metrics
            fan_out[caller] += len(real_calls)
            calls_map[caller].update(real_calls)
            for callee in real_calls:
                fan_in[callee] += 1
                callers_map[callee].add(caller)

    return fan_in, fan_out



















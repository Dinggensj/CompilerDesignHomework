import re

def preprocess(code):
    code = re.sub(r"#.*", "", code)
    code = re.sub(r'"""[\s\S]*?"""', '', code)
    code = re.sub(r"'''[\s\S]*?'''", '', code)
    code = re.sub(r'[^\w\s]', ' ', code)
    code = re.findall(r'[A-Za-z_]+|\d+|==|>=|<=|!=|[+\-*/%=(){};,]', code)
    return code

def calculate_similarity(tokens1, tokens2, n):
    set1 = set()
    set2 = set()

    for i in range(len(tokens1) - n + 1):
        piece = tuple(tokens1[i:i+n])
        set1.add(piece)

    for i in range(len(tokens2) - n + 1):
        piece = tuple(tokens2[i:i+n])
        set2.add(piece)

    if len(set2) == 0 or len(set1) == 0:
        return 0
    
    common = set1 & set2
    similarity = len(common) / min(len(set1), len(set2))

    return similarity

def print_highlight(code, duplicates):
    return 0
if __name__ == "__main__":
    with open("code1.py", "r", encoding="utf-8") as file:
        code_string1 = file.read()
    with open("code2.py", "r", encoding="utf-8") as file:
        code_string2 = file.read()
    code_string1 = preprocess(code_string1)
    code_string2 = preprocess(code_string2)
    #print(code_string1)
    #print(code_string2)

    similarity = calculate_similarity(code_string1, code_string2, n=3)
    print(similarity)
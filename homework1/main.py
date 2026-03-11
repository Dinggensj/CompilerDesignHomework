import re
import os
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox

def preprocess(code):
    code = re.sub(r"#.*", "", code)
    code = re.sub(r'"""[\s\S]*?"""', '', code)
    code = re.sub(r"'''[\s\S]*?'''", '', code)
    code = re.sub(r'[^\w\s]', ' ', code)
    code = re.findall(r'[A-Za-z_]+|\d+|==|>=|<=|!=|[+\-*/%=(){};,]', code)
    return code

def calculate_similarity(code1, code2, n):
    set1 = set()
    set2 = set()

    for i in range(len(code1) - n + 1):
        piece = tuple(code1[i:i+n])
        set1.add(piece)
    for i in range(len(code2) - n + 1):
        piece = tuple(code2[i:i+n])
        set2.add(piece)

    if len(set2) == 0 or len(set1) == 0:
        return 0
    
    common = set1 & set2
    similarity = len(common) / len(set1)

    return similarity

class CodeCompare:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x400")

        top_frame = tk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.btn_load1 = tk.Button(top_frame, text="导入 code1", command=self.load_file1)
        self.btn_load1.pack(side=tk.LEFT, padx=10)

        self.btn_load2 = tk.Button(top_frame, text="导入 code2", command=self.load_file2)
        self.btn_load2.pack(side=tk.LEFT, padx=10)

        self.lbl_n = tk.Label(top_frame, text="N:")
        self.lbl_n.pack(side=tk.LEFT, padx=(10, 2))
        
        self.entry_n = tk.Entry(top_frame, width=5)
        self.entry_n.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_calc = tk.Button(top_frame, text="计算重复率", command=self.calculate)
        self.btn_calc.pack(side=tk.LEFT, padx=10)

        self.result = tk.Label(top_frame, text="相似度：")
        self.result.pack(side=tk.LEFT, padx=10)

        bottom_frame = tk.Frame(root)
        bottom_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)

        self.text1 = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD)
        self.text1.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        self.text2 = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD)
        self.text2.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        self.text1.tag_config("highlight", foreground="red")
        self.text2.tag_config("highlight", foreground="red")

    def load_file1(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            with open(filepath, "r", encoding="utf-8") as f:
                self.text1.delete(1.0, tk.END)
                self.text1.insert(tk.END, f.read())

    def load_file2(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            with open(filepath, "r", encoding="utf-8") as f:
                self.text2.delete(1.0, tk.END)
                self.text2.insert(tk.END, f.read())

    def calculate(self):
        code1 = self.text1.get(1.0, tk.END)
        code2 = self.text2.get(1.0, tk.END)

        processed_code1 = preprocess(code1)
        processed_code2 = preprocess(code2)
        
        try:
            n_gram = int(self.entry_n.get())
            if n_gram < 2:
                raise ValueError
        except ValueError:
            messagebox.showwarning("N需要大于等于2")
            return
            
        similarity = calculate_similarity(processed_code1, processed_code2, n=n_gram)
        self.result.config(text=f"相似度：{similarity:.4f} ({similarity * 100:.2f}%)")

        self.highlight_duplicates(code1, code2, processed_code1, processed_code2, n=n_gram)

    def highlight_duplicates(self, code1, code2, tokens1, tokens2, n):
        self.text1.tag_remove("highlight", 1.0, tk.END)
        self.text2.tag_remove("highlight", 1.0, tk.END)

        if len(tokens1) < n or len(tokens2) < n:
            return

        set1 = set(tuple(tokens1[i:i+n]) for i in range(len(tokens1) - n + 1))
        set2 = set(tuple(tokens2[i:i+n]) for i in range(len(tokens2) - n + 1))
        common = set1 & set2

        def get_spans(code):
            pattern = r'#.*|"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|[A-Za-z_]+|\d+'
            tokens = []
            for match in re.finditer(pattern, code):
                text = match.group(0)
                if text.startswith('#') or text.startswith('"""') or text.startswith("'''"):
                    continue
                tokens.append((text, match.start(), match.end()))
            return tokens

        tokens_info1 = get_spans(code1)
        tokens_info2 = get_spans(code2)

        for i in range(len(tokens_info1) - n + 1):
            piece = tuple(t[0] for t in tokens_info1[i:i+n])
            if piece in common:
                start_index = f"1.0+{tokens_info1[i][1]}c"
                end_index = f"1.0+{tokens_info1[i+n-1][2]}c"
                self.text1.tag_add("highlight", start_index, end_index)

        for i in range(len(tokens_info2) - n + 1):
            piece = tuple(t[0] for t in tokens_info2[i:i+n])
            if piece in common:
                start_index = f"1.0+{tokens_info2[i][1]}c"
                end_index = f"1.0+{tokens_info2[i+n-1][2]}c"
                self.text2.tag_add("highlight", start_index, end_index)

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeCompare(root)
    root.mainloop()
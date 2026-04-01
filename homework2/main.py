import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox

def preprocess(code: str) -> str:
    code = code.replace("\r\n", "\n").replace("\r", "\n")
    return code

def run_lexical_analysis(code: str) -> str:
    KEYWORDS = {"if": 11, "then": 12, "else": 13, "int": 14, "char": 15, "for": 16}
    OPERATORS = {">=": 32, "==": 33, "++": 37, "=": 31, "+": 34, "/": 35, "%": 36}
    DELIMS = {'"': 21, ";": 22}
    ERR_TWO_CHAR_OPS = {"<=", "--", "!=", "&&", "||", "**"}
    TERMINATOR = "over"

    const_list, const_idx = [], {}
    id_list, id_idx = [], {}

    def add_const(v: str) -> int:
        if v in const_idx:
            return const_idx[v]
        const_idx[v] = len(const_list)
        const_list.append(v)
        return const_idx[v]

    def add_id(name: str) -> int:
        k = name.lower()
        if k in id_idx:
            return id_idx[k]
        id_idx[k] = len(id_list)
        id_list.append(k)
        return id_idx[k]

    def is_space(ch: str) -> bool:
        return ch in (" ", "\t", "\n", "\r")

    OP_STARTS = set()
    for op in OPERATORS:
        if op:
            OP_STARTS.add(op[0])
    for op in ERR_TWO_CHAR_OPS:
        if op:
            OP_STARTS.add(op[0])

    i, n = 0, len(code)
    out_lines = []

    def peek(k: int = 0) -> str:
        j = i + k
        return code[j] if 0 <= j < n else ""

    while i < n:
        ch = peek()

        if is_space(ch):
            i += 1
            continue

        if ch.isalpha():
            start = i
            while peek().isalpha():
                i += 1
            word = code[start:i]
            low = word.lower()

            if low == TERMINATOR:
                break

            if peek().isdigit() or peek() == "_":
                bad_start = start
                while i < n and (not is_space(peek())) and (peek() not in DELIMS) and (peek() not in OP_STARTS):
                    i += 1
                bad = code[bad_start:i]
                out_lines.append(f"{bad}\t({bad},err)")
                continue

            if low in KEYWORDS:
                out_lines.append(f"{word}\t({low},{KEYWORDS[low]})")
                continue

            if len(word) >= 10:
                out_lines.append(f"{word}\t({word},err)")
                continue

            idx = add_id(word)
            out_lines.append(f"{word}\t({word},{51 + idx})")
            continue

        if ch.isdigit():
            start = i
            while peek().isdigit():
                i += 1
            num = code[start:i]
            idx = add_const(num)
            out_lines.append(f"{num}\t({num},{41 + idx})")
            continue

        if ch in DELIMS:
            i += 1
            out_lines.append(f"{ch}\t({ch},{DELIMS[ch]})")
            continue

        two = ch + peek(1)
        if two in ERR_TWO_CHAR_OPS:
            i += 2
            out_lines.append(f"{two}\t({two},err)")
            continue

        if two in OPERATORS:
            i += 2
            out_lines.append(f"{two}\t({two},{OPERATORS[two]})")
            continue
        if ch in OPERATORS:
            i += 1
            out_lines.append(f"{ch}\t({ch},{OPERATORS[ch]})")
            continue

        i += 1
        out_lines.append(f"{ch}\t({ch},err)")

    out_lines.append("over")
    out_lines.append("")
    out_lines.append("常数表中的内容为：" + ("，".join(const_list) if const_list else ""))
    out_lines.append("变量表中的内容为：" + ("，".join(id_list) if id_list else ""))

    return "\n".join(out_lines)

class CodeAnalyze:
    def __init__(self, root):
        self.root = root
        self.root.title("词法分析器")
        self.root.geometry("600x400")

        top_frame = tk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.btn_load_file = tk.Button(top_frame, text="导入 code", command=self.load_file)
        self.btn_load_file.pack(side=tk.LEFT, padx=10)

        self.btn_analyze = tk.Button(top_frame, text="词法分析", command=self.analyze)
        self.btn_analyze.pack(side=tk.LEFT, padx=10)

        bottom_frame = tk.Frame(root)
        bottom_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)

        self.text_src = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD)
        self.text_src.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        self.text_out = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD)
        self.text_out.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

    def load_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            with open(filepath, "r", encoding="utf-8") as f:
                self.text_src.delete(1.0, tk.END)
                self.text_src.insert(tk.END, f.read())

    def analyze(self):
        code = self.text_src.get("1.0", tk.END).rstrip("\n")
        code = preprocess(code)

        if not code.strip():
            messagebox.showwarning("提示", "请先输入或加载源程序。")
            return

        result = run_lexical_analysis(code)

        self.text_out.delete("1.0", tk.END)
        self.text_out.insert(tk.END, result)

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeAnalyze(root)
    root.mainloop()
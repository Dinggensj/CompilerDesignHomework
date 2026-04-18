#include <iostream>
#include <string>
#include <vector>
#include <cctype>

using namespace std;

string removeSpaces(string &s) {
    string t;
    t.reserve(s.size());
    for (unsigned char ch : s) {
        if (!isspace(ch)) t.push_back((char)ch);
    }
    return t;
}

vector<string> splitBySemicolon(string &s) {
    vector<string> parts;
    string cur;
    for (char ch : s) {
        if (ch == ';') {
            parts.push_back(cur);
            cur.clear();
        } else {
            cur.push_back(ch);
        }
    }
    parts.push_back(cur);
    return parts;
}

bool accept(string &s) {
    size_t i = 0;
    auto next = [&]() -> char { return (i < s.size() ? s[i] : '\0'); };

    while (next() == 'a' || next() == 'b') i++;

    if (i + 2 > s.size() || s[i - 1] != 'b' || s[i - 2] != 'b') return false;

    string op;
    if (next() == '<' || next() == '>') {
        op.push_back(next()); i++;
        if (next() == '=') { op.push_back('='); i++; }
    } else if (next() == '=' || next() == '!') {
        op.push_back(next()); i++;
        if (next() != '=') return false;
        op.push_back('='); i++;
    } else return false;

    if (!(op=="<" || op=="<=" || op==">" || op==">=" || op=="==" || op=="!=")) return false;

    if (next() != '1') return false;
    i++;
    return i == s.size();
}

int main() {
    string line;
    while (getline(cin, line)) {
        string cleaned = removeSpaces(line);
        auto sentences = splitBySemicolon(cleaned);

        for (auto &sent : sentences) {
            if (sent.empty()) continue;
            cout << (accept(sent) ? "yes" : "no") << "\n";
        }
    }
    return 0;
} 
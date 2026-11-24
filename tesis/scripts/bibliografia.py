#!/usr/bin/env python3
"""Fuente única de la bibliografía.

Genera, desde la misma lista de referencias:
  - referencias/bibliografia_zotero.bib  (importable en Zotero)
  - referencias/bibliografia_zotero.ris  (importable en Zotero)
  - tesis/generado/referencias.tex       (lista APA 7 para LaTeX/natbib)
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

# Autores: lista de (apellidos, nombres).  type: book | article | inproceedings | incollection | misc | phdthesis | report | legislation
REFS = [
    dict(key="goodfellow2016", type="book", authors=[("Goodfellow", "Ian"), ("Bengio", "Yoshua"), ("Courville", "Aaron")],
         year=2016, title="Deep learning", publisher="MIT Press", url="https://www.deeplearningbook.org/"),
    dict(key="haykin2009", type="book", authors=[("Haykin", "Simon")], year=2009,
         title="Neural networks and learning machines", edition="3", publisher="Pearson Education"),
    dict(key="rumelhart1986", type="article", authors=[("Rumelhart", "David E."), ("Hinton", "Geoffrey E."), ("Williams", "Ronald J.")],
         year=1986, title="Learning representations by back-propagating errors", journal="Nature", volume="323", number="6088",
         pages="533--536", doi="10.1038/323533a0"),
    dict(key="bishop2006", type="book", authors=[("Bishop", "Christopher M.")], year=2006,
         title="Pattern recognition and machine learning", publisher="Springer"),
    dict(key="nielsen2015", type="book", authors=[("Nielsen", "Michael A.")], year=2015,
         title="Neural networks and deep learning", publisher="Determination Press", url="http://neuralnetworksanddeeplearning.com/"),
    dict(key="klabnik2023", type="book", authors=[("Klabnik", "Steve"), ("Nichols", "Carol")], year=2023,
         title="The Rust programming language", edition="2", publisher="No Starch Press", url="https://doc.rust-lang.org/book/"),
    dict(key="blandy2021", type="book", authors=[("Blandy", "Jim"), ("Orendorff", "Jason"), ("Tindall", "Leonora F. S.")], year=2021,
         title="Programming Rust: Fast, safe systems development", edition="2", publisher="O'Reilly Media"),
    dict(key="mcculloch1943", type="article", authors=[("McCulloch", "Warren S."), ("Pitts", "Walter")], year=1943,
         title="A logical calculus of the ideas immanent in nervous activity", journal="The Bulletin of Mathematical Biophysics",
         volume="5", number="4", pages="115--133", doi="10.1007/BF02478259"),
    dict(key="rosenblatt1958", type="article", authors=[("Rosenblatt", "Frank")], year=1958,
         title="The perceptron: A probabilistic model for information storage and organization in the brain",
         journal="Psychological Review", volume="65", number="6", pages="386--408", doi="10.1037/h0042519"),
    dict(key="minsky1969", type="book", authors=[("Minsky", "Marvin"), ("Papert", "Seymour")], year=1969,
         title="Perceptrons: An introduction to computational geometry", publisher="MIT Press"),
    dict(key="lecun2015", type="article", authors=[("LeCun", "Yann"), ("Bengio", "Yoshua"), ("Hinton", "Geoffrey")], year=2015,
         title="Deep learning", journal="Nature", volume="521", number="7553", pages="436--444", doi="10.1038/nature14539"),
    dict(key="cybenko1989", type="article", authors=[("Cybenko", "George")], year=1989,
         title="Approximation by superpositions of a sigmoidal function", journal="Mathematics of Control, Signals and Systems",
         volume="2", number="4", pages="303--314", doi="10.1007/BF02551274"),
    dict(key="hornik1989", type="article", authors=[("Hornik", "Kurt"), ("Stinchcombe", "Maxwell"), ("White", "Halbert")], year=1989,
         title="Multilayer feedforward networks are universal approximators", journal="Neural Networks", volume="2", number="5",
         pages="359--366", doi="10.1016/0893-6080(89)90020-8"),
    dict(key="glorot2010", type="inproceedings", authors=[("Glorot", "Xavier"), ("Bengio", "Yoshua")], year=2010,
         title="Understanding the difficulty of training deep feedforward neural networks",
         booktitle="Proceedings of the Thirteenth International Conference on Artificial Intelligence and Statistics",
         volume="9", pages="249--256", publisher="PMLR", url="https://proceedings.mlr.press/v9/glorot10a.html"),
    dict(key="he2015", type="inproceedings", authors=[("He", "Kaiming"), ("Zhang", "Xiangyu"), ("Ren", "Shaoqing"), ("Sun", "Jian")], year=2015,
         title="Delving deep into rectifiers: Surpassing human-level performance on ImageNet classification",
         booktitle="Proceedings of the IEEE International Conference on Computer Vision", pages="1026--1034", publisher="IEEE",
         doi="10.1109/ICCV.2015.123"),
    dict(key="lecun1998", type="incollection", authors=[("LeCun", "Yann"), ("Bottou", "Léon"), ("Orr", "Genevieve B."), ("Müller", "Klaus-Robert")],
         year=1998, title="Efficient BackProp", booktitle="Neural networks: Tricks of the trade",
         editors=[("Orr", "Genevieve B."), ("Müller", "Klaus-Robert")], pages="9--50", publisher="Springer", doi="10.1007/3-540-49430-8_2"),
    dict(key="strang2016", type="book", authors=[("Strang", "Gilbert")], year=2016,
         title="Introduction to linear algebra", edition="5", publisher="Wellesley-Cambridge Press"),
    dict(key="deisenroth2020", type="book", authors=[("Deisenroth", "Marc Peter"), ("Faisal", "A. Aldo"), ("Ong", "Cheng Soon")], year=2020,
         title="Mathematics for machine learning", publisher="Cambridge University Press", doi="10.1017/9781108679930"),
    dict(key="ruder2016", type="misc", authors=[("Ruder", "Sebastian")], year=2016,
         title="An overview of gradient descent optimization algorithms", publisher="arXiv", doi="10.48550/arXiv.1609.04747"),
    dict(key="bottou2010", type="inproceedings", authors=[("Bottou", "Léon")], year=2010,
         title="Large-scale machine learning with stochastic gradient descent", booktitle="Proceedings of COMPSTAT'2010",
         pages="177--186", publisher="Physica-Verlag", doi="10.1007/978-3-7908-2604-3_16"),
    dict(key="baydin2018", type="article", authors=[("Baydin", "Atılım Güneş"), ("Pearlmutter", "Barak A."), ("Radul", "Alexey Andreyevich"), ("Siskind", "Jeffrey Mark")],
         year=2018, title="Automatic differentiation in machine learning: A survey", journal="Journal of Machine Learning Research",
         volume="18", number="153", pages="1--43", url="https://jmlr.org/papers/v18/17-468.html"),
    dict(key="russell2021", type="book", authors=[("Russell", "Stuart"), ("Norvig", "Peter")], year=2021,
         title="Artificial intelligence: A modern approach", edition="4", publisher="Pearson"),
    dict(key="matsakis2014", type="article", authors=[("Matsakis", "Nicholas D."), ("Klock", "Felix S., II")], year=2014,
         title="The Rust language", journal="ACM SIGAda Ada Letters", volume="34", number="3", pages="103--104", doi="10.1145/2692956.2663188"),
    dict(key="jung2018", type="article", authors=[("Jung", "Ralf"), ("Jourdan", "Jacques-Henri"), ("Krebbers", "Robbert"), ("Dreyer", "Derek")],
         year=2018, title="RustBelt: Securing the foundations of the Rust programming language",
         journal="Proceedings of the ACM on Programming Languages", volume="2", number="POPL", pages="66:1--66:34", doi="10.1145/3158154"),
    dict(key="maslej2024", type="report", authors=[("Maslej", "Nestor"), ("Fattorini", "Loredana"), ("Perrault", "Raymond"), ("Parli", "Vanessa"),
         ("Reuel", "Anka"), ("Brynjolfsson", "Erik"), ("Etchemendy", "John"), ("Ligett", "Katrina"), ("Lyons", "Terah"), ("Manyika", "James"),
         ("Niebles", "Juan Carlos"), ("Shoham", "Yoav"), ("Wald", "Russell"), ("Clark", "Jack")], year=2024,
         title="The AI Index 2024 annual report", institution="AI Index Steering Committee, Institute for Human-Centered AI, Stanford University",
         url="https://aiindex.stanford.edu/report/"),
    dict(key="stackoverflow2024", type="misc", authors=[("Stack Overflow", None)], year=2024,
         title="2024 Stack Overflow developer survey", publisher="Stack Overflow", url="https://survey.stackoverflow.co/2024/"),
    dict(key="unesco2022", type="report", authors=[("UNESCO", None)], year=2022,
         title="Recommendation on the ethics of artificial intelligence", institution="United Nations Educational, Scientific and Cultural Organization",
         url="https://unesdoc.unesco.org/ark:/48223/pf0000381137"),
    dict(key="bolivia2011", type="legislation", authors=[("Asamblea Legislativa Plurinacional de Bolivia", None)], year=2011,
         title="Ley N.º 164: Ley General de Telecomunicaciones, Tecnologías de Información y Comunicación", publisher="Gaceta Oficial del Estado Plurinacional de Bolivia"),
    dict(key="hernandez2018", type="book", authors=[("Hernández Sampieri", "Roberto"), ("Mendoza Torres", "Christian Paulina")], year=2018,
         title="Metodología de la investigación: Las rutas cuantitativa, cualitativa y mixta", publisher="McGraw-Hill Interamericana", language="spanish"),
    dict(key="apa2020", type="book", authors=[("American Psychological Association", None)], year=2020,
         title="Publication manual of the American Psychological Association", edition="7", publisher="American Psychological Association",
         doi="10.1037/0000165-000"),
]

ORD = {"2": "2nd", "3": "3rd", "4": "4th", "5": "5th", "7": "7th"}


def inicial(nombres):
    partes = []
    for n in nombres.replace(",", " ,").split():
        if n == ",":
            continue
        if n in ("II", "III", "Jr."):
            partes.append(n)
        elif "-" in n:
            partes.append("-".join(p[0] + "." for p in n.split("-")))
        else:
            partes.append(n[0] + ".")
    return " ".join(partes).replace(" II", ", II")


def autor_apa(a):
    ap, no = a
    return ap if no is None else f"{ap}, {inicial(no)}"


def lista_apa(auts):
    f = [autor_apa(a) for a in auts]
    if len(f) == 1:
        return f[0]
    if len(f) <= 20:
        return ", ".join(f[:-1]) + ", \\& " + f[-1]
    return ", ".join(f[:19]) + ", \\ldots{} " + f[-1]


def cita_corta(auts):
    ap = [a[0] for a in auts]
    if len(ap) == 1:
        return ap[0]
    if len(ap) == 2:
        return f"{ap[0]} y {ap[1]}"
    return f"{ap[0]} et~al."


def tex(s):
    return s.replace("&", "\\&").replace("_", "\\_").replace("%", "\\%")


def enlace(r):
    if r.get("doi"):
        return f" \\url{{https://doi.org/{r['doi']}}}"
    if r.get("url"):
        return f" \\url{{{r['url']}}}"
    return ""


def apa(r):
    a = lista_apa(r["authors"])
    a = a if a.endswith(".") else a + "."
    y = f"({r['year']})."
    t = tex(r["title"])
    ed = f" ({ORD[r['edition']]} ed.)" if r.get("edition") else ""
    ty = r["type"]
    if ty == "book":
        pub = "" if r["publisher"] == r["authors"][0][0] else f" {tex(r['publisher'])}."
        s = f"{a} {y} \\emph{{{t}}}{ed}.{pub}"
    elif ty == "article":
        num = f"({r['number']})" if r.get("number") else ""
        s = f"{a} {y} {t}. \\emph{{{tex(r['journal'])}}}, \\emph{{{r['volume']}}}{num}, {r['pages'].replace('--', '–')}."
    elif ty == "inproceedings":
        vol = f"Vol.~{r['volume']}, " if r.get("volume") else ""
        s = f"{a} {y} {t}. En \\emph{{{tex(r['booktitle'])}}} ({vol}pp.~{r['pages'].replace('--', '–')}). {tex(r['publisher'])}."
    elif ty == "incollection":
        eds = " y ".join(f"{inicial(n)} {ap}" for ap, n in r["editors"])
        s = f"{a} {y} {t}. En {eds} (Eds.), \\emph{{{tex(r['booktitle'])}}} (pp.~{r['pages'].replace('--', '–')}). {tex(r['publisher'])}."
    elif ty == "phdthesis":
        s = f"{a} {y} \\emph{{{t}}} [Tesis doctoral, {tex(r['school'])}]."
    elif ty == "report":
        inst = "" if r["institution"] == r["authors"][0][0] else f" {tex(r['institution'])}."
        s = f"{a} {y} \\emph{{{t}}}.{inst}"
    elif ty == "legislation":
        s = f"{a} {y} \\emph{{{t}}}. {tex(r['publisher'])}."
    else:
        pub = "" if r["publisher"] == r["authors"][0][0] else f" {tex(r['publisher'])}."
        s = f"{a} {y} \\emph{{{t}}}.{pub}"
    return s + enlace(r)


def bib_nombre(a):
    ap, no = a
    if no is None:
        return f"{{{ap}}}"
    if no.endswith((", II", ", III", ", Jr.")):
        nombre, sufijo = no.rsplit(", ", 1)
        return f"{ap}, {sufijo}, {nombre}"
    return f"{ap}, {no}"


def bib(r):
    tipo = {"legislation": "misc", "report": "techreport"}.get(r["type"], r["type"])
    campos = [("author", " and ".join(bib_nombre(a) for a in r["authors"])), ("year", str(r["year"])), ("title", "{" + r["title"] + "}")]
    for k in ("journal", "booktitle", "volume", "number", "pages", "publisher", "school", "institution", "doi", "url", "language"):
        if r.get(k):
            v = r[k]
            if k in ("publisher", "institution", "school") and " and " in v:
                v = "{" + v + "}"
            campos.append((k, v))
    if r.get("edition"):
        campos.append(("edition", r["edition"]))
    if r.get("editors"):
        campos.append(("editor", " and ".join(bib_nombre(a) for a in r["editors"])))
    if r["type"] == "legislation":
        campos.append(("note", "Ley del Estado Plurinacional de Bolivia, 8 de agosto de 2011"))
    cuerpo = ",\n".join(f"  {k:<11}= {{{v}}}" if not v.startswith("{") else f"  {k:<11}= {{{v}}}" for k, v in campos)
    return f"@{tipo}{{{r['key']},\n{cuerpo}\n}}\n"


def ris(r):
    ty = {"book": "BOOK", "article": "JOUR", "inproceedings": "CPAPER", "incollection": "CHAP", "phdthesis": "THES",
          "report": "RPRT", "misc": "GEN", "legislation": "STAT"}[r["type"]]
    L = [f"TY  - {ty}"]
    for ap, no in r["authors"]:
        L.append(f"AU  - {ap}" + (f", {no}" if no else ""))
    for ap, no in r.get("editors", []):
        L.append(f"ED  - {ap}, {no}")
    L += [f"PY  - {r['year']}", f"TI  - {r['title']}"]
    if r.get("journal"):
        L.append(f"JO  - {r['journal']}")
    if r.get("booktitle"):
        L.append(f"T2  - {r['booktitle']}")
    for k, tag in (("volume", "VL"), ("number", "IS"), ("edition", "ET"), ("doi", "DO"), ("url", "UR")):
        if r.get(k):
            L.append(f"{tag}  - {r[k]}")
    if r.get("pages") and "--" in r["pages"]:
        sp, ep = r["pages"].split("--")
        L += [f"SP  - {sp}", f"EP  - {ep}"]
    pub = r.get("publisher") or r.get("school") or r.get("institution")
    if pub:
        L.append(f"PB  - {pub}")
    L.append(f"ID  - {r['key']}")
    L.append("ER  - ")
    return "\n".join(L) + "\n"


def orden(r):
    import unicodedata
    s = "".join(c for c in unicodedata.normalize("NFD", r["authors"][0][0]) if unicodedata.category(c) != "Mn")
    return (s.lower(), r["year"], r["title"].lower())


def main():
    refs = sorted(REFS, key=orden)
    assert len({r["key"] for r in refs}) == len(refs)
    cab = "% Bibliografía del proyecto «Construcción de una Red Neuronal Artificial desde Cero utilizando Rust»\n" \
          "% Generado por tesis/scripts/bibliografia.py — importar en Zotero: Archivo > Importar.\n\n"
    (RAIZ / "referencias/bibliografia_zotero.bib").write_text(cab + "\n".join(bib(r) for r in refs), encoding="utf-8")
    (RAIZ / "referencias/bibliografia_zotero.ris").write_text("\n".join(ris(r) for r in refs), encoding="utf-8")
    items = []
    for r in refs:
        corta = cita_corta(r["authors"])
        items.append(f"\\bibitem[{{{corta}}}({r['year']})]{{{r['key']}}}\n{apa(r)}\n")
    salida = RAIZ / "tesis/generado/referencias.tex"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text("\\begin{thebibliography}{99}\n\n" + "\n".join(items) + "\n\\end{thebibliography}\n", encoding="utf-8")
    print(f"{len(refs)} referencias exportadas")


if __name__ == "__main__":
    main()

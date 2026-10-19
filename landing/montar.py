"""Monta a landing page de SQL para Analistas a partir de src/ e config.json.

Uso: python3 landing/montar.py
Saídas:
  sql-para-analistas/  pronta para publicar, no caminho que o site serve (index.html, img/, fonts/, robots.txt, sitemap.xml)
  landing/previa/  a mesma página sem o envelope <html>/<head>, para pré-visualização
Campos vazios em config.json não quebram a página: o botão leva ao CTA final,
o preço some dos textos e a pergunta sobre garantia sai do FAQ.
"""
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl

AQUI = Path(__file__).resolve().parent
SRC, SITE, PREVIA = AQUI / "src", AQUI.parent / "sql-para-analistas", AQUI / "previa"


def checkout(cfg, posicao):
    url = cfg["hotmart_url"].strip()
    if not url:
        return "#cta-final"
    p = urlsplit(url)
    q = dict(parse_qsl(p.query))
    q.update({"utm_source": cfg.get("utm_source") or "landing", "utm_medium": cfg.get("utm_medium") or "site",
              "utm_campaign": cfg.get("utm_campaign") or "sql-analistas", "utm_content": posicao, "src": posicao})
    return html.escape(urlunsplit(p._replace(query=urlencode(q))), quote=True)


def condicionais(texto, cfg):
    def se(m):
        return m.group(2) if cfg.get(m.group(1), "").strip() else ""
    return re.sub(r"<!--se:(\w+)-->(.*?)<!--/se-->", se, texto, flags=re.S)


def faq(texto):
    itens = re.findall(r"<summary>(.*?)</summary><div class=\"resp\"><p>(.*?)</p>", texto, flags=re.S)
    limpar = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()
    return [{"@type": "Question", "name": limpar(q), "acceptedAnswer": {"@type": "Answer", "text": limpar(r)}}
            for q, r in itens]


def jsonld(cfg, texto, base):
    livro = {
        "@type": ["Book", "Product"], "name": "SQL para Analistas",
        "description": "Guia prático de SQL padrão para analistas de negócio que usam planilha: 8 capítulos, "
                       "6 casos de negócio, 9 erros que mudam decisões, base de prática e 10 exercícios resolvidos.",
        "inLanguage": "pt-BR", "bookFormat": "https://schema.org/EBook", "numberOfPages": 111,
        "bookEdition": "1ª edição", "datePublished": "2026-10",
        "image": base + "img/og-sql-para-analistas.jpg",
        "about": ["SQL", "Análise de dados", "Análise de negócio"],
    }
    if cfg["dominio"]:
        livro["url"] = cfg["dominio"] + "/"
        livro["@id"] = cfg["dominio"] + "/#ebook"
    if cfg["autor"]:
        livro["author"] = {"@type": "Person", "name": cfg["autor"]}
    if cfg["hotmart_url"] and cfg["preco_numero"]:
        livro["offers"] = {"@type": "Offer", "url": cfg["hotmart_url"], "price": cfg["preco_numero"],
                           "priceCurrency": "BRL", "availability": "https://schema.org/InStock"}
    grafo = {"@context": "https://schema.org", "@graph": [livro, {"@type": "FAQPage", "mainEntity": faq(texto)}]}
    return ('<script type="application/ld+json">\n'
            + json.dumps(grafo, ensure_ascii=False, indent=1).replace("</", "<\\/") + "\n</script>")


def main():
    cfg = json.loads((AQUI / "config.json").read_text(encoding="utf-8"))
    cfg = {k: (v.strip() if isinstance(v, str) else v) for k, v in cfg.items()}
    cfg["dominio"] = cfg.get("dominio", "").rstrip("/")
    base = cfg["dominio"] + "/" if cfg["dominio"] else ""
    preco = cfg.get("preco", "")

    t = (SRC / "index.html").read_text(encoding="utf-8")
    t = condicionais(t, cfg)
    t = re.sub(r"\{\{CHECKOUT:([\w-]+)\}\}", lambda m: checkout(cfg, m.group(1)), t)
    partes = ["PDF de 111 páginas", "Acesso imediato após a confirmação do pagamento", "Pagamento seguro pela Hotmart"]
    if cfg.get("garantia"):
        partes.append(f"Garantia de {html.escape(cfg['garantia'])}")
    trocas = {
        "{{TEXTO_BOTAO}}": f"Quero o e-book por {html.escape(preco)}" if preco else "Quero o e-book",
        "{{MICROCOPY}}": " · ".join(partes),
        "{{BARRA_LINHA}}": f"PDF · {preco}" if preco else "E-book em PDF",
        "{{GARANTIA}}": html.escape(cfg.get("garantia", "")),
        "{{AUTOR}}": html.escape(cfg.get("autor", "")),
        "{{DOMINIO}}": cfg["dominio"],
        "{{BASE}}": base,
    }
    for k, v in trocas.items():
        t = t.replace(k, v)
    t = t.replace("{{JSONLD}}", jsonld(cfg, t, base))
    if "{{" in t:
        raise SystemExit("Marcação sem valor: " + ", ".join(sorted(set(re.findall(r"\{\{[^}]+\}\}", t)))))

    for destino in (SITE, PREVIA):
        if destino.exists():
            shutil.rmtree(destino)
        shutil.copytree(SRC, destino, ignore=shutil.ignore_patterns("index.html", ".DS_Store"))
    (SITE / "index.html").write_text(t, encoding="utf-8")
    (SITE / "robots.txt").write_text("User-agent: *\nAllow: /\n" + (f"Sitemap: {cfg['dominio']}/sitemap.xml\n" if cfg["dominio"] else ""))
    if cfg["dominio"]:
        (SITE / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"<url><loc>{cfg['dominio']}/</loc></url></urlset>\n")

    # Prévia: sem doctype/html/head/body, com título curto.
    cab = re.search(r"<head>(.*?)</head>", t, flags=re.S).group(1)
    corpo = re.search(r"<body>(.*)</body>", t, flags=re.S).group(1)
    cab = re.sub(r'<meta (charset|name="viewport")[^>]*>\n?', "", cab)
    cab = cab.replace("<title>SQL para Analistas: e-book prático em PDF</title>", "<title>SQL para Analistas</title>")
    (PREVIA / "index.html").write_text(cab.strip() + "\n" + corpo.strip() + "\n", encoding="utf-8")

    faltando = [k for k in ("hotmart_url", "preco", "preco_numero", "garantia", "dominio", "autor") if not cfg.get(k)]
    print("Site:", SITE)
    print("Campos a preencher em config.json:", ", ".join(faltando) if faltando else "nenhum")


if __name__ == "__main__":
    main()

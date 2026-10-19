# Landing page · SQL para Analistas

Página de venda do e-book na Hotmart, no visual do PDF (faixa amarela, Inter, JetBrains Mono, consultas entre filetes).

## Publicar

1. Preencha `config.json`:
   - `hotmart_url`: link de checkout da Hotmart (ex.: `https://pay.hotmart.com/XXXXXX`).
   - `preco`: texto do botão, ex. `R$ 47` · `preco_numero`: só o número, ex. `47.00` (vai para o Google).
   - `garantia`: ex. `7 dias` (aparece na microcopy e no FAQ; vazio esconde os dois).
   - `dominio`: ex. `https://sqlparaanalistas.com.br` (canonical, Open Graph, sitemap).
   - `autor`: nome que aparece no rodapé e nos dados estruturados.
2. Rode `python3 landing/montar.py`.
3. A página sai em `sql-para-analistas/` na raiz do repositório, que é o caminho publicado. Faça o commit dessa pasta junto com as mudanças em `landing/`.

Cada botão de compra recebe UTMs e `src` próprios (`hero`, `capitulos`, `paraquem`, `final`, `barra-mobile`, `topo`), que aparecem nos relatórios da Hotmart. UTMs de quem chega à página são repassadas ao checkout.

## Estrutura

- `src/index.html`: modelo da página (edite textos aqui).
- `src/img/`: miniaturas de páginas reais do PDF (WebP), imagem de compartilhamento 1200×630, ícones.
- `src/fonts/`: Inter e JetBrains Mono reduzidas ao alfabeto latino (WOFF2, licença OFL em `licencas/`).
- `../sql-para-analistas/`: versão final gerada (não edite à mão). `previa/`: a mesma página sem o envelope `<html>`, para pré-visualização (fora do git).

## Depois de publicar

- Teste a imagem de compartilhamento no depurador do Facebook e no Post Inspector do LinkedIn.
- Valide os dados estruturados em validator.schema.org.
- A tag do Google Ads (gtag.js) já está no `<head>` de `src/index.html`. Para medir cliques nos botões, descomente a linha correspondente no fim do arquivo (com aviso de cookies/LGPD).
- Se regenerar o PDF, refaça as miniaturas (comandos no histórico desta pasta: `pdftoppm` + `cwebp`).

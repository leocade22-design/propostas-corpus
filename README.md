# Propostas CORPUS

Monta a **Proposta** e o **Aceite** em `.docx` a partir dos modelos do Word da
empresa, direto no celular ou no navegador do PC. Sem servidor, sem login: o
documento é montado no próprio aparelho.

## O que ele faz

- **Colar e extrair** — cole a mensagem do cliente, mesmo fora de padrão, e o app
  reconhece CNPJ, CEP, telefone e e-mail em qualquer formato.
- **Buscar por CNPJ** — puxa razão social e endereço da Receita (BrasilAPI, com
  Minha Receita de reserva). É a única coisa que sai do aparelho, e só quando você
  toca no botão.
- **Carteira de clientes** — toda proposta gerada alimenta a lista, e ela
  sincroniza entre os seus aparelhos (cifrada de ponta a ponta: o servidor
  guarda um embaralhado que nem ele consegue ler).
- **Timbrado no documento** — cabeçalho, marca d'água e rodapé com a assinatura
  de quem gerou e um QR code que leva o cliente à central de contato.
- **Linha de serviço em etapas** — categoria → classe → modalidade → veículo, com
  a descrição, a unidade e as observações técnicas já preenchidas pelo catálogo
  da Corpus (resíduos Classe I e II, recicláveis, mão de obra, locação).
- **Proposta e Aceite** — gera um, o outro ou os dois de uma vez. Cada tipo pode
  ter a própria pasta de destino (Chrome/Edge), e um popup confirma antes e diz
  onde o arquivo caiu depois.
- **Enquadramento calculado na hora** — a largura de cada coluna da tabela é
  medida com o texto que vai realmente sair, pra nenhuma coluna espremer o
  conteúdo nem sobrar espaço à toa.
- **Histórico** — toda proposta gerada fica salva e pode ser reaberta, editada
  ou duplicada.
- **Rascunho automático** — o que está preenchido é gravado a cada mudança e
  volta sozinho se o app for fechado no meio.

## Onde ficam os dados

No `localStorage` **deste aparelho**, e em nenhum outro lugar — nunca no HTML,
que é público e somente leitura. Com a sincronia ligada (Ajustes → Sincronizar
aparelhos), o mesmo conteúdo passa a valer nos três aparelhos, cifrado antes de
sair daqui.

| Chave                  | O que guarda                          | Exportável por        |
|------------------------|---------------------------------------|-----------------------|
| `corpus_propostas_v1`  | histórico de propostas geradas        | Propostas salvas → Exportar |
| `corpus_clientes_rapidos_v1` | a carteira de clientes          | Ajustes → Backup completo |
| `corpus_meus_dados_v1` | quem assina a proposta e o aceite     | Ajustes → Backup completo |
| `corpus_catalogo_v1`   | catálogo editado e categorias         | *(sem exportação)*    |
| `corpus_rascunho_v1`   | o preenchimento em andamento          | —                     |

**Atualizar o app não apaga nada.** O `sw.js` troca os arquivos, nunca o
armazenamento.

**O que apaga:** "limpar dados do site", desinstalar o app da tela inicial, aba
anônima, e — o mais traiçoeiro — o navegador descartando por falta de espaço em
disco, já que esse armazenamento é *best-effort*.

> Cuidado com "Limpar armazenamento"/"Limpar dados" nas configurações do Android.
> "Limpar cache" é seguro: só remove os arquivos guardados do app.

Por isso: exporte depois de cada lote de propostas e guarde o JSON numa pasta com
backup (rede da empresa, Drive). É o único jeito de sobreviver a trocar de
aparelho.

## A lista de clientes não mora aqui

O `.gitignore` bloqueia `clientes*.json` de propósito. A carteira tem razão
social, CNPJ, nome e telefone de contato de clientes reais; num repositório
público isso ficaria legível pra qualquer pessoa da internet.

O app nasce com a carteira vazia. O formato esperado está em
[`dados/clientes-exemplo.json`](dados/clientes-exemplo.json):

```json
[
  {
    "razaoSocial": "CLIENTE EXEMPLO LTDA",
    "cnpj": "00.000.000/0001-00",
    "contato": "Nome do contato - 27 99999-9999",
    "endereco": "RUA EXEMPLO, 100, CENTRO, VITÓRIA - ES. 29000-000",
    "ultimoPO": "100001-2026"
  }
]
```

Cliente novo com CNPJ que já existe é atualizado, não duplicado.

## Estrutura

| Arquivo                | O que é                                                  |
|------------------------|----------------------------------------------------------|
| `index.html`           | O app inteiro: estilos, marcação e o JavaScript          |
| `modelos.js`           | Os dois `.docx` da Corpus, em base64                      |
| `vendor/jszip.min.js`  | JSZip 3.10.1, servido pelo próprio site                    |
| `sw.js` / `manifest.json` | O que faz instalar na tela inicial e rodar offline     |
| `icons/`               | Os três PNGs do ícone (192, 512 e maskable)              |
| `ferramentas-icone.py` | Refaz os três PNGs do ícone a partir do logo em `modelos.js` |

### Como o `.docx` é montado

Um `.docx` é um zip. O app abre o modelo com o JSZip, lê o `word/document.xml`,
troca os marcadores `{razao_social}`, `{objeto}`, `{proposta_numero}` e afins pelo
que está no formulário, e fecha o zip de novo. A tabela de itens é a linha `<w:tr>`
marcada com `{#itens}…{/itens}`: ela é usada como molde e repetida por item.

**Trocar o modelo do Word:** converta o `.docx` novo para base64 e substitua
`TPL_P` (proposta) ou `TPL_A` (aceite) em `modelos.js`. Os marcadores precisam
continuar existindo, e cada um tem que estar inteiro dentro de um mesmo trecho de
texto — se o Word partir `{razao_social}` no meio, a troca não acontece. Editar o
campo de uma vez só, sem voltar com o cursor, costuma resolver.

## Publicar uma versão nova

`.github/workflows/pages.yml` publica a cada push na `main`. Dá pra publicar na
mão pela aba **Actions** → *Publicar no GitHub Pages* → *Run workflow*.

> O Pages precisa estar em *Settings → Pages → Source: GitHub Actions*.

**Ao publicar, mude a versão nos dois arquivos, juntos:**

| Arquivo      | Constante     |
|--------------|---------------|
| `sw.js`      | `VERSAO`      |
| `index.html` | `APP_VERSION` |

É a mudança do conteúdo de `sw.js` que faz o navegador perceber que existe versão
nova. Sem isso o app instalado continua rodando a versão antiga indefinidamente.
A versão aparece no card *Sobre o app*, com o botão de buscar atualização do lado.

## Testar localmente

O service worker exige HTTP — abrir o arquivo direto não serve pra testar
instalação:

```
python3 -m http.server 8098
```

Esse servidor não manda `Cache-Control`, então ele não reproduz o cenário de cache
do Pages. Pra testar atualização do app já instalado é preciso um servidor que
envie `Cache-Control: max-age=600`.

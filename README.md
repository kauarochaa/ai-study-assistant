# AI Study Assistant

Assistente de estudos que está sendo construído como projeto de portfólio. O objetivo final é permitir que a pessoa adicione materiais de estudo, faça perguntas sobre eles e receba respostas apoiadas nos próprios documentos.

## Etapa atual

O programa lê PDFs, arquivos de texto e Markdown guardados em `documents/`, extrai o texto e divide o conteúdo em trechos com referência ao arquivo e à página. Você pode digitar perguntas e ver até três trechos encontrados por busca de palavras (BM25), sem chamadas externas.

A busca ignora diferenças entre maiúsculas/minúsculas e acentos. Ela depende de palavras em comum: ainda não identifica sinônimos nem gera uma resposta com IA. Busca semântica e geração de respostas fazem parte das próximas etapas.

## Como executar

1. Ative o ambiente virtual do projeto.
2. Instale as dependências listadas em `requirements.txt` caso ainda não estejam instaladas.
3. Coloque arquivos `.pdf`, `.txt` ou `.md` dentro de `documents/`.
4. Na pasta do projeto, execute:

   ```powershell
   python main.py
   ```

O programa mostra quantos trechos foram preparados e uma pequena prévia do primeiro trecho de cada arquivo. Depois, digite uma pergunta, como `O que é SaaS?`, para ver os trechos e suas fontes. Digite `sair` para encerrar.

Para garantir o uso do ambiente virtual no Windows, também é possível executar diretamente:

```powershell
.\.venv\Scripts\python.exe main.py
```

## Próximas etapas do bootcamp

1. Criar embeddings e armazená-los em um banco vetorial.
2. Buscar os trechos mais relevantes para cada pergunta.
3. Conectar um provedor de IA para gerar respostas com base nesses trechos.
4. Adicionar histórico de perguntas, testes, logs, Docker e documentação da arquitetura.

## Segurança

Chaves de API devem ficar em um arquivo `.env` local, que não deve ser enviado ao GitHub. O arquivo `.gitignore` já exclui `.env` e ambientes virtuais.

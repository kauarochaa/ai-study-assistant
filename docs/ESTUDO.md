# O que construímos no bootcamp

## Dias 18–21: assistente de estudos

O projeto lê PDF, TXT e Markdown, divide o texto em trechos e mantém o nome do arquivo e a página de origem. A interface permite enviar materiais, fazer perguntas e consultar o histórico.

**Embeddings:** representações numéricas do significado de um texto. Transformamos os trechos e a pergunta em vetores para comparar sua proximidade.

**Banco vetorial:** o Qdrant guarda os vetores e suas referências. Podemos reutilizar o índice sem calcular tudo novamente.

**RAG:** buscar informações nos documentos antes de pedir uma resposta à IA. Nosso fluxo é: documento → trechos → vetores → busca → OpenAI → resposta com fontes.

**Histórico:** o SQLite salva perguntas, respostas e fontes. Fechar o navegador não apaga as consultas.

## Dias 22–24: organização e qualidade

O `.env` guarda a chave localmente; o `.env.example` mostra os campos sem revelar valores. Os testes conferem busca, fontes, erros, envio de arquivos e histórico. Os logs registram sucesso ou falha sem gravar a chave, as perguntas ou os textos dos documentos.

O Docker descreve o ambiente necessário para executar o aplicativo em outro computador. Volumes preservam os documentos, o índice e o histórico entre reinicializações.

## Dias 25–27: demonstração

1. Abrir a interface e mostrar os materiais.
2. Fazer uma pergunta e abrir as fontes.
3. Enviar um TXT sobre outro assunto e consultá-lo.
4. Reiniciar o aplicativo e mostrar que o histórico continua salvo.
5. Com saldo na API, ativar OpenAI e conferir uma resposta com as fontes.

## O que ainda depende de você

- Adicionar créditos à API para validar a geração real.
- Conferir as respostas: uma fonte válida não garante uma resposta correta.
- Executar Docker quando Docker Desktop estiver disponível.
- Preparar capturas da demonstração e escolher se publicará o projeto ou fará deploy.
- Atualizar currículo e perfil com o que você consegue explicar e demonstrar.

**Resumo para o caderno:** construí um assistente que busca nos meus materiais e usa os trechos como contexto para uma IA. Aprendi leitura de arquivos, divisão de texto, embeddings, banco vetorial, API, fontes, histórico, testes e configuração com Docker.

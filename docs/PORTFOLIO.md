# AI Study Assistant no portfólio

## Finalidade

Projeto educacional de um assistente pessoal para estudar documentos. Reúne leitura de PDF, TXT e Markdown, busca por palavras e significado, interface web e histórico. A integração opcional com OpenAI explica informações recuperadas e apresenta fontes para conferência.

O objetivo é demonstrar que consigo organizar uma aplicação Python, integrar ferramentas, tratar erros, testar comportamentos e explicar minhas decisões. A aplicação foi pensada para uma pessoa e para meus próprios materiais.

## Texto para currículo

**AI Study Assistant — projeto pessoal de estudos com Python e IA**

- Desenvolvi uma aplicação Streamlit para envio, consulta e exclusão de documentos PDF, TXT e Markdown, com histórico persistente em SQLite.
- Implementei busca semântica com embeddings locais e Qdrant, combinada com busca por palavras; preservei arquivo, página e trecho para conferir as fontes.
- Integrei a Responses API da OpenAI para respostas apoiadas nos documentos, com validação de referências, tratamento de erros e testes com chamadas simuladas.
- Preparei configuração Docker Compose e roteiro de deploy pessoal em VM Linux no Azure, com persistência de dados e acesso por túnel SSH.

**Tecnologias:** Python, Streamlit, pypdf, FastEmbed, Qdrant, SQLite, OpenAI API, Git e configuração Docker Compose.

Use a última linha de deploy exatamente como preparação enquanto o roteiro não for executado. Depois de validar a implantação, você poderá escrever: “Implantei a aplicação em VM Linux no Azure com Docker Compose, volumes persistentes e acesso pessoal por túnel SSH.” Inclua Azure como experiência prática de deploy somente nessa etapa.

## Apresentação de aproximadamente um minuto

“Criei o AI Study Assistant para estudar com meus próprios documentos. O usuário envia um PDF ou arquivo de texto, faz uma pergunta e consulta os trechos encontrados com suas fontes. O programa divide o material em partes menores, transforma o conteúdo em embeddings e usa um banco vetorial para encontrar informações relacionadas. Também combinei essa busca com palavras para melhorar a recuperação de termos específicos. A integração com OpenAI pode gerar uma explicação a partir desses trechos. Acrescentei histórico, exclusão de arquivos, tratamento de erros e testes. O projeto me ajudou a entender Python, RAG, persistência de dados e organização de aplicações. Preparei também a configuração Docker e um roteiro de implantação pessoal no Azure.”

Na demonstração, diga se está usando consulta aos trechos ou geração pela API. Se a chamada real não tiver sido validada, explique essa pendência em uma frase. Isso torna a apresentação fiel ao que você consegue demonstrar.

## Demonstração curta

1. Abra o assistente e mostre um material de exemplo sem dados pessoais.
2. Envie o documento e faça uma pergunta respondida nele.
3. Mostre o resultado e confira o trecho e a página.
4. Mostre o histórico persistente.
5. Exclua um documento de teste e confira a remoção das novas buscas.
6. Apresente o desenho da arquitetura e explique onde ficam documentos, vetores e histórico.
7. Mostre a saída dos testes e o README. Se já houver validação real, apresente um exemplo da OpenAI e as evidências de deploy.

Guarde uma captura da interface, o diagrama e um vídeo curto no repositório ou em um link apropriado. Não filme `.env`, chave de API, chave SSH, histórico pessoal ou documentos privados.

## Perguntas que devo saber responder

| Pergunta | Explicação simples |
|---|---|
| O que é RAG? | Buscar informações relevantes antes de pedir à IA que gere uma resposta. |
| Por que dividir o texto? | Para selecionar somente partes relacionadas à pergunta e manter suas referências. |
| O que são embeddings? | Representações numéricas usadas para comparar proximidade de significado. |
| Por que combinar duas buscas? | Palavras ajudam a localizar termos exatos; vetores ajudam com perguntas formuladas de outro modo. |
| Qual o papel do Qdrant? | Guardar e consultar os vetores e as informações dos trechos. |
| Qual o papel do SQLite? | Guardar as consultas e suas fontes para uso posterior. |
| O que a OpenAI recebe? | A pergunta, os trechos selecionados e as instruções para responder a partir desse contexto. |
| Uma citação garante uma resposta correta? | Não. O código valida as referências e o usuário deve conferir o conteúdo citado. |
| Por que usar Docker? | Descrever o ambiente para reproduzir a execução com dependências e volumes. |
| Como o uso pessoal é protegido no deploy? | A porta web fica em localhost e o acesso acontece por SSH com chave. |

## Limites que consigo explicar

- PDFs digitalizados precisam de OCR, ainda fora do escopo.
- A qualidade depende da clareza do material, da recuperação e do modelo; não há garantia de que toda resposta seja correta.
- O histórico guarda cópias dos trechos das consultas anteriores. Excluir um documento afeta novas buscas; para apagar essas cópias, exclua também o histórico correspondente quando esse recurso estiver disponível.
- A aplicação foi criada para uso pessoal. Não foi projetada como serviço público com várias pessoas e autenticação própria.
- Testes com API simulada verificam o comportamento do programa; não medem a qualidade de respostas reais.
- Configuração Docker e roteiro de deploy devem ser apresentados como preparados até haver execução e evidências. O teste real da OpenAI depende de créditos na conta da API.

## Registro honesto da entrega

Mantenha no README e em `docs/VALIDACAO.md` o que foi testado, a versão do código, os resultados e as pendências. Não informe percentual de precisão, economia de tempo, número de usuários, deploy concluído ou validação de IA real sem medir ou executar essas etapas.

Para o currículo, o mais valioso é conseguir abrir o projeto, demonstrar suas funções e explicar as decisões. Consulte [DEPLOY.md](DEPLOY.md) para executar a implantação pessoal quando estiver pronto para contratar e configurar a VM.

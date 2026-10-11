# Registro de validação — 09/10/2026

## Entrega local

| Requisito do bootcamp | Implementação e evidência |
|---|---|
| Upload de PDFs/textos | PDF, TXT e MD; validação de conteúdo e limite de20MB; testes isolados |
| Busca semântica/RAG | FastEmbed multilíngue e Qdrant local; combinação com BM25 e contexto vizinho |
| Perguntas e respostas | Consulta aos trechos funciona; Responses API integrada e testada por simulação |
| Fontes | Arquivo, página e posição preservados; referências geradas validadas |
| Histórico | SQLite persistente, compartilhado entre terminal e interface |
| Exclusão de documentos | Confirmação, validação de caminhos e limpeza dos índices derivados |
| Tratamento de erros | PDF inválido não interrompe demais materiais; falha semântica usa palavras; API exibe erro sanitizado |
| Logging | Eventos e tipo da falha, sem chave, perguntas ou texto dos documentos |
| README e arquitetura | README com fluxo Mermaid, instalação, limites, execução e aprendizado |
| Docker e Compose | Configuração pronta, volumes, healthcheck e reinicialização; build pendente |
| Testes | 19 testes aprovados no Windows/Python3.13; API simulada e documentos temporários |
| Dependências | `pip check`: nenhuma incompatibilidade encontrada |
| Demonstração e screenshot | Exemplo público em `examples/cloud.md`, imagem em `docs/demo.jpg` e roteiro no portfólio |
| Licença e Git | MIT, `.env.example`, `.gitignore` para dados pessoais e credenciais |
| Deploy | Roteiro privado Azure/SSH pronto; implantação ainda não executada |

Este registro descreve a árvore de trabalho local desta entrega; não representa um release remoto ou um deploy realizado. Comandos de verificação estão no README. O GitHub Actions está preparado, mas só haverá evidência de CI depois de executá-lo no repositório.

## Avaliação de recuperação com o modelo real

O script `scripts/evaluate_retrieval.py` usa exclusivamente `examples/cloud.md`, o modelo local real e um banco temporário. Não chama a OpenAI e não modifica documentos pessoais.

| Pergunta | Critério de aprovação | Resultado |
|---|---|---|
| O que é SaaS? | Recuperar trecho com software pronto | Passou |
| Qual serviço do Google permite salvar arquivos? | Recuperar Cloud Storage | Passou |
| Como pagar pelo que eu utilizo? | Recuperar pagamento conforme uso | Passou |
| O que é nuvem híbrida? | Recuperar combinação de ambientes | Passou |
| Máquinas virtuais em Azure e Google? | Recuperar Virtual Machines e Compute Engine | Passou |
| Capital da França? | Nenhum trecho recuperado | Passou |
| Receita de bolo de chocolate? | Nenhum trecho recuperado | Passou |
| Vencedor da Copa de2022? | Nenhum trecho recuperado | Passou |

**8/8 casos passaram.** Isso é uma pequena verificação de recuperação em um material de exemplo. Não é percentual de precisão geral e não mede qualidade da geração. Resultados semânticos abaixo de0,30 são filtrados; palavras coincidentes ainda podem produzir trechos fora do contexto. A IA continua instruída a recusar quando faltar suporte.

## Pendências externas para validação final

1. **OpenAI real:** adicionar créditos e executar `scripts/verify_openai.py`, depois conferir respostas na interface. Não foi realizada uma nova chamada real nesta entrega: a conta já estava sem saldo.
2. **Docker:** instalar Docker Desktop com WSL no Windows, ou executar o build na VM/CI. Esses ambientes ainda não estavam disponíveis para execução local.
3. **Deploy Azure:** criar a VM, iniciar o Compose, conferir persistência após reinício e executar o roteiro de teste. A criação tem custos e depende da conta do usuário.

O uso local sem geração pela API está disponível. Não afirmar que API real, Docker ou deploy foram validados antes de registrar seus resultados aqui.

## Atualização após o deploy

Registrar data, commit usado, ambiente, comandos executados, resultado de cada requisito e localização das evidências. Não incluir chaves, `.env`, IPs pessoais ou documentos privados em capturas públicas.

Observação técnica: o Qdrant1.19.1 em modo local emite um aviso de conexão temporária SQLite durante alguns testes. Os testes passaram; o adaptador de exclusão fecha as conexões persistentes antes de remover coleções no Windows. Reavaliar o adaptador ao atualizar essa dependência.

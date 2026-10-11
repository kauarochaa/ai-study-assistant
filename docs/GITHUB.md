# Colocar a entrega no GitHub

O código desta entrega está no computador. As alterações ainda precisam ser enviadas ao repositório para que outra instalação as receba e para que o GitHub Actions rode.

Na pasta que contém `app.py`, abra o terminal do VS Code:

```powershell
git status
git add .gitignore .env.example .dockerignore .streamlit .github src tests scripts examples docs app.py main.py requirements.txt README.md Dockerfile compose.yaml LICENSE
git diff --cached --stat
```

Confira a lista antes de continuar. `.env`, `data/`, ambientes virtuais, backups e documentos pessoais enviados não devem estar nela. As capturas em `docs/` devem mostrar somente materiais de exemplo. O PDF de Cloud já versionado é um exemplo público; não substitua seu conteúdo por material pessoal no mesmo arquivo.

Depois da revisão:

```powershell
git commit -m "Concluir assistente pessoal de estudos com RAG e documentação"
git push
```

Se houver alterações remotas ou um erro de autenticação, resolva-o antes de repetir. Não use `push --force`. Se o Git pedir nome e e-mail, configure sua identidade real no repositório. Nunca coloque chave da OpenAI na configuração do Git.

No GitHub, abra **Actions → Verificações** e aguarde os trabalhos de testes e Docker. O verde só vale quando o workflow realmente executar. Em caso de falha, confira o log correspondente e corrija antes de apresentar o build como validado.

Atualize `docs/VALIDACAO.md` com o resultado. No currículo, use o texto de `docs/PORTFOLIO.md`, mantendo as etapas ainda não executadas como preparação. O repositório pode mostrar seu trabalho enquanto a aplicação e os documentos permanecem privados.

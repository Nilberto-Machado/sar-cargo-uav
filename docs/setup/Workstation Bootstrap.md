# Workstation Bootstrap

Este procedimento prepara outro computador Windows para trabalhar com o mesmo repositório Git e o mesmo Vault do Obsidian. O script é conservador: ele não executa `pull`, não sobrescreve mudanças locais e não faz `commit`, `push`, `reset` ou `clean`.

## Arquivos mantidos no projeto

- `bootstrap_sar_workstation.ps1`: script principal de preparação da estação, salvo na raiz do repositório;
- `docs/setup/Workstation Bootstrap.md`: este procedimento operacional;
- `.obsidian/plugins/obsidian-git/data.json`: baseline compartilhada de configuração do Obsidian Git;
- `.obsidian/community-plugins.json`: lista de plugins comunitários habilitados para o Vault.

A pasta oficial de documentação do projeto é `docs/`. Não é necessário criar uma segunda pasta `doc/`.

## Configuração compartilhada do Obsidian Git

O arquivo `.obsidian/plugins/obsidian-git/data.json` foi revisado e incluído deliberadamente no projeto. Ele não contém token, senha ou caminho pessoal. A configuração compartilhada define:

- pull ao iniciar: ligado;
- auto commit: desligado;
- auto push: desligado;
- auto pull periódico: desligado;
- push no comando commit-and-sync: habilitado;
- pull antes do push: habilitado;
- método de sincronização: rebase.

Todos os demais arquivos `.obsidian/plugins/*/data.json` continuam ignorados, pois podem conter configurações locais ou credenciais. A autenticação Git também continua local e não é armazenada pelo bootstrap.

## O que o script faz

- verifica Git e Obsidian;
- opcionalmente oferece a instalação de cada ferramenta pelo `winget`, sempre pedindo confirmação;
- clona o repositório quando ele ainda não existe;
- quando o repositório já existe, valida o remoto `origin`, executa apenas `git fetch origin` e mostra o status;
- adiciona os dois cases de engenharia a `.git/info/exclude`, sem alterar `.gitignore`;
- confirma que a raiz do repositório é um Vault válido e contém `.obsidian`, `docs`, `.gitignore` e `.gitattributes`;
- verifica as regras de privacidade para workspaces e arquivos `data.json` de outros plugins, inclusive se algum deles foi rastreado por engano;
- verifica se o plugin `obsidian-git`, sua configuração compartilhada e sua referência em `community-plugins.json` estão no clone;
- avisa sobre arquivos untracked não ignorados;
- pode abrir o Vault no Obsidian;
- grava um log UTF-8 na pasta temporária do Windows, ou no caminho informado por `-LogPath`.

O arquivo `.obsidian/plugins/obsidian-git/data.json` é uma exceção revisada à regra geral de privacidade dos plugins. Ele é compartilhado pelo Git para aplicar a mesma baseline nas estações de trabalho. O arquivo atual não contém credenciais nem caminhos pessoais. Os arquivos `data.json` dos demais plugins continuam ignorados.

## Antes de executar

Obtenha uma cópia de `bootstrap_sar_workstation.ps1`, por exemplo por pendrive, compartilhamento local ou download do arquivo no GitHub. Não coloque token, senha ou credencial na URL. A autenticação deve ser tratada pelo Git Credential Manager ou por SSH.

Abra o PowerShell. Se a política do Windows bloquear scripts, libere apenas o processo atual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Essa configuração termina quando a janela do PowerShell é fechada.

## Exemplo: máquina Aurora

Para usar os valores recomendados, instalar ferramentas ausentes somente após confirmação e abrir o Vault ao final:

```powershell
.\bootstrap_sar_workstation.ps1 `
  -BaseDirectory "E:\GitHub" `
  -RepositoryUrl "https://github.com/Nilberto-Machado/sar-cargo-uav.git" `
  -InstallMissingTools `
  -OpenVault
```

O Vault resultante será:

```text
E:\GitHub\sar-cargo-uav
```

Se Git e Obsidian já estiverem instalados, omita `-InstallMissingTools`:

```powershell
.\bootstrap_sar_workstation.ps1 -OpenVault
```

Para usar outro disco ou pasta:

```powershell
.\bootstrap_sar_workstation.ps1 -BaseDirectory "D:\Projetos"
```

Para escolher onde salvar o log:

```powershell
.\bootstrap_sar_workstation.ps1 -LogPath "C:\Temp\sar-bootstrap.log"
```

## Se o repositório já existir

O diretório de destino precisa ser exatamente a raiz de um repositório Git cujo `origin` corresponda à URL solicitada. Se não corresponder, o script para sem mudar o remoto ou os arquivos.

Em um clone válido, o script executa `git fetch origin` e `git status`. Ele não integra as mudanças remotas automaticamente. Assim, arquivos modificados, staged ou untracked permanecem intactos para revisão manual.

## Configuração manual final no Obsidian

Depois do bootstrap, abra `E:\GitHub\sar-cargo-uav` como Vault:

1. sair do Restricted Mode, se necessário;
2. confirmar Community Plugins e ativar **Obsidian Git**;
3. confirmar que a baseline compartilhada foi carregada:
   - **Pull on startup**: `ON`;
   - intervalos de auto commit, auto push e auto pull: `0`/`OFF`;
   - push no commit-and-sync: habilitado;
   - pull antes do push: habilitado;
   - método de sincronização: `rebase`.

Credenciais não fazem parte dessa baseline e não devem ser adicionadas ao `data.json`. A autenticação continua local, pelo Git Credential Manager, SSH ou pelo armazenamento local do plugin.

## Reexecução segura

O script pode ser executado novamente. As entradas em `.git/info/exclude` são adicionadas de modo idempotente, e as verificações não apagam nem substituem conteúdo local. Se aparecer um aviso de arquivo untracked inesperado, revise o arquivo manualmente; o bootstrap não o remove.

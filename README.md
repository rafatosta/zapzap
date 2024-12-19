# [ZapZap](https://rtosta.com/zapzap-web/) - WhatsApp Desktop for Linux 


## Descrição
Este é um aplicativo Python que pode ser executado em três modos diferentes:
- **dev**: Modo de desenvolvimento
- **preview**: Modo de visualização/prévia
- **build**: Gera um executável para produção (zapzap.flatpak)

O projeto utiliza `zapzap.toml` para gerenciar dependências e um script Python (`run.py`) para executar os comandos.

## Requisitos

- Python 3.9 ou superior

## Instalação

1. **Clone o repositório**

```bash
git clone https://github.com/rafatosta/zapzap.git
cd zapzap
```

2. **Instale as dependências**

Certifique-se de que o Poetry está instalado. Caso não esteja, siga [este guia](https://python-poetry.org/docs/#installation).

Em seguida, instale as dependências do projeto:

```bash
poetry install
```

3. **Ative o ambiente virtual**

O Poetry cria um ambiente virtual para o projeto. Para ativá-lo, execute:

```bash
poetry shell
```

## Uso

### Executar em modo de desenvolvimento

Use o comando abaixo para iniciar o aplicativo em modo de desenvolvimento:

```bash
python run.py dev
```

### Executar em modo de prévia

Para visualizar a aplicação em modo de prévia:
(Constroi e executa diretamente em Flatpak)

```bash
python run.py preview
```

### Gerar o executável para produção

Para criar um executável da aplicação:

```bash
python run.py build
```

O executável será gerado na pasta `dist/` com o nome `zapzap.flatpak`.

## Estrutura do Projeto (Em construção)

```plaintext
zapzap/
├── zapzap.toml         # Arquivo de configuração do projeto
├── run.py                 # Script para gerenciar os modos de execução
├── zapzap/
│   └── main.py            # Arquivo principal da aplicação
├── dist/                  # (Geração) Pasta onde o executável será criado
└── README.md              # Documentação do projeto
```

## Contribuições

Contribuições são bem-vindas! Por favor, envie um pull request com as alterações ou melhorias que você deseja propor.

## Licença

Este projeto está licenciado sob a licença GPL. Consulte o arquivo LICENSE para mais informações.

## Contact
**Maintainer:** Rafael Tosta<br/>
**Email:** [rafa.ecomp@gmail.com](mailto:rafa.ecomp@gmail.com)


# ChatBot Lavanderia

Um chatbot inteligente para atendimento de clientes de lavanderia via WhatsApp, desenvolvido com Python, Flask e Twilio.

## Funcionalidades

- Menu interativo com opções de serviços
- Informações sobre horários e preços
- Solicitação de orçamentos
- Informações sobre serviços específicos
- Navegação intuitiva
- Processamento de linguagem natural básico

## Requisitos

- Python 3.8+
- Conta Twilio com WhatsApp habilitado
- Ambiente virtual Python (recomendado)

## Configuração

1. Clone o repositório:
```bash
git clone git@github.com:LuksbellN/ChatBot-Lavanderia.git
cd ChatBot-Lavanderia
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```
Edite o arquivo `.env` com suas credenciais do Twilio e outras configurações.

## Desenvolvimento

Para executar em modo de desenvolvimento:
```bash
flask run
```

## Produção

Para executar em produção:
```bash
gunicorn script:app
```

## Configuração do Twilio

1. Crie uma conta no [Twilio](https://www.twilio.com)
2. Habilite o WhatsApp Sandbox
3. Configure o webhook para apontar para sua URL: `https://seu-dominio.com/webhook`
4. Copie suas credenciais (Account SID e Auth Token) para o arquivo `.env`

## Estrutura do Projeto

```
ChatBot-Lavanderia/
├── script.py              # Código principal do chatbot
├── requirements.txt       # Dependências do projeto
├── .env.example          # Exemplo de configuração
├── .gitignore           # Arquivos ignorados pelo git
└── README.md            # Este arquivo
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes. 
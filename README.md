# **Streaming-insights**

**Descrição do Projeto**: Este projeto consiste em um sistema de coleta e armazenamento de tweets relacionados a serviços de streaming, como Disney Plus, Netflix, HBOGO, Globoplay, entre outros. Os tweets são coletados em tempo real, passam por um processo de limpeza e estruturação e são armazenados em um banco de dados PostgreSQL.

## Requisitos

- Python 3.10

## Configuração do Ambiente

1. Clone este repositório:
    
    ```bash
    git clone https://github.com/Cuadros99/Streaming-insights.git
    ```
    
2. Navegue até o diretório do projeto:
    
    ```bash
    cd Streaming-insights
    ```
    
3. Crie um ambiente virtual
    
    ```jsx
    python3 -m venv venv
    ```
    
4. Ative o ambiente virtual criado
    
    ```jsx
    source venv/bin/activate
    ```
    
5. Instale as dependências necessárias no ambiente virtual
    
    ```bash
    pip install -r requirements.txt
    ```
    
6. Configure as variáveis de ambiente em um arquivo **`.env`** na raiz do projeto seguindo a estrutura descrita no .env.example
    
    ⚠️ Adicione uma conta do twitter para cada plataforma de streaming listada no arquivo `/etls/streaming_platforms.json`
    
    
7. Execute os scripts separadamente para coletar e armazenar os tweets:
    
    ```bash
    python twitter-crawler.py
    
    python data-management.py
    ```
    
    **Obs:** Lembre-se de executar os comandos acima com o ambiente virtual ativado
    
8. O projeto pode ser utilizado juntamente com o Projeto Airflow que pode ser encontrado nesse link: https://github.com/Cuadros99/airflow
    
    **Obs:** Atente-se para deixar ambos os repositórios no mesmo diretório
    

## **Uso**

Este sistema coleta automaticamente tweets em tempo real relacionados aos serviços de streaming especificados no arquivo **`streaming_platforms.json`**. Os tweets são coletados, limpos e armazenados no banco de dados PostgreSQL.

## Banco de Dados

O projeto utiliza um banco de dados PostgreSQL com o seguinte esquema (schema) e tabela:

- **Esquema (Schema):** streamings
- **Tabela:** tweets

Você pode criar a tabela **`tweets`** no banco de dados PostgreSQL com o seguinte comando SQL:

```sql
CREATE TABLE streamings.tweets (
    tweet_id SERIAL PRIMARY KEY,
    text TEXT,
    author VARCHAR(25),
    created_at TIMESTAMP,
    platform VARCHAR(25)
);
```

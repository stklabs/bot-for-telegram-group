FROM python:3.11-slim
ENV POETRY_VIRTUALENVS_CREATE=false

# Etapa 2: Instala Poetry
RUN pip install poetry

# Etapa 3: Define diretório de trabalho
WORKDIR /app

# Etapa 4: Copia arquivos do projeto
COPY . .

# Etapa 5: Instala dependências do projeto
RUN poetry config installer.max-workers 10
RUN poetry install --no-root --no-interaction --no-ansi

# Etapa 6: Comando para rodar o bot
CMD python main.py

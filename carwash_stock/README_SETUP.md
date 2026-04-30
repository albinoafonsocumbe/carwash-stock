# Configuração do Sistema de Gestão de Stock — Carwash

## Pré-requisitos

- Python 3.10+
- PostgreSQL 15+

---

## 1. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## 2. Criar a base de dados PostgreSQL

Acede ao cliente `psql` como superutilizador e executa:

```bash
psql -U postgres -f create_db.sql
```

Ou manualmente:

```sql
CREATE DATABASE carwash_stock_db;
```

---

## 3. Configurar o ficheiro `.env`

Copia o ficheiro de exemplo e preenche as credenciais:

```bash
cp .env.example .env
```

Edita o `.env` com os teus valores:

```env
SECRET_KEY=coloca-aqui-uma-chave-secreta-longa
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=carwash_stock_db
DB_USER=postgres
DB_PASSWORD=a-tua-password
DB_HOST=localhost
DB_PORT=5432
```

---

## 4. Executar as migrações

```bash
python manage.py migrate
```

---

## 5. Criar superutilizador

```bash
python manage.py createsuperuser
```

Segue as instruções no terminal para definir username, email e password.

---

## 6. Iniciar o servidor de desenvolvimento

```bash
python manage.py runserver
```

A aplicação fica disponível em: [http://127.0.0.1:8000](http://127.0.0.1:8000)

O painel de administração está em: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

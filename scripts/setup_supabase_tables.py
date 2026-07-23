"""
One-time setup script: creates the Postgres tables this app needs in Supabase.

Supabase's Python client doesn't support raw DDL execution directly, so this
script prints the SQL for you to run in the Supabase SQL Editor
(Dashboard -> SQL Editor -> New Query -> paste -> Run).

This is the standard way to set up schema on Supabase — there's no official
"create table" call in the client library by design (DDL is meant to go
through migrations/SQL editor, not app code).
"""

SQL = """
-- documents: one row per uploaded file
create table if not exists documents (
    id uuid primary key default gen_random_uuid(),
    filename text not null,
    storage_path text not null,
    chunk_count integer not null default 0,
    created_at timestamptz not null default now()
);

-- chat_sessions: groups messages into conversations (optional, for multi-turn history)
create table if not exists chat_sessions (
    id uuid primary key default gen_random_uuid(),
    created_at timestamptz not null default now()
);

-- chat_messages: individual messages within a session
create table if not exists chat_messages (
    id uuid primary key default gen_random_uuid(),
    session_id uuid references chat_sessions(id) on delete cascade,
    role text not null check (role in ('user', 'assistant')),
    content text not null,
    sources jsonb,
    created_at timestamptz not null default now()
);

-- eval_runs: logs each evaluation run's config + resulting metrics
create table if not exists eval_runs (
    id uuid primary key default gen_random_uuid(),
    run_date timestamptz not null default now(),
    config jsonb,
    metrics jsonb,
    notes text
);

-- helpful indexes
create index if not exists idx_chat_messages_session_id on chat_messages(session_id);
create index if not exists idx_documents_created_at on documents(created_at desc);
"""


def main():
    print("=" * 70)
    print("Copy the SQL below into your Supabase project:")
    print("Dashboard -> SQL Editor -> New Query -> paste -> Run")
    print("=" * 70)
    print(SQL)


if __name__ == "__main__":
    main()

CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price INTEGER NOT NULL CHECK (price > 0),
    stock INTEGER NOT NULL CHECK (stock >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS order_agent_runs (
    run_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL DEFAULT 'order',
    actor_id TEXT NOT NULL,
    question TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN (
            'running', 'waiting_approval', 'change_executed',
            'completed', 'rejected', 'blocked', 'failed', 'stopped'
        )
    ),
    termination_reason TEXT,
    state JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL UNIQUE REFERENCES order_agent_runs(run_id),
    actor_id TEXT NOT NULL,
    product_id TEXT NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price INTEGER NOT NULL CHECK (unit_price > 0),
    total INTEGER NOT NULL CHECK (total = unit_price * quantity),
    status TEXT NOT NULL DEFAULT 'created' CHECK (status IN ('created', 'cancelled')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS order_agent_runs_actor_created_idx
    ON order_agent_runs (actor_id, created_at DESC);

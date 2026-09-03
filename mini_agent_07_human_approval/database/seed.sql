INSERT INTO products (product_id, name, price, stock) VALUES
    ('P-KEYBOARD', '무선 키보드', 45000, 7),
    ('P-MOUSE', '무선 마우스', 28000, 0)
ON CONFLICT (product_id) DO NOTHING;

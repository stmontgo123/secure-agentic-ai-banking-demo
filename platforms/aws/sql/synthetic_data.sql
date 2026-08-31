-- All records are fictional and exist only for the demonstration.

INSERT INTO customers
VALUES (1001, 'Jane Smith', 'Consumer', 'STANDARD')
ON CONFLICT (customer_id) DO NOTHING;

INSERT INTO accounts
VALUES (5001, 1001, 'ACTIVE', 4250.00, '4421')
ON CONFLICT (account_id) DO NOTHING;

INSERT INTO transactions
VALUES (
    847291,
    5001,
    'Best Buy',
    1250.00,
    CURRENT_TIMESTAMP,
    'Orlando, FL',
    'DECLINED',
    '65',
    'Transaction declined following an unusual spending pattern.'
)
ON CONFLICT (transaction_id) DO NOTHING;

INSERT INTO fraud_events
VALUES (
    90001,
    847291,
    'USR-09',
    'High-value purchase inconsistent with recent customer activity.',
    82,
    'Internal fraud model score exceeded review threshold.'
)
ON CONFLICT (fraud_event_id) DO NOTHING;

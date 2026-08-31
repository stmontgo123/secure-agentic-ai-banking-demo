-- Synthetic policy text used to demonstrate role-filtered RAG.

INSERT INTO policy_chunks (
    policy_id, title, chunk_text, classification, allowed_role
) VALUES (
    'CV-04',
    'Card Verification Procedure',
    'When a transaction is declined because of unusual spending behavior, the customer service representative must verify that the customer attempted the transaction before permitting a retry. The representative may disclose that the transaction was stopped by a fraud protection control but must not disclose internal fraud scores or detection thresholds.',
    'INTERNAL',
    'CUSTOMER_SERVICE'
);

INSERT INTO policy_chunks (
    policy_id, title, chunk_text, classification, allowed_role
) VALUES (
    'CA-12',
    'Card Account Status Procedure',
    'Before advising a customer about a declined card transaction, the representative should verify that the account is active and determine whether sufficient available funds exist.',
    'INTERNAL',
    'CUSTOMER_SERVICE'
);

INSERT INTO policy_chunks (
    policy_id, title, chunk_text, classification, allowed_role
) VALUES (
    'FR-09',
    'Fraud Investigation Procedures',
    'Fraud analysts may review internal fraud scores, rule thresholds, model indicators and investigative notes associated with a transaction.',
    'RESTRICTED',
    'FRAUD_ANALYST'
);

COMMIT;

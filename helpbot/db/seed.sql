INSERT OR IGNORE INTO orders VALUES ('PT-1001', 'in_transit', 'FedEx', 'FX123456789', '2026-06-27', NULL, NULL);
INSERT OR IGNORE INTO orders VALUES ('PT-1002', 'delivered', 'UPS', 'UP987654321', NULL, NULL, '2026-06-22');
INSERT OR IGNORE INTO orders VALUES ('PT-1003', 'processing', NULL, NULL, NULL, '2026-06-25', NULL);
INSERT OR IGNORE INTO orders VALUES ('PT-1004', 'shipped', 'DHL', 'DH456789123', '2026-06-28', NULL, NULL);
INSERT OR IGNORE INTO orders VALUES ('PT-1005', 'delivered', 'Royal Mail', 'RM111222333', NULL, NULL, '2026-06-20');

INSERT OR IGNORE INTO return_eligibility VALUES ('PT-1001', 1, 'Within 30-day return window.', '2026-06-10');
INSERT OR IGNORE INTO return_eligibility VALUES ('PT-1002', 0, 'Return window has expired — order was delivered more than 30 days ago.', '2026-05-01');
INSERT OR IGNORE INTO return_eligibility VALUES ('PT-1003', 0, 'Order has not been delivered yet — cannot initiate a return.', NULL);
INSERT OR IGNORE INTO return_eligibility VALUES ('PT-1004', 0, 'Return already processed and refund issued for this order.', NULL);
INSERT OR IGNORE INTO return_eligibility VALUES ('PT-1005', 1, 'Within 30-day return window.', '2026-06-20');

INSERT OR IGNORE INTO refunds VALUES ('PT-1002', 'paid', 24.99, 'original payment method', '2026-06-15', NULL, NULL);
INSERT OR IGNORE INTO refunds VALUES ('PT-1004', 'approved', 18.50, 'original payment method', NULL, '2026-06-26', NULL);
INSERT OR IGNORE INTO refunds VALUES ('PT-1005', 'received', 12.00, 'original payment method', NULL, NULL, '2026-06-23');

INSERT OR IGNORE INTO books VALUES ('the midnight library', 'in_stock', 14, 'paperback,hardcover,ebook', NULL, NULL);
INSERT OR IGNORE INTO books VALUES ('atomic habits', 'in_stock', 3, 'paperback,ebook', NULL, NULL);
INSERT OR IGNORE INTO books VALUES ('project hail mary', 'out_of_stock', 0, 'paperback,hardcover', '2026-07-05', 'high');
INSERT OR IGNORE INTO books VALUES ('the alchemist', 'in_stock', 22, 'paperback,ebook', NULL, NULL);
INSERT OR IGNORE INTO books VALUES ('dune', 'out_of_stock', 0, 'paperback,hardcover,ebook', '2026-07-12', 'medium');
INSERT OR IGNORE INTO books VALUES ('educated', 'in_stock', 7, 'paperback', NULL, NULL);
INSERT OR IGNORE INTO books VALUES ('sapiens', 'out_of_stock', 0, 'paperback,hardcover', NULL, 'unknown');

INSERT OR IGNORE INTO accounts VALUES ('john.doe@example.com', 'John Doe', 'active', NULL, NULL);
INSERT OR IGNORE INTO accounts VALUES ('jane.smith@example.com', 'Jane Smith', 'locked_self_service', NULL, 'https://pageturner.books/unlock');
INSERT OR IGNORE INTO accounts VALUES ('bob.jones@example.com', 'Bob Jones', 'locked_needs_agent', 'Multiple failed payment attempts — manual review required.', NULL);
INSERT OR IGNORE INTO accounts VALUES ('alice.brown@example.com', 'Alice Brown', 'suspended', 'Account suspended due to policy violation.', NULL);

INSERT OR IGNORE INTO promo_codes VALUES ('SUMMER20', 1, '20% off', '2026-08-31', 'all orders', NULL, NULL);
INSERT OR IGNORE INTO promo_codes VALUES ('BOOKS10', 1, '10% off', '2026-07-15', 'books only', NULL, NULL);
INSERT OR IGNORE INTO promo_codes VALUES ('WELCOME5', 0, NULL, NULL, NULL, 'Code has expired.', '2026-01-01');
INSERT OR IGNORE INTO promo_codes VALUES ('FLASH50', 0, NULL, NULL, NULL, 'Code has expired.', '2026-06-01');

INSERT OR IGNORE INTO loyalty VALUES ('john.doe@example.com', 1250, 'Silver', 750);
INSERT OR IGNORE INTO loyalty VALUES ('jane.smith@example.com', 3400, 'Gold', 1600);
INSERT OR IGNORE INTO loyalty VALUES ('bob.jones@example.com', 0, 'Bronze', 500);
INSERT OR IGNORE INTO loyalty VALUES ('alice.brown@example.com', 5200, 'Platinum', NULL);

INSERT OR IGNORE INTO digital_purchases VALUES ('john.doe@example.com', 'atomic habits', 1, 'active', 3, '2027-06-24', NULL);
INSERT OR IGNORE INTO digital_purchases VALUES ('jane.smith@example.com', 'sapiens', 1, 'expired', 0, NULL, '2026-01-01');
INSERT OR IGNORE INTO digital_purchases VALUES ('bob.jones@example.com', 'the alchemist', 1, 'exhausted', 0, NULL, NULL);
INSERT OR IGNORE INTO digital_purchases VALUES ('alice.brown@example.com', 'dune', 0, NULL, NULL, NULL, NULL);

INSERT OR IGNORE INTO gift_orders VALUES ('GFT-1001', 'delivered', 'Sarah Connor', 'sarah.c@example.com', 'The Midnight Library,Atomic Habits', '2026-06-21', NULL, NULL);
INSERT OR IGNORE INTO gift_orders VALUES ('GFT-1002', 'in_transit', 'Mike Torres', 'mike.t@example.com', 'Dune', NULL, '2026-06-27', NULL);
INSERT OR IGNORE INTO gift_orders VALUES ('GFT-1003', 'processing', 'Emma Wilson', 'emma.w@example.com', 'Sapiens,Educated', NULL, NULL, '2026-06-25');

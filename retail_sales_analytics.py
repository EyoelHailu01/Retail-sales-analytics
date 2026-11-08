"""Retail Sales Analytics: standalone Python + SQL project for Thonny.
All customer and transaction data is fictional. No extra packages needed.
Money is stored as integer cents. Canceled orders are excluded; refunds
are assigned to the original order month. Taxes/shipping are not modeled.
"""
import sqlite3
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE customers (
 customer_id INTEGER PRIMARY KEY, customer_name TEXT NOT NULL,
 region TEXT NOT NULL
);
CREATE TABLE products (
 product_id INTEGER PRIMARY KEY, product_name TEXT NOT NULL,
 category TEXT NOT NULL
);
CREATE TABLE orders (
 order_id INTEGER PRIMARY KEY,
 customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
 order_date TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('completed','refunded','canceled'))
);
CREATE TABLE order_items (
 order_id INTEGER NOT NULL REFERENCES orders(order_id),
 product_id INTEGER NOT NULL REFERENCES products(product_id),
 quantity INTEGER NOT NULL CHECK(quantity > 0),
 unit_price_cents INTEGER NOT NULL CHECK(unit_price_cents >= 0),
 PRIMARY KEY(order_id, product_id)
);
CREATE VIEW sales_lines AS
 SELECT o.order_id,o.customer_id,o.order_date,o.status,
 i.product_id,i.quantity,i.quantity*i.unit_price_cents AS amount_cents,
 CASE WHEN o.status='refunded' THEN -i.quantity*i.unit_price_cents
 ELSE i.quantity*i.unit_price_cents END AS net_cents
 FROM orders o JOIN order_items i ON o.order_id=i.order_id
 WHERE o.status <> 'canceled';
"""

SAMPLE_DATA = """
INSERT INTO customers VALUES
(1,'Customer A','Midwest'),(2,'Customer B','South'),
(3,'Customer C','Midwest'),(4,'Customer D','West'),(5,'Customer E','East');
INSERT INTO products VALUES
(1,'Keyboard','Accessories'),(2,'Monitor','Displays'),
(3,'Mouse','Accessories'),(4,'Webcam','Accessories'),(5,'Dock','Accessories');
INSERT INTO orders VALUES
(101,1,'2026-01-05','completed'),(102,2,'2026-01-12','completed'),
(103,1,'2026-02-03','completed'),(104,3,'2026-02-11','refunded'),
(105,4,'2026-02-19','canceled'),(106,2,'2026-03-04','completed'),
(107,3,'2026-03-08','completed'),(108,4,'2026-03-14','completed');
INSERT INTO order_items VALUES
(101,1,2,5000),(101,3,1,2500),(102,2,1,20000),
(103,4,2,7000),(104,2,1,20000),(105,1,3,5000),
(106,1,1,5000),(106,3,2,2500),(107,4,1,7000),(108,2,2,20000);
"""

QUERIES = """
-- 1. Monthly sales and refunds in dollars
SELECT substr(order_date,1,7) AS month,
 SUM(CASE WHEN status='completed' THEN amount_cents ELSE 0 END)/100.0 AS gross_sales,
 SUM(CASE WHEN status='refunded' THEN amount_cents ELSE 0 END)/100.0 AS refunds,
 SUM(net_cents)/100.0 AS net_revenue
FROM sales_lines GROUP BY month ORDER BY month;

-- 2. Product revenue, preserving unsold products
SELECT p.product_name, COALESCE(SUM(s.net_cents),0)/100.0 AS net_revenue
FROM products p LEFT JOIN sales_lines s ON p.product_id=s.product_id
GROUP BY p.product_id,p.product_name ORDER BY net_revenue DESC,p.product_id;

-- 3. Rank customers by net spending
WITH spending AS (
 SELECT c.customer_id,c.customer_name,COALESCE(SUM(s.net_cents),0) AS cents
 FROM customers c LEFT JOIN sales_lines s ON c.customer_id=s.customer_id
 GROUP BY c.customer_id,c.customer_name
)
SELECT customer_name,cents/100.0 AS net_spending,
 DENSE_RANK() OVER(ORDER BY cents DESC) AS spending_rank
FROM spending ORDER BY spending_rank,customer_id;

-- 4. Customers without a completed purchase
SELECT c.customer_id,c.customer_name FROM customers c
WHERE NOT EXISTS (
 SELECT 1 FROM orders o WHERE o.customer_id=c.customer_id AND o.status='completed'
) ORDER BY c.customer_id;

-- 5. Average order value: aggregate items to orders before averaging
WITH order_totals AS (
 SELECT customer_id,order_id,SUM(amount_cents) AS cents FROM sales_lines
 WHERE status='completed' GROUP BY customer_id,order_id
)
SELECT c.region,COUNT(*) AS completed_orders,ROUND(AVG(t.cents)/100.0,2) AS average_order_value
FROM order_totals t JOIN customers c ON t.customer_id=c.customer_id
GROUP BY c.region ORDER BY c.region;

-- 6. Running net revenue
WITH monthly AS (
 SELECT substr(order_date,1,7) AS month,SUM(net_cents) AS cents
 FROM sales_lines GROUP BY month
)
SELECT month,cents/100.0 AS net_revenue,
 SUM(cents) OVER(ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)/100.0 AS cumulative_revenue
FROM monthly ORDER BY month;
"""

def main():
    report = ['# Retail Sales Analytics', '', 'All data is fictional.', '']
    print('RETAIL SALES ANALYTICS — FICTIONAL SAMPLE DATA')
    # An in-memory database keeps your existing files untouched.
    connection = sqlite3.connect(':memory:')
    try:
        connection.executescript(SCHEMA)
        connection.executescript(SAMPLE_DATA)
        for number, query in enumerate(QUERIES.split(';'), start=1):
            if not query.strip():
                continue
            cursor = connection.execute(query)
            headings = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            title = query.strip().splitlines()[0].removeprefix('-- ').strip()
            print('\n' + title)
            print(' | '.join(headings))
            report.extend(['## ' + title, '',
                           '| ' + ' | '.join(headings) + ' |',
                           '| ' + ' | '.join(['---'] * len(headings)) + ' |'])
            for row in rows:
                values = [str(value) for value in row]
                print(' | '.join(values))
                report.append('| ' + ' | '.join(values) + ' |')
            report.append('')
    finally:
        connection.close()
    output = Path(__file__).resolve().parent / 'retail_sales_results.md'
    output.write_text('\n'.join(report), encoding='utf-8')
    print('\nReport saved:', output)


if __name__ == '__main__':
    try:
        main()
    except (sqlite3.Error, OSError) as error:
        print('Error:', error)

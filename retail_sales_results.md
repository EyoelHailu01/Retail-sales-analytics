# Retail Sales Analytics

All data is fictional.

## 1. Monthly sales and refunds in dollars

| month | gross_sales | refunds | net_revenue |
| --- | --- | --- | --- |
| 2026-01 | 325.0 | 0.0 | 325.0 |
| 2026-02 | 140.0 | 200.0 | -60.0 |
| 2026-03 | 570.0 | 0.0 | 570.0 |

## 2. Product revenue, preserving unsold products

| product_name | net_revenue |
| --- | --- |
| Monitor | 400.0 |
| Webcam | 210.0 |
| Keyboard | 150.0 |
| Mouse | 75.0 |
| Dock | 0.0 |

## 3. Rank customers by net spending

| customer_name | net_spending | spending_rank |
| --- | --- | --- |
| Customer D | 400.0 | 1 |
| Customer B | 300.0 | 2 |
| Customer A | 265.0 | 3 |
| Customer E | 0.0 | 4 |
| Customer C | -130.0 | 5 |

## 4. Customers without a completed purchase

| customer_id | customer_name |
| --- | --- |
| 5 | Customer E |

## 5. Average order value: aggregate items to orders before averaging

| region | completed_orders | average_order_value |
| --- | --- | --- |
| Midwest | 3 | 111.67 |
| South | 2 | 150.0 |
| West | 1 | 400.0 |

## 6. Running net revenue

| month | net_revenue | cumulative_revenue |
| --- | --- | --- |
| 2026-01 | 325.0 | 325.0 |
| 2026-02 | -60.0 | 265.0 |
| 2026-03 | 570.0 | 835.0 |

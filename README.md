# Serverless WordPress Order Fulfillment Engine

An event-driven, decoupled backend pipeline built to offload order processing and instant email notifications from WordPress to AWS serverless infrastructure.

---

## 🏗️ Architecture Overview
[ Fluent Forms / WordPress ]
│
▼ (HTTP POST via Custom PHP Webhook Hook)
[ AWS API Gateway ]
│
▼ (Triggers Integration Event)
[ AWS Lambda ]
/

/

▼              ▼
[ DynamoDB ]   [ AWS SES ]
(Order Store)  (Email Alert)   **Order Capture:** User submits order data on a WordPress landing page using Fluent Forms.
2. **Payload Dispatch:** A lightweight WordPress PHP action hook intercepts the submission and forwards structured JSON to an AWS API Gateway endpoint.
3. **Serverless Execution:** API Gateway triggers an AWS Lambda function running Python 3.12.
4. **Data Persistence & Alerting:** Lambda concurrently writes order records to Amazon DynamoDB and triggers an instant administrative email alert via Amazon SES.

---

## 💡 Key Architectural Benefits

* **Zero WordPress Overhead:** Offloads heavy database writes and third-party SMTP operations away from the web server, ensuring fast page load speeds during high-volume promotional traffic.
* **Fault Tolerant & Scalable:** Scales automatically from zero to thousands of order requests per minute without server infrastructure management.
* **Sub-Second Latency:** Complete event pipeline lifecycle (request to storage and email delivery) completes in $< 1.0\text{ second}$.
* **Idempotent Dispatch:** Prevents race conditions and duplicate triggers via single-hook registration and managed HTTP timeout handling.

---

## 🛠️ Tech Stack & Prerequisites

* **Frontend/CMS:** WordPress, Fluent Forms, Custom PHP Code Snippets
* **API Ingestion:** AWS API Gateway (REST API)
* **Compute:** AWS Lambda (Python 3.12)
* **Database:** AWS DynamoDB (NoSQL On-Demand Table)
* **Email Service:** AWS Simple Email Service (SES)

---

## 🚀 Environment Variables & Configuration

Configure the following environment variables inside your AWS Lambda function settings:

| Variable Name | Description | Example Value |
| :--- | :--- | :--- |
| `TABLE_NAME` | DynamoDB primary order table | `ordersTable` |
| `ADMIN_EMAIL` | Verified AWS SES sender and recipient email | `admin@yourdomain.com` |
| `AWS_REGION` | Target AWS deployment region | `us-east-1` |

---

## 📩 Sample Event Payload

The WordPress PHP hook transmits the following formatted JSON payload to AWS API Gateway:

```json
{
  "customer_name": "John Doe",
  "phone_number": "+2348012345678",
  "delivery_address": "123 Commercial Avenue, Victoria Island, Lagos",
  "package_selected": "Marsriva Mini Router UPS - 20,000mAh Dual Pack",
  "entry_id": 104,
  "submitted_at": "2026-10-06 11:53:32"
}
```
🔧 Local Development & Deployment
Deploy DynamoDB Table: Create a table named ordersTable with a primary partition key named order_id (String).

Configure Amazon SES: Verify domain or administrator email address under AWS SES Verified Identities.

Deploy Lambda Function: Copy lambda_function.py into AWS Lambda, attach the required IAM execution policies (AmazonDynamoDBFullAccess, AmazonSESFullAccess), and set the function timeout to 10 seconds.

Set Up API Gateway: Create an HTTP API or REST API trigger pointing to Lambda function and copy the invoking stage URL.

Activate WordPress Hook: Deploy wordpress_webhook_snippet.php into your site using Code Snippets or functions.php, updating $api_url with your API Gateway endpoint.

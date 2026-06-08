# serverless-contact-form-aws

> A fully serverless contact form built end-to-end on AWS free-tier services. A static HTML page hosted on S3 collects user messages and sends them via API Gateway to a Lambda function (Python), which stores each submission in DynamoDB — zero servers, zero maintenance, zero cost for personal use.

![AWS](https://img.shields.io/badge/AWS-Serverless-FF9900?logo=amazonaws&logoColor=white)
![S3](https://img.shields.io/badge/S3-Static%20Hosting-3F8624?logo=amazons3&logoColor=white)
![Lambda](https://img.shields.io/badge/Lambda-Python%203.12-E97B00?logo=awslambda&logoColor=white)
![DynamoDB](https://img.shields.io/badge/DynamoDB-NoSQL-2E73B8?logo=amazondynamodb&logoColor=white)

---

## Architecture

```
Browser  ──HTTPS POST──►  API Gateway (/contact)  ──Trigger──►  Lambda  ──PutItem──►  DynamoDB
   ▲                              │                                  │
   │                    (CORS enabled)                        (uuid + timestamp)
   └──────────────── 200 OK "Message sent successfully!" ◄──────────┘
```

| Service | Role |
|---|---|
| Amazon S3 | Hosts the static `index.html` contact form |
| Amazon API Gateway | Exposes `POST /contact` with CORS enabled |
| AWS Lambda | Python function that parses and saves form data |
| Amazon DynamoDB | Stores every submission with a UUID + timestamp |

---

## How It Works

1. **S3** serves `index.html` — a static contact form with Name, Email, and Message fields.
2. On submit, JavaScript sends a `POST` request to the **API Gateway** endpoint.
3. **API Gateway** triggers the **Lambda** Python function with the request body.
4. **Lambda** parses the JSON, generates a UUID, and writes the item to **DynamoDB**.
5. Lambda returns `200 OK` with `{"message": "Form submitted successfully!"}`.
6. The frontend displays a green success banner to the user.

---

## DynamoDB Schema

**Table name:** `ContactFormSubmissions`  
**Partition key:** `submissionId` (String)

| Attribute | Type | Example |
|---|---|---|
| `submissionId` | String | `9ef6dbd9-59f4-429f-b33...` |
| `name` | String | `Rukayat` |
| `email` | String | `test@test.com` |
| `message` | String | `Hello from Lambda test!` |
| `timestamp` | String | `2026-06-08T10:43:59.243480` |

---

## Setup Guide

---

### PHASE 1 — Host a Static Website on S3

#### Step 1.1 — Create an S3 Bucket
1. AWS Console → **S3** → **Create bucket**
2. Bucket name: `nextwork-contact-form-yourname` (must be unique globally)
3. Region: `us-east-1`
4. **Uncheck** "Block all public access" → confirm
5. Click **Create bucket**

#### Step 1.2 — Enable Static Website Hosting
1. Click your bucket → **Properties** tab
2. Scroll to **Static website hosting** → **Edit**
3. Enable it → Index document: `index.html`
4. Click **Save changes**

#### Step 1.3 — Create Your Website File
Create a file called `index.html` on your computer using the file in this repo (`index.html`).

#### Step 1.4 — Upload and Make Public
1. In your S3 bucket → **Objects** tab → **Upload** → upload `index.html`
2. Go to **Permissions** tab → **Bucket policy** → **Edit**
3. Paste this policy 

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::mystatic-website/*"
        }
    ]
}
```

4. Click **Save changes**
5. Go back to **Properties** → Static website hosting → copy the **website endpoint URL**
6. Open it in your browser — you should see your contact form! ✅

---

### PHASE 2 — Create the DynamoDB Database

#### Step 2.1 — Create a DynamoDB Table
1. AWS Console → **DynamoDB** → **Create table**
2. Table name: `ContactFormSubmissions`
3. Partition key: `submissionId` (String)
4. Leave everything else as default
5. Click **Create table**

> DynamoDB is a NoSQL database — no columns, no schemas. Each item can have different fields. Perfect for storing form submissions.

---

### PHASE 3 — Create the Lambda Function

#### Step 3.1 — Create the Function
1. AWS Console → **Lambda** → **Create function**
2. Select **Author from scratch**
3. Function name: `ContactFormProcessor`
4. Runtime: **Python 3.12**
5. Click **Create function**

#### Step 3.2 — Write the Lambda Code
Replace the default code with the contents of `lambda_function.py` from this repo, then click **Deploy**.

#### Step 3.3 — Give Lambda Permission to Write to DynamoDB
1. In your Lambda function → **Configuration** tab → **Permissions**
2. Click the IAM role name (opens IAM)
3. **Add permissions** → **Attach policies**
4. Search `AmazonDynamoDBFullAccess` → attach it
5. Go back to Lambda

#### Step 3.4 — Test Your Lambda
1. Click **Test** → **Create new test event**
2. Event name: `TestForm`
3. Replace the test JSON with:

```json
{
    "body": "{\"name\": \"Rukayat\", \"email\": \"test@test.com\", \"message\": \"Hello from Lambda test!\"}"
}
```

4. Click **Test** — you should see `statusCode: 200` ✅
5. Go to DynamoDB → your table → **Explore items** — you should see the test entry!

---

### PHASE 4 — Create the API Gateway

#### Step 4.1 — Create the API
1. AWS Console → **API Gateway** → **Create API**
2. Choose **REST API** → **Build**
3. API name: `ContactFormAPI`
4. API endpoint type: **Regional**
5. Click **Create API**

#### Step 4.2 — Create a Resource
1. In your API → **Resources** → **Create resource**
2. Resource name: `contact`
3. Resource path: `/contact`
4. Check **CORS (Cross Origin Resource Sharing)**
5. Click **Create resource**

#### Step 4.3 — Create a POST Method
1. Click the `/contact` resource → **Create method**
2. Method type: **POST**
3. Integration type: **Lambda function**
4. Select your `ContactFormProcessor` function
5. Click **Create method**

#### Step 4.4 — Deploy the API
1. Click **Deploy API** (top right)
2. Stage: **New stage**
3. Stage name: `prod`
4. Click **Deploy**
5. Copy the **Invoke URL** :
   `https://h2zgh2z1g9.execute-api.us-east-1.amazonaws.com/prod`
6. Your full API endpoint is:
   `https://h2zgh2z1g9.execute-api.us-east-1.amazonaws.com/prod/contact`

---

### PHASE 5 — Connect Everything

#### Step 5.1 — Update index.html with the API URL above
1. Open `index.html` o
2. Find this line: `const API_URL = 'YOUR_API_GATEWAY_URL_HERE';`
3. Replace it with your actual URL:
   `const API_URL = 'https://abc123.execute-api.us-east-1.amazonaws.com/contact';`
4. Upload the updated `index.html` to S3 (overwrite the old one)

#### Step 5.2 — Test the Full Flow
1. Open your S3 website URL in the browser
2. Fill in the contact form
3. Click **Send Message**
4. You will see: **"Message sent successfully!"** ✅
5. Go to DynamoDB → Explore items → the submission is there! ✅

---

## Screenshots

### Contact Form (Local)
![Contact form running locally](images/contactform.png)

### index.html Uploaded to S3
![index.html uploaded to S3 bucket](images/upload-index-file.png)

### API Gateway — /contact Resource
![API Gateway ContactFormAPI with POST and OPTIONS methods](images/API_create.png)

### Lambda Test — 200 OK
![Lambda function executing with 200 OK response](images/lambda_test.png)

### Successful Form Submission
![Form showing "Message sent successfully!" banner](images/sucessful-submittion.png)

### DynamoDB — First Submission (from Lambda test)
![DynamoDB table showing first test submission](images/dynamo-table.png)

### DynamoDB — Multiple Submissions (live form)
![DynamoDB table showing two real submissions](images/submitted-forms.png)

---

## What I Learned

- How to connect four AWS services end-to-end without managing any servers
- Setting up CORS correctly between a static S3 site, API Gateway, and Lambda
- Writing a Python Lambda function to parse JSON and write to DynamoDB
- Storing structured data in DynamoDB using a UUID as a partition key
- Hosting a static website publicly on S3

---


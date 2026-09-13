Autonomous Order Triage & Resolution Agent

An AI-powered order management agent that automates post-checkout order issues, especially out-of-stock products.

The system analyzes an order, checks product availability, determines the appropriate resolution, and updates the order accordingly.

Project Objective

The main objective is to reduce manual work in e-commerce order processing by automatically handling common post-checkout issues.

For example:

A customer places an order.
One or more products become unavailable.
The agent checks the order and inventory.
It determines the best possible resolution.
The order is updated automatically.
Core Features
Order management
Product and inventory checking
Out-of-stock detection
Automatic order triage
Conditional decision-making
Order resolution workflow
Customer/order data management
MySQL database integration
FastAPI backend
LangGraph-based workflow
AI-assisted decision making
Technology Stack
Python
FastAPI
LangGraph
SQLAlchemy
MySQL
phpMyAdmin
Pydantic
Jinja2
Gemini API
Project Structure
autonomous-order-agent/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py
│   │   ├── nodes.py
│   │   └── workflow.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── orders.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── inventory.py
│   │   └── order_service.py
│   │
│   └── templates/
│       └── ...
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
Workflow
Customer Order
      ↓
Order Validation
      ↓
Inventory Check
      ↓
Product Available?
   ↙          ↘
 Yes           No
 ↓              ↓
Process       AI Triage
Order           ↓
          Resolution Decision
                 ↓
        ┌────────┼────────┐
        ↓        ↓        ↓
     Replace   Partial   Cancel
     Product    Order     Item
        ↓        ↓        ↓
        └────────┼────────┘
                 ↓
          Update Order
                 ↓
          Final Resolution
Database

The project uses MySQL as its database.

Database management can be performed using phpMyAdmin.

Example database configuration:

DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=autonomous_order_agent
DB_USER=root
DB_PASSWORD=

Do not commit your actual .env file to GitHub.

Installation

Clone the repository:

git clone https://github.com/ali-ahmed-07/autonomous-order-agent.git
cd autonomous-order-agent

Create a virtual environment:

python -m venv .venv

Activate it on Windows:

.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt
Environment Configuration

Create a .env file:

DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=autonomous_order_agent
DB_USER=root
DB_PASSWORD=

GEMINI_API_KEY=your_api_key_here
Run the Application

Start the FastAPI application:

uvicorn app.main:app --reload

The application will normally be available at:

http://127.0.0.1:8000

FastAPI documentation:

http://127.0.0.1:8000/docs
Example Use Case

Suppose an order contains three products:

Order #1001

Product A → In Stock
Product B → Out of Stock
Product C → In Stock

The agent detects that Product B is unavailable and evaluates the available resolution.

Depending on the business rules, the agent can:

Replace the unavailable product.
Process the order partially.
Cancel the unavailable item.
Cancel the complete order when required.

The decision is handled through the LangGraph workflow rather than requiring manual intervention for every case.

AI Agent Architecture

The system uses a graph-based workflow where different nodes perform specific tasks.

Order Input
    ↓
Order Analysis
    ↓
Inventory Validation
    ↓
Issue Detection
    ↓
Resolution Decision
    ↓
Action Execution
    ↓
Order Update

LangGraph is used to control the workflow and conditional transitions between these steps.

API

The FastAPI backend provides endpoints for interacting with orders and the agent workflow.

Example:

POST /orders
GET  /orders
GET  /orders/{order_id}
POST /orders/{order_id}/process

The exact endpoints may evolve as development continues.





License

This project is currently intended for educational and development purposes.

# Tatweer

Tatweer is a logistics-focused platform designed to optimize transportation and container space using AI-powered solutions. This project is built with Django for the backend and integrates RabbitMQ for task management.

## Features
- **AI-Powered Container Space Optimization**: Uses volume-based calculations to optimize container space.
- **Secure Payment System**: Ensures secure transactions.
- **Task Management with RabbitMQ**: Efficient handling of asynchronous tasks.
- **Real-Time Updates**: Provides logistics tracking with WebSockets.
- **Scalable Backend**: Built using Django and Django Rest Framework (DRF).

## Installation
### Prerequisites
- Python 3.x
- Docker & Docker Compose
- RabbitMQ (Docker Container)
- PostgreSQL (Recommended)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Moundher122/tatweer.git
   cd tatweer
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Update the `.env` file with your configuration.

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```
6. Start the development server:
   ```bash
   python manage.py runserver
   ```
7. Run Celery worker:
   ```bash
   celery -A tatweer worker --loglevel=info
   ```

## Usage
- Access the API via `http://127.0.0.1:8000/api/`
- Login and test API endpoints using Postman or cURL

## Contributing
1. Fork the repository
2. Create a new branch (`feature-branch`)
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License
This project is licensed under the MIT License.

## Contact
For inquiries, contact [Moundher](https://github.com/Moundher122).


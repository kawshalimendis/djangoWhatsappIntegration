# Django WhatsApp Integration

A Django application that demonstrates WhatsApp messaging integration for customer support systems.

## Features

- Send and receive WhatsApp messages
- Store message history with status tracking
- Webhook endpoint for real-time updates
- Admin interface for message management
- REST API endpoints for programmatic access
- Docker and PostgreSQL setup

## Prerequisites

- Python 3.10+
- Docker and Docker Compose
- WhatsApp Business API credentials

## Project Setup

1. Clone the repository:
```bash
git clone https://github.com/kawshalimendis/djangoWhatsappIntegration.git
cd django-whatsapp-integration
```

2. Create a `.env` file with your configuration:
```bash
# Django settings
DEBUG=1
SECRET_KEY=your-secret-key-here

# Database settings
DB_ENGINE=django.db.backends.postgresql
DB_NAME=whatsapp_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# WhatsApp API settings
WHATSAPP_API_TOKEN=your-whatsapp-api-token
WHATSAPP_PHONE_NUMBER_ID=your-whatsapp-phone-number-id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your-verify-token

# Logging settings
DJANGO_LOG_LEVEL=INFO     # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
WHATSAPP_LOG_LEVEL=DEBUG  
```

3. Build and start the Docker containers:
```bash
# Build the images
docker-compose build

# Start the containers in the background
docker-compose up -d

# View logs (optional)
docker-compose logs -f
```

4. Run database migrations:
```bash
docker-compose exec web python manage.py migrate
```

5. Create a superuser for admin access:
```bash
docker-compose exec web python manage.py createsuperuser
```

## Development Workflow

1. Start the development server:
```bash
docker-compose up
```

2. Access the application:
- Admin interface: `http://localhost:8000/admin/`
- API endpoints: `http://localhost:8000/api/whatsapp/`

3. Make code changes and Docker will automatically reload

4. Run tests after making changes:
```bash
docker-compose exec web python manage.py test
```

## Setting Up Logging

1. Create the logs directory and set permissions:
```bash
mkdir -p logs
chmod 755 logs
```

2. Add logging environment variables to your `.env` file:
```bash
# Logging settings
DJANGO_LOG_LEVEL=INFO     # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
WHATSAPP_LOG_LEVEL=DEBUG  # Set to DEBUG during development
```

3. Monitor logs in real-time:
```bash
# View general application logs
tail -f logs/whatsapp.log

# View error-specific logs
tail -f logs/error.log
```

4. Log file locations:
- General logs: `logs/whatsapp.log`
- Error logs: `logs/error.log`
- Each log file is limited to 5MB with 5 backup files

5. Log format:
- Console logs: Simple format showing level and message
- File logs: Verbose format including timestamp, module, process, and thread IDs

## API Endpoints

### WhatsApp Webhook
- `GET /api/whatsapp/webhook/` - Webhook verification
- `POST /api/whatsapp/webhook/webhook/` - Receive WhatsApp updates
- `POST /api/whatsapp/webhook/send-message/` - Send a WhatsApp message

### Messages
- `GET /api/whatsapp/messages/` - List all messages
- `POST /api/whatsapp/messages/` - Create a new message
- `GET /api/whatsapp/messages/{id}/` - Retrieve a message
- `PUT /api/whatsapp/messages/{id}/` - Update a message
- `DELETE /api/whatsapp/messages/{id}/` - Delete a message

## Admin Interface
Access the admin interface at `http://localhost:8000/admin/` to:
- View message history
- Send test messages (both template and text messages)
- Monitor message status
- Filter and search messages


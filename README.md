# MailConnect

MailConnect is a powerful email campaign management system that helps you automate and track your email outreach campaigns. Built with Django, it offers a robust set of features for managing email sequences, tracking responses, and integrating with your favorite CRM platforms.

## What MailConnect Can Do

- Create and manage automated email campaigns
- Track email opens, clicks, and responses
- Connect multiple SMTP servers for better deliverability
- Integrate with popular CRM platforms
- Create reusable email templates
- Schedule campaigns with flexible timing
- Monitor campaign performance with detailed analytics

## Getting Started

### System Requirements
- Windows 10+, macOS, or Linux
- Python 3.9 or higher
- PostgreSQL database
- Redis server

### Installation Steps

#### Installing from GitHub

1. Clone the repository:

```
git clone https://github.com/<myusername>/mailconnect.git
cd mailconnect
```


2. Create and activate a virtual environment:

```
python -m venv venv
on linux: source venv/bin/activate 
 On Windows: venv\Scripts\activate
```


3. Install dependencies:

`pip install -r requirements.txt`


4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:

```
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://user:password@localhost:5432/mailconnect
REDIS_URL=redis://localhost:6379/0
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```


5. Initialize the database:

`python manage.py migrate`


6. Create a superuser:

`python manage.py createsuperuser`


7. Run the development server:

`python manage.py runserver`


## Project Structure

```
mailconnect/
├── apps/
│ ├── campaigns/ # Campaign management
│ ├── email_manager/ # Email handling and tracking
│ └── api_app/ # API endpoints
├── core/ # Project settings and main URLs
├── static/ # Static files (CSS, JS, images)
├── templates/ # HTML templates
└── manage.py # Django management script
```


## Key Features

### Campaign Management
- Create and manage email campaigns
- Schedule automated email sequences
- Track campaign performance
- A/B testing capabilities

### Email Templates
- Create and save reusable templates
- Dynamic variable support
- HTML and plain text versions
- Template preview functionality

### Contact Management
- Import/export contacts
- Contact segmentation
- Custom fields support
- Activity tracking

### Analytics & Tracking
- Open and click tracking
- Response rate analytics
- Campaign performance metrics
- Detailed reporting

### CRM Integration
- Integration with popular CRM platforms
- Two-way contact sync
- Campaign result synchronization
- Webhook support

## API Documentation

The application provides a RESTful API for integration with other services. Key endpoints include:

- `/api/campaigns/` - Campaign management
- `/api/contacts/` - Contact management
- `/api/templates/` - Email template management
- `/api/analytics/` - Analytics data

For detailed API documentation, visit `/api/docs/` after running the server.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.
# Todo-Rest-API: Tasks Management REST API

<!-- ![Todo-Rest-API Banner](https://example.com/path/to/banner-image.png) (Replace this link with a relevant banner image if available) -->

## Overview

Todo-Rest-API is a powerful Tasks Management REST API developed using Python and Django REST Framework. This project serves as the backend for a task management application and includes features such as social authentication using Google, unit testing with Test Driven Development (TDD) principles, and integration with MySQL database. The ultimate goal of this project is to imitate the functionality of "https://www.getminimalist.com/" while providing seamless integration with the frontend application developed in Next.js.

<!-- ![Application Demo](https://example.com/path/to/demo-gif.gif) -->

## Key Features

- **Social Authentication**: Utilizes dj-rest-auth, allauth, and JWT to enable users to authenticate via Google accounts.
- **Task Management**: Provides endpoints to manage tasks, including creating, reading, updating, and deleting tasks.
- **Test Driven Development (TDD)**: Ensures the codebase is thoroughly tested using Django tests and follows TDD principles.
- **MySQL Database**: Integrates with MySQL for data storage, ensuring robust and scalable data management.

## Frontend Repository

For the frontend part of this project, the Next.js 13 application can be found in the following repository: [Minimalist Todo App Next.js](https://github.com/matiasvallejosdev/minimalist-todo-app-nextjs).

## Installation

To run Todo-Rest-API locally or in your own server, follow these steps:

1. Clone this repository: `git clone https://github.com/matiavallejosdev/todo-rest-api.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Configure the MySQL database settings in `settings.py`.
4. Perform database migrations: `python manage.py migrate`
5. Start the development server: `python manage.py runserver`

## API Documentation

The API endpoints and their usage are documented using [Swagger](https://swagger.io/). Once the development server is running, you can access the API documentation by navigating to `http://localhost:8000/swagger/` in your web browser.

## Running Tests

To run the unit tests for the application, execute the following command:

```bash
python manage.py test
```


## Contributing

Contributions to Todo-Rest-API are welcome! If you find any bugs or have suggestions for new features, please feel free to open an issue or submit a pull request. For major changes, please open an issue first to discuss the proposed changes.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## Contact

If you have any questions or need further assistance, you can contact the project maintainer:

- Name: Matias Vallejos
- GitHub: [@matiavallejosdev](https://github.com/matiavallejosdev)
- Email: matias.vallejos@example.com (Replace this with your actual email address)

Feel free to reach out if you have any inquiries or need any additional information about the project.

---

Thank you for considering Todo-Rest-API for your tasks management needs. We hope this REST API serves as a solid foundation for your task management application. We look forward to your valuable contributions and feedback!
# Social Network API

## Installation

1. Clone the repository
2. Navigate to the project directory
3. Run `docker-compose up --build`
4. The API will be available at `http://localhost:8000`

## API Documentation

- `POST /api/users/signup/` - for signup using email and password

- `POST /api/users/token/` - Obtain JWT token
- `POST /api/users/token/refresh/` - Refresh JWT token
- `POST /api/users/friend-request/` - Send a friend request
- `POST /api/users/accept-friend-request/` - Accept a friend request
- `POST /api/users/reject-friend-request/` - Reject a friend request
- `GET /api/users/friends/` - List friends
- `GET /api/users/pending-requests/` - List pending friend requests
- `GET /api/users/search/` - Search users by email or name

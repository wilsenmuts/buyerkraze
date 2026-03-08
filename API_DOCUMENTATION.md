# BuyerKraze API Documentation

## Overview
This API provides endpoints for managing articles with API key authentication for creation and public access for reading. Articles support like/dislike functionality and view tracking.

## Authentication
API key authentication is required only for creating articles. Use the `X-API-Key` header for authentication.

### Obtaining an API Key
1. Log in to the Django admin panel at `/admin/`
2. Navigate to API Keys section
3. Click "Add API Key"
4. Provide a name for identification
5. Save - the system will automatically generate a unique API key
6. Copy and securely store the generated API key

## Endpoints

### 1. List All Articles (Public)
**GET** `/api/articles/`

Returns a list of all articles with their metadata.

**Response:**
```json
[
  {
    "id": 1,
    "title": "Article Title",
    "content": "Article content...",
    "published_date": "2026-03-08T10:30:00Z",
    "updated_date": "2026-03-08T10:30:00Z",
    "featured_image": "/media/articles/featured/image.jpg",
    "top_image": "/media/articles/top/image.jpg",
    "view_count": 150,
    "likes": 25,
    "dislikes": 3
  }
]
```

### 2. Create Article (Requires API Key)
**POST** `/api/articles/`

**Headers:**
```
X-API-Key: your-api-key-here
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "My New Article",
  "content": "This is the article content...",
  "featured_image": null,
  "top_image": null
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "title": "My New Article",
  "content": "This is the article content...",
  "published_date": "2026-03-08T15:45:00Z",
  "updated_date": "2026-03-08T15:45:00Z",
  "featured_image": null,
  "top_image": null,
  "view_count": 0,
  "likes": 0,
  "dislikes": 0
}
```

### 3. Get Article Detail (Public)
**GET** `/api/articles/{id}/`

Retrieves a single article and increments its view count.

**Response:**
```json
{
  "id": 1,
  "title": "Article Title",
  "content": "Full article content...",
  "published_date": "2026-03-08T10:30:00Z",
  "updated_date": "2026-03-08T10:30:00Z",
  "featured_image": "/media/articles/featured/image.jpg",
  "top_image": "/media/articles/top/image.jpg",
  "view_count": 151,
  "likes": 25,
  "dislikes": 3
}
```

### 4. Like Article (Public)
**POST** `/api/articles/{id}/like/`

Likes an article. Users are identified by their IP + User-Agent combination to prevent duplicate votes.

**Response (200 OK):**
```json
{
  "likes": 26,
  "dislikes": 3
}
```

**Response (400 Bad Request - Already Liked):**
```json
{
  "error": "Already liked"
}
```

### 5. Dislike Article (Public)
**POST** `/api/articles/{id}/dislike/`

Dislikes an article. Users can change from like to dislike and vice versa.

**Response (200 OK):**
```json
{
  "likes": 25,
  "dislikes": 4
}
```

**Response (400 Bad Request - Already Disliked):**
```json
{
  "error": "Already disliked"
}
```

## Example Usage

### Using cURL

#### List all articles:
```bash
curl -X GET http://localhost:8000/api/articles/
```

#### Create a new article:
```bash
curl -X POST http://localhost:8000/api/articles/ \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Article",
    "content": "This is a great article about reverse marketplaces."
  }'
```

#### Get article details:
```bash
curl -X GET http://localhost:8000/api/articles/1/
```

#### Like an article:
```bash
curl -X POST http://localhost:8000/api/articles/1/like/
```

#### Dislike an article:
```bash
curl -X POST http://localhost:8000/api/articles/1/dislike/
```

### Using Python

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api"
API_KEY = "your-api-key-here"

# List articles
response = requests.get(f"{BASE_URL}/articles/")
articles = response.json()
print(articles)

# Create article
headers = {"X-API-Key": API_KEY}
data = {
    "title": "My Article",
    "content": "Article content here"
}
response = requests.post(f"{BASE_URL}/articles/", json=data, headers=headers)
new_article = response.json()
print(new_article)

# Like article
response = requests.post(f"{BASE_URL}/articles/1/like/")
result = response.json()
print(f"Likes: {result['likes']}, Dislikes: {result['dislikes']}")
```

### Using JavaScript (Fetch API)

```javascript
// List articles
fetch('/api/articles/')
  .then(response => response.json())
  .then(data => console.log(data));

// Create article
fetch('/api/articles/', {
  method: 'POST',
  headers: {
    'X-API-Key': 'your-api-key-here',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: 'My Article',
    content: 'Article content here'
  })
})
  .then(response => response.json())
  .then(data => console.log(data));

// Like article
fetch('/api/articles/1/like/', {
  method: 'POST'
})
  .then(response => response.json())
  .then(data => console.log(data));
```

## Features

### View Tracking
- Every time an article is viewed (via web or API), the view count is automatically incremented
- View counts are displayed on both the article list and detail pages

### Like/Dislike System
- Users can like or dislike articles
- Duplicate votes are prevented using IP + User-Agent fingerprinting
- Users can change their vote (from like to dislike or vice versa)
- The counts update in real-time on the frontend

### Public Access
- All articles are publicly accessible (no authentication required for reading)
- API key authentication is only required for creating new articles

## Error Codes

- `200 OK` - Successful request
- `201 Created` - Article successfully created
- `400 Bad Request` - Invalid data or duplicate vote
- `401 Unauthorized` - Invalid or missing API key (for POST /api/articles/)
- `404 Not Found` - Article not found

## Notes

- Images can be uploaded via multipart/form-data when creating articles
- All timestamps are in UTC
- The API supports CORS for frontend integration
- Session-based duplicate vote prevention works across both web UI and API

# Admin API Endpoints

These endpoints are admin-only and require a valid JWT with `role: "admin"`.

Base prefix: `/admin`

## GET /admin/users
- Returns: list of users
- Response: 200
- Example item: { id, username, email, role }

## GET /admin/experts
- Returns: list of users where `role == "expert"`
- Response: 200

## GET /admin/rankings
- Purpose: Return expert rankings ordered from highest to lowest based on SAW weights
- Response: 200
- Schema: `ExpertRankingOut`
- Example item:
  {
    "expert_id": "3",
    "username": "expert3",
    "email": "expert3@example.com",
    "weight": 0.2345,
    "rank": 1
  }

## GET /admin/consensus
- Purpose: Return aggregated group decision results (consensus model) for each DASS-21 item
- Response: 200
- Schema: `ConsensusItem`
- Example item:
  {
    "dass21_id": 1,
    "depression": 33.33,
    "anxiety": 33.33,
    "stress": 33.33
  }


# Notes
- All endpoints must be called with `Authorization: Bearer <token>` header.
- Admin accounts are only created via seeders or scripts and cannot be registered via `/auth/register`.
- The `/auth/login` endpoint now returns a `redirect_to` field in the auth response which FE should use to route users after login (admin -> `/admin/dashboard`, regular users -> `/user/dashboard`).
- If a frontend needs additional management operations (suspend, delete, change role), backend endpoints must be added; UI placeholders will be used until then.
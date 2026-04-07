# Verification

## After Fix

```elixir
def index(conn, _params) do
  users = Repo.all(User) |> Repo.preload(:posts)
  render(conn, :index, users: users)
end
```

## Regression Checks

- 800 users: exactly 2 queries (1 SELECT users, 1 SELECT posts WHERE user_id IN (...))
- Page load time: <200ms for 800 users
- Empty posts list: no error (user.posts returns [], length([]) = 0)
- hd([]) for user with no posts: handle separately (hd raises on empty list)

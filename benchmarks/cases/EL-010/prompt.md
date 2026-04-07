# EL-010: User Listing Page Times Out in Production with 800 Users

## User Prompt

Our admin user listing page loads in 120ms in development with 50 users. In production with 800 users it times out after 30 seconds. No code changes between dev and prod. The DB has proper indexes. Running the queries individually shows each one completes in <5ms. We added database query logging and see thousands of queries firing for a single page load.

## Context Provided To The Skill

- stack: Elixir 1.16, Phoenix 1.7.11, Ecto 3.11.1, PostgreSQL 15
- environment: production (800 users), dev (50 users)
- logs: `SELECT * FROM posts WHERE user_id = $1` repeated 800 times
- code excerpt:
```elixir
defmodule MyAppWeb.Admin.UserController do
  def index(conn, _params) do
    users = Repo.all(User)
    render(conn, :index, users: users)
  end
end

# Template (index.html.heex)
# <%= for user <- @users do %>
#   <tr>
#     <td><%= user.name %></td>
#     <td><%= length(user.posts) %> posts</td>
#     <td><%= hd(user.posts).inserted_at %></td>  # latest post date
#   </tr>
# <% end %>
```

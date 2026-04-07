# EL-008: Product Detail Page Shows Previous Product's Data After Navigation

## User Prompt

Our Phoenix LiveView product catalog lets users browse products. When a user navigates from Product A to Product B using push_patch, the page briefly shows Product A's specs before updating. Sometimes it fully shows Product A's data and never updates to Product B. The async loading indicator shows "loading" correctly but the data that eventually appears is wrong.

## Context Provided To The Skill

- stack: Elixir 1.16, Phoenix 1.7.11, Phoenix LiveView 0.20.14
- environment: production and local
- logs:
  - `[debug] assign_async started for product_id=102`
  - `[debug] fetched product: id=99 name="Widget A"` ← wrong product fetched
- code excerpt:
```elixir
defmodule MyAppWeb.ProductLive.Show do
  use MyAppWeb, :live_view

  def mount(_params, _session, socket) do
    {:ok, socket}
  end

  def handle_params(%{"id" => id}, _uri, socket) do
    product_id = String.to_integer(id)
    socket = assign(socket, :product_id, product_id)

    {:noreply,
     assign_async(socket, :product, fn ->
       Logger.debug("fetched product: #{inspect(MyApp.Catalog.get_product(product_id))}")
       {:ok, %{product: MyApp.Catalog.get_product(product_id)}}
     end)}
  end
end
```

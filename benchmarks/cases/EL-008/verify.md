# Verification

## After Fix

`assign_async` in LiveView 0.20.x does not have a `reset:` option (added in LiveView 1.x).
The correct approach for 0.20.14 is `cancel_async/3` before starting the new task:

```elixir
def handle_params(%{"id" => id}, _uri, socket) do
  product_id = String.to_integer(id)
  socket = assign(socket, :product_id, product_id)

  # Cancel any in-flight async task for :product before starting new one
  socket = Phoenix.LiveView.cancel_async(socket, :product)

  {:noreply,
   assign_async(socket, :product, fn ->
     {:ok, %{product: MyApp.Catalog.get_product(product_id)}}
   end)}
end
```

For LiveView 1.x (if upgrading): `assign_async(socket, :product, fn -> ... end, reset: true)`
achieves the same result more concisely.

## Regression Checks

- Navigate A → B slowly: Product B data shows correctly
- Navigate A → B → C rapidly: Product C data shows (A and B tasks cancelled)
- Refresh Product B: correct data shown

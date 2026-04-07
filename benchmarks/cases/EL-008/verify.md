# Verification

## After Fix

```elixir
def handle_params(%{"id" => id}, _uri, socket) do
  product_id = String.to_integer(id)
  socket = assign(socket, :product_id, product_id)

  {:noreply,
   assign_async(socket, :product, fn ->
     {:ok, %{product: MyApp.Catalog.get_product(product_id)}}
   end, reset: true)}  # cancel previous async task before starting new one
end
```

## Regression Checks

- Navigate A → B slowly: Product B data shows correctly
- Navigate A → B → C rapidly: Product C data shows (A and B tasks cancelled)
- Refresh Product B: correct data shown

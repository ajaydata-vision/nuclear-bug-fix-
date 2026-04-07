# Verification

## After Fix

```elixir
# Job insertion — plain scalar values only
def after_order_created(order) do
  %{order_id: order.id}
  |> InvoiceWorker.new()
  |> Oban.insert()
end

# Worker — string key pattern match
def perform(%Oban.Job{args: %{"order_id" => order_id}}) do
  order = Repo.get!(Order, order_id)
  invoice = Invoices.generate(order)
  Mailer.send_invoice(order.user, invoice)
  :ok
end
```

## Regression Checks

- SELECT args FROM oban_jobs: shows `{"order_id": 42}` not `{}`
- Invoice created and email sent for each completed job
- Job retry: idempotent (same invoice not duplicated on retry)

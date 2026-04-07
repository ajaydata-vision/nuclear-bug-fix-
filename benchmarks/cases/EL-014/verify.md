# Verification

## After Fix

```elixir
def perform(%Oban.Job{args: %{"order_id" => order_id, "user_id" => user_id}}) do
  Logger.info("NotificationWorker started for order_id=#{order_id}")

  with {:ok, order}  <- Orders.get_shipped(order_id),
       {:ok, user}   <- Accounts.get_active(user_id),
       {:ok, device} <- Devices.get_primary(user) do
    Notifications.push(device, "Your order #{order_id} has shipped!")
    :ok
  else
    {:error, :order_not_shipped} ->
      {:snooze, 300}          # order not shipped yet — retry in 5 minutes
    {:error, :user_inactive} ->
      {:cancel, "user inactive, no notification needed"}
    {:error, :no_device} ->
      {:cancel, "no push device registered"}
    {:error, reason} ->
      {:error, reason}        # transient — Oban retries with backoff
  end
end
```

## Regression Checks

- Shipped order, active user, device registered: notification sent, job completed
- Order not yet shipped: job snoozed 5 minutes, retried automatically
- User inactive: job cancelled (not retried), state = cancelled
- API error: job retryable, state = retryable, retried up to max_attempts

# EL-014: Notification Worker Completes Successfully But Notifications Never Sent

## User Prompt

Our `NotificationWorker` sends push notifications when orders ship. The Oban job shows `state = completed`. No errors in logs. No entries in failed_jobs. The push notification service has zero calls in its dashboard for these jobs. Running the worker logic manually in IEx with a real order ID sends the notification correctly. The job appears to execute — we see the "Worker started" log line — but nothing happens after that.

## Context Provided To The Skill

- stack: Elixir 1.16, Phoenix 1.7.11, Oban 2.17.3
- environment: production and local
- logs:
  - `[info] NotificationWorker started for order_id=77`
  - (no further log output for this job)
- code excerpt:
```elixir
defmodule MyApp.Workers.NotificationWorker do
  use Oban.Worker, queue: :notifications, max_attempts: 5

  def perform(%Oban.Job{args: %{"order_id" => order_id, "user_id" => user_id}}) do
    Logger.info("NotificationWorker started for order_id=#{order_id}")

    result = with {:ok, order}  <- Orders.get_shipped(order_id),
                  {:ok, user}   <- Accounts.get_active(user_id),
                  {:ok, device} <- Devices.get_primary(user) do
      Notifications.push(device, "Your order #{order_id} has shipped!")
    end

    :ok
  end
end
```

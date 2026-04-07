# EL-A03: Oban Job — Partial Struct Serialization, One Field Correct

## User Prompt

Our `ShipmentWorker` processes shipment notifications. The job args look correct — the order_id is right. But the shipment never gets processed. The worker runs, completes, no errors. We checked the args in the DB and see: `{"order_id": 42, "carrier": {}, "tracking": {}}`. The order_id is correct. We thought "args look fine, order_id is there." But shipments still aren't processed. No pattern match errors visible anywhere.

## Context Provided To The Skill

- stack: Elixir 1.16, Phoenix 1.7.11, Oban 2.17.5
- environment: production
- logs: `[info] ShipmentWorker started` (no further logs)
- database:
  ```
  SELECT args FROM oban_jobs WHERE worker = 'MyApp.Workers.ShipmentWorker' LIMIT 3;
  args: {"order_id": 42, "carrier": {}, "tracking": {}}
  args: {"order_id": 99, "carrier": {}, "tracking": {}}
  args: {"order_id": 14, "carrier": {}, "tracking": {}}
  ```
- code excerpt:
```elixir
defmodule MyApp.Workers.ShipmentWorker do
  use Oban.Worker, queue: :shipments

  def perform(%Oban.Job{args: %{"order_id" => order_id}}) do
    Logger.info("ShipmentWorker started")
    # order_id matches correctly
    order = Repo.get!(Order, order_id)
    process_shipment(order, ???)  # how to get carrier and tracking?
  end
end

# Job insertion:
def dispatch_shipment(order, carrier, tracking_info) do
  %{
    order_id: order.id,
    carrier: carrier,           # %MyApp.Carrier{name: "FedEx", code: "FX"}
    tracking: tracking_info     # %MyApp.TrackingInfo{number: "1Z999", url: "..."}
  }
  |> ShipmentWorker.new()
  |> Oban.insert()
end
```

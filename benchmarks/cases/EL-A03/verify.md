# Verification

## After Fix

```elixir
def dispatch_shipment(order, carrier, tracking_info) do
  %{
    order_id: order.id,
    carrier_code: carrier.code,
    carrier_name: carrier.name,
    tracking_number: tracking_info.number,
    tracking_url: tracking_info.url
  }
  |> ShipmentWorker.new()
  |> Oban.insert()
end

def perform(%Oban.Job{args: %{
  "order_id" => order_id,
  "carrier_code" => carrier_code,
  "carrier_name" => carrier_name,
  "tracking_number" => tracking_number,
  "tracking_url" => tracking_url
}}) do
  order = Repo.get!(Order, order_id)
  carrier = %{code: carrier_code, name: carrier_name}
  tracking = %{number: tracking_number, url: tracking_url}
  process_shipment(order, carrier, tracking)
end
```

## Regression Checks

- SELECT args FROM oban_jobs: shows `{"order_id": 42, "carrier_code": "FX", "carrier_name": "FedEx", "tracking_number": "1Z999", "tracking_url": "..."}` — no {} values
- Shipment processed: carrier and tracking data correctly available in perform/1
- Job state: completed AND shipment actually sent

# EL-013: Invoice Worker Runs and Completes But Invoices Never Created

## User Prompt

We have an Oban worker that generates PDF invoices and emails them to customers. The worker shows `state = completed` in the database. No errors anywhere. No entries in failed_jobs. But invoices are never created and customers never receive emails. Running the same logic manually in IEx with the same order works perfectly — invoice created, email sent.

## Context Provided To The Skill

- stack: Elixir 1.16, Phoenix 1.7.11, Oban 2.17.6, PostgreSQL 15
- environment: production and local (same behaviour)
- logs: no errors
- database: `SELECT id, state, args FROM oban_jobs WHERE worker = 'MyApp.Workers.InvoiceWorker' LIMIT 3;`
  ```
  id  | state     | args
  ----+-----------+------
  142 | completed | {}
  143 | completed | {}
  144 | completed | {}
  ```
- code excerpt:
```elixir
defmodule MyApp.Workers.InvoiceWorker do
  use Oban.Worker, queue: :invoices, max_attempts: 3

  def perform(%Oban.Job{args: %{"order_id" => order_id}}) do
    order = Repo.get!(Order, order_id)
    invoice = Invoices.generate(order)
    Mailer.send_invoice(order.user, invoice)
    :ok
  end
end

# Job insertion:
def after_order_created(order) do
  %{order: order, customer: order.customer}
  |> InvoiceWorker.new()
  |> Oban.insert()
end
```

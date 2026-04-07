# EL-009: Shipping Address Fields Always Empty After Form Save

## User Prompt

Our checkout form has a shipping address section using an embedded schema. The parent order saves correctly (products, quantities, total). But the shipping address is always nil/empty in the database. No validation errors shown. The form has all the address fields visible and the user fills them in. Inspecting the saved order shows `shipping_address: nil`.

## Context Provided To The Skill

- stack: Elixir 1.16, Phoenix 1.7.11, Phoenix LiveView 0.20.14
- environment: production and local
- logs: no errors
- code excerpt:
```elixir
# Schema
defmodule MyApp.Order do
  use Ecto.Schema
  embedded_schema do
    field :total, :decimal
    embeds_one :shipping_address, MyApp.Address, on_replace: :update
  end
  def changeset(order, attrs) do
    order
    |> cast(attrs, [:total])
    |> cast_embed(:shipping_address, required: true)
  end
end

defmodule MyApp.Address do
  use Ecto.Schema
  embedded_schema do
    field :street, :string
    field :city, :string
    field :country, :string
  end
  def changeset(addr, attrs) do
    addr |> cast(attrs, [:street, :city, :country])
  end
end
```
```heex
<%# Checkout form template %>
<.form for={@form} phx-submit="checkout">
  <.input field={@form[:total]} label="Total" type="hidden" />
  <h3>Shipping Address</h3>
  <.inputs_for :let={addr_form} field={@form[:shipping_address]}>
    <.input field={addr_form[:street]} label="Street" />
    <.input field={addr_form[:city]} label="City" />
    <%# country field intentionally managed by backend based on account settings %>
  </.inputs_for>
  <.button>Place Order</.button>
</.form>
```

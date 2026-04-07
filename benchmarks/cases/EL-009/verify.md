# Verification

## After Fix

```heex
<.inputs_for :let={addr_form} field={@form[:shipping_address]}>
  <.input field={addr_form[:street]} label="Street" />
  <.input field={addr_form[:city]} label="City" />
  <.input type="hidden" field={addr_form[:country]} />  <%# backend-managed field %>
</.inputs_for>
```

## Regression Checks

- Submit with street and city filled: order saved with shipping_address.country set to account default
- Submit with blank street: validation error shown (if street is required)
- Existing order edit: address fields pre-populated correctly

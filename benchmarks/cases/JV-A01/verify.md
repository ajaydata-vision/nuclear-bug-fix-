# Verification

## Before Fix

1. Deploy CartServlet with instance variables `cart` and `currentUser`
2. Run 50 concurrent users each adding a unique SKU and immediately fetching cart
3. Observe: some users receive another user's SKU in their cart response

## After Fix

1. Move `cart` and `currentUser` to local variables inside `doPost`/`doGet`
2. Pass cart via `req.setAttribute("cart", cart)` or use `HttpSession`
3. Re-run 50 concurrent users — each user sees only their own items
4. No synchronization primitives needed

## Regression Checks

- Single user flow: add item, get cart, checkout — still works correctly
- Session isolation: two users with same SKU — each sees only their own
- High concurrency (500 threads): zero cross-user contamination in logs

# Verification

## Before Fix
- Order submitted → confirmation displays → URL bar shows `/orders`
- F5 → browser shows "Confirm Form Resubmission?" dialog
- User clicks Continue → duplicate order created

## After Fix
```java
// OrderServlet.java
@Override
protected void doPost(HttpServletRequest req, HttpServletResponse resp)
        throws ServletException, IOException {

    Order order = orderService.createOrder(
        req.getParameter("productId"),
        req.getParameter("quantity"),
        req.getParameter("customerId")
    );
    log.info("[ORDER] created order {} for customer {}",
             order.getId(), order.getCustomerId());

    // Store order in session so it survives the redirect (attributes are lost)
    req.getSession().setAttribute("lastOrder", order);

    // PRG: redirect to GET — browser URL changes, F5 is safe
    resp.sendRedirect(req.getContextPath() + "/confirmation");
}

// ConfirmationServlet.java (new GET handler) or add doGet to OrderServlet:
@Override
protected void doGet(HttpServletRequest req, HttpServletResponse resp)
        throws ServletException, IOException {

    Order order = (Order) req.getSession().getAttribute("lastOrder");
    req.getSession().removeAttribute("lastOrder"); // consume once
    req.setAttribute("order", order);
    req.getRequestDispatcher("/WEB-INF/views/confirmation.jsp")
       .forward(req, resp);
}
```
1. Submit order → POST creates order → `sendRedirect` → browser makes GET to `/confirmation`
2. Browser URL bar now shows `/confirmation` (GET URL)
3. Press F5 → browser re-requests GET `/confirmation` — no "Resend form data?" prompt
4. Confirmation page redisplays, no second order created

## Regression Checks
- Back button after confirmation: browser goes back to form page (not to /orders POST) — no resubmission risk
- Session timeout before GET request arrives: handle `order == null` in GET handler gracefully
- Direct navigation to /confirmation with no session: redirect to home or show neutral message

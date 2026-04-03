# JV-019: Order Form Creates Duplicate Orders On F5 Refresh

## User Prompt

Our order submission form creates duplicate orders when users press F5 after
submitting. Support is getting complaints about customers being charged twice.
The form submits via POST to a servlet which processes the order and then forwards
to a confirmation JSP. Pressing F5 on the confirmation page triggers the browser
to ask "Resend form data?" and if the user clicks OK the order is created again.
How do we stop the duplicate submissions?

## Context Provided To The Skill

- stack: Java 17, Tomcat 10.1.19, Jakarta Servlet 6.0, JSP, no Spring
- versions: Jakarta EE 10
- environment: production
- logs:
  - `[ORDER] created order ORD-9041 for customer cust-17`
  - ← user presses F5, clicks "Resend" in browser dialog
  - `[ORDER] created order ORD-9042 for customer cust-17` (duplicate)
- code excerpt:
```java
// OrderServlet.java
@WebServlet("/orders")
public class OrderServlet extends HttpServlet {

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

        // Pass order to confirmation page
        req.setAttribute("order", order);
        req.getRequestDispatcher("/WEB-INF/views/confirmation.jsp")
           .forward(req, resp);  // ← browser URL still shows /orders (POST)
    }
}
```
- reproduction:
  1. Submit order form → POST /orders → order created → confirmation.jsp displayed
  2. Browser URL bar still shows `/orders` (POST URL unchanged by forward)
  3. Press F5
  4. Browser prompts: "Confirm Form Resubmission — Do you want to resubmit the data?"
  5. Click Continue → second POST to /orders → duplicate order created

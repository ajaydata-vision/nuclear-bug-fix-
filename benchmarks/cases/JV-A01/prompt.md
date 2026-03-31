# JV-A01: Users Occasionally See Each Other's Cart Items

## User Prompt

Our Java e-commerce servlet is showing the wrong user's cart under load. User A adds items, then User B sees User A's items. Never happens during testing. Only in production under traffic. What is the real bug?

## Context Provided To The Skill

- stack: Java 17, Tomcat 10.1.18, plain HttpServlet (no Spring)
- versions: jakarta.servlet-api 6.0.0
- environment: production, 200+ concurrent users, never reproduces under 10 concurrent users
- logs:
  - [INFO] User 9182 added item SKU-4421 to cart
  - [INFO] User 7703 checkout started, cart=[SKU-4421] ← wrong user's item
  - [INFO] User 9182 session valid, userId=9182
  - [INFO] User 7703 session valid, userId=7703
- code excerpt:
```java
public class CartServlet extends HttpServlet {
    private List<String> cart = new ArrayList<>();
    private User currentUser;

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) {
        currentUser = userService.findById(req.getSession().getAttribute("userId"));
        String sku = req.getParameter("sku");
        cart.add(sku);
        resp.setStatus(200);
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) {
        renderCart(resp, currentUser, cart);
    }
}
```
- reproduction:
  1. Two concurrent users add items to cart simultaneously
  2. Under load, User B's GET sees User A's cart contents
  3. Sessions are correctly isolated (confirmed via logs)
  4. Single Tomcat instance, no clustering

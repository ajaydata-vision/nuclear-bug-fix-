# JV-002: JSP Search Results Appear in Next User's Page Load

## User Prompt

Our JSP-based product search stores search results and the query string somewhere. When User A searches, then User B visits the same page, User B sees User A's search results briefly before their own load. Only happens in production, not locally with one user.

## Context Provided To The Skill

- stack: Java 17, Tomcat 10.1, JSP 3.1, JSTL 3.0, no Spring
- environment: production, multiple concurrent users
- logs: no errors, normal INFO logs only
- code excerpt:
```java
// SearchServlet.java
@WebServlet("/search")
public class SearchServlet extends HttpServlet {
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) {
        String query = req.getParameter("q");
        List<Product> results = productService.search(query);
        req.getSession().setAttribute("searchResults", results);
        req.getSession().setAttribute("searchQuery", query);
        req.getRequestDispatcher("/search.jsp").forward(req, resp);
    }
}
```
```jsp
<%-- search.jsp --%>
<p>Results for: ${sessionScope.searchQuery}</p>
<c:forEach var="p" items="${sessionScope.searchResults}">
    <div>${p.name}</div>
</c:forEach>
```
- reproduction:
  1. User A searches for "laptop"
  2. User B opens search page (no query yet)
  3. User B sees "Results for: laptop" with User A's results
  4. After User B searches, correct results appear

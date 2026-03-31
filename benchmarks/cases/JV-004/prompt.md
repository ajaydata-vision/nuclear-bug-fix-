# JV-004: JSP Shows Null for User Name Despite Servlet Setting It

## User Prompt

Our JSP profile page shows null for the username. The servlet is definitely fetching the user from the database. The Java code prints the name correctly with System.out. The JSP ${user.name} renders as empty. What is wrong?

## Context Provided To The Skill

- stack: Java 17, Tomcat 10.1, JSP 3.1, JSTL 3.0
- environment: local and production, fully reproducible
- logs:
  - [INFO] ProfileServlet: Loaded user name=Alice for userId=42
- code excerpt:
```java
// ProfileServlet.java
protected void doGet(HttpServletRequest req, HttpServletResponse resp) {
    Long userId = (Long) req.getSession().getAttribute("userId");
    User user = userService.findById(userId);
    System.out.println("Loaded user name=" + user.getName()); // prints Alice
    req.getRequestDispatcher("/profile.jsp").forward(req, resp);
}
```
```jsp
<%-- profile.jsp --%>
<h1>Welcome, ${user.name}</h1>
<%-- renders: Welcome,  --%>

<%-- Trying scriptlet as workaround: --%>
<% User u = (User) request.getAttribute("user"); %>
<h2><%= u != null ? u.getName() : "also null" %></h2>
<%-- also renders: also null --%>
```
- reproduction:
  1. Log in, navigate to /profile
  2. Server log shows user loaded correctly
  3. JSP renders empty name
  4. Scriptlet confirms request.getAttribute("user") is null

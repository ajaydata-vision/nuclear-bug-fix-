# JV-003: Footer Change Not Appearing After Deployment

## User Prompt

We updated our JSP footer template to add a privacy policy link. Deployed to Tomcat. The old footer still shows. Deployed again. Still old footer. Server logs show the new file is on disk. What is wrong?

## Context Provided To The Skill

- stack: Java 17, Tomcat 10.1.18, JSP 3.1
- environment: production Tomcat, WAR deployment
- logs:
  - [INFO] Deployment of war file /opt/tomcat/webapps/app.war completed successfully
- code excerpt:
```jsp
<%-- main.jsp --%>
<%@ include file="/WEB-INF/includes/footer.jsp" %>
```
```jsp
<%-- footer.jsp (updated version on disk) --%>
<footer>
  <a href="/privacy">Privacy Policy</a>  <%-- NEW LINK — not appearing --%>
  <p>Copyright 2025</p>
</footer>
```
- reproduction:
  1. footer.jsp updated with new privacy link
  2. WAR redeployed
  3. Browser shows old footer without privacy link
  4. curl directly also shows old footer
  5. cat /opt/tomcat/webapps/app/WEB-INF/includes/footer.jsp shows new content

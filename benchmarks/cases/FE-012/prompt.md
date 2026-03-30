# FE-012: SPA Hard Refresh Returns 404 Because Server Does Not Route to index.html

## User Prompt

Our React SPA works when navigating within the app but returns 404 on hard refresh for any route except the root. Nginx is the server. What is wrong?

## Context Provided To The Skill

- stack: React 18.2, React Router 6, Nginx
- environment: production Nginx deployment
- logs:
- navigating within the app works
  - hard refreshing any route other than / returns 404
  - Nginx error.log shows: 'open() /var/www/html/about failed (2: No such file or directory)'
- code excerpt:
```nginx
server {
  root /var/www/html;
  location / {
    try_files $uri $uri/ =404;
  }
}
```
- reproduction:
1. Navigate to /about within the SPA
2. Hard refresh the page
3. Observe Nginx 404

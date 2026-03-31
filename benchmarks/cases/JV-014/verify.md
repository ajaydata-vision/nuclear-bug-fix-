# Verification

## Before Fix
Valid JWT → JwtFilter sets Authentication → Spring Security overwrites → null principal

## After Fix
```java
// Remove @WebFilter from JwtFilter

// SecurityConfig
@Autowired JwtFilter jwtFilter;

@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
        .authorizeHttpRequests(a -> a.anyRequest().authenticated());
    return http.build();
}
```
Valid JWT → JwtFilter sets Authentication inside Security chain → principal non-null in controller

## Regression Checks
- Invalid JWT: Authentication not set, 401 returned
- No JWT: 401 returned
- Enable debug: logging.level.org.springframework.security=DEBUG — confirm JwtFilter appears in chain

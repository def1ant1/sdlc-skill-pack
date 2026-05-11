# Scraping Governor

`core/scraping-governor/` contains governance interceptors that run before any source adapter call.

Interceptors enforce policy decisions such as robots.txt and terms-of-service allowability, per-source throttle constraints, and proxy-route controls.

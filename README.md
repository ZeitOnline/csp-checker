# Content Security Policy Checker

## Purpose

A content security is defined by the server and checked by the browser. In
large web applications a delivering HTTP reverse proxy might not know and can
not evaluate, if all delivered content is secure according to it's own policy.
It can however define a policy indicated by a HTTP header 
(e.g. `Content-Security-Policy "upgrade-insecure-requests;"`), which the 
browser checks. With this method the calculating effort is shifted towards the
client. The client might block or upgrade content according to the policy.

In addition the client browser can send all policy violations to an HTTP header
indicated enpoint
( `Content-Security-Policy-Report-Only "default-src https:; report-uri /csp-report") .
It will compose JSON data structures, which are send via
POST to this endpoint for each security violation.

In this repository we set up an Elastic-Logstash-Kibana (ELK) stack with
`docker-compose`, which is able to process, index and visualize these
violations. We also added a script to process our XML sitemaps, which helps us
to process our content systematicallly.

## How to use

Execute `docker-compose up` to start the ELK stack.
If you want to run the crawler execute `docker build . -t crawler` in the
crawler directory and run with `docker run crawler`. It will process the
sitemap and request the sitemap's URLs via selenium with chromium in headless state.

Make sure that the `Content-Security-Policy-Report-Only` of the crawled 
website defines an endpoint, that will reach your freshly defined ELK stack
(see below for example config).

### Example config for NGINX

```
# Report CSP violations to the logstash http server
upstream logstash {
    server csp-checker.zeit.de:8080;
}

server {
    # config of your webserver goes here
    add_header Content-Security-Policy "upgrade-insecure-requests;";
    add_header Content-Security-Policy-Report-Only "default-src https: ; report-uri /csp-report";
}
```

## How to deploy with chef

The `chef` directory contains the `zeit-csp-checker` cookbook, which will
install docker and docker compose on the node.


## To Do

- Write logs for every application
- Monitor the application state
- Provide unit tests for the crawler

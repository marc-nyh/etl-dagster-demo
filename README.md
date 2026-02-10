# ETL Demo with DAGster, Postgres, and pgAdmin

This project demonstrates a simple ETL pipeline using:
- DAGster for orchestration
- Postgres as source and target database
- pgAdmin for database inspection

All services are containerized using Docker Compose.



## ⚠️ Corporate Network Workaround

### SSL Verification Disabled in Dockerfile

**Location**: `dagster/Dockerfile`

The `pip install` command uses `--trusted-host` flags to bypass SSL certificate verification:

```dockerfile
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org dagster dagster-webserver psycopg2-binary
```

### Why This Was Necessary

When building Docker images on corporate networks (like SATS Ltd), SSL inspection/proxies intercept HTTPS connections and replace certificates with corporate certificates. This causes pip to fail with:

```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate
```

### Security Implications

⚠️ **This workaround reduces security**:
- ✅ Traffic is still HTTPS encrypted
- ❌ Certificate validation is disabled (vulnerable to man-in-the-middle attacks)
- ⚠️ Acceptable for **local development** in trusted corporate networks
- ❌ **NOT recommended for production**

### Better Alternatives for Production

1. **Install corporate CA certificates** in the Docker image
2. **Use a private PyPI mirror** within the corporate network
3. **Pre-build images** in a secure environment and push to a private Docker registry
4. **Configure Docker Desktop** to use the corporate proxy properly

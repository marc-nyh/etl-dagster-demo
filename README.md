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

## 📁 Accessing Postgres Data Volume (Windows)

The Postgres data is stored in a Docker **Named Volume** called `postgres_data` (this name is not special; it could be named anything you like).

This volume is managed by Docker and lives inside the WSL 2 VM.

### 🔗 Understanding the Linkage

Use this mental model to understand how the data moves:

1.  **Storage on Host (WSL)**: The physical files live on your computer inside the hidden WSL drive.
    *   **Path**: `\\wsl$\docker-desktop-data\data\docker\volumes\etl-dagster-demo_postgres_data\_data`
    *   *Note: Docker automatically prefixes the volume name with your project folder name (`etl-dagster-demo`).*

2.  **The Named Volume**: `postgres_data`
    *   This is just a label or a "pointer" that Docker manages. It points to that messy WSL path above so you don't have to type it.

3.  **Destination inside Container**: `/var/lib/postgresql/data`
    *   This is where the Postgres application *thinks* it is writing data.
    *   When Postgres writes to this folder, Docker effectively "teleports" those writes directly to the **Storage on Host**.

**Access Steps:**

1.  Open File Explorer.
2.  Paste this path into the address bar:
    ```
    \\wsl$\docker-desktop\mnt\docker-desktop-disk\data\docker\volumes
    ```
3.  Navigate to `etl-dagster-demo_postgres_data` > `_data`.

> **⚠️ WARNING**: Do not edit, add, or delete files in this folder while the container is running. Doing so can corrupt your database. Use **pgAdmin** (localhost:5050) to manage data safely.

### 🆚 Named Volume vs. Bind Mount

There are two main ways to persist data in Docker:

1.  **📛 Named Volume** (What we are using, docker decides where to store locally):
    *   **Syntax**: `volumes: - postgres_data:/var/lib/postgresql/data`
    *   **Pro**: Managed by Docker for you. Faster performance on Windows/WSL.
    *   **Con**: Harder to browse files directly (requires the `\\wsl$` trick).
    *   **Best For**: Databases (`postgres_data`), logs, or app data you don't need to touch manually.

2.  **🤝 Bind Mount** (You decide where to store locally):
    *   **Syntax**: `volumes: - ./my_local_folder:/app/data`
    *   **Pro**: Files appear directly in your project folder. Easier to edit.
    *   **Con**: Slower performance on Windows. Permission issues can be tricky.
    *   **Best For**: Code you are actively editing (e.g., your `./dagster` source code).

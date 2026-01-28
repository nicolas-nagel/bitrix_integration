FROM astrocrpublic.azurecr.io/runtime:3.1-11

USER root

RUN set -eux; \
    apt-get update -o Acquire::Retries=5 -o Acquire::ForceIPv4=true; \
    apt-get install -y --no-install-recommends \
        curl ca-certificates gnupg \
        unixodbc unixodbc-dev; \
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
      | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg; \
    . /etc/os-release; \
    curl -fsSL "https://packages.microsoft.com/config/${ID}/${VERSION_ID}/prod.list" \
      -o /etc/apt/sources.list.d/mssql-release.list; \
    apt-get update -o Acquire::Retries=5 -o Acquire::ForceIPv4=true; \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18; \
    rm -rf /var/lib/apt/lists/*

USER astro
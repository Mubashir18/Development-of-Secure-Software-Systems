# Dockerfile
FROM postgres:17

# Install locale for Russian
RUN apt-get update && apt-get install -y locales && \
    localedef -i ru_RU -c -f UTF-8 -A /usr/share/locale/locale.alias ru_RU.UTF-8

# Set environment variables
ENV LANG ru_RU.UTF-8
ENV POSTGRES_INITDB_ARGS "--locale=ru_RU.UTF-8 --encoding=UTF8"
ENV POSTGRES_PASSWORD admin123

# Copy configuration files
COPY postgresql.conf /etc/postgresql/postgresql.conf
COPY init-db.sql /docker-entrypoint-initdb.d/

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD pg_isready -U postgres || exit 1

EXPOSE 5432
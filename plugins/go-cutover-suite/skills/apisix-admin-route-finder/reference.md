# APISIX Admin API Notes

## Official Source

- Official docs: [Admin API](https://apisix.apache.org/zh/docs/apisix/admin-api/)

## Relevant Behaviors

### Route list endpoint

- `GET /apisix/admin/routes`

### Paging

APISIX v3 supports paging on route listing:

- `page`: starts from `1`
- `page_size`: recommended `10-500`

Example from docs:

```bash
curl "http://127.0.0.1:9180/apisix/admin/routes?page=1&page_size=10" \
  -H "X-API-KEY: $admin_key" \
  -X GET
```

### Route list filters

The docs show these list query filters:

- `name`
- `uri`
- `label`

When multiple filters are used together, APISIX intersects them.

Example from docs:

```bash
curl 'http://127.0.0.1:9180/apisix/admin/routes?name=test&uri=foo&label=' \
  -H "X-API-KEY: $admin_key" \
  -X GET
```

### `filter=` limitations

The docs note that route list `filter=` currently supports:

- `service_id`
- `upstream_id`

So for outward-route discovery, use:

1. APISIX server-side narrowing with `uri`, `name`, `label`
2. local ranking for exact route, prefix, suffix, method, host

### Route fields worth checking

- `uri`
- `uris`
- `methods`
- `host`
- `hosts`
- `status`
- `priority`
- `service_id`
- `upstream_id`

## Operational Rules

- Do not store the admin key in files
- Read the admin key from an environment variable at runtime
- Use APISIX only for read-only route discovery in this workflow
- Treat APISIX evidence as gateway evidence, not as frontend-entry evidence by itself

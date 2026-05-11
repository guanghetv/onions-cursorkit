#!/usr/bin/env python3
"""Utilities for comparing route traffic from Volcengine TLS results."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import hmac
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from io import StringIO
from typing import Any, Iterable
from urllib import error as urlerror
from urllib import parse, request


REQUIRED_ENV = (
    "VOLCENGINE_ACCESS_KEY_ID",
    "VOLCENGINE_SECRET_ACCESS_KEY",
    "VOLCENGINE_REGION",
)
OPTIONAL_ENDPOINT_ENV = "VOLCENGINE_ENDPOINT"

PROJECTS = {
    "prod": "prod-vke",
    "stage": "stage-vke",
}

DEFAULT_QUERY = (
    "status:>=200 | SELECT route,method,count(*) pv "
    "GROUP BY route,method ORDER BY pv DESC LIMIT 999"
)

OUTPUT_COLUMNS = ("路由地址", "method", "A服务流量", "B服务流量")
DEFAULT_STRIP_PREFIXES = ("/teacher-school",)
VARIABLE_SEGMENT_PATTERN = re.compile(r"^(:[^/{}]+|\{[^/{}]+\})$")


class ConfigError(RuntimeError):
    """Configuration is missing or invalid."""


class TopicNotFoundError(RuntimeError):
    """TLS topic cannot be resolved."""


class DataShapeError(RuntimeError):
    """TLS query response cannot be normalized."""


@dataclass
class HttpResponse:
    status: int
    body: bytes


@dataclass(frozen=True)
class AssistedRule:
    pattern: str
    replacement: str
    risk: str = ""
    examples: tuple[str, ...] = ()


def validate_credentials(env: dict[str, str] | None = None) -> dict[str, str]:
    """Return required credential values, reporting only missing variable names."""

    source = env if env is not None else os.environ
    missing = [name for name in REQUIRED_ENV if not source.get(name)]
    if missing:
        raise ConfigError("Missing required environment variables: " + ", ".join(missing))
    return {name: source[name] for name in REQUIRED_ENV}


def sanitize_error(error: BaseException | str, secrets: Iterable[str] | None = None) -> str:
    """Remove known secret values from an error string."""

    message = str(error)
    for secret in secrets or ():
        if secret:
            message = message.replace(secret, "[REDACTED]")
    return message


def resolve_project(env: str) -> str:
    key = env.strip().lower()
    if key not in PROJECTS:
        raise ConfigError(f"Unsupported environment: {env}")
    return PROJECTS[key]


def parse_service_identity(value: str) -> tuple[str | None, str]:
    value = value.strip()
    if not value:
        raise ConfigError("Service identity is required")
    if "/" not in value:
        return None, value
    namespace, service = value.split("/", 1)
    namespace = namespace.strip()
    service = service.strip()
    if not namespace or not service:
        raise ConfigError("Service identity must be namespace/service")
    return namespace, service


def parse_time_range(value: str, *, now_ms: int | None = None) -> tuple[int, int]:
    value = value.strip().lower()
    current = now_ms if now_ms is not None else int(time.time() * 1000)
    units = {
        "m": 60 * 1000,
        "h": 60 * 60 * 1000,
        "d": 24 * 60 * 60 * 1000,
    }
    for suffix, multiplier in units.items():
        if value.endswith(suffix):
            amount = int(value[: -len(suffix)])
            return current - amount * multiplier, current
    if "," in value:
        start, end = value.split(",", 1)
        return int(start.strip()), int(end.strip())
    raise ConfigError("Unsupported time range. Use relative values like 15m, 24h, 7d or start_ms,end_ms")


def build_topic_name(namespace: str, service: str) -> str:
    namespace = namespace.strip()
    service = service.strip()
    if not namespace or not service:
        raise ConfigError("Both namespace and service are required")
    return f"{namespace}-{service}"


def default_endpoint(region: str) -> str:
    return f"tls-{region}.volces.com"


def _topic_name(topic: dict[str, Any]) -> str:
    return str(topic.get("topic_name") or topic.get("TopicName") or topic.get("TopicName".lower()) or "")


def _topic_id(topic: dict[str, Any]) -> str:
    return str(topic.get("topic_id") or topic.get("TopicID") or topic.get("topicId") or "")


def _read_value(obj: Any, *names: str) -> Any:
    for name in names:
        getter = f"get_{name}"
        if hasattr(obj, getter):
            return getattr(obj, getter)()
        if hasattr(obj, name):
            return getattr(obj, name)
    if isinstance(obj, dict):
        for name in names:
            if name in obj:
                return obj[name]
    return None


def extract_projects(projects: Iterable[Any]) -> list[dict[str, str]]:
    extracted = []
    for project in projects:
        name = _read_value(project, "project_name", "ProjectName")
        project_id = _read_value(project, "project_id", "ProjectID", "ProjectId", "projectId")
        if name and project_id:
            extracted.append({"project_name": str(name), "project_id": str(project_id)})
    return extracted


def extract_topics(topics: Iterable[Any]) -> list[dict[str, str]]:
    extracted = []
    for topic in topics:
        name = _read_value(topic, "topic_name", "TopicName")
        topic_id = _read_value(topic, "topic_id", "TopicID", "TopicId", "topicId")
        if name and topic_id:
            extracted.append({"topic_name": str(name), "topic_id": str(topic_id)})
    return extracted


def extract_search_rows(response: Any) -> list[dict[str, Any]]:
    analysis_result = _read_value(response, "analysis_result", "AnalysisResult")
    if isinstance(analysis_result, dict) and "Data" in analysis_result:
        return list(analysis_result["Data"])

    analysis = _read_value(response, "analysis", "Analysis")
    if analysis is None:
        analysis = _read_value(response, "logs", "Logs", "results", "Results")
    if analysis is None:
        raise DataShapeError("TLS search response does not contain analysis rows")
    if isinstance(analysis, bool):
        raise DataShapeError("TLS search response does not contain analysis result data")
    if isinstance(analysis, str):
        analysis = json.loads(analysis)
    return list(analysis)


def _describe_topics(
    client: Any,
    project: str,
    **filters: Any,
) -> list[dict[str, Any]]:
    try:
        return client.describe_topics(project, **filters)
    except TypeError:
        return client.describe_topics(project)


def find_topic_candidates(client: Any, *, env: str, service: str) -> list[dict[str, Any]]:
    project = resolve_project(env)
    suffix = f"-{service}"
    topics = _describe_topics(client, project, fuzzy_search_key=service)
    return [topic for topic in topics if _topic_name(topic).endswith(suffix)]


def resolve_topic(client: Any, *, env: str, namespace: str, service: str) -> dict[str, Any]:
    project = resolve_project(env)
    expected = build_topic_name(namespace, service)
    topics = _describe_topics(client, project, topic_name=expected, is_full_name=True)
    for topic in topics:
        if _topic_name(topic) == expected:
            return topic
    raise TopicNotFoundError(f"TLS topic not found in {project}: {expected}")


def normalize_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        missing = [name for name in ("route", "method", "pv") if row.get(name) in (None, "")]
        if missing:
            raise DataShapeError("Missing required TLS result fields: " + ", ".join(missing))
        normalized.append(
            {
                "route": str(row["route"]),
                "method": str(row["method"]).lower(),
                "pv": int(row["pv"]),
            }
        )
    return normalized


def normalize_route(route: str, strip_prefixes: Iterable[str] | None = None) -> str:
    normalized = route.strip() or "/"
    if not normalized.startswith("/"):
        normalized = "/" + normalized

    for prefix in strip_prefixes if strip_prefixes is not None else DEFAULT_STRIP_PREFIXES:
        clean_prefix = "/" + prefix.strip("/")
        if normalized == clean_prefix:
            normalized = "/"
            break
        if normalized.startswith(clean_prefix + "/"):
            normalized = normalized[len(clean_prefix) :]
            break

    parts = normalized.split("/")
    normalized_parts = [
        "{param}" if VARIABLE_SEGMENT_PATTERN.match(part) else part
        for part in parts
    ]
    return "/".join(normalized_parts) or "/"


def route_segments(route: str) -> list[str]:
    normalized = route.strip("/")
    return [] if not normalized else normalized.split("/")


def route_from_segments(segments: list[str]) -> str:
    return "/" + "/".join(segments) if segments else "/"


def build_candidate_report(
    a_rows: Iterable[dict[str, Any]],
    b_rows: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Find conservative literal route groups that may deserve assisted normalization."""

    records: list[dict[str, str]] = []
    for row in normalize_rows(a_rows):
        records.append(
            {
                "raw_route": row["route"],
                "route": normalize_route(row["route"]),
                "method": row["method"],
            }
        )
    for row in normalize_rows(b_rows):
        records.append(
            {
                "raw_route": row["route"],
                "route": normalize_route(row["route"]),
                "method": row["method"],
            }
        )

    groups: dict[tuple[str, tuple[str, ...]], dict[str, Any]] = {}
    for record in records:
        segments = route_segments(record["route"])
        if len(segments) < 3:
            continue
        for index, segment in enumerate(segments):
            if index == 0 or index == len(segments) - 1 or segment == "{param}":
                continue
            candidate_segments = list(segments)
            candidate_segments[index] = "{param}"
            key = (record["method"], tuple(candidate_segments))
            if key not in groups:
                groups[key] = {
                    "candidate_route": route_from_segments(candidate_segments),
                    "method": record["method"],
                    "raw_routes": [],
                    "values": set(),
                }
            group = groups[key]
            if record["raw_route"] not in group["raw_routes"]:
                group["raw_routes"].append(record["raw_route"])
            group["values"].add(segment)

    candidates = []
    for group in groups.values():
        if len(group["raw_routes"]) < 2 or len(group["values"]) < 2:
            continue
        candidates.append(
            {
                "candidate_route": group["candidate_route"],
                "method": group["method"],
                "raw_routes": group["raw_routes"],
                "reason": "same prefix and suffix with one varying literal segment",
                "value_count": len(group["values"]),
            }
        )
    candidates.sort(key=lambda item: (item["method"], item["candidate_route"]))
    return {"candidates": candidates}


def parse_assisted_rules(raw_rules: Iterable[dict[str, Any]] | None) -> list[AssistedRule]:
    parsed: list[AssistedRule] = []
    for rule in raw_rules or []:
        parsed.append(
            AssistedRule(
                pattern=str(rule["pattern"]),
                replacement=str(rule["replacement"]),
                risk=str(rule.get("risk") or ""),
                examples=tuple(str(item) for item in rule.get("examples") or ()),
            )
        )
    return parsed


def apply_assisted_rules(route: str, rules: Iterable[AssistedRule]) -> str:
    route_parts = route_segments(route)
    for rule in rules:
        pattern_parts = route_segments(rule.pattern)
        if len(pattern_parts) != len(route_parts):
            continue
        if all(pattern == "*" or pattern == part for pattern, part in zip(pattern_parts, route_parts)):
            return rule.replacement
    return route


def ensure_non_empty(rows: list[dict[str, Any]], label: str) -> list[dict[str, Any]]:
    if not rows:
        raise DataShapeError(f"No TLS route traffic rows returned for {label}")
    return rows


def compare_traffic(
    a_rows: Iterable[dict[str, Any]],
    b_rows: Iterable[dict[str, Any]],
    *,
    assisted_rules: Iterable[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    a_norm = normalize_rows(a_rows)
    b_norm = normalize_rows(b_rows)
    rules = parse_assisted_rules(assisted_rules)
    order: list[tuple[str, str]] = []
    merged: dict[tuple[str, str], dict[str, Any]] = {}

    def touch(row: dict[str, Any], side: str) -> None:
        route = apply_assisted_rules(normalize_route(row["route"]), rules)
        key = (route, row["method"])
        if key not in merged:
            order.append(key)
            merged[key] = {
                "路由地址": route,
                "method": row["method"],
                "A服务流量": 0,
                "B服务流量": 0,
            }
        merged[key][side] += row["pv"]

    for row in a_norm:
        touch(row, "A服务流量")
    for row in b_norm:
        touch(row, "B服务流量")

    return [merged[key] for key in order]


def resolve_display_names(
    *,
    a_name: str | None = None,
    b_name: str | None = None,
    a_display_name: str | None = None,
    b_display_name: str | None = None,
) -> tuple[str | None, str | None]:
    a_resolved = (a_display_name or a_name or "").strip() or None
    b_resolved = (b_display_name or b_name or "").strip() or None
    return a_resolved, b_resolved


def output_columns_for(
    *,
    a_name: str | None = None,
    b_name: str | None = None,
    a_display_name: str | None = None,
    b_display_name: str | None = None,
) -> list[str]:
    a_resolved, b_resolved = resolve_display_names(
        a_name=a_name,
        b_name=b_name,
        a_display_name=a_display_name,
        b_display_name=b_display_name,
    )
    if not a_resolved or not b_resolved:
        return list(OUTPUT_COLUMNS)
    return [
        "路由地址",
        "method",
        f"{a_resolved}流量",
        f"{b_resolved}流量",
        f"{a_resolved}有流量",
        f"{b_resolved}有流量",
    ]


def render_output_rows(
    rows: list[dict[str, Any]],
    *,
    a_name: str | None = None,
    b_name: str | None = None,
    a_display_name: str | None = None,
    b_display_name: str | None = None,
) -> list[dict[str, Any]]:
    a_resolved, b_resolved = resolve_display_names(
        a_name=a_name,
        b_name=b_name,
        a_display_name=a_display_name,
        b_display_name=b_display_name,
    )
    if not a_resolved or not b_resolved:
        return rows

    rendered = []
    a_traffic_key = f"{a_resolved}流量"
    b_traffic_key = f"{b_resolved}流量"
    a_has_traffic_key = f"{a_resolved}有流量"
    b_has_traffic_key = f"{b_resolved}有流量"
    for row in rows:
        a_traffic = int(row["A服务流量"])
        b_traffic = int(row["B服务流量"])
        rendered.append(
            {
                "路由地址": row["路由地址"],
                "method": row["method"],
                a_traffic_key: a_traffic,
                b_traffic_key: b_traffic,
                a_has_traffic_key: a_traffic > 0,
                b_has_traffic_key: b_traffic > 0,
            }
        )
    return rendered


def build_compare_output(
    rows: list[dict[str, Any]],
    *,
    limit: int = 10,
    a_name: str | None = None,
    b_name: str | None = None,
    a_display_name: str | None = None,
    b_display_name: str | None = None,
) -> dict[str, Any]:
    rendered = render_output_rows(
        rows,
        a_name=a_name,
        b_name=b_name,
        a_display_name=a_display_name,
        b_display_name=b_display_name,
    )
    return build_preview(rendered, limit=limit)


def build_preview(rows: list[dict[str, Any]], *, limit: int = 10) -> dict[str, Any]:
    return {
        "total": len(rows),
        "rows": rows[:limit],
    }


def csv_value(value: Any) -> Any:
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


def to_csv(rows: list[dict[str, Any]], *, columns: Iterable[str] | None = None) -> str:
    fieldnames = list(columns) if columns is not None else list(OUTPUT_COLUMNS)
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(
        [
            {fieldname: csv_value(row.get(fieldname)) for fieldname in fieldnames}
            for row in rows
        ]
    )
    return output.getvalue()


def read_json_file(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_text(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(content)


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _hash_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _hmac_sha256(key: bytes, content: str) -> bytes:
    return hmac.new(key, content.encode("utf-8"), hashlib.sha256).digest()


def canonical_query(params: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in sorted(params):
        value = params[key]
        values = value if isinstance(value, list) else [value]
        for item in values:
            parts.append(
                parse.quote(str(key), safe="-_.~") + "=" + parse.quote(str(item), safe="-_.~")
            )
    return "&".join(parts).replace("+", "%20")


def sign_request(
    *,
    method: str,
    host: str,
    path: str,
    query: dict[str, Any],
    body: str,
    access_key_id: str,
    secret_access_key: str,
    region: str,
    request_datetime: dt.datetime | None = None,
    api_version: str = "0.3.0",
) -> dict[str, str]:
    request_time = request_datetime or utc_now()
    x_date = request_time.astimezone(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    short_date = x_date[:8]
    body_hash = _hash_sha256(body)

    signed_headers = {
        "content-type": "application/json",
        "host": host,
        "x-content-sha256": body_hash,
        "x-date": x_date,
        "x-tls-apiversion": api_version,
    }
    signed_headers_str = ";".join(sorted(signed_headers))
    canonical_headers = "".join(f"{name}:{signed_headers[name]}\n" for name in sorted(signed_headers))
    canonical_request = "\n".join(
        [
            method.upper(),
            parse.quote(path or "/", safe="/-_.~"),
            canonical_query(query),
            canonical_headers,
            signed_headers_str,
            body_hash,
        ]
    )
    credential_scope = "/".join([short_date, region, "TLS", "request"])
    string_to_sign = "\n".join(
        ["HMAC-SHA256", x_date, credential_scope, _hash_sha256(canonical_request)]
    )

    signing_key = _hmac_sha256(secret_access_key.encode("utf-8"), short_date)
    signing_key = _hmac_sha256(signing_key, region)
    signing_key = _hmac_sha256(signing_key, "TLS")
    signing_key = _hmac_sha256(signing_key, "request")
    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    return {
        "Content-Type": signed_headers["content-type"],
        "Host": signed_headers["host"],
        "X-Content-Sha256": body_hash,
        "X-Date": x_date,
        "x-tls-apiversion": api_version,
        "Authorization": (
            "HMAC-SHA256 "
            f"Credential={access_key_id}/{credential_scope}, "
            f"SignedHeaders={signed_headers_str}, "
            f"Signature={signature}"
        ),
    }


def json_body(payload: dict[str, Any] | None) -> str:
    if not payload:
        return ""
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _default_opener(http_request: request.Request, timeout: int) -> HttpResponse:
    try:
        with request.urlopen(http_request, timeout=timeout) as response:
            return HttpResponse(status=response.status, body=response.read())
    except urlerror.HTTPError as exc:
        raise ConfigError(exc.read().decode("utf-8", errors="replace") or str(exc)) from exc
    except urlerror.URLError as exc:
        raise ConfigError(str(exc.reason)) from exc


@dataclass
class VolcengineTlsClient:
    """Minimal Volcengine TLS HTTP client using standard-library SigV4 signing."""

    access_key_id: str
    secret_access_key: str
    region: str
    endpoint: str = ""
    opener: Any = _default_opener
    timeout: int = 60
    api_version: str = "0.3.0"

    def __post_init__(self) -> None:
        if self.endpoint.startswith("https://"):
            self.endpoint = self.endpoint[len("https://") :]
        elif self.endpoint.startswith("http://"):
            self.endpoint = self.endpoint[len("http://") :]

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "VolcengineTlsClient":
        credentials = validate_credentials(env)
        source = env if env is not None else os.environ
        return cls(
            access_key_id=credentials["VOLCENGINE_ACCESS_KEY_ID"],
            secret_access_key=credentials["VOLCENGINE_SECRET_ACCESS_KEY"],
            region=credentials["VOLCENGINE_REGION"],
            endpoint=source.get(OPTIONAL_ENDPOINT_ENV) or default_endpoint(credentials["VOLCENGINE_REGION"]),
        )

    def _request_json(
        self,
        *,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        query = {key: value for key, value in (params or {}).items() if value is not None}
        body = json_body(payload)
        headers = sign_request(
            method=method,
            host=self.endpoint,
            path=path,
            query=query,
            body=body,
            access_key_id=self.access_key_id,
            secret_access_key=self.secret_access_key,
            region=self.region,
            api_version=self.api_version,
        )
        url = f"https://{self.endpoint}{path}"
        encoded_query = canonical_query(query)
        if encoded_query:
            url = f"{url}?{encoded_query}"
        http_request = request.Request(
            url,
            data=body.encode("utf-8"),
            headers=headers,
            method=method.upper(),
        )
        response = self.opener(http_request, self.timeout)
        if response.status < 200 or response.status >= 300:
            raise ConfigError(f"TLS API returned HTTP {response.status}")
        if not response.body:
            return {}
        return json.loads(response.body.decode("utf-8"))

    def describe_projects(self) -> list[dict[str, str]]:
        response = self._request_json(
            method="GET",
            path="/DescribeProjects",
            params={"PageNumber": 1, "PageSize": 100},
        )
        return extract_projects(response.get("Projects") or response.get("projects") or [])

    def _resolve_project_id(self, project_name: str) -> str:
        projects = self.describe_projects()
        for project in projects:
            if project["project_name"] == project_name:
                return project["project_id"]
        raise TopicNotFoundError(f"TLS project not found: {project_name}")

    def describe_topics(
        self,
        project_name: str,
        *,
        topic_name: str | None = None,
        is_full_name: bool | None = None,
        fuzzy_search_key: str | None = None,
    ) -> list[dict[str, Any]]:
        project_id = self._resolve_project_id(project_name)
        response = self._request_json(
            method="GET",
            path="/DescribeTopics",
            params={
                "ProjectId": project_id,
                "ProjectName": project_name,
                "TopicName": topic_name,
                "IsFullName": is_full_name,
                "FuzzySearchKey": fuzzy_search_key,
                "PageNumber": 1,
                "PageSize": 100,
            },
        )
        return extract_topics(response.get("Topics") or response.get("topics") or [])

    def search_logs(self, topic_id: str, query: str, start_time: int, end_time: int, limit: int = 1000) -> list[dict[str, Any]]:
        response = self._request_json(
            method="POST",
            path="/SearchLogs",
            payload={
                "TopicId": topic_id,
                "Query": query,
                "StartTime": start_time,
                "EndTime": end_time,
                "Limit": limit,
                "Sort": "desc",
            },
        )
        rows = [
            row
            for row in extract_search_rows(response)
            if row.get("route") not in (None, "") and row.get("method") not in (None, "")
        ]
        return ensure_non_empty(normalize_rows(rows), topic_id)


def command_compare(args: argparse.Namespace) -> int:
    a_rows = read_json_file(args.a)
    b_rows = read_json_file(args.b)
    if args.candidate_report:
        report = build_candidate_report(a_rows, b_rows)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    assisted_rules = read_json_file(args.assisted_rules) if args.assisted_rules else None
    compared = compare_traffic(a_rows, b_rows, assisted_rules=assisted_rules)
    rendered = render_output_rows(
        compared,
        a_name=args.a_name,
        b_name=args.b_name,
        a_display_name=args.a_display_name,
        b_display_name=args.b_display_name,
    )
    columns = output_columns_for(
        a_name=args.a_name,
        b_name=args.b_name,
        a_display_name=args.a_display_name,
        b_display_name=args.b_display_name,
    )
    if args.csv:
        content = to_csv(rendered, columns=columns)
        if args.output:
            write_text(args.output, content)
        else:
            print(content, end="")
    else:
        print(json.dumps(build_preview(rendered, limit=args.limit), ensure_ascii=False, indent=2))
    return 0


def command_discover_topic(args: argparse.Namespace) -> int:
    namespace, service = parse_service_identity(args.service)
    client = VolcengineTlsClient.from_env()
    if namespace:
        topic = resolve_topic(client, env=args.env, namespace=namespace, service=service)
        print(json.dumps(topic, ensure_ascii=False))
        return 0

    candidates = find_topic_candidates(client, env=args.env, service=service)
    print(json.dumps({"candidates": candidates, "requires_confirmation": True}, ensure_ascii=False))
    return 0


def command_query(args: argparse.Namespace) -> int:
    start_ms, end_ms = parse_time_range(args.time_range)
    client = VolcengineTlsClient.from_env()
    rows = client.search_logs(
        topic_id=args.topic_id,
        query=args.query,
        start_time=start_ms,
        end_time=end_ms,
        limit=args.limit,
    )
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


def command_validate_env(_: argparse.Namespace) -> int:
    validate_credentials()
    print(json.dumps({"ok": True, "checked": list(REQUIRED_ENV)}, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare route traffic from Volcengine TLS query results")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-env", help="Validate required environment variables without printing values")
    validate.set_defaults(func=command_validate_env)

    discover = subparsers.add_parser("discover-topic", help="Resolve TLS topic for env and namespace/service")
    discover.add_argument("--env", required=True, help="Environment, such as prod or stage")
    discover.add_argument("--service", required=True, help="Service identity: namespace/service or service")
    discover.set_defaults(func=command_discover_topic)

    query = subparsers.add_parser("query", help="Query route traffic from a TLS topic")
    query.add_argument("--topic-id", required=True, help="TLS topic ID")
    query.add_argument("--time-range", required=True, help="Relative range like 15m/24h or start_ms,end_ms")
    query.add_argument("--query", default=DEFAULT_QUERY, help="TLS query string")
    query.add_argument("--limit", type=int, default=1000, help="Query result limit")
    query.set_defaults(func=command_query)

    compare = subparsers.add_parser("compare", help="Compare two normalized TLS query result JSON files")
    compare.add_argument("--a", required=True, help="A service normalized JSON rows")
    compare.add_argument("--b", required=True, help="B service normalized JSON rows")
    compare.add_argument("--limit", type=int, default=10, help="Preview row limit")
    compare.add_argument("--csv", action="store_true", help="Write CSV instead of JSON preview")
    compare.add_argument("--output", help="Output file path")
    compare.add_argument("--candidate-report", action="store_true", help="Emit assisted normalization candidate report JSON")
    compare.add_argument("--assisted-rules", help="JSON file with explicit assisted normalization rules")
    compare.add_argument("--a-name", help="A service identity used for output columns")
    compare.add_argument("--b-name", help="B service identity used for output columns")
    compare.add_argument("--a-display-name", help="A service display name used for output columns")
    compare.add_argument("--b-display-name", help="B service display name used for output columns")
    compare.set_defaults(func=command_compare)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:  # noqa: BLE001 - CLI must sanitize before display.
        secrets = [os.environ.get(name, "") for name in REQUIRED_ENV]
        print(sanitize_error(exc, secrets), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

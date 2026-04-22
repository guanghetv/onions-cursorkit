#!/usr/bin/env python3
import argparse
import json
import os
import re
import ssl
import sys
import urllib.parse
import urllib.request
from typing import Dict, Iterable, List, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query APISIX Admin API routes with paging and local ranking."
    )
    parser.add_argument("--admin-url", required=True, help="APISIX admin routes URL")
    parser.add_argument(
        "--source-name",
        default="",
        help="Optional gateway source label, e.g. apisix-school-test",
    )
    parser.add_argument(
        "--key-env",
        default="APISIX_ADMIN_KEY",
        help="Environment variable name that stores the APISIX X-API-KEY",
    )
    parser.add_argument(
        "--old-route",
        default="",
        help="Original internal or old outward route used to derive search seeds",
    )
    parser.add_argument(
        "--new-route",
        default="",
        help="New route used to derive search seeds",
    )
    parser.add_argument("--method", default="", help="HTTP method to match, e.g. GET")
    parser.add_argument(
        "--route",
        action="append",
        default=[],
        help="Exact outward route candidate, can be repeated",
    )
    parser.add_argument(
        "--uri-prefix",
        action="append",
        default=[],
        help="URI prefix candidate, can be repeated",
    )
    parser.add_argument(
        "--uri-fragment",
        action="append",
        default=[],
        help="URI fragment used for APISIX server-side filtering, can be repeated",
    )
    parser.add_argument(
        "--same-suffix",
        action="append",
        default=[],
        help="Stable route suffix for speculative matching, can be repeated",
    )
    parser.add_argument(
        "--name-hint",
        action="append",
        default=[],
        help="Route name hint for APISIX server-side filtering, can be repeated",
    )
    parser.add_argument(
        "--label-hint",
        action="append",
        default=[],
        help="Route label hint for APISIX server-side filtering, can be repeated",
    )
    parser.add_argument(
        "--host-hint",
        action="append",
        default=[],
        help="Host hint for local ranking, can be repeated",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=100,
        help="APISIX page size, recommended range is 10-500",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=20,
        help="Maximum pages per query plan to avoid unbounded scans",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="HTTP timeout in seconds",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print derived seeds and query plans without calling APISIX",
    )
    return parser.parse_args()


def unique_strings(values: Iterable[str]) -> List[str]:
    seen = set()
    ordered = []
    for value in values:
        value = value.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def normalize_path(path: str) -> str:
    path = path.strip()
    if not path:
        return path
    if not path.startswith("/"):
        path = "/" + path
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]
    return path


def normalize_admin_url(url: str) -> str:
    return url.rstrip("/")


def default_source_name(admin_url: str) -> str:
    parsed = urllib.parse.urlparse(admin_url)
    if parsed.netloc:
        return parsed.netloc
    return normalize_admin_url(admin_url)


def split_segments(path: str) -> List[str]:
    normalized = normalize_path(path)
    if not normalized or normalized == "/":
        return []
    return [segment for segment in normalized.strip("/").split("/") if segment]


def is_param_segment(segment: str) -> bool:
    if not segment:
        return False
    if segment in {"*", "**"}:
        return True
    if segment.startswith(":"):
        return True
    if segment.startswith("{") and segment.endswith("}"):
        return True
    if "${" in segment and "}" in segment:
        return True
    if re.fullmatch(r"\{[^{}]+\}", segment):
        return True
    return False


def normalize_segment(segment: str) -> str:
    if is_param_segment(segment):
        return "{param}"
    return segment


def join_segments(segments: List[str]) -> str:
    if not segments:
        return ""
    return "/" + "/".join(segments)


def normalize_shape(path: str) -> str:
    return join_segments([normalize_segment(segment) for segment in split_segments(path)])


def stable_static_prefix(path: str) -> str:
    segments = split_segments(path)
    static_segments = []
    for segment in segments:
        if is_param_segment(segment):
            break
        static_segments.append(segment)
    if len(static_segments) < 2:
        return ""
    return join_segments(static_segments)


def parent_static_prefix(path: str) -> str:
    segments = split_segments(path)
    if len(segments) < 2:
        return ""
    normalized_segments = [normalize_segment(segment) for segment in segments]
    if len(normalized_segments) >= 2 and normalized_segments[-2] == "{param}":
        parent = segments[:-2]
    else:
        parent = segments[:-1]
    if len(parent) < 2:
        return ""
    return join_segments(parent)


def common_suffix_path(left: str, right: str) -> str:
    left_segments = [normalize_segment(segment) for segment in split_segments(left)]
    right_segments = [normalize_segment(segment) for segment in split_segments(right)]
    suffix = []
    i = 1
    while i <= len(left_segments) and i <= len(right_segments):
        if left_segments[-i] != right_segments[-i]:
            break
        suffix.insert(0, left_segments[-i])
        i += 1
    if len(suffix) < 2:
        return ""
    return join_segments(suffix)


def tail_windows(path: str, min_size: int = 2, max_size: int = 4) -> List[str]:
    segments = [normalize_segment(segment) for segment in split_segments(path)]
    windows: List[str] = []
    for size in range(min_size, max_size + 1):
        if len(segments) >= size:
            window = segments[-size:]
            if window[0] == "{param}":
                continue
            if any(segment != "{param}" for segment in window):
                windows.append(join_segments(window))
    return unique_strings(windows)


def route_fragments(paths: Iterable[str]) -> List[str]:
    fragments: List[str] = []
    for path in paths:
        for segment in split_segments(path):
            normalized = normalize_segment(segment)
            if normalized == "{param}":
                continue
            if len(normalized) < 3:
                continue
            fragments.append(normalized)
    return unique_strings(fragments)[:8]


def derive_seed_context(args: argparse.Namespace) -> Dict[str, List[str]]:
    base_routes = unique_strings(
        [normalize_path(value) for value in [args.old_route, args.new_route] + args.route]
    )
    normalized_shapes = unique_strings(
        [
            value
            for value in [normalize_shape(args.old_route), normalize_shape(args.new_route)]
            if value
        ]
    )

    prefixes = unique_strings(args.uri_prefix)
    for path in base_routes + normalized_shapes:
        for candidate in [stable_static_prefix(path), parent_static_prefix(path)]:
            if candidate:
                prefixes.append(candidate)

    suffixes = unique_strings(args.same_suffix)
    shared_suffix = common_suffix_path(args.old_route, args.new_route)
    if shared_suffix:
        suffixes.append(shared_suffix)
    for path in unique_strings(
        [args.old_route, args.new_route, normalize_shape(args.old_route), normalize_shape(args.new_route)]
    ):
        suffixes.extend(tail_windows(path))

    fragments = unique_strings(args.uri_fragment)
    fragments.extend(route_fragments(base_routes))
    fragments.extend(route_fragments(normalized_shapes))

    effective_routes = unique_strings(base_routes + normalized_shapes)
    effective_prefixes = [normalize_path(value) for value in unique_strings(prefixes)]
    effective_suffixes = [normalize_path(value) for value in unique_strings(suffixes)]

    return {
        "route": effective_routes,
        "uriPrefix": effective_prefixes,
        "uriFragment": unique_strings(fragments),
        "sameSuffix": effective_suffixes,
        "nameHint": unique_strings(args.name_hint),
        "labelHint": unique_strings(args.label_hint),
        "hostHint": unique_strings(args.host_hint),
        "derivedFrom": unique_strings(
            [normalize_path(args.old_route), normalize_path(args.new_route)]
        ),
    }


def request_json(
    admin_url: str, api_key: str, query: Dict[str, str], timeout: int
) -> Dict:
    query_string = urllib.parse.urlencode(query)
    url = admin_url if not query_string else f"{admin_url}?{query_string}"
    req = urllib.request.Request(
        url,
        headers={"X-API-KEY": api_key, "Accept": "application/json"},
        method="GET",
    )
    with urllib.request.urlopen(
        req, timeout=timeout, context=ssl.create_default_context()
    ) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)


def route_paths(route_value: Dict) -> List[str]:
    paths = []
    uri = route_value.get("uri")
    if isinstance(uri, str) and uri:
        paths.append(uri)
    uris = route_value.get("uris")
    if isinstance(uris, list):
        for item in uris:
            if isinstance(item, str) and item:
                paths.append(item)
    return unique_strings(paths)


def route_hosts(route_value: Dict) -> List[str]:
    hosts = []
    host = route_value.get("host")
    if isinstance(host, str) and host:
        hosts.append(host)
    host_list = route_value.get("hosts")
    if isinstance(host_list, list):
        for item in host_list:
            if isinstance(item, str) and item:
                hosts.append(item)
    return unique_strings(hosts)


def route_methods(route_value: Dict) -> List[str]:
    methods = route_value.get("methods")
    if not isinstance(methods, list):
        return []
    return unique_strings(
        method.upper() for method in methods if isinstance(method, str) and method
    )


def wildcard_prefix_match(route_path: str, prefix: str) -> bool:
    if route_path.endswith("*"):
        return prefix.startswith(route_path[:-1])
    return route_path.startswith(prefix)


def build_query_plans(seed_context: Dict[str, List[str]]) -> List[Dict[str, str]]:
    plans = []
    for fragment in seed_context["uriFragment"]:
        plans.append({"uri": fragment})
    for name in seed_context["nameHint"]:
        plans.append({"name": name})
    for label in seed_context["labelHint"]:
        plans.append({"label": label})
    if not plans:
        plans.append({})
    return plans


def paginate_routes(
    args: argparse.Namespace, api_key: str, seed_context: Dict[str, List[str]]
) -> Tuple[Dict[str, Dict], List[Dict]]:
    route_map: Dict[str, Dict] = {}
    executed_plans: List[Dict] = []
    admin_url = normalize_admin_url(args.admin_url)

    for plan in build_query_plans(seed_context):
        plan_record = {"query": plan, "pages": 0, "itemsSeen": 0}
        executed_plans.append(plan_record)
        for page in range(1, args.max_pages + 1):
            query = dict(plan)
            query["page"] = str(page)
            query["page_size"] = str(args.page_size)
            payload = request_json(admin_url, api_key, query, args.timeout)
            items = payload.get("list") or []
            total = payload.get("total")
            plan_record["pages"] = page
            plan_record["itemsSeen"] += len(items)

            for item in items:
                if not isinstance(item, dict):
                    continue
                value = item.get("value") or {}
                route_id = str(value.get("id") or item.get("key") or "")
                if not route_id:
                    continue
                existing = route_map.setdefault(
                    route_id,
                    {
                        "item": item,
                        "value": value,
                        "plans": [],
                    },
                )
                existing["plans"].append(plan)

            if not items:
                break
            if isinstance(total, int) and page * args.page_size >= total:
                break
    return route_map, executed_plans


def score_route(
    route_value: Dict, args: argparse.Namespace, seed_context: Dict[str, List[str]]
) -> Tuple[int, str, List[str]]:
    score = 0
    reasons: List[str] = []
    match_level = "speculative"
    paths = route_paths(route_value)
    methods = route_methods(route_value)
    hosts = route_hosts(route_value)
    target_method = args.method.upper().strip()

    exact_routes = seed_context["route"]
    prefixes = seed_context["uriPrefix"]
    suffixes = seed_context["sameSuffix"]
    host_hints = seed_context["hostHint"]

    for path in paths:
        normalized = normalize_path(path)
        if normalized in exact_routes:
            score += 120
            reasons.append(f"精确路由匹配: {normalized}")
            match_level = "confirmed"
        for prefix in prefixes:
            if wildcard_prefix_match(normalized, prefix) or normalized.startswith(prefix):
                score += 90
                reasons.append(f"路由前缀匹配: {prefix}")
                if match_level != "confirmed":
                    match_level = "confirmed"
        for suffix in suffixes:
            if normalized.endswith(suffix):
                score += 55
                reasons.append(f"相同后缀匹配: {suffix}")
        for fragment in seed_context["uriFragment"]:
            if fragment and fragment in normalized:
                score += 25
                reasons.append(f"路由片段命中: {fragment}")

    if target_method:
        if not methods:
            score += 10
            reasons.append("路由未限制 methods，视为兼容目标方法")
        elif target_method in methods:
            score += 20
            reasons.append(f"方法匹配: {target_method}")
        else:
            score -= 80
            reasons.append(f"方法不匹配: 目标 {target_method}，路由 {methods}")

    if route_value.get("status", 1) == 1:
        score += 5
        reasons.append("路由已启用")
    else:
        score -= 20
        reasons.append("路由已禁用")

    for host in hosts:
        for hint in host_hints:
            if hint and hint in host:
                score += 15
                reasons.append(f"Host 命中线索: {hint}")

    if score >= 120 and match_level == "confirmed":
        confidence = "confirmed"
    elif score >= 60:
        confidence = "probable"
    else:
        confidence = "speculative"

    return score, confidence, unique_strings(reasons)


def main() -> int:
    args = parse_args()
    seed_context = derive_seed_context(args)
    query_plans = build_query_plans(seed_context)

    if args.dry_run:
        print(
            json.dumps(
                {
                    "adminUrl": normalize_admin_url(args.admin_url),
                    "sourceName": args.source_name or default_source_name(args.admin_url),
                    "keyEnv": args.key_env,
                    "method": args.method.upper().strip(),
                    "manualInputs": {
                        "oldRoute": normalize_path(args.old_route),
                        "newRoute": normalize_path(args.new_route),
                        "route": unique_strings(args.route),
                        "uriPrefix": unique_strings(args.uri_prefix),
                        "uriFragment": unique_strings(args.uri_fragment),
                        "sameSuffix": unique_strings(args.same_suffix),
                        "nameHint": unique_strings(args.name_hint),
                        "labelHint": unique_strings(args.label_hint),
                        "hostHint": unique_strings(args.host_hint),
                    },
                    "querySeeds": seed_context,
                    "plans": query_plans,
                    "dryRun": True,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    api_key = os.environ.get(args.key_env, "").strip()
    if not api_key:
        print(
            json.dumps(
                {
                    "error": f"missing api key in env var: {args.key_env}",
                    "sourceName": args.source_name or default_source_name(args.admin_url),
                    "keyEnv": args.key_env,
                },
                ensure_ascii=False,
            )
        )
        return 1

    try:
        route_map, executed_plans = paginate_routes(args, api_key, seed_context)
    except Exception as exc:  # noqa: BLE001
        print(
            json.dumps(
                {
                    "error": str(exc),
                    "adminUrl": normalize_admin_url(args.admin_url),
                    "sourceName": args.source_name or default_source_name(args.admin_url),
                    "keyEnv": args.key_env,
                },
                ensure_ascii=False,
            )
        )
        return 2

    ranked = []
    for route_id, payload in route_map.items():
        route_value = payload["value"]
        score, confidence, reasons = score_route(route_value, args, seed_context)
        if score <= 0:
            continue
        ranked.append(
            {
                "id": route_id,
                "key": payload["item"].get("key"),
                "name": route_value.get("name", ""),
                "desc": route_value.get("desc", ""),
                "status": route_value.get("status", 1),
                "methods": route_methods(route_value),
                "uri": route_value.get("uri"),
                "uris": route_value.get("uris", []),
                "host": route_value.get("host"),
                "hosts": route_hosts(route_value),
                "service_id": route_value.get("service_id"),
                "upstream_id": route_value.get("upstream_id"),
                "priority": route_value.get("priority", 0),
                "score": score,
                "confidence": confidence,
                "matchedBy": reasons,
                "matchedPlans": payload["plans"],
            }
        )

    ranked.sort(key=lambda item: (-item["score"], item["id"]))

    print(
        json.dumps(
            {
                "adminUrl": normalize_admin_url(args.admin_url),
                "sourceName": args.source_name or default_source_name(args.admin_url),
                "keyEnv": args.key_env,
                "method": args.method.upper().strip(),
                "manualInputs": {
                    "oldRoute": normalize_path(args.old_route),
                    "newRoute": normalize_path(args.new_route),
                    "route": unique_strings(args.route),
                    "uriPrefix": unique_strings(args.uri_prefix),
                    "uriFragment": unique_strings(args.uri_fragment),
                    "sameSuffix": unique_strings(args.same_suffix),
                    "nameHint": unique_strings(args.name_hint),
                    "labelHint": unique_strings(args.label_hint),
                    "hostHint": unique_strings(args.host_hint),
                },
                "querySeeds": seed_context,
                "plans": executed_plans,
                "items": ranked,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

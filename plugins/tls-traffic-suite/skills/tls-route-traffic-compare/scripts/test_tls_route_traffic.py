import csv
import io
import os
import unittest
from datetime import datetime, timezone

import tls_route_traffic as tls


class FakeProject:
    def __init__(self, name, project_id):
        self.name = name
        self.project_id = project_id

    def get_project_name(self):
        return self.name

    def get_project_id(self):
        return self.project_id


class FakeTopic:
    def __init__(self, name, topic_id):
        self.name = name
        self.topic_id = topic_id

    def get_topic_name(self):
        return self.name

    def get_topic_id(self):
        return self.topic_id


class FakeSearchResponse:
    def __init__(self):
        self.analysis = [
            {"route": "/a", "method": "GET", "pv": "2"},
            {"route": "/b", "method": "post", "pv": 3},
        ]


class FakeTopicClient:
    def __init__(self, topics):
        self.topics = topics
        self.calls = []

    def describe_topics(self, project_name, **filters):
        self.calls.append((project_name, filters))
        return self.topics.get(project_name, [])


class TlsRouteTrafficTest(unittest.TestCase):
    def test_validate_credentials_reports_missing_names_without_values(self):
        env = {
            "VOLCENGINE_ACCESS_KEY_ID": "ak-secret",
            "VOLCENGINE_REGION": "cn-beijing",
        }

        with self.assertRaises(tls.ConfigError) as ctx:
            tls.validate_credentials(env)

        message = str(ctx.exception)
        self.assertIn("VOLCENGINE_SECRET_ACCESS_KEY", message)
        self.assertNotIn("ak-secret", message)

    def test_resolve_project_maps_supported_environment(self):
        self.assertEqual(tls.resolve_project("prod"), "prod-vke")
        self.assertEqual(tls.resolve_project("stage"), "stage-vke")

    def test_default_query_limits_result_count(self):
        self.assertIn("LIMIT 999", tls.DEFAULT_QUERY)

    def test_default_endpoint_uses_public_volces_domain(self):
        self.assertEqual(tls.default_endpoint("cn-beijing"), "tls-cn-beijing.volces.com")

    def test_parse_service_identity_splits_namespace_and_service(self):
        self.assertEqual(
            tls.parse_service_identity("teacherschool/teacher-school"),
            ("teacherschool", "teacher-school"),
        )

    def test_parse_service_identity_allows_service_only(self):
        self.assertEqual(tls.parse_service_identity("teacher-school"), (None, "teacher-school"))

    def test_parse_relative_time_range_returns_milliseconds(self):
        now_ms = 1_700_000_000_000

        start_ms, end_ms = tls.parse_time_range("15m", now_ms=now_ms)

        self.assertEqual(start_ms, now_ms - 15 * 60 * 1000)
        self.assertEqual(end_ms, now_ms)

    def test_resolve_topic_exact_namespace_service(self):
        client = FakeTopicClient(
            {
                "prod-vke": [
                    {"topic_name": "teacherschool-teacher-school", "topic_id": "topic-1"},
                    {"topic_name": "other-teacher-school", "topic_id": "topic-2"},
                ]
            }
        )

        topic = tls.resolve_topic(
            client,
            env="prod",
            namespace="teacherschool",
            service="teacher-school",
        )

        self.assertEqual(topic["topic_id"], "topic-1")
        self.assertEqual(
            client.calls[-1],
            ("prod-vke", {"topic_name": "teacherschool-teacher-school", "is_full_name": True}),
        )

    def test_project_response_objects_are_extracted(self):
        projects = tls.extract_projects([FakeProject("prod-vke", "project-1")])

        self.assertEqual(projects, [{"project_name": "prod-vke", "project_id": "project-1"}])

    def test_topic_response_objects_are_extracted(self):
        topics = tls.extract_topics([FakeTopic("teacherschool-teacher-school", "topic-1")])

        self.assertEqual(
            topics,
            [{"topic_name": "teacherschool-teacher-school", "topic_id": "topic-1"}],
        )

    def test_search_response_analysis_rows_are_extracted(self):
        rows = tls.extract_search_rows(FakeSearchResponse())

        self.assertEqual(
            rows,
            [
                {"route": "/a", "method": "GET", "pv": "2"},
                {"route": "/b", "method": "post", "pv": 3},
            ],
        )

    def test_search_response_analysis_result_data_rows_are_extracted(self):
        rows = tls.extract_search_rows(
            {
                "Analysis": True,
                "AnalysisResult": {
                    "Schema": ["route", "method", "pv"],
                    "Data": [{"route": "/a", "method": "GET", "pv": "2"}],
                },
            }
        )

        self.assertEqual(rows, [{"route": "/a", "method": "GET", "pv": "2"}])

    def test_canonical_query_sorts_and_escapes_values(self):
        query = tls.canonical_query({"b": "hello world", "a": ["2", "1"]})

        self.assertEqual(query, "a=2&a=1&b=hello%20world")

    def test_sign_request_adds_volcengine_sigv4_headers_without_secret(self):
        signed = tls.sign_request(
            method="POST",
            host="tls-cn-beijing.ivolces.com",
            path="/SearchLogs",
            query={},
            body='{"TopicId":"topic-1"}',
            access_key_id="ak-example",
            secret_access_key="sk-secret",
            region="cn-beijing",
            request_datetime=datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
        )

        self.assertEqual(signed["X-Date"], "20240102T030405Z")
        self.assertEqual(signed["Content-Type"], "application/json")
        self.assertEqual(signed["Host"], "tls-cn-beijing.ivolces.com")
        self.assertEqual(len(signed["X-Content-Sha256"]), 64)
        self.assertIn("Credential=ak-example/20240102/cn-beijing/TLS/request", signed["Authorization"])
        self.assertIn("SignedHeaders=content-type;host;x-content-sha256;x-date;x-tls-apiversion", signed["Authorization"])
        self.assertNotIn("sk-secret", signed["Authorization"])

    def test_http_client_uses_tls_paths_and_json_bodies(self):
        captured = []

        def opener(request, timeout):
            captured.append(request)
            return tls.HttpResponse(status=200, body=b'{"Projects":[{"ProjectName":"prod-vke","ProjectId":"project-1"}]}')

        client = tls.VolcengineTlsClient(
            access_key_id="ak-example",
            secret_access_key="sk-secret",
            region="cn-beijing",
            endpoint="tls-cn-beijing.ivolces.com",
            opener=opener,
        )

        projects = client.describe_projects()

        self.assertEqual(projects, [{"project_name": "prod-vke", "project_id": "project-1"}])
        request = captured[0]
        self.assertEqual(
            request.full_url,
            "https://tls-cn-beijing.ivolces.com/DescribeProjects?PageNumber=1&PageSize=100",
        )
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(request.data, b"")
        self.assertIn("Authorization", dict(request.header_items()))

    def test_search_logs_posts_expected_json_body(self):
        captured = []

        def opener(request, timeout):
            captured.append(request)
            return tls.HttpResponse(
                status=200,
                body=b'{"Analysis":[{"route":"/a","method":"GET","pv":"3"}]}',
            )

        client = tls.VolcengineTlsClient(
            access_key_id="ak-example",
            secret_access_key="sk-secret",
            region="cn-beijing",
            endpoint="tls-cn-beijing.ivolces.com",
            opener=opener,
        )

        rows = client.search_logs("topic-1", tls.DEFAULT_QUERY, 1_700_000_000_000, 1_700_000_900_000)

        self.assertEqual(rows, [{"route": "/a", "method": "get", "pv": 3}])
        request = captured[0]
        self.assertEqual(request.full_url, "https://tls-cn-beijing.ivolces.com/SearchLogs")
        self.assertEqual(request.get_method(), "POST")
        self.assertIn(b'"TopicId":"topic-1"', request.data)
        self.assertIn(b'"Limit":1000', request.data)

    def test_search_logs_filters_rows_missing_route_or_method(self):
        def opener(request, timeout):
            return tls.HttpResponse(
                status=200,
                body=(
                    b'{"Analysis":['
                    b'{"route":"/a","method":"GET","pv":"3"},'
                    b'{"route":null,"method":"GET","pv":"9"},'
                    b'{"route":"/b","method":null,"pv":"4"}'
                    b"]}"
                ),
            )

        client = tls.VolcengineTlsClient(
            access_key_id="ak-example",
            secret_access_key="sk-secret",
            region="cn-beijing",
            endpoint="tls-cn-beijing.ivolces.com",
            opener=opener,
        )

        rows = client.search_logs("topic-1", tls.DEFAULT_QUERY, 1_700_000_000_000, 1_700_000_900_000)

        self.assertEqual(rows, [{"route": "/a", "method": "get", "pv": 3}])

    def test_find_topic_candidates_when_namespace_missing(self):
        client = FakeTopicClient(
            {
                "prod-vke": [
                    {"topic_name": "teacherschool-teacher-school", "topic_id": "topic-1"},
                    {"topic_name": "xxxx-teacher-school", "topic_id": "topic-2"},
                    {"topic_name": "xxxx-other", "topic_id": "topic-3"},
                ]
            }
        )

        candidates = tls.find_topic_candidates(client, env="prod", service="teacher-school")

        self.assertEqual([item["topic_id"] for item in candidates], ["topic-1", "topic-2"])
        self.assertEqual(client.calls[-1], ("prod-vke", {"fuzzy_search_key": "teacher-school"}))

    def test_normalize_rows_lowercases_method_and_converts_pv(self):
        rows = [
            {"route": "/rooms/:id", "method": "GET", "pv": "12"},
            {"route": "/rooms", "method": "post", "pv": 3},
        ]

        self.assertEqual(
            tls.normalize_rows(rows),
            [
                {"route": "/rooms/:id", "method": "get", "pv": 12},
                {"route": "/rooms", "method": "post", "pv": 3},
            ],
        )

    def test_normalize_rows_rejects_missing_route(self):
        with self.assertRaises(tls.DataShapeError):
            tls.normalize_rows([{"path": "/rooms/1", "method": "GET", "pv": 1}])

    def test_normalize_route_strips_teacher_school_prefix(self):
        self.assertEqual(
            tls.normalize_route("/teacher-school/admin-room/base"),
            "/admin-room/base",
        )

    def test_normalize_route_rewrites_colon_variables(self):
        self.assertEqual(
            tls.normalize_route("/admin-room/students/:studentId/rooms/:id"),
            "/admin-room/students/{param}/rooms/{param}",
        )

    def test_normalize_route_rewrites_braced_variables(self):
        self.assertEqual(
            tls.normalize_route("/admin-room/students/{studentId}/rooms/{id}"),
            "/admin-room/students/{param}/rooms/{param}",
        )

    def test_ensure_non_empty_rejects_empty_results(self):
        with self.assertRaises(tls.DataShapeError):
            tls.ensure_non_empty([], "A service")

    def test_compare_traffic_full_joins_by_route_and_method(self):
        a_rows = [
            {"route": "/both", "method": "GET", "pv": 10},
            {"route": "/a-only", "method": "POST", "pv": 5},
        ]
        b_rows = [
            {"route": "/both", "method": "get", "pv": 8},
            {"route": "/b-only", "method": "delete", "pv": 2},
        ]

        compared = tls.compare_traffic(a_rows, b_rows)

        self.assertEqual(
            compared,
            [
                {"路由地址": "/both", "method": "get", "A服务流量": 10, "B服务流量": 8},
                {"路由地址": "/a-only", "method": "post", "A服务流量": 5, "B服务流量": 0},
                {"路由地址": "/b-only", "method": "delete", "A服务流量": 0, "B服务流量": 2},
            ],
        )

    def test_compare_traffic_joins_normalized_migration_routes(self):
        a_rows = [
            {"route": "/admin-room/students/:studentId/rooms/base", "method": "GET", "pv": 10},
        ]
        b_rows = [
            {"route": "/teacher-school/admin-room/students/{studentId}/rooms/base", "method": "get", "pv": 8},
        ]

        compared = tls.compare_traffic(a_rows, b_rows)

        self.assertEqual(
            compared,
            [
                {
                    "路由地址": "/admin-room/students/{param}/rooms/base",
                    "method": "get",
                    "A服务流量": 10,
                    "B服务流量": 8,
                }
            ],
        )

    def test_compare_traffic_sums_same_side_normalized_routes(self):
        a_rows = [
            {"route": "/admin-room/students/:id", "method": "GET", "pv": 10},
            {"route": "/admin-room/students/{studentId}", "method": "get", "pv": 5},
        ]
        b_rows = [
            {"route": "/teacher-school/admin-room/students/{id}", "method": "GET", "pv": 8},
        ]

        compared = tls.compare_traffic(a_rows, b_rows)

        self.assertEqual(
            compared,
            [
                {
                    "路由地址": "/admin-room/students/{param}",
                    "method": "get",
                    "A服务流量": 15,
                    "B服务流量": 8,
                }
            ],
        )

    def test_candidate_report_groups_literal_ref_routes(self):
        report = tls.build_candidate_report(
            [
                {"route": "/rooms/refs/703A/search", "method": "GET", "pv": 12},
                {"route": "/rooms/refs/G411626201508261231/search", "method": "GET", "pv": 8},
                {"route": "/rooms/refs/ex2026028Fafafa62/search", "method": "GET", "pv": 5},
            ],
            [],
        )

        self.assertEqual(
            report["candidates"],
            [
                {
                    "candidate_route": "/rooms/refs/{param}/search",
                    "method": "get",
                    "raw_routes": [
                        "/rooms/refs/703A/search",
                        "/rooms/refs/G411626201508261231/search",
                        "/rooms/refs/ex2026028Fafafa62/search",
                    ],
                    "reason": "same prefix and suffix with one varying literal segment",
                    "value_count": 3,
                }
            ],
        )

    def test_candidate_report_uses_deterministic_normalization_first(self):
        report = tls.build_candidate_report(
            [
                {"route": "/teacher-school/rooms/refs/{ref}/search", "method": "GET", "pv": 12},
                {"route": "/rooms/refs/:id/search", "method": "GET", "pv": 8},
            ],
            [],
        )

        self.assertEqual(report["candidates"], [])

    def test_candidate_report_does_not_group_fixed_semantic_routes(self):
        report = tls.build_candidate_report(
            [
                {"route": "/users/me", "method": "GET", "pv": 12},
                {"route": "/schools/password", "method": "GET", "pv": 8},
                {"route": "/new-level/tasks", "method": "GET", "pv": 5},
            ],
            [],
        )

        self.assertEqual(report["candidates"], [])

    def test_candidate_report_requires_single_varying_segment(self):
        report = tls.build_candidate_report(
            [
                {"route": "/rooms/refs/703A/search", "method": "GET", "pv": 12},
                {"route": "/rooms/codes/G411626201508261231/detail", "method": "GET", "pv": 8},
            ],
            [],
        )

        self.assertEqual(report["candidates"], [])

    def test_compare_traffic_applies_assisted_literal_route_rule(self):
        compared = tls.compare_traffic(
            [{"route": "/rooms/refs/703A/search", "method": "GET", "pv": 12}],
            [{"route": "/rooms/refs/Fafafa54/search", "method": "GET", "pv": 8}],
            assisted_rules=[
                {
                    "pattern": "/rooms/refs/*/search",
                    "replacement": "/rooms/refs/{param}/search",
                    "risk": "low",
                    "examples": ["/rooms/refs/703A/search"],
                }
            ],
        )

        self.assertEqual(
            compared,
            [
                {
                    "路由地址": "/rooms/refs/{param}/search",
                    "method": "get",
                    "A服务流量": 12,
                    "B服务流量": 8,
                }
            ],
        )

    def test_compare_traffic_sums_same_side_after_assisted_rule(self):
        compared = tls.compare_traffic(
            [
                {"route": "/rooms/refs/703A/search", "method": "GET", "pv": 12},
                {"route": "/rooms/refs/G411626201508261231/search", "method": "GET", "pv": 8},
            ],
            [{"route": "/rooms/refs/{ref}/search", "method": "GET", "pv": 5}],
            assisted_rules=[
                {
                    "pattern": "/rooms/refs/*/search",
                    "replacement": "/rooms/refs/{param}/search",
                    "risk": "low",
                    "examples": ["/rooms/refs/703A/search"],
                }
            ],
        )

        self.assertEqual(compared[0]["A服务流量"], 20)
        self.assertEqual(compared[0]["B服务流量"], 5)

    def test_compare_traffic_keeps_missing_side_zero_after_assisted_rule(self):
        compared = tls.compare_traffic(
            [{"route": "/rooms/refs/703A/search", "method": "GET", "pv": 12}],
            [],
            assisted_rules=[
                {
                    "pattern": "/rooms/refs/*/search",
                    "replacement": "/rooms/refs/{param}/search",
                    "risk": "low",
                    "examples": ["/rooms/refs/703A/search"],
                }
            ],
        )

        self.assertEqual(compared[0]["B服务流量"], 0)

    def test_compare_traffic_assisted_rule_keeps_required_output_columns(self):
        compared = tls.compare_traffic(
            [{"route": "/rooms/refs/703A/search", "method": "GET", "pv": 12}],
            [],
            assisted_rules=[
                {
                    "pattern": "/rooms/refs/*/search",
                    "replacement": "/rooms/refs/{param}/search",
                    "risk": "low",
                    "examples": ["/rooms/refs/703A/search"],
                }
            ],
        )

        self.assertEqual(list(compared[0].keys()), list(tls.OUTPUT_COLUMNS))

    def test_render_output_rows_uses_service_name_traffic_columns(self):
        rows = [{"路由地址": "/a", "method": "get", "A服务流量": 12, "B服务流量": 0}]

        rendered = tls.render_output_rows(
            rows,
            a_name="teacherschool/teacher",
            b_name="teacherschool/teacher-school",
        )

        self.assertEqual(rendered[0]["teacherschool/teacher流量"], 12)
        self.assertEqual(rendered[0]["teacherschool/teacher-school流量"], 0)
        self.assertNotIn("A服务流量", rendered[0])
        self.assertNotIn("B服务流量", rendered[0])

    def test_render_output_rows_display_names_override_service_names(self):
        rows = [{"路由地址": "/a", "method": "get", "A服务流量": 12, "B服务流量": 0}]

        rendered = tls.render_output_rows(
            rows,
            a_name="teacherschool/teacher",
            b_name="teacherschool/teacher-school",
            a_display_name="旧 teacher",
            b_display_name="新 teacher-school",
        )

        self.assertIn("旧 teacher流量", rendered[0])
        self.assertIn("新 teacher-school流量", rendered[0])
        self.assertNotIn("teacherschool/teacher流量", rendered[0])

    def test_render_output_rows_marks_positive_traffic_as_true(self):
        rows = [{"路由地址": "/a", "method": "get", "A服务流量": 12, "B服务流量": 0}]

        rendered = tls.render_output_rows(
            rows,
            a_name="teacherschool/teacher",
            b_name="teacherschool/teacher-school",
        )

        self.assertIs(rendered[0]["teacherschool/teacher有流量"], True)

    def test_render_output_rows_marks_zero_traffic_as_false(self):
        rows = [{"路由地址": "/a", "method": "get", "A服务流量": 12, "B服务流量": 0}]

        rendered = tls.render_output_rows(
            rows,
            a_name="teacherschool/teacher",
            b_name="teacherschool/teacher-school",
        )

        self.assertIs(rendered[0]["teacherschool/teacher-school有流量"], False)

    def test_enhanced_output_columns_keep_route_and_method_first(self):
        columns = tls.output_columns_for(
            a_name="teacherschool/teacher",
            b_name="teacherschool/teacher-school",
        )

        self.assertEqual(columns[:2], ["路由地址", "method"])

    def test_resolve_display_names_prefers_explicit_names(self):
        self.assertEqual(
            tls.resolve_display_names(
                a_name="teacherschool/teacher",
                b_name="teacherschool/teacher-school",
                a_display_name="旧 teacher",
                b_display_name="新 teacher-school",
            ),
            ("旧 teacher", "新 teacher-school"),
        )

    def test_render_output_rows_preserves_legacy_columns_without_service_names(self):
        rows = [{"路由地址": "/a", "method": "get", "A服务流量": 12, "B服务流量": 0}]

        self.assertEqual(tls.render_output_rows(rows), rows)

    def test_build_compare_output_enhances_preview_rows_with_service_names(self):
        compared = [
            {"路由地址": "/rooms/refs/{param}/search", "method": "get", "A服务流量": 12, "B服务流量": 0}
        ]

        output = tls.build_compare_output(
            compared,
            a_name="teacherschool/teacher",
            b_name="teacherschool/teacher-school",
            limit=1,
        )

        self.assertEqual(output["rows"][0]["teacherschool/teacher流量"], 12)
        self.assertIs(output["rows"][0]["teacherschool/teacher-school有流量"], False)

    def test_csv_output_supports_enhanced_columns_and_lowercase_booleans(self):
        rows = [
            {
                "路由地址": "/a",
                "method": "get",
                "teacherschool/teacher流量": 1,
                "teacherschool/teacher-school流量": 0,
                "teacherschool/teacher有流量": True,
                "teacherschool/teacher-school有流量": False,
            }
        ]

        output = tls.to_csv(
            rows,
            columns=[
                "路由地址",
                "method",
                "teacherschool/teacher流量",
                "teacherschool/teacher-school流量",
                "teacherschool/teacher有流量",
                "teacherschool/teacher-school有流量",
            ],
        )
        reader = csv.reader(io.StringIO(output))

        self.assertEqual(
            list(reader),
            [
                [
                    "路由地址",
                    "method",
                    "teacherschool/teacher流量",
                    "teacherschool/teacher-school流量",
                    "teacherschool/teacher有流量",
                    "teacherschool/teacher-school有流量",
                ],
                ["/a", "get", "1", "0", "true", "false"],
            ],
        )

    def test_assisted_rules_apply_before_enhanced_output_rendering(self):
        compared = tls.compare_traffic(
            [{"route": "/rooms/refs/703A/search", "method": "GET", "pv": 12}],
            [{"route": "/rooms/refs/Fafafa54/search", "method": "GET", "pv": 8}],
            assisted_rules=[
                {
                    "pattern": "/rooms/refs/*/search",
                    "replacement": "/rooms/refs/{param}/search",
                    "risk": "low",
                    "examples": ["/rooms/refs/703A/search"],
                }
            ],
        )

        rendered = tls.render_output_rows(
            compared,
            a_name="teacherschool/teacher",
            b_name="teacherschool/teacher-school",
        )

        self.assertEqual(rendered[0]["路由地址"], "/rooms/refs/{param}/search")
        self.assertEqual(rendered[0]["teacherschool/teacher流量"], 12)
        self.assertEqual(rendered[0]["teacherschool/teacher-school流量"], 8)

    def test_preview_does_not_require_persistent_output(self):
        rows = [
            {"路由地址": "/a", "method": "get", "A服务流量": 1, "B服务流量": 0},
            {"路由地址": "/b", "method": "post", "A服务流量": 0, "B服务流量": 2},
        ]

        preview = tls.build_preview(rows, limit=1)

        self.assertEqual(preview["total"], 2)
        self.assertEqual(len(preview["rows"]), 1)

    def test_csv_output_uses_required_columns(self):
        rows = [{"路由地址": "/a", "method": "get", "A服务流量": 1, "B服务流量": 0}]

        output = tls.to_csv(rows)
        reader = csv.reader(io.StringIO(output))

        self.assertEqual(
            list(reader),
            [["路由地址", "method", "A服务流量", "B服务流量"], ["/a", "get", "1", "0"]],
        )


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def fail(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def build_endpoint() -> str:
    sourcegraph_url = os.environ.get("SOURCEGRAPH_URL", "").strip()
    if not sourcegraph_url:
        fail("SOURCEGRAPH_URL is required")

    sourcegraph_url = sourcegraph_url.rstrip("/")
    if sourcegraph_url.endswith("/.api/graphql"):
        return sourcegraph_url
    return f"{sourcegraph_url}/.api/graphql"


def get_headers() -> dict:
    token = os.environ.get("SOURCEGRAPH_TOKEN", "").strip()
    if not token:
        fail("SOURCEGRAPH_TOKEN is required")

    return {
        "Authorization": f"token {token}",
        "Content-Type": "application/json",
    }


def graphql(query: str, variables: dict | None = None) -> dict:
    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    request = urllib.request.Request(
        build_endpoint(),
        data=payload,
        headers=get_headers(),
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        fail(f"GraphQL request failed with HTTP {exc.code}: {body}", exc.code)
    except urllib.error.URLError as exc:
        fail(f"GraphQL request failed: {exc.reason}")

    data = json.loads(raw)
    if data.get("errors"):
        fail(json.dumps(data["errors"], ensure_ascii=False, indent=2))
    return data.get("data") or {}


def print_json(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def do_whoami(_: argparse.Namespace) -> None:
    query = """
    query CurrentUser {
      currentUser {
        username
      }
    }
    """
    data = graphql(query)
    print_json({"username": (((data.get("currentUser") or {}).get("username")) or "")})


def do_search(args: argparse.Namespace) -> None:
    query = """
    query Search($query: String!) {
      search(query: $query, version: V3) {
        results {
          matchCount
          results {
            __typename
            ... on FileMatch {
              repository {
                name
              }
              file {
                path
              }
              lineMatches {
                preview
                lineNumber
                offsetAndLengths
              }
            }
            ... on Repository {
              name
            }
          }
        }
      }
    }
    """
    data = graphql(query, {"query": args.query})
    results = (((data.get("search") or {}).get("results")) or {})

    normalized = {"matchCount": results.get("matchCount", 0), "results": []}
    raw_results = results.get("results") or []
    for item in raw_results[: args.first]:
        item_type = item.get("__typename", "")
        if item_type == "FileMatch":
            normalized["results"].append(
                {
                    "type": "file",
                    "repository": ((item.get("repository") or {}).get("name")) or "",
                    "path": ((item.get("file") or {}).get("path")) or "",
                    "lineMatches": [
                        {
                            "lineNumber": match.get("lineNumber"),
                            "preview": match.get("preview"),
                            "offsetAndLengths": match.get("offsetAndLengths"),
                        }
                        for match in (item.get("lineMatches") or [])[: args.lines_per_file]
                    ],
                }
            )
        elif item_type == "Repository":
            normalized["results"].append(
                {
                    "type": "repository",
                    "repository": item.get("name") or "",
                }
            )
        else:
            normalized["results"].append({"type": item_type or "unknown"})

    print_json(normalized)


def do_repos(args: argparse.Namespace) -> None:
    repo_query = args.query
    if "type:repo" not in repo_query:
        repo_query = f"type:repo {repo_query}".strip()

    search_args = argparse.Namespace(
        query=repo_query,
        first=args.first,
        lines_per_file=0,
    )
    query = """
    query SearchRepos($query: String!) {
      search(query: $query, version: V3) {
        results {
          matchCount
          results {
            __typename
            ... on Repository {
              name
            }
          }
        }
      }
    }
    """
    data = graphql(query, {"query": search_args.query})
    results = (((data.get("search") or {}).get("results")) or {}).get("results") or []
    repos = []
    for item in results[: args.first]:
        if item.get("__typename") == "Repository":
            repos.append(item.get("name") or "")

    print_json({"repositories": repos})


def do_file(args: argparse.Namespace) -> None:
    query = """
    query ReadFile($repo: String!, $rev: String!, $path: String!) {
      repository(name: $repo) {
        commit(rev: $rev) {
          blob(path: $path) {
            binary
            byteSize
            content
          }
        }
      }
    }
    """
    data = graphql(query, {"repo": args.repo, "rev": args.rev, "path": args.path})
    blob = ((((data.get("repository") or {}).get("commit") or {}).get("blob")) or {})
    if not blob:
        fail("File not found in Sourcegraph response")
    if blob.get("binary"):
        fail("Binary files are not supported by this helper")

    lines = (blob.get("content") or "").splitlines()
    start_line = args.start_line or 1
    end_line = args.end_line or len(lines)
    start_index = max(start_line - 1, 0)
    end_index = min(end_line, len(lines))
    sliced_lines = lines[start_index:end_index]

    print_json(
        {
            "repository": args.repo,
            "path": args.path,
            "rev": args.rev,
            "startLine": start_line,
            "endLine": end_index,
            "lines": [
                {"lineNumber": index, "text": text}
                for index, text in enumerate(sliced_lines, start=start_index + 1)
            ],
        }
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Sourcegraph GraphQL queries using SOURCEGRAPH_URL and SOURCEGRAPH_TOKEN."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    whoami = subparsers.add_parser("whoami", help="Validate auth and print the current user.")
    whoami.set_defaults(func=do_whoami)

    search = subparsers.add_parser("search", help="Search code or repositories with Sourcegraph syntax.")
    search.add_argument("--query", required=True, help="Sourcegraph search query.")
    search.add_argument("--first", type=int, default=20, help="Maximum number of results to print.")
    search.add_argument(
        "--lines-per-file",
        type=int,
        default=3,
        help="Maximum line matches to keep for each file result.",
    )
    search.set_defaults(func=do_search)

    repos = subparsers.add_parser("repos", help="Search repositories only.")
    repos.add_argument("--query", required=True, help="Repository search query.")
    repos.add_argument("--first", type=int, default=20, help="Maximum number of repositories to print.")
    repos.set_defaults(func=do_repos)

    file_parser = subparsers.add_parser("file", help="Read one file from a Sourcegraph repository.")
    file_parser.add_argument("--repo", required=True, help="Repository name in Sourcegraph.")
    file_parser.add_argument("--path", required=True, help="File path inside the repository.")
    file_parser.add_argument("--rev", default="HEAD", help="Revision, branch, or commit.")
    file_parser.add_argument("--start-line", type=int, default=1, help="First line to print.")
    file_parser.add_argument("--end-line", type=int, help="Last line to print.")
    file_parser.set_defaults(func=do_file)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

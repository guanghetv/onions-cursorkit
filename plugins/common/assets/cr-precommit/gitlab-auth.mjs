#!/usr/bin/env node

/**
 * GitLab API auth helper.
 * CI: prefer CI_JOB_TOKEN (injected by GitLab). Local upload: PAT only.
 */

export function resolveGitLabAuth({ localOnly = false } = {}) {
  if (!localOnly && process.env.CI_JOB_TOKEN) {
    return { token: process.env.CI_JOB_TOKEN, type: "job" };
  }
  const pat = process.env.GITLAB_TOKEN || process.env.GITLAB_PRIVATE_TOKEN;
  if (pat) {
    return { token: pat, type: "private" };
  }
  return null;
}

export function authHeaderName(auth) {
  return auth.type === "job" ? "JOB-TOKEN" : "PRIVATE-TOKEN";
}

export function authHeaders(auth, extra = {}) {
  if (!auth?.token) {
    return { ...extra };
  }
  return {
    [authHeaderName(auth)]: auth.token,
    ...extra
  };
}

export async function gitlabFetch(url, auth, options = {}) {
  if (!auth?.token) {
    throw new Error("missing GitLab auth (CI_JOB_TOKEN or GITLAB_TOKEN)");
  }
  const headers = authHeaders(auth, options.headers || {});
  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`gitlab api failed (${response.status}): ${body}`);
  }
  return response;
}

export async function gitlabJson(url, auth, options = {}) {
  const response = await gitlabFetch(url, auth, options);
  return response.json();
}

export async function gitlabText(url, auth, options = {}) {
  const response = await gitlabFetch(url, auth, options);
  return response.text();
}

export function authSourceLabel(auth) {
  if (!auth) {
    return "none";
  }
  return auth.type === "job" ? "CI_JOB_TOKEN" : "GITLAB_TOKEN";
}

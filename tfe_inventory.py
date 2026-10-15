#!/usr/bin/env python3

import json
import ssl
import sys
import argparse
import urllib.error
import urllib.request
from collections import Counter
from urllib.parse import urljoin

# Disable TLS verification
ssl._create_default_https_context = ssl._create_unverified_context


def api_get(url, token):
  req = urllib.request.Request(url)
  req.add_header("Authorization", "Bearer " + token)
  req.add_header("Accept", "application/vnd.api+json")

  with urllib.request.urlopen(req) as response:
    body = response.read().decode()
    return json.loads(body)


def get_all_pages(url, token, base_host):
  while url:
    data = api_get(url, token)

    for item in data.get("data", []):
      yield item

    next_link = data.get("links", {}).get("next")

    if next_link:
      url = urljoin(base_host, next_link)
    else:
      url = None


def print_table(headers, rows):
  col_widths = []

  for i in range(len(headers)):
    max_width = len(headers[i])
    for row in rows:
      max_width = max(max_width, len(str(row[i])))
    col_widths.append(max_width)

  def separator():
    return "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

  def format_row(row):
    return "| " + " | ".join(
      str(row[i]).ljust(col_widths[i]) for i in range(len(row))
    ) + " |"

  print(separator())
  print(format_row(headers))
  print(separator())

  for row in rows:
    print(format_row(row))

  print(separator())


# Resource types excluded from HashiCorp's billable RUM definition
NON_BILLABLE_TYPES = {"null_resource", "terraform_data"}


def is_billable(rtype):
  """Return True if the resource type counts as a billable managed resource."""
  if rtype.startswith("data."):
    return False
  if rtype in NON_BILLABLE_TYPES:
    return False
  return True


def get_workspace_resources(workspace_id, token, base_url, base_host, detail=False, debug=False):
  """Return (count, type_counter) for billable resources in a workspace."""
  url = f"{base_url}/workspaces/{workspace_id}/resources?page[size]=100"
  type_counts = Counter()
  total = 0
  try:
    for r in get_all_pages(url, token, base_host):
      if debug:
        print(f"DEBUG resource attributes: {json.dumps(r.get('attributes', {}), indent=2)}", file=sys.stderr)
      rtype = r["attributes"].get("provider-type", "(unknown)")
      if not is_billable(rtype):
        continue
      total += 1
      if detail:
        type_counts[rtype] += 1
  except urllib.error.HTTPError as e:
    print(f"warning: could not list resources for {workspace_id}: HTTP {e.code} {e.reason}", file=sys.stderr)
  return total, type_counts


def print_resource_type_detail(type_counts):
  """Print a sorted breakdown of resource types for a workspace."""
  if not type_counts:
    return
  headers = ["Resource Type", "Count"]
  rows = sorted(type_counts.items(), key=lambda x: (-x[1], x[0]))
  print_table(headers, rows)


def main():
  parser = argparse.ArgumentParser(
    description="List all Terraform Enterprise orgs and workspaces with resource counts"
  )
  parser.add_argument(
    "--addr",
    required=True,
    help="Terraform Enterprise base URL (e.g. https://tfe.mycompany.com)",
  )
  parser.add_argument(
    "--token",
    required=True,
    help="Terraform Enterprise API token",
  )
  parser.add_argument(
    "--detail",
    action="store_true",
    default=False,
    help="Show a per-resource-type breakdown for each workspace",
  )
  parser.add_argument(
    "--debug",
    action="store_true",
    default=False,
    help="Print raw attributes of the first resource in each workspace (stderr)",
  )

  args = parser.parse_args()

  base_host = args.addr.rstrip("/")
  token = args.token
  detail = args.detail
  debug = args.debug

  base_url = f"{base_host}/api/v2"
  org_url = f"{base_url}/organizations?page[size]=100"

  print(f"TFE Address: {base_host}\n")

  total_rum = 0
  org_summaries = []

  for org in get_all_pages(org_url, token, base_host):
    org_name = org["attributes"]["name"]

    print("\n" + org_name)
    print("=" * len(org_name))

    ws_url = f"{base_url}/organizations/{org_name}/workspaces?page[size]=100"
    workspaces = list(get_all_pages(ws_url, token, base_host))

    if not workspaces:
      print("(no workspaces)\n")
      continue

    headers = ["Workspace", "Created", "Exec Mode", "TF Version", "Resources"]
    rows = []
    org_rum = 0
    ws_type_counts = {}

    for ws in workspaces:
      attrs = ws["attributes"]
      workspace_id = ws["id"]
      resource_count, type_counts = get_workspace_resources(
        workspace_id, token, base_url, base_host, detail=detail, debug=debug
      )
      org_rum += resource_count
      total_rum += resource_count

      rows.append([
        attrs["name"],
        attrs["created-at"],
        attrs.get("execution-mode", ""),
        attrs.get("terraform-version", ""),
        resource_count,
      ])

      if detail:
        ws_type_counts[attrs["name"]] = type_counts

    print_table(headers, rows)

    if detail:
      for ws_name, type_counts in ws_type_counts.items():
        if type_counts:
          print(f"\n  {ws_name} — resource type breakdown:")
          print_resource_type_detail(type_counts)

    org_summaries.append((org_name, len(workspaces), org_rum))
    print(f"\nOrganization Summary: {len(workspaces)} workspaces, {org_rum} total resources\n")

  # Print global summary
  print("\nGlobal Summary")
  print("=" * 15)
  summary_headers = ["Organization", "Workspaces", "Resources"]
  summary_rows = org_summaries
  print_table(summary_headers, summary_rows)
  print(f"\nTotal across all organizations: {sum(s[1] for s in org_summaries)} workspaces, {total_rum} resources")


if __name__ == "__main__":
  main()

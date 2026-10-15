# Terraform Enterprise Inventory Tool

Lists all organizations and workspaces in Terraform Enterprise, and provide a resource count per workspace.

## Requirements

- Python 3.9+
- No external dependencies
- Terraform Enterprise token with permissions to get a list of all organizations and all workspaces in each organization.

## Usage

```bash
export TFE_ADDR=https://tfe.example.com
export TFE_TOKEN=<token>

python3 tfe_inventory.py \
  --addr  $TFE_ADDR \
  --token $TFE_TOKEN
```

### Example

```bash
python3 tfe_inventory.py --addr $TFE_ADDRESS --token $TFE_TOKEN
```

## Example run
```
❯ python3 tfe_inventory.py --addr $TFE_ADDRESS --token $TFE_TOKEN
TFE Address: https://tfe.example.com


org0
====
+-----------------------------+--------------------------+-----------+------------+-----------+
| Workspace                   | Created                  | Exec Mode | TF Version | Resources |
+-----------------------------+--------------------------+-----------+------------+-----------+
| tls-demo-mod-04             | 2026-10-15T12:16:27.783Z | remote    | 1.14.3     | 32        |
| tls-demo-mod-03             | 2026-10-15T12:16:13.045Z | remote    | 1.13.4     | 14        |
| tls-demo-mod-02             | 2026-10-15T12:15:59.448Z | remote    | 1.13.0     | 26        |
| tls-demo-mod-01             | 2026-10-15T12:15:44.291Z | remote    | 1.15.1     | 32        |
| random-demo-mod-04          | 2026-10-15T12:15:27.272Z | remote    | 1.15.5     | 28        |
| random-demo-mod-03          | 2026-10-15T12:15:13.568Z | remote    | 1.15.1     | 12        |
| random-demo-mod-02          | 2026-10-15T12:14:59.530Z | remote    | 1.14.6     | 22        |
| random-demo-mod-01          | 2026-10-15T12:14:43.285Z | remote    | 1.15.0     | 6         |
| tls-demo-trusty-mink        | 2026-10-15T02:42:41.705Z | remote    | 1.15.5     | 10        |
| tls-demo-aware-viper        | 2026-10-15T02:42:41.344Z | remote    | 1.15.5     | 10        |
| tls-demo-amusing-scorpion   | 2026-10-15T02:42:40.925Z | remote    | 1.15.5     | 10        |
| tls-demo-trusting-unicorn   | 2026-10-15T02:42:40.345Z | remote    | 1.15.5     | 10        |
| random-demo-helping-meerkat | 2026-10-15T02:42:39.822Z | remote    | 1.15.5     | 10        |
| random-demo-loved-giraffe   | 2026-10-15T02:42:39.356Z | remote    | 1.15.5     | 10        |
| random-demo-active-starfish | 2026-10-15T02:42:38.897Z | remote    | 1.15.5     | 10        |
| random-demo-frank-lion      | 2026-10-15T02:42:38.232Z | remote    | 1.15.5     | 10        |
+-----------------------------+--------------------------+-----------+------------+-----------+

Organization Summary: 16 workspaces, 252 total resources


org1
====
+-------------+--------------------------+-----------+------------+-----------+
| Workspace   | Created                  | Exec Mode | TF Version | Resources |
+-------------+--------------------------+-----------+------------+-----------+
| api-demo-03 | 2026-10-15T13:15:19.907Z | remote    | 1.14.4     | 2         |
| api-demo-02 | 2026-10-15T13:15:05.041Z | remote    | 1.13.1     | 3         |
| api-demo-01 | 2026-10-15T13:14:50.091Z | remote    | 1.11.2     | 3         |
+-------------+--------------------------+-----------+------------+-----------+

Organization Summary: 3 workspaces, 8 total resources


Global Summary
===============
+--------------+------------+-----------+
| Organization | Workspaces | Resources |
+--------------+------------+-----------+
| org0         | 16         | 252       |
| org1         | 3          | 8         |
+--------------+------------+-----------+

Total across all organizations: 19 workspaces, 260 resources
```

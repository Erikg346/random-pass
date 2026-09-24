#!/bin/bash
set -eu

: "${KIBANA_URL:=http://localhost:5601}"
: "${ELASTIC_USER:=elastic}"
: "${ELASTIC_PASSWORD:?Set ELASTIC_PASSWORD before running this script}"

# Create a temporary file to store SLO ID mappings
temp_mappings=$(mktemp)
trap "rm -f $temp_mappings" EXIT

# Track SLOs by name and index
jq -c '.[]' dashboards/random-pass-slos.json | while read -r slo; do
  name=$(printf '%s' "$slo" | jq -r '.name')
  response=$(curl -fsS -u "$ELASTIC_USER:$ELASTIC_PASSWORD" \
    -X POST "$KIBANA_URL/api/observability/slos" \
    -H 'kbn-xsrf: true' \
    -H 'content-type: application/json' \
    -d "$slo")
  
  slo_id=$(printf '%s' "$response" | jq -r '.id')
  printf 'Created SLO: %s (ID: %s)\n' "$name" "$slo_id"
  
  # Store mapping for dashboard update
  printf '%s|%s\n' "$name" "$slo_id" >> "$temp_mappings"
done

# Update the dashboard JSON with the new SLO IDs
if [ -f "$temp_mappings" ]; then
  python3 << PYTHON_EOF
import json
from pathlib import Path

# Read the mappings
mappings = {}
with open('$temp_mappings') as f:
    for line in f:
        name, slo_id = line.strip().split('|')
        mappings[name] = slo_id

# Read the dashboard
dashboard_path = Path('dashboards/random-pass-service-health.json')
with open(dashboard_path) as f:
    dashboard = json.load(f)

# Update SLO panels with correct IDs
slo_name_to_panel_id = {
    'User password generation availability': 'slo-availability-1',
    'User password generation latency': 'slo-latency-1',
    'Notification delivery availability (internal)': 'slo-error-rate-1'
}

for slo_name, slo_id in mappings.items():
    panel_id = slo_name_to_panel_id.get(slo_name)
    if panel_id:
        for panel in dashboard.get('panels', []):
            if panel.get('id') == panel_id:
                # Update with SLO overview panel type
                panel['type'] = 'slo_overview'
                panel['config'] = {
                    'hide_title': False,
                    'overview_mode': 'single',
                    'slo_id': slo_id,
                    'slo_instance_id': '*'
                }
                print(f'✓ Updated panel {panel_id} with SLO ID: {slo_id} ({slo_name})')

# Write back the dashboard
with open(dashboard_path, 'w') as f:
    json.dump(dashboard, f, indent=2)

print('✓ Dashboard JSON updated with SLO IDs')
PYTHON_EOF
fi


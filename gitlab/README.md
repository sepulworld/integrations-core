# Gitlab Integration

## Overview

Integration that allows to:

* Visualize and monitor metrics collected via Gitlab through Prometheus

See the [Gitlab documentation][1] for more information about Gitlab and its integration with Prometheus

## Setup
### Installation

The Gitlab check is included in the [Datadog Agent][2] package, so you don't need to install anything else on your Gitlab servers.

### Configuration

Edit the `gitlab.d/conf.yaml` file, in the `conf.d/` folder at the root of your [Agent's configuration directory][3], to point to the Gitlab's Prometheus metrics endpoint.
See the [sample gitlab.d/conf.yaml][4] for all available configuration options.

**Note**: The `allowed_metrics` item in the `init_config` section allows to specify the metrics that should be extracted.


#### Log Collection

To enable collecting logs in the Datadog Agent, update `logs_enabled` in `datadog.yaml`:
```yaml
    logs_enabled: true
```

Next, edit `gitlab.d/conf.yaml` by uncommenting the `logs` lines at the bottom. Update the logs `path` with the correct path to your Gitlab log files.

```yaml
logs:
   - type: file
     path: /var/log/gitlab/gitlab-rails/production_json.log
     service: <SERVICE_NAME>
     source: gitlab
   - type: file
     path: /var/log/gitlab/gitlab-rails/production.log
     service: <SERVICE_NAME>
     source: gitlab
   - type: file
     path: /var/log/gitlab/gitlab-rails/api_json.log
     service: <SERVICE_NAME>
     source: gitlab
```

### Validation

[Run the Agent's `status` subcommand][5] and look for `gitlab` under the Checks section.

## Data Collected
### Metrics
See [metadata.csv][6] for a list of metrics provided by this integration.

### Events
The Gitlab check does not include any events.

### Service Checks
The Gitlab check includes a readiness and a liveness service check.
Moreover, it provides a service check to ensure that the local Prometheus endpoint is available.

## Troubleshooting
Need help? Contact [Datadog support][7].

[1]: https://docs.gitlab.com/ee/administration/monitoring/prometheus
[2]: https://app.datadoghq.com/account/settings#agent
[3]: https://docs.datadoghq.com/agent/guide/agent-configuration-files/?tab=agentv6#agent-configuration-directory
[4]: https://github.com/DataDog/integrations-core/blob/master/gitlab/datadog_checks/gitlab/data/conf.yaml.example
[5]: https://docs.datadoghq.com/agent/guide/agent-commands/?tab=agentv6#agent-status-and-information
[6]: https://github.com/DataDog/integrations-core/blob/master/gitlab/metadata.csv
[7]: https://docs.datadoghq.com/help

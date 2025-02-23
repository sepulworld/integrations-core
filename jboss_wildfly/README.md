# Agent Check: JBoss/WildFly

## Overview

This check monitors [JBoss][1] and [WildFly][2] applications.

## Setup

### Installation

The JBoss/WildFly check is included in the [Datadog Agent][3] package.
No additional installation is needed on your server.

### Configuration

1. Edit the `jboss_wildfly.d/conf.yaml` file, in the `conf.d/` folder at the root of your
   Agent's configuration directory to start collecting your JBoss or WildFly application server's
   performance data. See the [sample jboss_wildfly.d/conf.yaml][4] for all available configuration options.

   This check has a limit of 350 metrics per instance. The number of returned metrics is indicated in the info page.
   You can specify the metrics you are interested in by editing the configuration below. 
   To learn how to customize the collected metrics, visit the [JMX Checks documentation][5] for more detailed instructions.
   If you need to monitor more metrics, contact [Datadog support][6].

2. [Restart the Agent][7].

#### Log Collection

To enable collecting logs in the Datadog Agent, update `logs_enabled` in `datadog.yaml`:
```
    logs_enabled: true
```

Next, edit `jboss_wildfly.d/conf.yaml` by uncommenting the `logs` lines at the bottom. Update the logs `path` with the correct path to your JBoss log files.

```yaml
logs:
 - type: file
   path: /opt/jboss/wildfly/standalone/log/*.log
   source: jboss_wildfly
   service: <APPLICATION_NAME>
```

### Validation

[Run the Agent's status subcommand][8] and look for `jboss_wildfly` under the Checks section.

## Data Collected

### Metrics

See [metadata.csv][8] for a list of metrics provided by this integration.

### Service Checks

The JBoss/WildFly integration does not include any service checks.

### Events

The JBoss/WildFly integration does not include any events.

## Troubleshooting

Need help? Contact [Datadog support][7].

[1]: https://developers.redhat.com/products/eap/overview
[2]: http://wildfly.org
[3]: https://app.datadoghq.com/account/settings#agent
[4]: https://github.com/DataDog/integrations-core/blob/master/jboss_wildfly/datadog_checks/jboss_wildfly/data/conf.yaml.example
[5]: https://docs.datadoghq.com/integrations/java
[6]: https://docs.datadoghq.com/help
[7]: https://docs.datadoghq.com/agent/guide/agent-commands/#start-stop-restart-the-agent
[8]: https://docs.datadoghq.com/agent/guide/agent-commands/#agent-status-and-information
[9]: https://github.com/DataDog/integrations-core/blob/master/jboss_wildfly/metadata.csv

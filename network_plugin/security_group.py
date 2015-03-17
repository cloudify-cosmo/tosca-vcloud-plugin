from cloudify import ctx
from cloudify import exceptions as cfy_exc
from cloudify.decorators import operation
from vcloud_plugin_common import with_vca_client, get_mandatory, get_vcloud_config
from network_plugin import (check_ip, get_vm_ip, save_gateway_configuration,
                            check_protocol, check_port, get_gateway)


CREATE_RULE = 1
DELETE_RULE = 2

ADDRESS_LITERALS = ("Any", "Internal", "External")
ACTIONS = ("allow", "deny")


@operation
@with_vca_client
def create(vca_client, **kwargs):
    _rule_operation(CREATE_RULE, vca_client)


@operation
@with_vca_client
def delete(vca_client, **kwargs):
    _rule_operation(DELETE_RULE, vca_client)


@operation
@with_vca_client
def creation_validation(vca_client, **kwargs):
    getaway = get_gateway(vca_client, _get_gateway_name(ctx.node.properties))
    if not getaway.is_fw_enabled():
        raise cfy_exc.NonRecoverableError("Giteway firewall is disabled. Please turn on firewall.")
    rules = get_mandatory(ctx.node.properties, 'rules')
    for rule in rules:
        description = rule.get("description")
        if description and not isinstance(description, str):
            raise cfy_exc.NonRecoverableError("Parameter 'description' must be string.")

        source = rule.get("source")
        if source and not isinstance(source, str):
            raise cfy_exc.NonRecoverableError("Parameter 'source' must be valid IP address string.")
        if source.capitalize() not in ADDRESS_LITERALS:
            check_ip(source)

        check_port(rule.get('source_port'), "any")

        destination = get_mandatory(rule)
        if not destination or not isinstance(destination, str):
            raise cfy_exc.NonRecoverableError("Parameter 'destination' must be valid IP address string.")
        if destination.capitalize() not in ADDRESS_LITERALS:
            check_ip(source)

        check_port(get_mandatory('destination_port'))

        check_protocol(rule.get('protocol', "any"))

        action = get_mandatory(rule, "action")
        if not isinstance(action, str) and action.lower() not in ACTIONS:
            raise cfy_exc.NonRecoverableError("Action must be on of{0}.".format(ACTIONS))

        log = rule.get('log_traffic')
        if log and not isinstance(log, bool):
            raise cfy_exc.NonRecoverableError("Parameter 'log_traffic' must be boolean.")


def _rule_operation(operation, vca_client):
    gateway = get_gateway(vca_client, _get_gateway_name(ctx.node.properties))
    for rule in ctx.target.node.properties['rules']:
        protocol = check_protocol(rule.get('protocol', "Any"))
        dest_port = str(rule['port'])
        description = rule['description']
        dest_ip = check_ip(get_vm_ip(vca_client, ctx))
        if operation == CREATE_RULE:
            gateway.add_fw_rule(True, description, "allow", protocol, dest_port, dest_ip,
                                "Any", "External", False)
            error_message = "Could not add firewall rule: {0}".format(description)
            ctx.logger.info("Firewall rule has been created {0}".format(description))
        elif operation == DELETE_RULE:
            gateway.delete_fw_rule(protocol, dest_port, dest_ip,
                                   "Any", "external")
            error_message = "Could not delete firewall rule: {0}".format(description)
            ctx.logger.info("Firewall rule has been deleted {0}".format(description))
    save_gateway_configuration(gateway, vca_client, error_message)


def _get_gateway_name(properties):
    security_group = properties.get('security_group')
    if security_group and 'edge_gateway' in security_group:
        getaway_name = security_group.get('edge_gateway')
    else:
        getaway_name = get_vcloud_config()['edge_gateway']
    return getaway_name

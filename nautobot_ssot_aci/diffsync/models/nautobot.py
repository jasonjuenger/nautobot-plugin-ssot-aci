"""Nautobot Models for Cisco ACI integration with SSoT plugin."""

import logging
from django.contrib.contenttypes.models import ContentType
from nautobot.tenancy.models import Tenant as OrmTenant
from nautobot.dcim.models import DeviceType as OrmDeviceType
from nautobot.dcim.models import DeviceRole as OrmDeviceRole
from nautobot.dcim.models import Device as OrmDevice
from nautobot.dcim.models import InterfaceTemplate as OrmInterfaceTemplate
from nautobot.dcim.models import Interface as OrmInterface
from nautobot.ipam.models import IPAddress as OrmIPAddress
from nautobot.ipam.models import Prefix as OrmPrefix
from nautobot.dcim.models import Manufacturer
from nautobot.dcim.models import Site
from nautobot.extras.models import Status
from nautobot.extras.models import Tag
from nautobot_ssot_aci.diffsync.models.base import (
    Tenant,
    DeviceType,
    DeviceRole,
    Device,
    InterfaceTemplate,
    Interface,
    IPAddress,
    Prefix,
)
from nautobot_ssot_aci.constant import PLUGIN_CFG


logger = logging.getLogger("rq.worker")


class NautobotTenant(Tenant):
    """Nautobot implementation of the Tenant Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Tenant object in Nautobot."""
        _tenant = OrmTenant(name=ids["name"], description=attrs["description"], comments=attrs["comments"])
        _tenant.tags.add(Tag.objects.get(slug=PLUGIN_CFG.get("tag").lower().replace(" ", "-")))
        _tenant.validated_save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update Tenant object in Nautobot."""
        _tenant = OrmTenant.objects.get(name=self.name)
        if attrs.get("description"):
            _tenant.description = attrs["description"]
        if attrs.get("comments"):
            _tenant.comments = attrs["comments"]
        _tenant.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete Tenant object in Nautobot."""
        self.diffsync.job.log_warning(f"Tenant {self.name} will be deleted.")
        _tenant = OrmTenant.objects.get(name=self.get_identifiers()["name"])
        _tenant.delete()
        return super().delete()


class NautobotDeviceType(DeviceType):
    """Nautobot implementation of the DeviceType Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create DeviceType object in Nautobot."""

        _devicetype = OrmDeviceType(
            model=ids["model"],
            manufacturer=Manufacturer.objects.get(name=ids["manufacturer"]),
            part_number=ids["part_nbr"],
            u_height=attrs["u_height"],
            comments=attrs["comments"],
        )
        _devicetype.tags.add(Tag.objects.get(slug=PLUGIN_CFG.get("tag").lower().replace(" ", "-")))
        _devicetype.validated_save()

        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update DeviceType object in Nautobot."""
        _devicetype = OrmDeviceType.objects.get(model=self.model)
        if attrs.get("comments"):
            _devicetype.comments = attrs["comments"]
        if attrs.get("u_height"):
            _devicetype.u_height = attrs["u_height"]
        _devicetype.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete DeviceType object in Nautobot."""
        self.diffsync.job.log_warning(f"Device Type {self.model} will be deleted.")
        _devicetype = OrmDeviceType.objects.get(model=self.get_identifiers()["model"])
        _devicetype.delete()
        return super().delete()


class NautobotDeviceRole(DeviceRole):
    """Nautobot implementation of the DeviceRole Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create DeviceRole object in Nautobot."""
        _devicerole = OrmDeviceRole(name=ids["name"], description=attrs["description"])
        _devicerole.validated_save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update DeviceRole object in Nautobot."""
        _devicerole = OrmDeviceRole.objects.get(name=self.name)
        if attrs.get("description"):
            _devicerole.description = attrs["description"]
        _devicerole.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete DeviceRole object in Nautobot."""
        self.diffsync.job.log_warning(f"Device Role {self.name} will be deleted.")
        _devicerole = OrmDeviceRole.objects.get(name=self.get_identifiers()["name"])
        _devicerole.delete()
        return super().delete()


class NautobotDevice(Device):
    """Nautobot implementation of the Device Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Device object in Nautobot."""
        _device = OrmDevice(
            name=ids["name"],
            device_role=OrmDeviceRole.objects.get(name=ids["device_role"]),
            device_type=OrmDeviceType.objects.get(model=ids["device_type"]),
            serial=ids["serial"],
            comments=attrs["comments"],
            site=Site.objects.get(name=PLUGIN_CFG.get("site")),
            status=Status.objects.get(name="Active"),
        )
        _device.custom_field_data["node-id"] = attrs["node_id"]
        _device.tags.add(Tag.objects.get(slug=PLUGIN_CFG.get("tag").lower().replace(" ", "-")))
        _device.validated_save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update Device object in Nautobot."""
        _device = OrmDevice.objects.get(name=self.name)
        if attrs.get("comments"):
            _device.comments = attrs["comments"]
        if attrs.get("node_id"):
            _device.custom_field_data["node-id"] = attrs["node_id"]
        _device.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete Device object in Nautobot."""
        self.diffsync.job.log_warning(f"Device {self.name} will be deleted.")
        _device = OrmDevice.objects.get(name=self.get_identifiers()["name"])
        _device.delete()
        return super().delete()


class NautobotInterfaceTemplate(InterfaceTemplate):
    """Nautobot implementation of the InterfaceTemplate Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create InterfaceTemplate object in Nautobot."""
        _interfacetemplate = OrmInterfaceTemplate(
            device_type=OrmDeviceType.objects.get(model=ids["device_type"]),
            name=ids["name"],
            type=ids["type"],
            description=attrs["description"],
            mgmt_only=attrs["mgmt_only"],
        )
        _interfacetemplate.validated_save()

        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update InterfaceTemplate object in Nautobot."""
        _interfacetemplate = OrmInterfaceTemplate.objects.get(
            name=self.get_identifiers()["name"],
            device_type=OrmDeviceType.objects.get(model=self.get_identifiers()["device_type"]),
        )
        if attrs.get("description"):
            _interfacetemplate.description = attrs["description"]
        if attrs.get("mgmt_only"):
            _interfacetemplate.mgmt_only = attrs["mgmt_only"]
        _interfacetemplate.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete InterfaceTemplate object in Nautobot."""
        self.diffsync.job.log_warning(f"Interface Template {self.name} will be deleted.")
        _interfacetemplate = OrmInterfaceTemplate.objects.get(
            name=self.get_identifiers()["name"],
            device_type=OrmDeviceType.objects.get(model=self.get_identifiers()["device_type"]),
        )
        _interfacetemplate.delete()
        return super().delete()


class NautobotInterface(Interface):
    """Nautobot implementation of the Interface Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Interface object in Nautobot."""

        q = OrmInterface.objects.filter(name=ids["name"], device=OrmDevice.objects.get(name=ids["device"]))
        if q.exists():
            # If interface already exists, then update it instead.
            # This will be the case when first creating devices and the interface templates are created.
            # Without this check, the plugin will attempt to create interfaces that were already created as part of the interface template.
            # This results in a ValidationError: 'Interface with this Device and Name already exists.'
            _interface = OrmInterface.objects.get(name=ids["name"], device=OrmDevice.objects.get(name=ids["device"]))
            if attrs.get("description"):
                _interface.description = attrs["description"]
            _interface.validated_save()

            return super().create(ids=ids, diffsync=diffsync, attrs=attrs)
        else:
            _interface = OrmInterface(
                name=ids["name"], device=OrmDevice.objects.get(name=ids["device"]), description=attrs["description"]
            )
            _interface.validated_save()

            return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update Interface object in Nautobot."""
        _interface = OrmInterface.objects.get(
            name=self.get_identifiers()["name"], device=OrmDevice.objects.get(name=self.get_identifiers()["device"])
        )
        if attrs.get("description"):
            _interface.description = attrs["description"]
        _interface.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete DeviceType object in Nautobot."""
        self.diffsync.job.log_warning(f"Interface {self.name} will be deleted.")
        _interface = OrmInterface.objects.get(
            name=self.get_identifiers()["name"], device=OrmDevice.objects.get(device=self.get_identifiers()["device"])
        )
        _interface.delete()
        return super().delete()


class NautobotIPAddress(IPAddress):
    """Nautobot implementation of the IPAddress Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create IPAddress object in Nautobot."""
        logging.debug(f"DEVICE: {attrs['device']}")
        if attrs["device"] and attrs["interface"]:
            obj_type = ContentType.objects.get(model="interface")
            obj_id = OrmDevice.objects.get(name=attrs["device"]).interfaces.get(name=attrs["interface"]).id
        else:
            obj_type = None
            obj_id = None
        if attrs["tenant"]:
            tenant_name = OrmTenant.objects.get(name=attrs["tenant"])
        else:
            tenant_name = None
        _ipaddress = OrmIPAddress(
            address=ids["address"],
            status=Status.objects.get(name=ids["status"]),
            description=attrs["description"],
            tenant=tenant_name,
            assigned_object_type=obj_type,
            assigned_object_id=obj_id,
        )
        _ipaddress.tags.add(Tag.objects.get(slug=PLUGIN_CFG.get("tag").lower().replace(" ", "-")))
        _ipaddress.validated_save()
        # Update device with newly created address in the "Primary IPv4 field"
        if attrs["device"]:
            device = OrmDevice.objects.get(name=attrs["device"])
            device.primary_ip4 = OrmIPAddress.objects.get(address=ids["address"])
            device.save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update IPAddress object in Nautobot."""
        _ipaddress = OrmIPAddress.objects.get(address=self.address)
        if attrs.get("description"):
            _ipaddress.description = attrs["description"]
        if attrs.get("tenant"):
            _ipaddress.tenant = OrmTenant.objects.get(name=attrs["tenant"])
        if attrs.get("device") and attrs.get("interface"):
            _ipaddress.assigned_object_type = ContentType.objects.get(model="interface")
            _ipaddress.assigned_object_id = (
                OrmDevice.objects.get(name=attrs["device"]).interfaces.get(name=attrs["interface"]).id
            )
        _ipaddress.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete IPAddress object in Nautobot."""
        self.diffsync.job.log_warning(f"IP Address {self.address} will be deleted.")
        _ipaddress = OrmIPAddress.objects.get(address=self.get_identifiers()["address"])
        _ipaddress.delete()
        return super().delete()


class NautobotPrefix(Prefix):
    """Nautobot implementation of the Prefix Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Prefix object in Nautobot."""
        _prefix = OrmPrefix(
            prefix=ids["prefix"],
            status=Status.objects.get(name=ids["status"]),
            description=attrs["description"],
            tenant=OrmTenant.objects.get(name=attrs["tenant"]),
            site=Site.objects.get(name=PLUGIN_CFG.get("site")),
        )
        _prefix.tags.add(Tag.objects.get(slug=PLUGIN_CFG.get("tag").lower().replace(" ", "-")))
        _prefix.validated_save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update Prefix object in Nautobot."""
        _prefix = OrmPrefix.objects.get(prefix=self.prefix)
        if attrs.get("description"):
            _prefix.description = attrs["description"]
        if attrs.get("tenant"):
            _prefix.tenant = OrmTenant.objects.get(name=attrs["tenant"])
        _prefix.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete Prefix object in Nautobot."""
        self.diffsync.job.log_warning(f"Prefix {self.prefix} will be deleted.")
        _prefix = OrmPrefix.objects.get(prefix=self.get_identifiers()["prefix"])
        _prefix.delete()
        return super().delete()


NautobotDevice.update_forward_refs()
NautobotDeviceType.update_forward_refs()

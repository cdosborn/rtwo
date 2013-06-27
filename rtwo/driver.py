"""
Atmosphere service driver.

Driver classes define interfaces and implement functionality using providers.
"""
from abc import ABCMeta, abstractmethod
import copy
from datetime import datetime
import sys
import time

from libcloud.compute.deployment import ScriptDeployment
from libcloud.compute.deployment import MultiStepDeployment
from libcloud.compute.types import DeploymentError

from threepio import logger

from rtwo import settings
from rtwo.drivers.common import LoggedScriptDeployment

from rtwo.exceptions import MissingArgsException, ServiceException

from rtwo.provider import AWSProvider
from rtwo.provider import EucaProvider
from rtwo.provider import OSProvider

from rtwo.identity import AWSIdentity
from rtwo.identity import EucaIdentity
from rtwo.identity import OSIdentity

from rtwo.mixins.driver import APIFilterMixin, MetaMixin,\
    InstanceActionMixin


class BaseDriver():
    """
    BaseDriver lists a basic set of expected functionality for an esh-driver.
    Abstract class - Should not be instantiated!!
    """

    __metaclass__ = ABCMeta

    _connection = None

    identity = None

    provider = None

    identityCls = None

    providerCls = None

    @abstractmethod
    def __init__(self, identity, provider):
        raise NotImplementedError

    @abstractmethod
    def list_instances(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def list_machines(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def list_sizes(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def list_locations(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def create_instance(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def deploy_instance(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def reboot_instance(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def destroy_instance(self, *args, **kwargs):
        raise NotImplementedError

    def start_instance(self, *args, **kwargs):
        raise NotImplementedError

    def stop_instance(self, *args, **kwargs):
        raise NotImplementedError

    def resume_instance(self, *args, **kwargs):
        raise NotImplementedError

    def suspend_instance(self, *args, **kwargs):
        raise NotImplementedError

    def resize_instance(self, *args, **kwargs):
        raise NotImplementedError


class VolumeDriver():
    """
    VolumeDriver provides basic storage volume functionality for libcloud
    or esh-drivers.
    Abstract class - Should not be instantiated!!
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def list_volumes(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def create_volume(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def destroy_volume(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def attach_volume(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def detach_volume(self, *args, **kwargs):
        raise NotImplementedError


class LibcloudDriver(BaseDriver, VolumeDriver, APIFilterMixin):
    """
    Provides direct access to the libcloud methods and data.
    """

    def __init__(self, provider, identity):
        if provider is None or identity is None:
            raise MissingArgsException(
                'LibcloudDriver is Missing Required Identity and/or Provider.')
        self.identity = identity
        self.provider = provider
        self._connection = self.provider.get_driver(self.identity)

    def list_instances(self, *args, **kwargs):
        return self._connection.list_nodes()

    def list_machines(self, *args, **kwargs):
        return self._connection.list_images()

    def list_sizes(self, *args, **kwargs):
        return self._connection.list_sizes()

    def list_locations(self, *args, **kwargs):
        return self._connection.list_locations()

    def create_instance(self, *args, **kwargs):
        return self._connection.create_node(*args, **kwargs)

    def deploy_instance(self, *args, **kwargs):
        return self._connection.deploy_node(*args, **kwargs)

    def reboot_instance(self, *args, **kwargs):
        return self._connection.reboot_node(*args, **kwargs)

    def destroy_instance(self, *args, **kwargs):
        return self._connection.destroy_node(*args, **kwargs)

    def list_volumes(self, *args, **kwargs):
        return self._connection.list_volumes(*args, **kwargs)

    def create_volume(self, *args, **kwargs):
        return self._connection.create_volume(*args, **kwargs)

    def destroy_volume(self, *args, **kwargs):
        return self._connection.destroy_volume(*args, **kwargs)

    def attach_volume(self, *args, **kwargs):
        return self._connection.attach_volume(*args, **kwargs)

    def detach_volume(self, *args, **kwargs):
        return self._connection.detach_volume(*args, **kwargs)


class EshDriver(LibcloudDriver, MetaMixin):
    """
    """

    @classmethod
    def settings_init(cls):
        raise ServiceException('Settings init not available for this class')

    def __init__(self, provider, identity):
        super(EshDriver, self).__init__(provider, identity)
        if not(isinstance(provider, self.providerCls)
           and isinstance(identity, self.identityCls)):
            raise ServiceException('Wrong Provider or Identity')

    def list_instances(self, *args, **kwargs):
        """
        Return the InstanceClass representation of a libcloud node
        """
        return self.provider.instanceCls.get_instances(
            super(EshDriver, self).list_instances())

    def list_machines(self, *args, **kwargs):
        """
        Return the MachineClass representation of a libcloud NodeImage
        """
        return self.provider.machineCls.get_machines(
            super(EshDriver, self).list_machines)

    def list_sizes(self, *args, **kwargs):
        """
        Return the SizeClass representation of a libcloud NodeSize
        """
        return self.provider.sizeCls.get_sizes(
            super(EshDriver, self).list_sizes)

    def list_locations(self, *args, **kwargs):
        return super(EshDriver, self).list_locations()

    def create_instance(self, *args, **kwargs):
        """
        Return the InstanceClass representation of a libcloud node
        """
        logger.debug(str(args))
        logger.debug(str(kwargs))
        return self.provider.instanceCls(
            super(EshDriver, self).create_instance(*args, **kwargs))

    def deploy_instance(self, *args, **kwargs):
        return self.provider.instanceCls(
            super(EshDriver, self).deploy_instance(*args, **kwargs))

    def reboot_instance(self, *args, **kwargs):
        return super(EshDriver, self).reboot_instance(*args, **kwargs)

    def start_instance(self, *args, **kwargs):
        return super(EshDriver, self).start_instance(*args, **kwargs)

    def stop_instance(self, *args, **kwargs):
        return super(EshDriver, self).stop_instance(*args, **kwargs)

    def resume_instance(self, *args, **kwargs):
        return super(EshDriver, self).resume_instance(*args, **kwargs)

    def suspend_instance(self, *args, **kwargs):
        return super(EshDriver, self).suspend_instance(*args, **kwargs)

    def destroy_instance(self, *args, **kwargs):
        return super(EshDriver, self).destroy_instance(*args, **kwargs)

    def list_volumes(self, *args, **kwargs):
        return self.provider.volumeCls.get_volumes(
            super(EshDriver, self).list_volumes(*args, **kwargs))

    def create_volume(self, *args, **kwargs):
        return super(EshDriver, self).create_volume(*args, **kwargs)

    def destroy_volume(self, *args, **kwargs):
        return super(EshDriver, self).destroy_volume(*args, **kwargs)

    def attach_volume(self, *args, **kwargs):
        return super(EshDriver, self).attach_volume(*args, **kwargs)

    def detach_volume(self, *args, **kwargs):
        return super(EshDriver, self).detach_volume(*args, **kwargs)


class OSDriver(EshDriver, InstanceActionMixin):
    """
    """
    providerCls = OSProvider

    identityCls = OSIdentity

    @classmethod
    def settings_init(cls):
        os_args = copy.deepcopy(settings.OPENSTACK_ARGS)
        try:
            username = os_args.pop('username')
            password = os_args.pop('password')
            tenant_name = os_args.pop('tenant_name')
        except:
            raise ServiceException(
                'Settings init not available for this class:'
                'Expected settings.OPENSTACK_ARGS with'
                'username/password/tenant_name fields')
        OSProvider.set_meta()
        provider = OSProvider()
        identity = OSIdentity(provider, username, password,
                              ex_tenant_name=tenant_name,
                              **settings.OPENSTACK_ARGS)
        driver = cls(provider, identity)
        return driver

    def __init__(self, provider, identity):
        super(OSDriver, self).__init__(provider, identity)
        self._connection._ex_force_service_region =\
            settings.OPENSTACK_DEFAULT_REGION
        self._connection.connection.service_region =\
            settings.OPENSTACK_DEFAULT_REGION

    def deploy_init_to(self, *args, **kwargs):
        """
        Creates a multi script deployment to prepare and call
        the latest init script
        TODO: Add versioning for 30+
        """
        if args:
            instance = args[0]
        else:
            raise MissingArgsException("Missing instance argument.")
        if isinstance(self.identity.user, basestring):
            username = self.identity.user
        else:
            # Django.contrib.auth.models.User
            username = self.identity.user.username
        atmo_init = "/usr/sbin/atmo_init_full.py"
        server_atmo_init = "/init_files/30/atmo-init-full.py"
        script_init = ScriptDeployment(
            'if [ ! -d "/var/log/atmo" ];then\n'
            'mkdir -p /var/log/atmo\n'
            'fi\n'
            'if [ ! -f "/var/log/atmo/deploy.log" ]; then\n'
            'touch /var/log/atmo/deploy.log\n'
            'fi',
            name="deploy_init_log.sh")
        script_deps = LoggedScriptDeployment(
            "apt-get update;apt-get install -y emacs vim wget language-pack-en"
            + " make gcc g++ gettext texinfo autoconf automake",
            name="deploy_aptget_update.sh",
            logfile="/var/log/atmo/deploy.log")
        script_wget = LoggedScriptDeployment(
            "wget -O %s %s%s" % (atmo_init, settings.SERVER_URL,
                                 server_atmo_init),
            name='deploy_wget_atmoinit.sh',
            logfile='/var/log/atmo/deploy.log')
        script_chmod = LoggedScriptDeployment(
            "chmod a+x %s" % atmo_init,
            name='deploy_chmod_atmoinit.sh',
            logfile='/var/log/atmo/deploy.log')
        instance_token = kwargs.get('token', '')
        if not instance_token:
            instance_token = instance.id
        awesome_atmo_call = "%s --service_type=%s --service_url=%s"
        awesome_atmo_call += " --server=%s --user_id=%s --token=%s"
        awesome_atmo_call += " --vnc_license=%s"
        awesome_atmo_call %= (
            atmo_init,
            "instance_service_v1",
            settings.INSTANCE_SERVICE_URL,
            settings.SERVER_URL,
            username,
            instance_token,
            settings.ATMOSPHERE_VNC_LICENSE)
        #kludge: weirdness without the str cast...
        str_awesome_atmo_call = str(awesome_atmo_call)
        #logger.debug(isinstance(str_awesome_atmo_call, basestring))
        script_atmo_init = LoggedScriptDeployment(
            str_awesome_atmo_call,
            name='deploy_call_atmoinit.sh',
            logfile='/var/log/atmo/deploy.log')
        msd = MultiStepDeployment([script_init,
                                   script_deps,
                                   script_wget,
                                   script_chmod,
                                   script_atmo_init])
        kwargs.update({'deploy': msd})

        private_key = "/opt/dev/atmosphere/extras/ssh/id_rsa"
        kwargs.update({'ssh_key': private_key})

        kwargs.update({'timeout': 120})

        return self.deploy_to(instance, *args, **kwargs)

    def deploy_to(self, *args, **kwargs):
        """
        Deploy to an instance.
        """
        if args:
            instance = args[0]
        else:
            raise MissingArgsException("Missing instance argument.")
        if not kwargs.get('deploy'):
            raise MissingArgsException("Missing deploy argument.")
        if not kwargs.get('ssh_key'):
            private_key = "/opt/dev/atmosphere/extras/ssh/id_rsa"
            kwargs.update({'ssh_key': private_key})
        if not kwargs.get('timeout'):
            kwargs.update({'timeout': 120})

        username = self.identity.user.username
        logger.info("Attempting deployment to node")
        self._connection.ex_deploy_to_node(instance._node,
                                           *args, **kwargs)
        return True

    def deploy_instance(self, *args, **kwargs):
        """
        Deploy instance.

        NOTE: This is blocking and uses the blocking create_node.
        """
        if not kwargs.get('deploy'):
            raise MissingArgsException("Missing deploy argument.")
        username = self.identity.user.username

        private_key = "/opt/dev/atmosphere/extras/ssh/id_rsa"
        kwargs.update({'ssh_key': private_key})
        kwargs.update({'timeout': 120})

        #cloudinit_script = prepare_cloudinit_script()
        #kwargs.update({'ex_userdata': cloudinit_script})
        try:
            self.deploy_node(*args, **kwargs)
        except DeploymentError as de:
            logger.error(sys.exc_info())
            logger.error(de.value)
            return False
        return True

    def destroy_instance(self, *args, **kwargs):
        return self._connection.destroy_node(*args, **kwargs)

    def start_instance(self, *args, **kwargs):
        return self._connection.ex_start_node(*args, **kwargs)

    def stop_instance(self, *args, **kwargs):
        return self._connection.ex_stop_node(*args, **kwargs)

    def suspend_instance(self, *args, **kwargs):
        return self._connection.ex_suspend_node(*args, **kwargs)

    def resume_instance(self, *args, **kwargs):
        return self._connection.ex_resume_node(*args, **kwargs)

    def resize_instance(self, *args, **kwargs):
        return self._connection.ex_resize(*args, **kwargs)

    def reboot_instance(self, *args, **kwargs):
        return self._connection.reboot_node(*args, **kwargs)

    def confirm_resize_instance(self, *args, **kwargs):
        return self._connection.ex_confirm_resize(*args, **kwargs)

    def revert_resize_instance(self, *args, **kwargs):
        return self._connection.ex_revert_resize(*args, **kwargs)

    def _add_floating_ip(self, instance, *args, **kwargs):
        return self._connection._add_floating_ip(instance, *args, **kwargs)

    def _clean_floating_ip(self, *args, **kwargs):
        return self._connection.ex_clean_floating_ip(**kwargs)

    def _is_active_instance(self, instance):
        #Other things may need to be tested
        status = instance.extra['status']
        task = instance.extra['task']
        power = instance.extra['power']
        if status == 'active':
            #Active, not being deleted or suspended
            if task not in ['deleting', 'suspending']:
                return True
        elif (status == 'build' or status == 'resize') and task != 'deleting':
            #The instance is moving toward an active state
            return True
        return False


class AWSDriver(EshDriver):
    """
    """
    providerCls = AWSProvider

    identityCls = AWSIdentity

    def deploy_instance(self, *args, **kwargs):
        """
        Deploy an AWS node.
        """
        username = self.identity.user.username
        atmo_init = "/usr/sbin/atmo_init_full.py"
        server_atmo_init = "/init_files/30/atmo-init-full.py"
        script_deps = ScriptDeployment(
            "sudo apt-get install -y emacs vim wget")
        script_wget = ScriptDeployment(
            "sudo wget -O %s %s%s" %
            (atmo_init, settings.SERVER_URL, server_atmo_init))
        script_chmod = ScriptDeployment("sudo chmod a+x %s" % atmo_init)
        instance_token = kwargs.get('token', '')
        awesome_atmo_call = "sudo %s --service_type=%s --service_url=%s"
        awesome_atmo_call += " --server=%s --user_id=%s --token=%s &> %s"
        awesome_atmo_call %= (
            atmo_init,
            "instance_service_v1",
            settings.INSTANCE_SERVICE_URL,
            settings.SERVER_URL,
            username,
            instance_token,
            '/var/log/atmo_init_full.err')
        logger.debug(awesome_atmo_call)
        str_awesome_atmo_call = str(awesome_atmo_call)
        #kludge: weirdness without the str cast...
        script_atmo_init = ScriptDeployment(str_awesome_atmo_call)
        private_key = ("/opt/dev/atmosphere/extras/ssh/id_rsa")
        scripts = [script_deps,
                   script_wget,
                   script_chmod,
                   script_atmo_init]
        for s in scripts:
            logger.debug(s.name)
            s.name = s.name.replace('/root', '/home/ubuntu')
            logger.debug(s.name)
        msd = MultiStepDeployment(scripts)
        kwargs.update({'ex_keyname': 'dalloway-key'})
        kwargs.update({'ssh_username': 'ubuntu'})
        kwargs.update({'ssh_key': private_key})
        kwargs.update({'deploy': msd})
        kwargs.update({'timeout': 400})

        instance = super(AWSDriver, self).deploy_instance(*args, **kwargs)
        created = datetime.strptime(instance.extra['created'],
                                    "%Y-%m-%dT%H:%M:%SZ")
        # NOTE: Removed for rtwo port. Moved to service tasks.
        # send_instance_email(username, instance.id, instance.ip,
        # created, username)
        return instance

    def filter_machines(self, machines, black_list=[]):
        """
        Filtered machines:
            Keep the machine if it does NOT match any word in the black_list
        """
        def _filter_machines(ms, cond):
            return [m for m in ms if cond(m)]
        black_list.extend(['bitnami', 'kernel', 'microsoft', 'Windows'])
        filtered_machines = super(AWSDriver, self).filter_machines(
            machines, black_list)
        filtered_machines = _filter_machines(
            filtered_machines,
            lambda(m): any(word in m.alias
                           for word in ['aki-', 'ari-']))
        filtered_ubuntu = _filter_machines(
            filtered_machines,
            lambda(m): any(word == m._image.extra['ownerid']
                           for word in ['099720109477']))
#        filtered_ubuntu = [machine for machine in filtered_machines
#        if any(word == machine._image.extra['ownerid'] for word in
#        ['099720109477'])]
        filtered_amazon = _filter_machines(
            filtered_machines,
            lambda(m): any(word == m._image.extra['owneralias']
                           for word in ['amazon', 'aws-marketplace']))
        filtered_ubuntu.extend(filtered_amazon)
        return filtered_ubuntu  # [-400:] #return filtered[-400:]

    def create_volume(self, *args, **kwargs):
        if 'description' in kwargs:
            kwargs.pop('description')
        return super(EshDriver, self).create_volume(*args, **kwargs)


class EucaDriver(EshDriver):
    """
    """
    providerCls = EucaProvider

    identityCls = EucaIdentity

    def deploy_instance(self, *args, **kwargs):
        raise NotImplementedError

    def resume_instance(self, *args, **kwargs):
        raise NotImplementedError

    def suspend_instance(self, *args, **kwargs):
        raise NotImplementedError

    def start_instance(self, *args, **kwargs):
        raise NotImplementedError

    def stop_instance(self, *args, **kwargs):
        raise NotImplementedError
import requests
import time
"""
Proxmox management API WRAPPER
"""


class NetworkError(RuntimeError):
    pass


class Proxmox:
    def __init__(self, name):
        """
        :param name: Cluster Proxmox
        """
        self.name = name
        self.socket = None
        self.ticket = None
        self.PVEAuthCookie = None
        self.csrf = None
        self.nodes = None
        self.status = None
        self.storage = None
        self.disks = None
        self.qemu = None
        self.config = None

    def get_ticket(self, url, user, password):
        """
        Get a new ticket from Proxmox api
        :param url: Generic ticket url
        :param user: Proxmox user API
        :param password: Proxmox password user API
        """
        request = "https://{0}/api2/json/access/ticket".format(url)
        try:
            self.socket = requests.session()
            params = {'username': user, 'password': password}
            self.ticket = self.socket.post(request,  params=params, verify=False, timeout=5)

            if self.ticket.status_code == 200:
                result = {
                    "result": "OK",
                    "value": self.ticket.json()
                }
                self.PVEAuthCookie = {'PVEAuthCookie': self.ticket.json()['data']['ticket']}
                self.csrf = {'CSRFPreventionToken': self.ticket.json()['data']['CSRFPreventionToken']}
            else:
                result = {
                    "result": "ERROR",
                    "target": "{0}".format(request),
                    "type": "PROXMOX - STATUS CODE",
                    "value": "Error nodes informations. Bad HTTP Status code : "
                             "{0} -- {1}".format(self.ticket.status_code, self.ticket.text)
                }
        except (TypeError, ValueError, requests.exceptions.RequestException) as e:
            result = {
                "result": "ERROR",
                "target": "{0}".format(url),
                "type": "PYTHON",
                "value": "Cannot get ticket session {0} ({1})".format(url, e)
            }

        return result

    def get_nodes(self, url):
        """
        Get Nodes from cluster
        :param url: Generic node url (node = physical hypervisor)
        """
        request = "https://{0}/api2/json/nodes".format(url)
        try:
            nodes = self.nodes = self.socket.get(request,
                                                 cookies=self.PVEAuthCookie,
                                                 verify=False, timeout=5)

            if nodes.status_code == 200:
                result = {
                    "result": "OK",
                    "value": nodes.json()
                }
            else:
                result = {
                    "result": "ERROR",
                    "target": "{0}".format(request),
                    "type": "PROXMOX - STATUS CODE",
                    "value": "Error nodes informations. Bad HTTP Status code : "
                                   "{0} -- {1}".format(nodes.status_code, nodes.text)
                }

        except (TypeError, ValueError, requests.exceptions.RequestException) as e:
            result = {
                "result": "ERROR",
                "target": "{0}".format(request),
                "type": "PYTHON",
                "value": "Cannot get node information for {0} ({1})".format(url, e)
            }

        return result

    def get_clusters(self, url):
        """
        Get Nodes from cluster
        :param url: Generic node url (node = physical hypervisor)
        """
        request = "https://{0}/api2/json/clusters/status".format(url)
        try:
            nodes = self.nodes = self.socket.get(request,
                                                 cookies=self.PVEAuthCookie,
                                                 verify=False, timeout=5)

            if nodes.status_code == 200:
                result = {
                    "result": "OK",
                    "value": nodes.json()
                }
            else:
                result = {
                    "result": "ERROR",
                    "target": "{0}".format(request),
                    "type": "PROXMOX - STATUS CODE",
                    "value": "Error nodes informations. Bad HTTP Status code : "
                                   "{0} -- {1}".format(nodes.status_code, nodes.text)
                }

        except (TypeError, ValueError, requests.exceptions.RequestException) as e:
            result = {
                "result": "ERROR",
                "target": "{0}".format(request),
                "type": "PYTHON",
                "value": "Cannot get node information for {0} ({1})".format(url, e)
            }

        return result

    def get_status(self, url, nodename):
        """
        Get node informations
        :param url: Generic node url
        :param nodename: Node name (not int id)
        """
        request = "https://{0}/api2/json/nodes/{1}/status".format(url, nodename)
        try:
            self.status = self.socket.get(request, cookies=self.PVEAuthCookie, verify=False, timeout=5).json()
            result = {
                "result": "OK",
                "value": self.status

            }
        except (TypeError, ValueError, requests.exceptions.RequestException) as e:
            result = {
                "result": "ERROR",
                "target": "{0}".format(nodename),
                "type": "PYTHON - ERROR",
                "value": "Cannot get node information for {0} ({1})".format(url, e)
            }

        return result

    def get_storages(self, url, nodename):
        """
        Get Storage from nodes
        :param url: Generic storage url
        :param nodename: Node name (no int id)
        """
        request = "https://{0}/api2/json/nodes/{1}/storage".format(url, nodename)
        try:
            self.storage = self.socket.get(request,  cookies=self.PVEAuthCookie, verify=False, timeout=5).json()
            result = {
                "result": "OK",
                "value": self.storage
            }
        except (TypeError, ValueError, requests.exceptions.RequestException) as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - ERROR",
                "target": "{0}".format(nodename),
                "value": "Cannot get storage information for {0} ({1})".format(url, e)
            }

        return result

    def get_disks(self, url, nodename, sto_id):
        """
        Get VMs disk from storages
        :param url: Generic content url
        :param nodename: Node name (no int id)
        :param sto_id: Storage name (no int id)
        """
        request = "https://{0}/api2/json/nodes/{1}/storage/{2}/content".format(url, nodename, sto_id)
        try:
            self.disks = self.socket.get(request,  cookies=self.PVEAuthCookie, verify=False, timeout=5).json()
            result = {
                "result": "OK",
                "value": self.disks
            }
        except (TypeError, ValueError, requests.exceptions.RequestException) as e:
            result = {
                "result": "ERROR",
                "type": "PYTHON - ERROR",
                "target": "{0}".format(nodename),
                "value": "Cannot get disks information for {0} ({1})".format(url, e)
            }

        return result

    def get_instance(self, url, nodename, category):
        """
        Get basic VMs informations from nodes
        :param url: Generic qemu url
        :param nodename: Node name (not int id)
        :param category: lxc or qemu
        """
        request = "https://{0}/api2/json/nodes/{1}/{2}".format(url, nodename, category)
        try:
            instances = self.socket.get(request,
                                        cookies=self.PVEAuthCookie,
                                        verify=False, timeout=5)

            if instances.status_code == 200:
                result = {
                    "result": "OK",
                    "value": instances.json()
                }
            else:
                result = {
                    "result": "ERROR",
                    "target": "{0}".format(url),
                    "type": "PROXMOX - STATUS CODE",
                    "value": "Error nodes informations. Bad HTTP Status code : "
                                   "{0} -- {1}".format(instances.status_code, instances.text)
                }
        except (TypeError, ValueError, requests.exceptions.RequestException) as e:
            result = {
                "result": "ERROR",
                "target": "{0}".format(url),
                "type": "PYTHON",
                "value": "Cannot get VM information for {0} {1} ({2})".format(url, nodename, e)
            }

        return result

    def get_config(self, url, nodename, category, instanceid):
        """
        Get avanced VM information from nodes
        :param url: Generic qemu config url
        :param category: lxc or qemu
        :param nodename: Node name (not int id)
        :param instanceid: VM id (int id)
        """
        request = "https://{0}/api2/json/nodes/{1}/{2}/{3}/config".format(url, nodename, category, instanceid)
        try:
            config = self.socket.get(request,  cookies=self.PVEAuthCookie, verify=False, timeout=5)
            if config.status_code == 200:
                result = {
                    "result": "OK",
                    "value": config.json()
                }
            else:
                result = {
                    "result": "ERROR",
                    "target": "{0}".format(url),
                    "type": "PROXMOX - STATUS CODE",
                    "value": "Error nodes informations. Bad HTTP Status code : "
                                   "{0} -- {1}".format(config.status_code, config.text)
                }
        except (TypeError, ValueError, requests.exceptions.RequestException) as e:
                result = {
                    "result": "ERROR",
                    "target": "{0}".format(url),
                    "type": "PYTHON",
                    "value": "Cannot get VM information for {0} {1} ({2})".format(url, nodename, e)
                }

        return result

    def create_instance(self, url, nodename, category, data):
        """
        :param url: 
        :param nodename: 
        :param category: 
        :param data: 
        :return: 
        """
        request = "https://{0}/api2/json/nodes/{1}/{2}".format(url, nodename, category)
        try:
            createvm = self.socket.post(request,
                                        data=data,
                                        headers=self.csrf,
                                        cookies=self.PVEAuthCookie,
                                        verify=False,
                                        timeout=5)

            if createvm.status_code == 200:
                result = {
                    "result": "OK",
                    "value": createvm.json()
                }
            else:
                result = {
                    "result": "ERROR",
                    "target": "{0}".format(nodename),
                    "type": "PROXMOX - STATUS CODE",
                    "value": "Error creating Container. Bad HTTP Status code : "
                                   "{0} -- {1} -- with data: {2} -- Possible problem: Duplicate entry".format(createvm.status_code, createvm.text, data)
                }

        except (TypeError, ValueError, requests.exceptions.RequestException) as e:
            result = {"result": "ERROR",
                      "target": "{0}".format(nodename),
                      "type": "PYTHON",
                      "value": "Cannot create this instance on {0} : ({1})".format(url, e)}

        return result

    def delete_instance(self, url, nodename, category, vmid):
        """
        :param url: 
        :param nodename: 
        :param category: 
        :param vmid:
        :return: 
        """
        request = "https://{0}/api2/json/nodes/{1}/{2}/{3}".format(url, nodename, category, vmid)
        try:
            deletevm = self.socket.delete(request,
                                          headers=self.csrf,
                                          cookies=self.PVEAuthCookie,
                                          verify=False,
                                          timeout=5
                                          )

            if deletevm.status_code == 200:
                result = {
                    "result": "OK",
                    "value": deletevm.json()
                }

            else:
                result = {
                    "result": "ERROR",
                    "target": "{0}".format(nodename),
                    "type": "PROXMOX - STATUS CODE",
                    "value": "Error delete Container. Bad HTTP Status code : "
                                   "{0} -- {1}".format(deletevm.status_code, deletevm.text)
                }

        except (TypeError, ValueError, requests.exceptions.RequestException) as e:
            result = {"result": "ERROR",
                      "target": "{0}".format(nodename),
                      "type": "PYTHON",
                      "value": "Cannot delete Container ({2}) on {0} : ({1})".format(url, e, vmid)}

        return result

    def status_instance(self, url, nodename, category, vmid, action):
        """
        :param url: 
        :param nodename: 
        :param category: 
        :param vmid:
        :param action:
        :return: 
        """
        request = "https://{0}/api2/json/nodes/{1}/{2}/{3}/status/{4}".format(url, nodename, category, vmid, action)
        try:
            if action == "current":
                statusm = self.socket.get(request,
                                          cookies=self.PVEAuthCookie,
                                          verify=False,
                                          timeout=5)
            else:
                statusm = self.socket.post(request,
                                           headers=self.csrf,
                                           cookies=self.PVEAuthCookie,
                                           verify=False,
                                           timeout=5)

            if statusm.status_code == 200:
                result = {
                    "result": "OK",
                    "value": statusm.json()
                }
            else:
                result = {
                    "result": "ERROR",
                    "target": "{0}".format(nodename),
                    "type": "PROXMOX - STATUS CODE",
                    "value": "Error action Container. Bad HTTP Status code : "
                                   "{0} -- {1}".format(statusm.status_code, statusm.text)
                }

        except (TypeError, ValueError, requests.exceptions.RequestException) as e:
            result = {"result": "ERROR",
                      "target": "{0}".format(nodename),
                      "type": "PYTHON",
                      "value": "Cannot do this action this instance ({2}) on {0} : ({1})".format(url, e, vmid)}

        return result

    def resize_instance(self, url, nodename, category, instanceid, data):
        """
        :param url: 
        :param nodename: 
        :param category: 
        :param instanceid: 
        :param data: 
        :return: 
        """
        request = "https://{0}/api2/json/nodes/{1}/{2}/{3}/config".format(url, nodename, category, instanceid)
        try:
            resizevm = self.socket.put(request,
                                       data=data,
                                       headers=self.csrf,
                                       cookies=self.PVEAuthCookie,
                                       verify=False,
                                       timeout=5)

            if resizevm.status_code == 200:
                result = {
                    "result": "OK",
                    "value": resizevm.json()
                }
            else:
                result = {
                    "result": "ERROR",
                    "target": "{0}".format(nodename),
                    "type": "PROXMOX - STATUS CODE",
                    "value": "Error resizing container. Bad HTTP Status code : "
                                   "{0} -- {1}".format(resizevm.status_code, resizevm.text)
                }
        except (TypeError, ValueError, requests.exceptions.RequestException) as e:
                result = {
                    "result": "ERROR",
                    "target": "{0}".format(nodename),
                    "type": "PYTHON",
                    "value": "Cannot resize this instance {2} on {0} : ({1})".format(url, e, instanceid)
                }

        return result

    def stats_instance(self, url, nodename, category, instanceid):
        """
        :param url: 
        :param nodename: 
        :param category: 
        :param instanceid: 
        :return: 
        """
        request = "https://{0}/api2/json/nodes/{1}/{2}/{3}/rrddata".format(url, nodename, category, instanceid)
        try:
            statsvm = self.socket.get(request, cookies=self.PVEAuthCookie, verify=False, timeout=5)

            if statsvm.status_code == 200:
                result = {
                    "result": "OK",
                    "value": statsvm.json()
                }
            else:
                result = {
                    "result": "ERROR",
                    "target": "{0}".format(nodename),
                    "type": "PROXMOX - STATUS CODE",
                    "value": "Error to find statistic for instance {2}. Bad HTTP Status code : "
                                   "{0} -- {1}".format(statsvm.status_code, statsvm.text, instanceid)
                }
        except (TypeError, ValueError, requests.exceptions.RequestException) as e:
            result = {
                "result": "ERROR",
                "target": "{0}".format(nodename),
                "type": "PYTHON",
                "value": "Cannot find statistic for this instance {2} on {0} : ({1})".format(url, e, instanceid)
            }

        return result

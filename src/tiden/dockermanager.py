from os.path import basename
from pprint import PrettyPrinter
from re import match
from uuid import uuid4

from .tidenexception import *
from .util import *


class DockerManager:
    """
    Common actions with docker
    """

    def __init__(self, config, ssh):
        self.ssh = ssh
        self.config = config
        self.running_containers = {}

    def remove_all_containers(self):
        """
        Delete all containers from all hosts
        """
        self.running_containers = {}
        log_print("Remove all running containers")
        cmd = "docker rm -f $(docker ps -aq)"
        self.ssh.exec([cmd])

    def kill_running_containers(self):
        """
        Kill running containers from all hosts
        """
        self.running_containers = {}
        log_print("Kill running containers")
        cmd = "docker kill $(docker ps -q)"
        self.ssh.exec([cmd])

    def prune(self):
        """
        Delete all images/caches/networks from all hosts
        """
        log_print("Clean all host docker data")
        cmd = "docker system prune -fa"
        self.ssh.exec([cmd])

    def clean_host(self):
        """
        Delete all docker data from each host
        :return:
        """
        self.remove_all_containers()
        self.prune()

    def get_containers_info(self, additional_key=''):
        """
        Get information about all running container for all hosts

        :return:    list({
                            "id": container id,
                            "image": image name,
                            "status": container status,
                            "name": container name
                        }, ...)
        """
        res = self.ssh.exec([
            'docker ps --format "{{.ID}} | {{.Image}} | {{.Status}} | {{.Names}} | {{.Ports}}" '+additional_key + ' -a'
        ])
        running_containers = {}
        for host, out in res.items():
            rows = out[0].split("\n")[:-1]
            for row in rows:
                if match(".*\|.*\|.*\|.*\|.*", row):
                    info_list = [item.strip() for item in row.split("|")]
                    info = {
                        "id": info_list[0],
                        'image': info_list[1],
                        'status': info_list[2],
                        'name': info_list[3],
                        'port': info_list[4]
                    }
                    running_containers[host] = running_containers.get(host, []) + [info]
        return running_containers

    def get_all_containers(self, host=None):
        containers = self.get_containers_info(additional_key='-f "status=exited"')
        all_running_containers = self.get_running_containers(host)
        return all_running_containers, containers


    def get_running_containers(self, host=None, predicate=lambda x: True):
        all_running_containers = dict()
        containers = self.get_containers_info()
        # get running containers
        for current_host in containers.keys():
            running_containers = [container for container in containers.get(current_host)
                                  if 'Up' in container.get('status') and predicate(container)]
            if running_containers:
                all_running_containers[current_host] = running_containers

        return all_running_containers if not host else all_running_containers.get(host)

    def remove_containers(self, host=None, name=None, name_pattern=None, image_name=None):
        """
        Remove containers from host
        :param host:                host with expected containers  (otherwise containers will be searching on all hosts)
        :param name:                whole container name
        :param name_pattern:        name pattern
        :return:                    list: removed containers
        """
        hosts = self.get_containers_info()
        removed_containers = []
        for _host, containers in hosts.items():
            if host is not None and _host != host:
                continue
            for container in containers:
                if name is not None and name != container['name']:
                    continue
                elif name_pattern is not None and not match(name_pattern, container['name']):
                    continue
                elif image_name is not None and image_name != container['image']:
                    continue
                log_print("Remove container '{}' on host {}".format(container['name'], _host))
                self.ssh.exec_on_host(_host, ['docker rm -f {}'.format(container['id'])])
                if _host in self.running_containers and container['name'] in self.running_containers[_host]:
                    del self.running_containers[_host][container['name']]
                removed_containers.append(container)
        return removed_containers

    def get_pulled_images(self):
        """
        Get information about all pulled images for all hosts

        :return:    list({
                            "id": "[container_id]",
                            "name": "[repository]:[tag]",
                        }, ...)
        """
        res = self.ssh.exec(['docker images --format "{{.ID}} | {{.Repository}} | {{.Tag}}"'])
        pulled_images = {}
        for host, out in res.items():
            rows = out[0].split("\n")[:-1]
            for row in rows:
                if match(".*\|.*\|.*", row):
                    info_list = [item.strip() for item in row.split("|")]
                    info = {
                        "id": info_list[0],
                        'name': '{}:{}'.format(info_list[1], info_list[2])
                    }
                    pulled_images[host] = pulled_images.get(host, []) + [info]
        return pulled_images

    def remove_images(self, host=None, name=None, name_pattern=None):
        """
        Remove containers from host
        :param host:                host with expected image (otherwise images will be searching on all hosts)
        :param name:                whole image name
        :param name_pattern:        name pattern
        :return:                    list: removed images
        """
        hosts = self.get_pulled_images()
        removed_images = []
        for _host, images in hosts.items():
            if host is not None and _host != host:
                continue
            for image in images:
                if name is not None and name != image['name']:
                    continue
                elif name_pattern is not None and not match(name_pattern, image['name']):
                    continue
                log_print("Remove image '{}' on host {}".format(image['name'], _host))
                self.ssh.exec_on_host(_host, ['docker rmi -f {}'.format(image['id'])])
                removed_images.append(image)
        return removed_images

    def image(self, artifact_name):
        """
        Find image name by artifact name
        """
        artifact = self.config["artifacts"][artifact_name]
        if artifact["type"] == "image_dump":
            path = artifact["glob_path"]
            file_name = basename(path)
            if '.' in file_name:
                image_name = file_name[:file_name.rindex(".")]
            else:
                image_name = file_name
            return image_name

    def wait_for_text(self, host, log_file, grep_text, compare, timeout=60, interval=1, strict=True):
        """
        Waiting for expected text in log file

        :param host:        host where collecting all data
        :param log_file:    log file path where need to find expected text
        :param grep_text:   grep pattern for searched file lines
        :param compare:     compare functions which decide searched condition
        :param timeout:     timeout for wait
        :param interval:    time between compare function execute
        :param strict:      throw exception if searched time is up
        :return:            True - condition was correct
                            False - can't wait for condition execute
        """
        cmd = "grep '{}' {}".format(grep_text, log_file)
        end_time = time() + timeout
        while True:
            output = self.ssh.exec_on_host(host, [cmd])[host]
            last_line = output[-1:][0] if output else ""
            if compare(last_line):
                return True
            if time() > end_time:
                if strict:
                    raise AssertionError("Can't wait '{}' on {} in '{}' log".format(grep_text, host, log_file))
                else:
                    return False
            sleep(interval)

    def load_images(self, artifacts_filter=None):
        """
        Unpack image on host from archive

        :param artifacts_filter     str regex to filter artifacts for load
        """
        log_print("Unpack images")
        load_cmd = "docker image load -i {}"
        packed_image_paths = []
        for name, artifact in self.config["artifacts"].items():
            if artifacts_filter is not None:
                if not search(artifacts_filter, name):
                    continue
            if artifact.get("type") != "image_dump":
                continue
            packed_image_paths.append(artifact["remote_path"])
        if not packed_image_paths:
            return
        commands = [load_cmd.format(path) for path in packed_image_paths]
        self.ssh.exec(commands)

    def run(self, image_name, host, **kwargs):
        """
        Run container from image
        Log all container data into log

        :param image_name:      source image name
        :param host:            host where need to run container
        :param kwargs:          tag - custom image tag
                                network - select different network
                                kw_params - custom params (--param_key param_value)
                                commands -  commands list which need to after image start
                                            and declare which process would be main in container
                                volume - map directory in container
                                params - custom params (-i, -t)

        :return:                tuple(Image ID, log file path, image name)
        """

        run_command = "docker run -d {params} {kw_params} {image} {commands}"
        params = ""
        kw_params = ""
        commands = ""
        image = image_name

        # setting up unique image name (adding UUID4 at the name end)
        _kw_params = kwargs.get("kw_params", {})
        base_name = _kw_params["name"] if _kw_params.get("name") else image_name
        container_name = "{}-{}".format(base_name.replace('/', '-'), str(uuid4())[:8])
        _kw_params["name"] = container_name
        kwargs["kw_params"] = _kw_params

        if kwargs.get("tag"):
            image = "{}:{}".format(image_name, kwargs["tag"])
        if kwargs.get("network"):
            kw = kwargs.get("kw_params", {})
            kw["network"] = kwargs["network"]
            kwargs["kw_params"] = kw
        if kwargs.get('ports'):
            kwargs['skw_params'] = kwargs.get('skw_params', [])
            for host_port, container_port in kwargs['ports']:
                kwargs['skw_params'].append(('p', '{}:{}'.format(host_port, container_port)))
        if kwargs.get("kw_params"):
            param_list = []
            iter_params = [kwargs.get("kw_params", {}).items(), kwargs.get("skw_params", [])]
            for iter_param in iter_params:
                for key, value in iter_param:
                    special_symbol = '' if len(key) == 1 else '-'
                    param_list.append("{}-{} {}".format(special_symbol, key, value))
            kw_params += ' '.join(param_list)
        if kwargs.get("commands"):
            commands = " ".join(kwargs["commands"])
        if kwargs.get("volume"):
            param = []
            for local_dir, container_dir in kwargs["volume"].items():
                param.append("-v {}:{}".format(local_dir, container_dir))
            kw_params = "{} {}".format(kw_params, " ".join(param))
        if kwargs.get("params"):
            params = "-{}".format("".join(kwargs))

        cmd = run_command.format(params=params,
                                 kw_params=kw_params,
                                 image=image,
                                 commands=commands)

        log_print("Running container '{}' from image '{}' on {}".format(container_name, image_name, host))
        output = self.ssh.exec_on_host(host, [cmd])[host]
        if len(output) != 1:
            raise AssertionError("Can't run image {} on host:\n{}".format(image_name, host, "".join(output)))

        last_line = output[-1:][0]
        image_id = last_line.replace("\n", "")
        assert len(image_id) > 30, "Image ID is not correct: '{}'".format(image_id)

        # log container output
        logs_dir = self.config["rt"]["remote"]["test_dir"]
        log_file = "{}/{}".format(logs_dir, "{}.log".format(container_name))
        write_logs_command = "cd {log_dir}; " \
                             "nohup " \
                             "  docker logs -f {image} " \
                             "> {log} 2>&1 &".format(log_dir=logs_dir,
                                                     image=image_id,
                                                     log=log_file)
        self.ssh.exec_on_host(host, [write_logs_command])
        return image_id, log_file, kwargs["kw_params"]["name"]

    def exec_in_container(self, cmd, container):
        """
        Execute command into container
        :param cmd:             command
        :param container:       container object
        :return:                command output
        """
        exec_cmd = "docker exec {} {}".format(container["id"], cmd)
        output = self.ssh.exec_on_host(container["host"], [exec_cmd])[container["host"]]
        return output[0] if len(output) == 1 else ""

    def _find_host(self, searched_container):
        """
        Find host by container name
        :param searched_container:  container obj
        :return:                    host address
        """
        for host, images in self.running_containers.items():
            for name, image in images.items():
                if image["id"] == searched_container["id"]:
                    return host
        raise AssertionError("Can't find image {} ({}) in running pool".format(searched_container["name"],
                                                                               searched_container["id"]))

    def get_logs(self, container):
        """
        Finding container logs
        :param container:   container onj
        :return:            logs result
        """
        cmd = 'cat {}'.format(container["log"])
        host = self._find_host(container)
        return self.ssh.exec_on_host(host, [cmd])[host]

    def _finds(self, items, condition):
        """
        filter containers by condition
        :param items:       where need to search
        :param condition:   condition to decide
        :return:            found items list
        """
        result = []
        for host, images in items.items():
            for name, image in images.items():
                if condition(image):
                    result.append(image)
        return result

    def find(self, items, condition):
        """
        Find first item which satisfied the condition
        :param items:       where need to search
        :param condition:
        :return:
        """
        result = self._finds(items, condition)
        return result[0] if result else result

    def find_image_by_type(self, type):
        return self.find(self.running_containers, lambda image: image["type"] == type)

    def find_image_by_name(self, name):
        return self.find(self.running_containers, lambda image: image["name"] == name)

    def remove_container(self, container):
        """
        Remove container from host
        :param container:   str - container name
                            dict - container obj
        """
        if isinstance(container, str):
            container = self.find_image_by_name(container)
        self.remove_containers(host=container["host"], name=container["name"])
        del self.running_containers[container["host"]][container["name"]]

    def check_hosts(self):
        """
        Docker on host must have 'overlay' storage driver
        """
        for host in self.ssh.hosts:
            results = self.ssh.exec_on_host(host, ["docker info"])[host][0]
            for line in results.split("\n"):
                if 'Storage Driver' in line:
                    if 'overlay' not in line:
                        raise TidenException("Host '{}' have no 'overlay' docker "
                                             "storage driver ($ docker info -> Storage Driver:)".format(host))
                    else:
                        break

    def check_docker_on_hosts(self, hosts):
        docker_ps_out = ['CONTAINER', 'ID', 'IMAGE', 'COMMAND', 'CREATED', 'STATUS', 'PORTS', 'NAMES']
        hosts_with_docker = []
        if not isinstance(hosts, list):
            hosts = [hosts]

        for host in hosts:
            results = self.ssh.exec_on_host(host, ["docker ps"])[host][0]
            if len([header_column for header_column in docker_ps_out if header_column in results]) == len(docker_ps_out):
                hosts_with_docker.append(host)

        return hosts_with_docker

    def print_and_terminate_containers(self, need_stop=False):
        def print_warning(running, stop):
            if running:
                log_print('Found running docker containers:', color='red')
                log_print((self.pp.pformat(running)))
            if stop:
                log_print('Found stop docker containers:', color='red')
                log_print(self.pp.pformat(stop))

        running, stop = self.get_all_containers()
        self.pp = PrettyPrinter()
        print_warning(running, stop)
        if running:
            if need_stop:
                log_print('Going to terminate those dockers containers!', color='red')
                self.kill_running_containers()
                running, _ = self.get_all_containers()
                if not len(running):
                    log_print('all containers removed successfully', color='green')
                else:
                    log_print('There are still some containers on hosts', color='red')
                    print_warning(running, None)
                    return len(running)
            else:
                return len(running)
        return -1
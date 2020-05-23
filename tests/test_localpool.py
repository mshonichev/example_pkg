#!/usr/bin/env python3

from tiden.localpool import LocalPool
import os.path


def test_local_pool_exec_on_host_rm_one_file(local_config):
    pool = LocalPool(local_config['ssh'])
    home_path = local_config['environment']['home']
    host = local_config['ssh']['hosts'][0]
    host_home_path = os.path.join(home_path, host)
    file_path = os.path.join(host_home_path, 'test')
    os.makedirs(host_home_path, exist_ok=True)
    with open(file_path, 'w') as f:
        f.close()

    pool.exec_on_host(host, ["rm -rf %s/test" % local_config['environment']['home']])
    assert not os.path.exists(file_path)


def test_local_pool_exec_on_host_rm_files_by_mask(local_config):
    pool = LocalPool(local_config['ssh'])
    home_path = local_config['environment']['home']
    host = local_config['ssh']['hosts'][0]
    host_home_path = os.path.join(home_path, host)
    file1_path = os.path.join(host_home_path, 'test')
    file2_path = os.path.join(host_home_path, 'test')
    os.makedirs(host_home_path, exist_ok=True)
    with open(file1_path, 'w') as f:
        f.close()
    with open(file2_path, 'w') as f:
        f.close()

    pool.exec_on_host(host, ["rm -rf %s/*" % local_config['environment']['home']])
    assert not os.path.exists(file1_path)
    assert not os.path.exists(file2_path)

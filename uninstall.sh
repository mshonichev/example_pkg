#/bin/bash

sudo pip3.7 uninstall -y tiden tiden_gridgain twine keyring keyrings.alt

# remove remnants of previous `setup.py develop`
for script_name in run_tests merge_yaml_reports patch_artifacts_config prepare_apache_ignite_builds; do
  for bin_path in /usr/local/bin /usr/bin ~/.local/bin; do
    if [ -f $bin_path/$script_name.py ]; then
      sudo rm -f $bin_path/$script_name.py
    fi
  done
done

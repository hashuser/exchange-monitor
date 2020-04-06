#!/bin/bash
create_service(){
  touch $(cd "$(dirname "$0")";pwd)/Monitor.service
  cat>$(cd "$(dirname "$0")";pwd)/Monitor.service<<EOF
  [Unit]
  Description=Monitor Service
  After=rc-local.service

  [Service]
  Type=simple
  User=root
  Group=root
  WorkingDirectory=$(cd "$(dirname "$0")";pwd)
  ExecStart=/usr/bin/python3.8 $(cd "$(dirname "$0")";pwd)/core.py
  Restart=always
  TasksMax=infinity

  [Install]
  WantedBy=multi-user.target
EOF
}

install_service(){
  mv $(cd "$(dirname "$0")";pwd)/Monitor.service /etc/systemd/system/
  systemctl enable Monitor.service
  systemctl start Monitor.service
}

install_Monitor(){
  mkdir $(cd "$(dirname "$0")";pwd)/Monitor
  cd $(cd "$(dirname "$0")";pwd)/Monitor
  apt-get update
  apt-get install python3.8 -y
  wget -O core.py https://raw.githubusercontent.com/hashuser/exchange-monitor/master/core.py
}

main(){
  install_Monitor
  create_service
  install_service
}

main

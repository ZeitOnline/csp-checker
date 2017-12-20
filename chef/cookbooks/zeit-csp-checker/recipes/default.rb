apt_repository "docker" do
   uri "https://download.docker.com/linux/ubuntu"
   distribution "xenial"
   components ["stable"]
   arch "amd64"
   key "9DC858229FC7DD38854AE2D88D81803C0EBFCD88"
end

package "docker-ce" do
    version "17.09.1~ce-0~ubuntu"
end

package "python-pip"

execute "pip install docker-compose"

git '/srv/csp-checker' do
  repository 'https://github.com/ZeitOnline/csp-checker.git'
  revision 'production'
  action :sync
end

execute "docker-compose up -d" do
    cwd "/srv/csp-checker"
end

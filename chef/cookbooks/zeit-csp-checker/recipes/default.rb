apt_repository "docker" do
   uri "https://download.docker.com/linux/ubuntu"
   distribution "xenial"
   components ["stable"]
   arch "amd64"
   key "9DC858229FC7DD38854AE2D88D81803C0EBFCD88"
end

package "docker-ce" do
    version "17.03.2~ce-0~ubuntu-xenial"
end

git '/srv/csp-checker' do
  repository 'https://github.com/ZeitOnline/csp-checker.git'
  revision 'master'
  action :sync
end

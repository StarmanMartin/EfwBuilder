# EFW (ELN File Watcher) builder
## How to set up a EFW builder server

To host an instance of the EFW builder you simply need to clone the Repo into your server. Then copy end rename the __.env.example__ file as __.env__. Make sure to replace xxx.xxx.xxx with either the domain of the server or the public server IP.
```yaml
ALLOWED_HOST=0.0.0.0,django,xxx.xxx.xxx
WEBDAV_HOST=http://xxx.xxx.xxx
PORT=80
FLAVOR=production

DJANGO_SUPERUSER_USERNAME=EBA
DJANGO_SUPERUSER_EMAIL=efw@kit.edu
DJANGO_SUPERUSER_PASSWORD=ChangePasswordFast
```
<p>File: <b>.env</b></p>

Make sure that you have docker and docker-compose installed. More info [here](https://docs.docker.com/desktop/)

Finally, simply run:

```shell
docker-compose up -d
```

You can install a local server if you only need a EFW build server and no WebDAV server. In this case replace xxx.xxx.xxx by 127.0.0.1. It is also recommender to change the port in such a case. With:
```shell
docker-compose up
```
a local server can be started. The page can be accessed at http://127.0.0.1:<PORT>.
 
<h2>Welcome to the EFW manager</h2>
<p>Full documentation <a target="_blank" href="https://www.chemotion.net/chemotionsaurus/docs/eln/devices/device_configuration">here</a></p>
<p>This server-side application allows you to monitor and organise the data transmission of devices integrated in
    your ELN Chemotion instance (for more infos click <a
            href="https://www.chemotion.net/chemotionsaurus/docs/category/device-integration"
            target="_blank">here</a> ). With the <a href="https://github.com/ComPlat/ELN_file_watcher"
                                                    target="_blank">EFW (ELN File Watcher)</a> manager, EFW
    instances adapted to the requirements can be generated quickly and simply. These instances can then be installed
    on the target system in just a few steps. In addition, this server provides a data storage unit with an
    interface to receive data from your target systems. These data are then automatically entered in the ELN.</p>
<h3>How to install EFW</h3>
<p>The following section introduces the installation of the EFW. Note that the installation is <b>only</b> intended for Windows devices.</p>
<ol>
    <li><b>Generate EFW instance:</b> <p>There will be a distinction in 2 cases how to generate an EFW instance. The first case is a new external EFW instance adapted to external WebDAV server. The second case is a new internal EFW instance adapted to this WebDAV server.</p></li>
    <li><b>Install EFW instance:</b> <p>In both cases of the previous step the installation on the target system is the same. However, the installation is simple but require administration rights.</p>
    <ol>
        <li>Make a directory "C:\Program Files\eln_exporter"</li>
        <li>Copy the (on this server generated) <b>efw.exe</b> into "C:\Program Files\file_exporter"</li>
        <li>Copy the file file_exporter_task.vbs into the startup directory.<p style="margin-left: 5px">Hint: Press <b>Windows Key + R</b> to open run and type <b>shell:startup</b>. This will open startup directory</p></li>
    </ol></li>
</ol>
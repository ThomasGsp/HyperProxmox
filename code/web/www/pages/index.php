<?php
include(dirname(__DIR__).'/pages/includes/header.php');
?>
<div id="page-wrapper">
    <div class="row">
        <div class="col-lg-12">
            <h2 class="page-header">Information</h2>
        </div>
        <div class="col-lg-12" id="List_Dates">

        </div>
        <!-- /.col-lg-12 -->
    </div>
    <!-- /.row -->
    <div class="row">
        <div class="col-lg-12">

            HyperProxmox provides a centralized platform for managing your Proxmox environments.</br>
            The web based client lets you manage the essential functions of your Proxmox infrastructure from any browser,
            offering responsiveness and usability.</br>
            Gain the visibility and control needed for your virtual machines, hosts and datastore.</br>
            Assign users to custom roles, search in inventory or provision new virtual machines at the click of a button.</br>
            </br>
            <ul>
               <li> Author : ThomasGSP</li>
               <li> Date : 2017/2018</li>
               <li> Version : V1.0-beta (4 May 2018) </li>
               <li> Status: Dev</li>
               <li> Object : Massive LXC CT / KVM deployment, management and viewer system for Proxmox clusters.</li>
               <li> Proxmox version supported: 3.x/4.x/5.x</li>
               <li> Information : This project is currently in active development. You shouldn't use in production mode or... use at your risks !</li>
            </ul>
            This version provide:
            <ul>
                <li> Web interface to list instances, nodes and clusters</li>
                <li> Current usage (cpu / ram / disks...) for your nodes, instances...</li>
                <li> Quick usage visualisation by color (Green for low, yellow, red)</li>
                <li> Node scoring based on their usage</li>
                <li> Infrastructure historic</li>
                <li> Instance management (stop/start/restart...)</li>
                <li> Search system by VM-name, mac address ...</li>
                <li> Proxmox crawler (Getting cluster information)</li>
                <li> Security : Encipher the critical data (cluster access)</li>
                <li> LDAP authentication for web interface</li>
                <li> Group & cluster viewing in web interface</li>
                <li> Api</li>
            </ul>
            Weakness on this version (in progress):
            <ul>
                <li>Logs system</li>
                <li>Purge system</li>
            </ul>

            This version don't provide (next features):
                <ul>
                    <li>Advanced management</li>
                    <li>Provision new virtual machines</li>
                    <li>...</li>
                </ul>

        </div>
    </div>
<?php
    include(dirname(__DIR__).'/pages/includes/footer.php');
?>

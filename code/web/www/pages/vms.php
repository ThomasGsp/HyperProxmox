<?php

include(dirname(__DIR__).'/pages/includes/header.php');


$html_VMs = $html->List_VMs($lastdate);

?>
<div id="page-wrapper">
    <div class="row">
        <div class="col-lg-12">
            <h1 class="page-header">VM list</h1>
        </div>
        <div class="col-lg-12" id="List_Dates">


        </div>
        <!-- /.col-lg-12 -->
    </div>
    <!-- /.row -->
    <div class="row">
        <div class="col-lg-12">
            <div class="panel panel-default">

                <!-- /.panel-heading -->
                <div class="result"></div>
                <div class="panel-body" >

                    <table width="100%"  class="display nowrap table table-striped table-bordered table-hover dataTables-vm">
                        <thead class="thead-inverse">
                            <tr>
                                <th></th>
                                <th data-priority="1">Cluster</th>
                                <th data-priority="1">Node</th>
                                <th data-priority="1">Name</th>
                                <th data-priority="1">vmid</th>
                                <th data-priority="1">RAM</th>
                                <th data-priority="1">CPU </th>
                                <th data-priority="1">Disk</th>
                                <th data-priority="1">Macs</th>
                                <th data-priority="1">Uptime</th>
                                <th data-priority="1">Status</th>
                                <th data-priority="0">Actions</th>
                            </tr>
                        </thead>
                        <?php echo $html_VMs;  ?>
                    </table>
                </div>
                <div class="result"></div>
            </div>
        </div>
    </div>
</div>

<!-- /#wrapper -->
<div id="dialog-form" title="/!\ VM ACTION /!\" style="background-color: #8c8c8c;z-index: 3;">
    <p class="validateTips">Proxmox authentification required.</p>
    <form>
        <fieldset>
            <label for="name">Username:</label>
            <input type="text" name="name" id="name" value="root@pam" class="text ui-widget-content ui-corner-all">
            <br />
            <label for="password">Password:</label>
            <input type="password" name="password" id="password" value="" class="text ui-widget-content ui-corner-all">

            <input type="hidden" name="action" id="action" value="">
            <input type="hidden" name="vmid" id="vmid" value="">
            <input type="hidden" name="node" id="node" value="">
            <input type="submit" tabindex="-1" style="position:absolute; top:-1000px">
        </fieldset>
    </form>
</div>
<?php
include(dirname(__DIR__).'/pages/includes/footer.php');
?>

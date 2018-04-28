<?php
include(dirname(__DIR__).'/pages/includes/header.php');
$html_VMs = $html->List_VMs($lastdate);
?>
<div id="page-wrapper">
    <div class="row">
        <div class="col-lg-12">
            <h1 class="page-header">Instances - kvm/lxc/vz</h1>
        </div>
    </div>
    <div class="row">
        <div class="col-lg-12">
            <div class="panel panel-default">
                <div class="panel-body" >
                    <table width="100%"  class="display nowrap table table-striped table-bordered table-hover dataTables-vm">
                        <thead class="thead-inverse">
                            <tr>
                                <th></th>
                                <th data-priority="1">cluster</th>
                                <th data-priority="1">node</th>
                                <th data-priority="1">name</th>
                                <th data-priority="1">type</th>
                                <th data-priority="1">vmid</th>
                                <th data-priority="1">ram</th>
                                <th data-priority="1">cpu </th>
                                <th data-priority="1">disk</th>
                                <th data-priority="1">macs</th>
                                <th data-priority="1">uptime</th>
                                <th data-priority="1">status</th>
                            </tr>
                        </thead>
                        <?php echo $html_VMs;  ?>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
<?php
include(dirname(__DIR__).'/pages/includes/footer.php');
?>

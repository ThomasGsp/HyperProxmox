<?php

include(dirname(__DIR__).'/pages/includes/header.php');

// ajouter detection precedant

switch (htmlspecialchars($_GET["type"])) {
    case "sto":
        $node = json_decode($q->GET_byid("storages", $_GET['id']), true)['value'];
        break;
    case "node":
        $node = json_decode($q->GET_byid("nodes", $_GET['id']), true)['value'];
        break;
    case "vm":
        $node = json_decode($q->GET_byid("instances", $_GET['id']), true)['value'];
        break;
}

$node = (object) $node;

$html_Custer = $html->List_HYPs($node->date, $node->cluster, $node->node);
$html_VMs = $html->List_VMs($node->date,  $node->cluster, $node->node);
$html_sto = $html->List_STO($node->date,  $node->cluster, $node->node);

?>
<div id="page-wrapper">
    <div class="row">
        <div class="col-lg-12">
            <h1 class="page-header"><?php echo  $node->node; ?> - Informations</h1>
        </div>
    </div>
    <!-- /.row -->
    <div class="row">
        <div class="col-lg-12">
            <div class="panel panel-default">
                <!-- /.panel-heading -->
                <div class="panel-body" >
                    <h1> Nodes </h1>
                    <table width="100%"  class="display nowrap responsive table table-striped table-bordered table-hover" id="dataTables-hypervisor" >
                        <thead class="thead-inverse">
                        <tr>
                            <th></th>
                            <th data-priority="1">cluster</th>
                            <th data-priority="1">name</th>
                            <th data-priority="1">ram (used)</th>
                            <th data-priority="1">ram (alloc/total)</th>
                            <th data-priority="1">cpu (alloc/total)</th>
                            <th data-priority="1">storage (used)</th>
                            <th data-priority="1">storage (alloc/total)</th>
                            <th data-priority="1">load</th>
                            <th data-priority="1">uptime</th>
                            <th data-priority="1">eligibility</th>
                            <th class="none" >swap (used/total)</th>
                            <th class="none" >pve-version Version</th>
                            <th class="none" >kernel</th>
                            <th class="none" >cpu informations</th>
                        </tr>
                        </thead>
                        <?php echo $html_Custer;  ?>
                    </table>
                    <hr>
                    <h1> Storages and disks</h1>
                    <table width="100%"  class="display nowrap table table-striped table-bordered table-hover" id="dataTables-storages" >
                        <thead class="thead-inverse">
                        <tr>
                            <th> </th>
                            <th data-priority="1">node</th>
                            <th data-priority="1">name</th>
                            <th data-priority="1">total</th>
                            <th data-priority="1">allocate</th>
                            <th data-priority="1">available</th>
                            <th data-priority="1">used </th>
                            <th class="none">disks</th>
                        </tr>
                        </thead>
                        <?php echo $html_sto;  ?>
                    </table>
                    <hr>
                    <h1> Instances </h1>
                    <table width="100%"  class="display nowrap table table-striped table-bordered table-hover dataTables-vm" >
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
                <div class="result"></div>
            </div>
        </div>
    </div>
    <?php
    include(dirname(__DIR__).'/pages/includes/footer.php');
    ?>

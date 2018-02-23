<?php
include(dirname(__DIR__).'/pages/includes/header.php');

$html_Custer = $html->List_HYPs($lastdate, htmlspecialchars($_GET['cluster']));
$html_VM = $html->List_VMs($lastdate, htmlspecialchars($_GET['cluster']));

$html_VM_final ='
                <br /> <hr>
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
                    '.$html_VM.'
                </table>';

?>

<div id="page-wrapper">
    <div class="row">
        <div class="col-lg-12">
            <h1 class="page-header">Nodes - <?php echo  htmlspecialchars($_GET['cluster']); ?></h1>
        </div>
    </div>

    <div class="row">
        <div class="col-lg-12">
            <div class="panel panel-default">
                <div class="panel-body" >
                    <table width="100%"  class="display nowrap responsive table table-striped table-bordered table-hover" id="dataTables-cluster" >
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
                    <?php echo  $html_VM_final;  ?>
                </div>
                * The storage used is the largest.<br/>
                * This is a score to evaluate the eligibility to receive news VM. Lower score are the best.
            </div>
        </div>
    </div>
<?php
include(dirname(__DIR__).'/pages/includes/footer.php');
?>
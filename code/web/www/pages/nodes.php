<?php
include(dirname(__DIR__).'/pages/includes/header.php');
$html_HYPs = $html->List_HYPs($lastdate);

?>
<div id="page-wrapper">
    <div class="row">
        <div class="col-lg-12">
            <h1 class="page-header">HYPERVISORS</h1>
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
                <div class="panel-body" >

                    <table width="100%"  class="table table-striped table-bordered table-hover" id="dataTables-hypervisors" >
                        <thead class="thead-inverse">
                        <tr>
                            <th></th>
                            <th data-priority="1">Cluster</th>
                            <th data-priority="1">Name</th>
                            <th data-priority="1">RAM(Used)</th>
                            <th data-priority="1">RAM(Alloc/Total)</th>
                            <th data-priority="1">CPU(Alloc/Total)</th>
                            <th data-priority="1">STO(Used)*</th>
                            <th data-priority="1">STO(Alloc/Total)</th>
                            <th data-priority="1">Load</th>
                            <th data-priority="1">Uptime</th>
                            <th data-priority="1">Eligibility*</th>
                            <th class="none" >Swap (used/total)</th>
                            <th class="none" >PVE Version</th>
                            <th class="none" >Kernel</th>
                            <th class="none" >CPU - Informations</th>
                        </tr>
                        </thead>
                        <?php echo $html_HYPs;  ?>
                    </table>
                </div>
                <div id="result"></div>
                * The storage used is the largest.<br/>
                * This is a score to evaluate the eligibility to receive news VM. Lower score are the best.
            </div>

        </div>
    </div>
    <?php
    include(dirname(__DIR__).'/pages/includes/footer.php');
    ?>

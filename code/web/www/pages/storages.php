<?php
include(dirname(__DIR__).'/pages/includes/header.php');

// GEN HTML LIST Dates
$html = new API_Gen_HTML;

$html_sto = $html->List_STO($lastdate);

?>
<div id="page-wrapper">
    <div class="row">
        <div class="col-lg-12">
            <h1 class="page-header">Storages</h1>
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

                    <table width="100%"  class="display nowrap table table-striped table-bordered table-hover" id="dataTables-storages" >
                        <thead class="thead-inverse">
                        <tr>
                            <th> </th>
                            <th data-priority="1">Node</th>
                            <th data-priority="1">Name</th>
                            <th data-priority="1">Total</th>
                            <th data-priority="1">Allocate</th>
                            <th data-priority="1">Available</th>
                            <th data-priority="1">Used </th>
                            <th class="none">Disks</th>
                        </tr>
                        </thead>
                        <?php echo $html_sto;  ?>
                    </table>
                </div>
                <div id="result"></div>
            </div>
        </div>
    </div>
    <!-- /#wrapper -->
    <?php
    include(dirname(__DIR__).'/pages/includes/footer.php');
    ?>

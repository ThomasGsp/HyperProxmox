<?php
include(dirname(__DIR__).'/pages/includes/header.php');
$html_sto = $html->List_STO($lastdate);
?>
<div id="page-wrapper">
    <div class="row">
        <div class="col-lg-12">
            <h1 class="page-header">Storages</h1>
        </div>
    </div>
    <div class="row">
        <div class="col-lg-12">
            <div class="panel panel-default">
                <div class="panel-body" >
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
                </div>
            </div>
        </div>
    </div>
</div>
<?php
include(dirname(__DIR__).'/pages/includes/footer.php');
?>

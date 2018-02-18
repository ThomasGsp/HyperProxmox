<?php
include(dirname(__DIR__).'/pages/includes/header.php');
$html_HYPs = $html->List_HYPs($lastdate);
?>
<div id="page-wrapper">
    <div class="row">
        <div class="col-lg-12">
            <h1 class="page-header">Nodes</h1>
        </div>
    </div>
    <div class="row">
        <div class="col-lg-12">
            <div class="panel panel-default">
                <div class="panel-body" >
                    <table width="100%"  class="table table-striped table-bordered table-hover" id="dataTables-hypervisors" >
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
                        <?php echo $html_HYPs;  ?>
                    </table>
                </div>
                <div id="result"></div>
                * The storage used is the largest.<br/>
                * This is a score to evaluate the eligibility to receive news VM. Lower score are the best.
            </div>
        </div>
    </div>
</div>
<?php
include(dirname(__DIR__).'/pages/includes/footer.php');
?>

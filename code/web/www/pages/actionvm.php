<?php

include(dirname(__DIR__).'/pages/includes/header.php');

$instanceinfo = json_decode($q->GET_byid("instances", htmlspecialchars($_GET['id'])), true)['value'];
$instanceinfo = (object) $instanceinfo;

$status = json_decode($q->GET_status('current', htmlspecialchars($_GET['id'])), true)['value']['data'];
$status = (object) $status;    
?>
<div id="page-wrapper">

    <div class="row">
        <div class="col-lg-12">
            <h1 class="page-header"> VM - actions </h1>
        </div>
        <!-- /.col-lg-12 -->
    </div>
    <div class="row">
        <div class="col-lg-12">
            <div class="panel panel-default">
                <div class="panel-body" >
                   	<ul>
                		<li> Cluster: <?php echo  $instanceinfo->cluster; ?> </li>
                    	<li> Node: <?php echo  $instanceinfo->node; ?> </li>
                    	<li> VM: <?php echo  $instanceinfo->name; ?> </li>
                    	<li> ID: <?php echo  $instanceinfo->vmid; ?> </li>
                	</ul>
                	
                    <select id="action" class="selectaction" data-width="auto" >
                    	<option  value="">Choice </option>
                            <option value="current">Status</option>
                            <option value="start">Start</option>
                            <option value="stop">Stop</option>
                            <option value="shutdown">Shutdown</option>
                            <option value="reset">Reset</option>
                        </optgroup>
                    </select>
		             <button id="bbaction" value="<?php echo  $instanceinfo->_id["\$oid"]; ?>">Send</button>
                </div>
 				<div class="result"></div>
            </div>
        </div>
    </div>
    <?php
    include(dirname(__DIR__).'/pages/includes/footer.php');
    ?>

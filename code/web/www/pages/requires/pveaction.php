<?php

require(dirname(__DIR__).'/requires/configs.php');
require(dirname(__DIR__).'/requires/functions.php');

function mappingstatus($status){
 
    switch ($status) {
        case "stopped":
            $outmap = "stop";
            break;
        case "running":
            $outmap = "start";
            break;
        default: $outmap = "";
    }
    
    return $outmap;
}

$q = new API_GET_INFO;

$id = $_GET["id"];
$action = $_GET["action"];


// Get status before action
$status_before = json_decode($q->GET_status('current', $id), true)['value']['data'];
$status_before = (object) $status_before;


if (mappingstatus($status_before->status) != $action)
{
    if(in_array($action, ["shutdown","stop","reset"]) && $status_before->status == "stopped")     
    {
        echo "Action not available! VM <b>".$status_before->name."</b> is currently :<b>".$status_before->status."</b>";
    }
    else if ($action == "current")
    {
        echo "The VM <b>".$status_before->name."</b> is currently <b>".$status_before->status."</b>"; 
    }
    else
    {
        $status_after = $status_before;
        
        $q->GET_status($action, $id);
            
        for ($i = 1; ($status_after->status == $status_before->status) && $i <= 9; $i++) {
            sleep(3); // 30s max (10*3)
            $status_after = json_decode($q->GET_status('current', $id), true)['value']['data'];
            $status_after = (object) $status_after;     
        }
        
        if($status_after->status == $status_before->status) 
        {
            echo "Command time out";
        } 
        else 
        {
            echo "The VM <b>".$status_after->name."</b> is now :<b>".$status_after->status."</b>";
        }
    }
} 
else 
{
    echo "Your VM <b>".$status_before->name."</b> is already:<b>".$status_before->status."</b>";
}
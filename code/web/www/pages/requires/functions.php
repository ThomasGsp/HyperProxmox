<?php

class API_GET_INFO
{

    
    public function GET_status($action, $id)
    {
        $info = curl("api/v1/instance/id/".$id."/status/".$action);
        return $info;
    }
    
    public function GET_byid($selector, $id)
    {
        $info = curl("api/v1/static/".$selector."/id/".$id);
        return $info;
    }
    
    public function GET_Dates($select="all")
    {
        $dates = curl("api/v1/static/dates/".$select);
        return $dates;
    }

    public function GET_clusters_conf($cluster=null)
    {
        if (!empty($cluster))
            $cluster_conf = curl("api/v1/administration/cluster/".$cluster);
        else
            $cluster_conf = curl("api/v1/administration/cluster/");
        return $cluster_conf;
    }
    
    public function GET_qemu($date, $cluster=null, $node=null, $vmid=null)
    {
        if (!empty($vmid))
            $qemu = curl("api/v1/static/instances/".$date."/".$cluster."/".$node."/".$vmid);
        else if (!empty($node))
            $qemu = curl("api/v1/static/instances/".$date."/".$cluster."/".$node."/");
        else if (!empty($cluster))
            $qemu = curl("api/v1/static/instances/".$date."/".$cluster."/");
        else
            $qemu = curl("api/v1/static/instances/".$date."/");
        return $qemu;
    }

    public function GET_hyp($date, $cluster=null, $node=null)
    {
        if (!empty($node))
            $nodes = curl("api/v1/static/nodes/".$date."/".$cluster."/".$node);
        else if (!empty($cluster))
            $nodes = curl("api/v1/static/nodes/".$date."/".$cluster."/");
        else
            $nodes = curl("api/v1/static/nodes/".$date."/");
    
        return $nodes;
    }

    public function GET_sto($date, $cluster=null, $node = null, $storage = null)
    {
        
        if (!empty($storage))
            $storages = curl("api/v1/static/storages/".$date."/".$cluster."/".$node."/".$storage);
        else if (!empty($node))
            $storages = curl("api/v1/static/storages/".$date."/".$cluster."/".$node."/");
        else if (!empty($cluster))
            $storages = curl("api/v1/static/storages/".$date."/".$cluster."/");
        else
            $storages = curl("api/v1/static/storages/".$date."/");
        return $storages;
    }

    public function GET_Groups()
    {
        $groups = curl("api/v1/administration/cluster/");
        return $groups;
    }

    public function GET_Disk($date, $cluster = null, $node = null, $vmid = null)
    {
        if (!empty($vmid))
            $disks = curl("api/v1/static/disks/".$date."/".$cluster."/".$node."/".$vmid);
        else   
            $disks = curl("api/v1/static/disks/".$date."/".$cluster."/".$node."/");
        
        return $disks;
        
    }
}


class API_Gen_HTML
{

    var $sto_regx; // regex ou size
    var $sto_regx_status;

    public function View_VM($node, $search)
    {
        $d = new API_GET_INFO;
        $dates = $d->GET_Dates();
        $array = json_decode($dates, true);
        $result = array();
        foreach ($array as $keydate => $value)
        {
            $vm = $d->GET_qemu($keydate, $node, $search);
            $array = json_decode($vm, true);
            $array['cpu'] = $array['cpu']*100;
            $array['mem'] = $array['mem'] / (1024 * 1024);
            $array['timestamp'] = $array['timestamp'] * 1000;
            $array['netout'] = $array['netout'] / (1024 * 1024);
            $array['netin'] = $array['netin']  / (1024 * 1024);
            $result[] = $array;
        }

        return $result;
    }


    public function List_Groups($date)
    {
        $d = new API_GET_INFO;
        $html = '';

        $clusters = json_decode($d->GET_Groups(), true)['value'];
       
        
        $group_arr = array();
        foreach ($clusters as $cluster)
        {
            $cluster = (object) $cluster;
            foreach ($cluster->groups as $group)
            {
                if(!array_key_exists($group, $group_arr))
                {
                    $group_arr[$group] = array($cluster->name);
                }
                else {
                    array_push($group_arr[$group], $cluster->name);
                }
            }
        }
        
        foreach ($group_arr as $keygroup => $group)
        {
            $html = $html.'<li><a href="#">'.$keygroup.'<span class="fa arrow"></span></a>';
            $html = $html.'<ul class="nav nav-third-level">';
            foreach ($group as $cluster)
            {;
                $html = $html.'<li><a href="cluster.php?date='.$date.'&cluster='.$cluster.'">'.$cluster.'</a></li>';
            }
            $html = $html.'</ul></li>';
        }
        
        $html = $html.'';

        return $html;
    }


    public function List_Dates($timestamp = "")
    {
        $d = new API_GET_INFO;
        $dates = $d->GET_Dates();
        $dates_list = json_decode($dates, true)['value'];
        arsort($dates_list);
        
        $html = '<select id="List-Dates" name="date" class="selectpicker selectdate show-tick">';

        foreach ($dates_list as $key => $value)
        {
            $date = (object) $value;
            if (intval($timestamp) == intval($date->date))
                $html = $html.'<option value='.$date->date.' selected="selected">'.date('m/d/Y H:i', $date->date).'</option>';
            else
                $html = $html.'<option value='.$date->date.'>'.date('m/d/Y H:i', $date->date).'</option>';
        }
        $html = $html.'</select>';
        return $html;
    }


    public function List_VMs($date, $cluster=null, $node=null)
    {
        $html = '';
        $d = new API_GET_INFO; 
        $vms_list = json_decode($d->GET_qemu($date, $cluster, $node), true)['value'];       
        $last_clust = "";
        $last_disk = "";

        foreach ($vms_list as $qemu)
        {
            $qemu = (object) $qemu;
            $macs = "";
            $volids = "";
            $volsize = 0;

            if($last_clust != $qemu->cluster)
            {
                $last_clust = $qemu->cluster;
                $clusters_info = json_decode($d->GET_clusters_conf($qemu->cluster), true)['value'][0];
                $clusters_info = (object) $clusters_info;
            }
 
            //$disklists  = json_decode($d->GET_Disk($date, $qemu->cluster, $qemu->node, $qemu->vmid), true)['value'];
            // Disk selection. Dump all disk from node ismore quickly to dump all disk from vmid (less requests on api)
            if($last_disk != $date.$qemu->cluster.$qemu->node)
            {
                $last_disk = $date.$qemu->cluster.$qemu->node;
                $disklists  = json_decode($d->GET_Disk($date, $qemu->cluster, $qemu->node), true)['value'];
             
            }
           
            foreach($disklists as $vol) 
            { 
                $vol = (object) $vol; 
                if (property_exists($vol, 'vmid'))
                {
                    if ($vol->vmid == $qemu->vmid)
                    {
                        $volids =  $vol->volid.",".$volids ; 
                        $volsize =  $volsize + $vol->size ; 
                    }
                } 
            }
            
            foreach($qemu->macaddr as $mac) { $macs =  $mac.",".$macs ; }
            
            $html = $html.'
                <tr>
                    <td></td>
                    <td>'.$qemu->cluster.'</td>
                    <td>
                        <a href="node.php?id='.$qemu->_id["\$oid"].'&type=vm&date='.$date.'"> '.$qemu->node.'</a> 
                        <a data-toggle="tooltip" title="External Link: https://'.$clusters_info->url.':'.$clusters_info->port.'" href="https://'.$clusters_info->url.':'.$clusters_info->port.'/#v1:0:=qemu%2F'.$qemu->vmid.':4::::::" target="_blank"> 
                        <img src="images/fb-lien-420.png" alt="ExternalProxmoxLink" style="width:20px;height:20px;"></a>
                    </td>
                    <td> 
                        <a href="actionvm.php?id='.$qemu->_id["\$oid"].'&date='.$date.'" >'.$qemu->name.'
                        <a data-toggle="tooltip" title="External Link: https://'.$clusters_info->url.':'.$clusters_info->port.'/#v1:0:=qemu%2F'.$qemu->vmid.':4::::::" href="https://'.$clusters_info->url.':'.$clusters_info->port.'/#v1:0:=qemu%2F'.$qemu->vmid.':4::::::" target="_blank">
                        <img src="images/fb-lien-420.png" alt="ExternalProxmoxLink" style="width:20px;height:20px;"></a>
                    </td>
                    <td>'.$qemu->type.'</td>
                    <td>'.$qemu->vmid.'</td>
                    <td  data-order="'.$qemu->maxmem.'">'.formatBytes(round($qemu->maxmem)).'</td>
                    <td>'.$qemu->cpus.'</td>
                    <td data-order="'.$volsize.'" id="wrapper-mac"> <a data-toggle="tooltip" data-html="true" title="'.str_replace(",", "<br/>", $volids).'">'.formatBytes($volsize).'</a></td>
                    <td id="wrapper-mac"> <a data-toggle="tooltip" data-html="true" title="'.str_replace(",", "<br/>", $macs).'">'.$macs.'</a></td>
                    <td>'.secondsToDays($qemu->uptime).'</td>
                    <td>'.$qemu->status.'</td>
                </tr>';
        }
        return $html;
    }

    public function List_HYPs($date, $cluster=null, $node=null)
    {
        require(dirname(__DIR__).'/requires/configs.php');
        //$m = new REQUESTS_MYSQL;
        //$non_grata = $m->non_grata_select();


        $q = new API_GET_INFO;
        $nodes = json_decode($q->GET_hyp($date, $cluster, $node), true)['value'];
 
        arsort($nodes);
        $row_non_grata = [];
    
        /*
        foreach ($non_grata as $rows) {
            $row_non_grata[] = $rows->name;
        }
        */
        $sto_selection = "";
        $html = '';
        $last_sto = "";
        $last_clust = "";
   
        
        foreach ($nodes as $node)
        {
            $node = (object) $node;
      
            $sto_info  = json_decode($q->GET_sto($date, $node->cluster, $node->node), true)['value'];
            
            if ($sto_regx_status == true)
            {
                foreach ($sto_info as $sto)
                {
                    $sto = (object)$sto;
                    if (preg_match($sto_regx, $sto->storage))
                    {
                        $sto_selection = $sto;
                        break;
                    }
                }
            }

            if($sto_selection == "" or $sto_regx_status == false)
            {
                foreach ($sto_info as $sto) {
                    $sto = (object)$sto;
                    $sto_new = $sto->total;
                    if ($sto_new > $sto_max) {
                        $sto_max = $sto_new;
                        $sto_selection = $sto;
                    }
                }
            }
           

            
            if($last_clust != $node->cluster)
            {
                $last_clust = $node->cluster;
                $clusters_info = json_decode($q->GET_clusters_conf($node->cluster), true)['value'][0];
                $clusters_info = (object) $clusters_info;
            }
            
            $ram_use_percent = round(($node->memory['used']/$node->memory['total'])*100);
            $ram_alloc_percent = round(($node->totalallocram/$node->memory['total'])*100);
            $cpu_alloc_percent = round(($node->totalalloccpu/$node->cpuinfo['cpus'])*100);
            $disk_use_percent = round((100/$sto_selection->total)*$sto_selection->used);
            
            $disk_alloc_percent = round(($sto_selection->totalallocdisk/$sto_selection->total)*100); // revoir param 1
            $load_percent = round($node->loadavg[0]);

            $eligibility = eligibility($ram_use_percent, $ram_alloc_percent, $cpu_alloc_percent, $disk_use_percent, $disk_alloc_percent, $load_percent);
            
            
            if (in_array($node->node, $row_non_grata)) {
                //$grata = '<a class="nongratalink" data-toggle="tooltip" title="Switch to grata" id="'.$node->node.'" action="sw_ON" node="'.$node->node.'" href="#" > <img src="images/nongrata_on.png" alt="Nongrataimg" style="width:16px;height:16px;"></a>';
                $eligibility = round($eligibility +  $non_grata_weight);
            }
            /*
            else{
                $grata = '<a class="nongratalink" data-toggle="tooltip" title="Switch to non grata" id="'.$node->node.'"  action="sw_OFF" node="'.$node->node.'"  href="#" > <img src="images/nongrata_off.png" alt="Nongrataimg" style="width:16px;height:16px;"></a>';
            }
            */
            
            $grata = "";
            
            $html = $html.'
                <tr>
                    <td></td>
                    <td>'.$node->cluster.'</td>
                    <td> 
                        <a href="node.php?id='.$node->_id["\$oid"].'&type=node&date='.$date.'"> '.$node->node.'</a> 
                        <a  data-toggle="tooltip" title="External Link: https://'.$clusters_info->url.':'.$clusters_info->port.'"  href="https://'.$clusters_info->url.':'.$clusters_info->port.'/#v1:0:=node%2F'.$node->node.':4:5:::::" target="_blank"> <img src="images/fb-lien-420.png" alt="ExternalProxmoxLink" style="width:20px;height:20px;"></a>
                        '.$grata.'                    
                    </td>
                    <td style="color:'.testcolor("ram_use", $ram_use_percent).'" data-order="'.$ram_use_percent.'">'.formatBytes($node->memory['used']).' ('.$ram_use_percent.'%)</td>
                    <td style="color:'.testcolor("ram_alloc", $ram_alloc_percent).'"  data-order="'.$ram_alloc_percent.'">'.formatBytes($node->totalallocram).'/'.formatBytes($node->memory['total']).' ('.$ram_alloc_percent.'%)</td>
                    <td style="color:'.testcolor("cpu_alloc", $cpu_alloc_percent).'" data-order="'.$cpu_alloc_percent.'">'.$node->totalalloccpu.'/'.$node->cpuinfo['cpus'].' ('.$cpu_alloc_percent.'%)</td>
                    <td style="color:'.testcolor("disk_use", $disk_use_percent).'" data-order="'.$sto_selection->used.'">'.formatBytes($sto_selection->used).'('.$disk_use_percent.'% - '.$sto_selection->storage.')</td>
                    <td style="color:'.testcolor("disk_alloc", $disk_alloc_percent).'"  data-order="'.$sto_selection->used.'">'.formatBytes($sto_selection->totalallocdisk).'/'.formatBytes($sto_selection->total).' ('.$disk_alloc_percent.'%) </td>
                    <td style="color:'.testcolor("cpu_use", $load_percent).'" >'.$load_percent.'%</td>
                    <td data-order="'.secondsToDays($node->uptime).'">'.secondsToDays($node->uptime).'d</td>
                    <td>'.$eligibility.'</td>  
                       
                       
                    <td>'.formatBytes($node->swap['used']).'/'.formatBytes($node->swap['total']).'</td>  
                    <td>'.$node->pveversion.'</td>  
                    <td>'.$node->kversion.'</td>  
                    <td>'.$node->cpuinfo['model'].'</td>  
                </tr>
                    ';
        }
        return $html;
    }


    public function List_STO($date, $cluster=null, $node=null, $sto=null)
    {
        
        $q = new API_GET_INFO;
        $stos_list = json_decode($q->GET_sto($date, $cluster, $node, $sto), true)['value'];
        $html = '';
        $last_clust = "";
        $last_disk = "";
        
        foreach ($stos_list as $sto)
        {
            $sto = (object) $sto;
            // Limit requests
            if($last_clust != $sto->cluster)
            {
                $last_clust = $sto->cluster;
                $clusters_info = json_decode($q->GET_clusters_conf($sto->cluster), true)['value'][0];
                $clusters_info = (object) $clusters_info;
            }

            try {
                $stoavail = round(($sto->avail * 100 ) / $sto->total);
                $stoused = round(100 - ($sto->avail * 100) / $sto->total);
                $disk_alloc_percent = round(($sto->totalallocdisk/$sto->total) * 100);
            } catch (Exception $e) {
                $stoavail = 'Not available';
                $stoused = 'Not available';
                $disk_alloc_percent = 'Not available';
            }

            $htmldisk = '<table class="display nowrap responsive table table-striped table-bordered table-hover">
                            <thead class="thead-inverse">
                            <tr>
                                <th>type</th>
                                <th>vol.id</th>
                                <th>size</th>
                                <th>format</th>  
                            </tr>
                        </thead>';

            // Limit requests
            if($last_disk != $date.$sto->cluster.$sto->node)
            {
                $last_disk = $date.$sto->cluster.$sto->node;
                $disklists  = json_decode($q->GET_Disk($date, $sto->cluster, $sto->node), true)['value'];
            }
            
            
            foreach ($disklists as $disklist) {
                $disklist = (object) $disklist;
                if ($disklist->storage == $sto->storage)
                    $htmldisk = $htmldisk.' <tr>
                                                <td>'.$disklist->content.'</td>  
                                                <td>'.$disklist->volid.'</td>  
                                                <td>'.formatBytes($disklist->size).'</td>
                                                <td>'.$disklist->format.'</td>
                                            </tr>';
            }
            $htmldisk = $htmldisk.'</table>';

            $html = $html.'
                <tr>
                    <td></td>
                    <td> 
                        <a href="node.php?id='.$sto->_id["\$oid"].'&type=sto&date='.$date.'"> '.$sto->node.'</a> 
                        <a  data-toggle="tooltip" title="External Link: https://'.$clusters_info->url.':'.$clusters_info->port.'/#v1:0:=node%2F'.$sto->node.':4:5:::::"  href="https://'.$clusters_info->url.':'.$clusters_info->port.'/#v1:0:=storage%2F'.$sto->node.'%2F'.$sto->storage.':4::::::" target="_blank">
                        <img src="images/fb-lien-420.png" alt="ExternalProxmoxLink" style="width:20px;height:20px;"></a> </td>
                    <td> '.$sto->storage.'</td>
                    <td data-order="'.$sto->total.'"> '.formatBytes($sto->total).'</td>
                    <td data-order="'.$sto->totalallocdisk.'"> '.formatBytes($sto->totalallocdisk).' ('.$disk_alloc_percent.'%)</td>
                    <td data-order="'.$sto->avail.'"> '.formatBytes($sto->avail).' ('.$stoavail.'%)</td>
                    <td data-order="'.$sto->used.'"> '.formatBytes($sto->used).' ('.$stoused.'%)</td>
                    <td> '.$htmldisk.' </td>
                </tr>';
        }
        return $html;
    }




}


function testcolor($type, $value)
{

    //  charges points in percents
    $cpu_low = 30; // less than
    $cpu_height = 60 ; // more than

    $cpu_low_alloc = 100; // less than
    $cpu_height_alloc = 200 ; // more than

    $ram_low = 50; // less than
    $ram_height = 75 ; // more than

    $ram_low_alloc = 75; // less than
    $ram_height_alloc = 110 ; // more than

    $disk_low = 50; // less than
    $disk_height = 70 ; // more than

    $disk_low_alloc = 90; // less than
    $disk_height_alloc = 190 ; // more than

    $color = "";

    $l_color = '#088A08'; // Green
    $m_color = '#DF7401'; // Yellow
    $h_color = '#B40404'; // Red

    $array_calc = array(
        "ram_alloc" => array("low" => $ram_low_alloc, "height" =>$ram_height_alloc),
        "ram_use" => array("low" => $ram_low, "height" => $ram_height),
        "disk_use" => array("low" => $disk_low, "height" => $disk_height),
        "disk_alloc" => array("low" => $disk_low_alloc, "height" => $disk_height_alloc),
        "cpu_alloc" => array("low" => $cpu_low_alloc, "height" => $cpu_height_alloc),
        "cpu_use" => array("low" => $cpu_low, "height" => $cpu_height)
    );

    if($value < $array_calc[$type]["low"])
        $color =  $l_color;
    elseif (($array_calc[$type]["low"] <= $value ) and ($value < $array_calc[$type]["height"]))
        $color =  $m_color;
    elseif ($value >= $array_calc[$type]["height"])
        $color =  $h_color;


    return $color;
}

function testvalue($val, $min, $max) {
    return ($val >= $min && $val <= $max);
}


class DbConn
{
    public $conn;
    public function __construct()
    {
        require(dirname(__DIR__).'/dbconf.php');
        $this->host = $host; // Host name
        $this->username = $username; // Mysql username
        $this->password = $password; // Mysql password
        $this->db_name = $db_name; // Database name
        $this->tbl_logs = $tbl_logs;
        $this->tbl_nodes = $tbl_nodes;
        try {
            // Connect to server and select database.
            $this->conn = new PDO('mysql:host=' . $host . ';dbname=' . $db_name . ';charset=utf8', $username, $password);
            $this->conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        } catch (Exception $e)  {
            error_log("Database connection error:".$e);
            die('Database connection error');
        }
    }
}


class REQUESTS_MYSQL
{

    function non_grata_select()
    {
        try {
            $db = new DbConn;
            $tbl_nodes = $db->tbl_nodes;
            $stmt = $db->conn->prepare("SELECT `name` FROM ".$tbl_nodes." WHERE `status` = 1");
            $stmt->execute();
            $result = $stmt->fetchAll(PDO::FETCH_OBJ);
            return $result;
        } catch (PDOException $e) {
            $err = "Error: " . $e->getMessage();
        }

        //Determines returned value ('true' or error code)
        $resp = ($err == '') ? 'true' : $err;
        return $resp;
    }

    function non_grata_update($node, $value)
    {
        try {
            $db = new DbConn;
            $tbl_nodes = $db->tbl_nodes;
            $stmt = $db->conn->prepare("REPLACE INTO ".$tbl_nodes."(`name`, `status`) VALUES ('".$node."','".$value."')");
            $stmt->execute();
            $result = $stmt->fetchAll(PDO::FETCH_OBJ);
            return $result;
        } catch (PDOException $e) {
            $err = "Error: " . $e->getMessage();
        }
        //Determines returned value ('true' or error code)
        $resp = ($err == '') ? 'true' : $err;
        return $resp;
    }

}

function eligibility($ram_use, $ram_alloc, $cpu_alloc, $disk_use, $disk_alloc, $load) // data in percent !!! // ' .$sto->total - $sto->avail - $sto->used.'
{
    $coef_ram_use = 4;
    $coef_ram_alloc = 3;
    $coef_cpu_alloc = 2;
    $coef_disk_use = 4;
    $coef_disk_alloc = 3;
    $coef_load = 3;

    $coef_total = $coef_ram_use + $coef_ram_alloc + $coef_cpu_alloc + $coef_disk_use + $coef_disk_alloc + $coef_load;
    $calc = 0 - ($ram_use * $coef_ram_use) - ($ram_alloc * $coef_ram_alloc) - ($cpu_alloc * $coef_cpu_alloc) - ($disk_use * $coef_disk_use) - ($disk_alloc * $coef_disk_alloc) - ($load * $coef_load);
    $calc = $calc / $coef_total;
    $calc = $calc / 10;

    return round($calc*-1,1);
}


function curl($url, $ip="127.0.0.1", $port="8080", $type="GET", $fieldsjson="")
{

    $url = "http://".$ip.":".$port."/".$url;
    $ch = curl_init();

    if($type == "POST")
    {
        curl_setopt($ch,CURLOPT_POST, count($fieldsjson));
        curl_setopt($ch,CURLOPT_POSTFIELDS, $fieldsjson);
    }

    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_HEADER, false);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);

    $data = curl_exec($ch);
    curl_close($ch);

    return $data;
}


function secondsToDays($seconds)
{
    // extract hours
    $days = floor($seconds / 86400);
    return $days;
}

function secondsToTime($seconds)
{
    // extract hours
    $hours = floor($seconds / (60 * 60));

    // extract minutes
    $divisor_for_minutes = $seconds % (60 * 60);
    $minutes = floor($divisor_for_minutes / 60);

    // extract the remaining seconds
    $divisor_for_seconds = $divisor_for_minutes % 60;
    $seconds = ceil($divisor_for_seconds);

    // return the final array
    $obj = array(
        "h" => (int) $hours,
        "m" => (int) $minutes,
        "s" => (int) $seconds,
    );
    return $obj;
}

function formatBytes($bytes, $precision = 2) {
    $kilobyte = 1024;
    $megabyte = $kilobyte * 1024;
    $gigabyte = $megabyte * 1024;
    $terabyte = $gigabyte * 1024;

    if (($bytes >= 0) && ($bytes < $kilobyte)) {
        return $bytes . ' B';

    } elseif (($bytes >= $kilobyte) && ($bytes < $megabyte)) {
        return round($bytes / $kilobyte, $precision) . ' KB';

    } elseif (($bytes >= $megabyte) && ($bytes < $gigabyte)) {
        return round($bytes / $megabyte, $precision) . ' MB';

    } elseif (($bytes >= $gigabyte) && ($bytes < $terabyte)) {
        return round($bytes / $gigabyte, $precision) . ' GB';

    } elseif ($bytes >= $terabyte) {
        return round($bytes / $terabyte, $precision) . ' TB';
    } else {
        return $bytes . ' B';
    }
}
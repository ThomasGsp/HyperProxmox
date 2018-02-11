<?php

class API_GET_INFO
{

    public function GET_Dates($select="all")
    {
        $dates = curl("api/v1/static/dates/".$select);
        return $dates;
    }

    public function GET_clusters_conf($cluster=null)
    {
        $cluster_conf = curl("api/v1/administration/cluster/".$cluster);
        return $cluster_conf;
    }
    
    public function GET_qemu($date, $cluster=null, $node=null, $vmid= null)
    {
        
        $qemu = curl("api/v1/static/instances/".$date."/");
        return $qemu;
    }

    public function GET_hyp($date, $cluster=null, $node=null)
    {
        $nodes = curl("api/v1/static/nodes/".$date."/");
        return $nodes;
    }

    public function GET_sto($date, $node = null, $storage = null)
    {
        
        $storages = curl("api/v1/static/storages/".$date."/");
        return $storages;
    }

    public function GET_Groups($date, $group = null)
    {
        if (!empty($group))
            $groups = curl($date."/groups/".$group);
        else
            $groups = curl($date."/groups/");

        return $groups;
    }

    public function GET_Disk($date, $cluster = null, $node = null)
    {
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


    public function List_Groups($timestamp = "")
    {
        $d = new API_GET_INFO;
        $groups = $d->GET_Groups($timestamp);
        $html = '';

        $arr_groups = json_decode($groups, true);


        foreach ($arr_groups as $group)
        {
            $clusters = $d->GET_Groups($timestamp, $group);

            $arr_clusters = json_decode($clusters, true);
            sort($arr_clusters);

            reset($arr_clusters);
            if (!empty($group))
            {
                $html = $html.'<li><a href="#">'.$group.'<span class="fa arrow"></span></a>';
                $html = $html.'<ul class="nav nav-third-level">';
                foreach ($arr_clusters as $cluster)
                {
                    $cluster = (object) $cluster;
                    $html = $html.'<li><a href="cluster.php?cluster='.$cluster->cluster.'">'.$cluster->cluster.'</a></li>';
                }
                $html = $html.'</ul></li>';
            }
            else {
                $html = $html.'<li><a href="#">'.$group.'<span class="fa arrow"></span></a>';
                $html = $html.'<ul class="nav nav-second-level"></ul></li>';
            }
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


    public function List_VMs($date, $node=null)
    {
        $html = '';
        $d = new API_GET_INFO; 
        $vms_list = json_decode($d->GET_qemu($date), true)['value'];       
         

        foreach ($vms_list as $qemu)
        {
            $qemu = (object) $qemu;
            $macs = "";
            $clusters_info = json_decode($d->GET_clusters_conf($qemu->cluster), true)['value'][0];
            $clusters_info = (object) $clusters_info;

            foreach($qemu->macaddr as $mac) { $macs =  $mac.",".$macs ; }
            $html = $html.'
                <tr>
                    <td></td>
                    <td>'.$qemu->cluster.'</td>
                    <td><a href="node.php?hyp='.$qemu->node.'&date='.$date.'"> '.$qemu->node.'</a> 
                     
                    <a data-toggle="tooltip" title="External Link: https://'.$clusters_info->url.':'.$clusters_info->port.'" href="https://'.$clusters_info->url.':'.$clusters_info->port.'/#v1:0:=qemu%2F'.$qemu->vmid.':4::::::" target="_blank"> <img src="images/fb-lien-420.png" alt="ExternalProxmoxLink" style="width:20px;height:20px;"></a></td>                    
                    <td><a href="vm.php?hyp='.$qemu->node.'&id='.$qemu->vmid.'&date='.$date.'"> '.$qemu->name.'</a></td>


                    <td>'.$qemu->vmid.'</td>
                    <td  data-order="'.$qemu->maxmem.'">'.formatBytes(round($qemu->maxmem)).'</td>
                    <td>'.$qemu->cpus.'</td>
                    <td>xx GB</td>
                    <td id="wrapper-mac"> <a data-toggle="tooltip" data-html="true" title="'.str_replace(",", "<br/>", $macs).'">'.$macs.'</a></td>
                    <td>'.secondsToDays($qemu->uptime).'</td>
                    <td>'.$qemu->status.'</td>
                    <td>
                        <select class="selectaction" data-width="auto" >
                        <option  value="{\'node\':\''.$qemu->node.'\',\'vmid\':\''.$qemu->vmid.'\',\'action\':\'none\'} ">Choice </option>
                            <optgroup label="No unavailability risk">                   
                                <option value="{\'node\':\''.$qemu->node.'\',\'vmid\':\''.$qemu->vmid.'\',\'action\':\'status\'}">Status</option>
                                <option value="{\'node\':\''.$qemu->node.'\',\'vmid\':\''.$qemu->vmid.'\',\'action\':\'start\'} ">Start</option>
                            </optgroup>
                            <optgroup label="Hight unavailability risk">   
                                <option value="{\'node\':\''.$qemu->node.'\',\'vmid\':\''.$qemu->vmid.'\',\'action\':\'stop\'} ">Stop</option>
                                <option value="{\'node\':\''.$qemu->node.'\',\'vmid\':\''.$qemu->vmid.'\',\'action\':\'shutdown\'} ">Shutdown</option>
                                <option value="{\'node\':\''.$qemu->node.'\',\'vmid\':\''.$qemu->vmid.'\',\'action\':\'reset\'} ">Reset</option>
                            </optgroup>
                            <optgroup label="Others">   
                                <option disabled value="{\'node\':\''.$qemu->node.'\',\'vmid\':\''.$qemu->vmid.'\',\'action\':\'migration\'} ">Migration</option>
                            </optgroup>
                        </select>
                    <!-- <img src="images/configuration_13194.png" alt="ExternalProxmoxLink" style="width:30px;height:30px;"> --> </td>
                </tr>';
        }
        return $html;
    }

    public function List_HYPs($date, $cluster = null)
    {
        require(dirname(__DIR__).'/requires/configs.php');
        //$m = new REQUESTS_MYSQL;
        //$non_grata = $m->non_grata_select();


        $q = new API_GET_INFO;
        $nodes = json_decode($q->GET_hyp($date, $cluster), true)['value'];
        arsort($nodes);
      
        $row_non_grata = [];
    
        /*
        foreach ($non_grata as $rows) {
            $row_non_grata[] = $rows->name;
        }
        */

        $html = '';
        
        foreach ($nodes as $node)
        {
            $node = (object) $node;
          
            $sto_info =  json_decode($q->GET_sto($date, $node->cluster, $node->name), true)['value'];
            
            if ($this->sto_regx_status == true)
            {
                foreach ($sto_info as $sto)
                {
                    $sto = (object)$sto;
                    if (preg_match($this->sto_regx, $sto->storage))
                    {
                        $sto_el = $sto->storage;
                        break;
                    }
                }
            }

            if($sto_el == "" or $this->sto_regx_status == false)
            {
                foreach ($sto_info as $sto) {
                    $sto = (object)$sto;
                    $sto_new = $sto->total;
                    if ($sto_new > $sto_max) {
                        $sto_max = $sto_new;
                        $sto_el = $sto->storage;
                    }
                }
            }
           

            $sto_el_node = json_decode($q->GET_sto($date, $node->cluster, $node->name, $sto_el), true)['value'][0];
            $sto_el_node = (object) $sto_el_node;

    
            $clusters_info = json_decode($q->GET_clusters_conf($node->cluster), true)['value'][0];
            $clusters_info = (object) $clusters_info;
            
            $ram_use_percent = round(($node->memory['used']/$node->memory['total'])*100);
            $ram_alloc_percent = round(($node->totalallocram/$node->memory['total'])*100);
            $cpu_alloc_percent = round(($node->totalalloccpu/$node->cpuinfo['cpus'])*100);
            $disk_use_percent = round((100/$sto_el_node->total)*$sto_el_node->used);
            $disk_alloc_percent = round(($sto_el_node->totalallocdisk/$sto_el_node->total)*100); // revoir param 1
            $load_percent = round($node->load*100);

            $eligibility = eligibility($ram_use_percent, $ram_alloc_percent, $cpu_alloc_percent, $disk_use_percent, $disk_alloc_percent, $load_percent);
            

            if (in_array($node->name, $row_non_grata)) {
                $grata = '<a class="nongratalink" data-toggle="tooltip" title="Switch to grata" id="'.$node->node.'" action="sw_ON" node="'.$node->name.'" href="#" > <img src="images/nongrata_on.png" alt="Nongrataimg" style="width:16px;height:16px;"></a>';
                $eligibility = round($eligibility +  $non_grata_weight);
            }
            else{
                $grata = '<a class="nongratalink" data-toggle="tooltip" title="Switch to non grata" id="'.$node->node.'"  action="sw_OFF" node="'.$node->name.'"  href="#" > <img src="images/nongrata_off.png" alt="Nongrataimg" style="width:16px;height:16px;"></a>';
            }


            $html = $html.'
                <tr>
                    <td></td>
                    <td>'.$node->cluster.'</td>
                    <td> 
                        <a href="node.php?hyp='.$node->node.'&date='.$date.'"> '.$node->node.'</a> 
                        <a  data-toggle="tooltip" title="External Link: https://'.$clusters_info->url.':'.$clusters_info->port.'"  href="https://'.$clusters_info->url.':'.$clusters_info->port.'/#v1:0:=node%2F'.$node->name.':4:5:::::" target="_blank"> <img src="images/fb-lien-420.png" alt="ExternalProxmoxLink" style="width:20px;height:20px;"></a>
                        '.$grata.'                    
                    </td>
                    <td style="color:'.testcolor("ram_use", $ram_use_percent).'" data-order="'.$ram_use_percent.'">'.formatBytes($node->memory['used']).' ('.$ram_use_percent.'%)</td>
                    <td style="color:'.testcolor("ram_alloc", $ram_alloc_percent).'"  data-order="'.$ram_alloc_percent.'">'.formatBytes($node->totalallocram).'/'.formatBytes($node->memory['total']).' ('.$ram_alloc_percent.'%)</td>
                    <td style="color:'.testcolor("cpu_alloc", $cpu_alloc_percent).'" data-order="'.$cpu_alloc_percent.'">'.$node->totalalloccpu.'/'.$node->maxcpu.' ('.$cpu_alloc_percent.'%)</td>
                    <td style="color:'.testcolor("disk_use", $disk_use_percent).'" data-order="'.$sto_el_node->used.'">'.formatBytes($sto_el_node->used).'('.$disk_use_percent.'% - '.$sto_el.')</td>
                    <td style="color:'.testcolor("disk_alloc", $disk_alloc_percent).'"  data-order="'.$sto_el_node->used.'">'.formatBytes($sto_el_node->totalallocdisk).'/'.formatBytes($sto_el_node->total).' ('.$disk_alloc_percent.'%) </td>
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


    public function List_STO($date, $node=null, $sto=null)
    {
        
        $q = new API_GET_INFO;
        $stos_list = json_decode($q->GET_sto($date), true)['value'];
        $html = '';
        
        foreach ($stos_list as $sto)
        {
            $sto = (object) $sto;
            
            $clusters_info = json_decode($q->GET_clusters_conf($sto->cluster), true)['value'][0];
            $clusters_info = (object) $clusters_info;
            
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
                                <th>Type</th>
                                <th>Vol.id</th>
                                <th>Size</th>
                            </tr>
                        </thead>';

            $disklists  = json_decode($q->GET_Disk($date, $sto->cluster, $sto->node), true)['value'];
            
            foreach ($disklists as $disklist) {
                $disklist = (object) $disklist;
                if ($disklist->storage == $sto->storage)
                    $htmldisk = $htmldisk.' <tr><td>'.$disklist->content.'</td>  <td>'.$disklist->volid.'</td>  <td>'.formatBytes($disklist->size).'</td></tr>';
            }
            $htmldisk = $htmldisk.'</table>';

            $html = $html.'
                <tr>
                    <td></td>
                    <td> <a href="node.php?hyp='.$sto->node.'&date='.$date.'"> '.$sto->node.'</a> <a  data-toggle="tooltip" title="External Link: https://'.$clusters_info->url.':'.$clusters_info->port.'"  href="https://'.$clusters_info->url.':'.$clusters_info->port.'/#v1:0:=storage%2F'.$sto->node.'%2F'.$sto->storage.':4::::::" target="_blank"> <img src="images/fb-lien-420.png" alt="ExternalProxmoxLink" style="width:20px;height:20px;"></a> </td>
                    <td> '.$sto->storage.'</td>
                    <td data-order="'.$sto->total.'"> '.formatBytes($sto->total).'</td>
                    <td data-order="'.$sto->totalalloc.'"> '.formatBytes($sto->totalallocdisk).' ('.$disk_alloc_percent.'%)</td>
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

        } catch (\Exception $e) {
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
<?php
require(dirname(__DIR__).'/requires/configs.php');
require(dirname(__DIR__).'/requires/functions.php');

//SESSION
session_start();
if (!isset($_SESSION['uid']) && ($useldap == true)) {
    header("location:login.php");
    die();
}

// GEN HTML LIST Dates
$html = new API_Gen_HTML;
$q = new API_GET_INFO;
$html_dates = [];
$lastdate = "";


if(!empty($_POST['date']))
{
    $html_dates = $html->List_Dates($_POST['date']);
    $lastdate = intval($_POST['date']);
}
else if(!empty($_GET['date']))
{
    $html_dates = $html->List_Dates($_GET['date']);
    $lastdate = intval($_GET['date']);
}
else
{
    $html_dates = $html->List_Dates();
    $lastdate = intval(json_decode($q->GET_Dates("last"), true)['value']);
}

//$html_groups = $html->List_Groups($lastdate);
?>


<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">

    <title>PCM</title>

    <!-- Bootstrap Core CSS -->
    <link href="../css/jquery-ui.css" rel="stylesheet">

    <!-- Bootstrap Core CSS -->
    <link href="../css/style.css" rel="stylesheet">

    <!-- Bootstrap Core CSS -->
    <link href="../vendor/bootstrap/css/bootstrap.css" rel="stylesheet">
    <link href="../vendor/bootstrap-select/css/bootstrap-select.css" rel="stylesheet">

    <!-- MetisMenu CSS -->
    <link href="../vendor/metisMenu/metisMenu.min.css" rel="stylesheet">

    <!-- DataTables CSS -->
    <link href="../vendor/datatables-plugins/dataTables.bootstrap.css" rel="stylesheet">

    <!-- DataTables Responsive CSS -->
    <link href="../vendor/datatables-responsive/dataTables.responsive.css" rel="stylesheet">

    <!-- Custom CSS -->
    <link href="../dist/css/sb-admin-2.css" rel="stylesheet">

    <!-- Custom Fonts -->
    <link href="../vendor/font-awesome/css/font-awesome.min.css" rel="stylesheet" type="text/css">

    <!-- jQuery -->
    <script src="../js/jquery-1.12.3.js"></script>
    <script src="../js/jquery-ui.js"></script>

    <!-- Bootstrap Core JavaScript -->
    <script src="../vendor/bootstrap/js/bootstrap.min.js"></script>
    <script src="../vendor/bootstrap-select/js/bootstrap-select.js"></script>


    <!-- Metis Menu Plugin JavaScript -->
    <script src="../vendor/metisMenu/metisMenu.min.js"></script>

    <!-- DataTables JavaScript -->
    <script src="../vendor/datatables/js/jquery.dataTables.min.js"></script>
    <script src="../vendor/datatables-plugins/dataTables.bootstrap.min.js"></script>
    <script src="../vendor/datatables-responsive/dataTables.responsive.js"></script>

     <!-- Morris Charts JavaScript -->
    <script src="../vendor/raphael/raphael.min.js"></script>
    <script src="../vendor/morrisjs/morris.min.js"></script>

    <!-- Custom Theme JavaScript -->
    <script src="../dist/js/sb-admin-2.js"></script>

    <!-- Include the plugin's CSS and JS: -->
    <script type="text/javascript" src="../vendor/bootstrap-multisltc/js/bootstrap-multiselect.js"></script>
    <link rel="stylesheet" href="../vendor/bootstrap-multisltc/css/bootstrap-multiselect.css" type="text/css"/>

    <!-- Main -->
    <script src="js/main.js"></script>

</head>

<body>
<div id="wrapper">

    <!-- Navigation -->
    <nav class="navbar navbar-default navbar-static-top" role="navigation" style="margin-bottom: 0">
        <div class="navbar-header">
            <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="index.php">Hyperproxmox - alpha 1.0</a>

            <form method="POST" class="navbar-brand" action="" style="margin-top: -7px">
                    <?php echo $html_dates; ?> &nbsp;&nbsp; <INPUT type="submit" class="btn btn-default pull-right" value="OK">
            </form>
        </div>
        <!-- /.navbar-header -->

        <ul class="nav navbar-top-links navbar-right">
            <?php
            if ($useldap == true)
            {
                echo "Welcome ".$_SESSION['uid'];
            }
            else
                echo "Welcome guest !";
            ?>

            <!-- /.dropdown -->
            <li class="dropdown">
                <a class="dropdown-toggle" data-toggle="dropdown" href="#">
                    <i class="fa fa-user fa-fw"></i> <i class="fa fa-caret-down"></i>
                </a>
                <?php
                if ($useldap == true)
                {
                    echo '
                    <ul class="dropdown-menu dropdown-user">
                        <li><a href="login.php?logout="><i class="fa fa-sign-out fa-fw"></i> Logout</a></li>
                    </ul>
                    ';
                }
                ?>
            </li>
        </ul>
        <div class="navbar-default sidebar" role="navigation">
            <div class="sidebar-nav navbar-collapse">
                <ul class="nav" id="side-menu">
                    <li><a href="vms.php?date=<?php echo $lastdate; ?>"><i class="fa fa-table fa-fw"></i>Instances</a></li>
                    <li><a href="nodes.php?date=<?php echo $lastdate; ?>"><i class="fa fa-table fa-fw"></i>Nodes</a></li>
                    <li><a href="storages.php?date=<?php echo $lastdate; ?>"><i class="fa fa-table fa-fw"></i>Storages</a></li>
                    <!--
                    <li>
                        <a href="#"><i class="fa fa-sitemap fa-fw"></i> Groups <span class="fa arrow"></span></a>
                        <ul class="nav nav-second-level">
                            <?php // echo $html_groups;  ?>
                        </ul>
                    </li>
                </ul>
            </div>
            <!-- /.sidebar-collapse -->
        </div>
        <!-- /.navbar-static-side -->
    </nav>

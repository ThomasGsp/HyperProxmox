<?php
require("connectors/ldap.php");


// check to see if login form has been submitted
if(isset($_POST['username'])){
    // run information through authenticator
    if(ldaplogin($_POST['username'], $_POST['password']))
    {
        session_start();
        $_SESSION['uid'] = $_POST['username'];
        // authentication passed
        header("Location: index.php");
        die();
    } else {
        // authentication failed
        $error = 1;
    }
}

$message = "";

// output error to user
if(isset($error)) $message = '<div class="alert alert-warning">Login failed: Incorrect user name or password</div>';

// output logout success
if(isset($_GET['logout']))
{
    session_start();
    $message = '<div class="alert alert-info">Logout successful</div>';
    session_destroy();
}

?>



<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">

    <title>Proxmox Viewer</title>

    <!-- Bootstrap Core CSS -->
    <link href="../vendor/bootstrap/css/bootstrap.min.css" rel="stylesheet">

    <!-- MetisMenu CSS -->
    <link href="../vendor/metisMenu/metisMenu.min.css" rel="stylesheet">

    <!-- Custom CSS -->
    <link href="../dist/css/sb-admin-2.css" rel="stylesheet">

    <!-- Custom Fonts -->
    <link href="../vendor/font-awesome/css/font-awesome.min.css" rel="stylesheet" type="text/css">

</head>

<body>

<div class="container">
    <div class="row">
        <div class="col-md-4 col-md-offset-4">
            <div class="login-panel panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Please Sign In with your LDAP authentication</h3>
                </div>
                <div class="panel-body">
                    <form method="post" action="login.php" role="form">
                        <fieldset>
                            <div class="form-group">
                                <input class="form-control" placeholder="Username" name="username" type="text" autofocus>
                            </div>
                            <div class="form-group">
                                <input class="form-control" placeholder="Password" name="password" type="password" value="">
                            </div>
                            <div class="checkbox">
                                <label>
                                    <input name="remember" type="checkbox" value="Remember Me">Remember Me
                                </label>
                            </div>
                            <input type="submit" class="btn btn-lg btn-success btn-block" name="submit" value="Login" />
                        </fieldset>
                    </form>
                    <br />
                    <?php echo  $message ?>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- jQuery -->
<script src="../vendor/jquery/jquery.min.js"></script>

<!-- Bootstrap Core JavaScript -->
<script src="../vendor/bootstrap/js/bootstrap.min.js"></script>

<!-- Metis Menu Plugin JavaScript -->
<script src="../vendor/metisMenu/metisMenu.min.js"></script>

<!-- Custom Theme JavaScript -->
<script src="../dist/js/sb-admin-2.js"></script>

</body>

</html>

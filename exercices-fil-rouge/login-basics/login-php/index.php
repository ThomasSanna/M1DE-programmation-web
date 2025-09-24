<?php
require_once 'db.php';
require_once 'functions.php';

if (!check_login()) {
    header("Location: login.php");
    exit;
}
?>

<h1>Bienvenue <?= htmlspecialchars($_SESSION['username']) ?></h1>
<p><a href="logout.php">Se déconnecter</a></p>
<?php
require 'db.php';
require 'functions.php';

// Utilisateur déjà connecté?
if (isset($_SESSION['user_id'])) {
    header("Location: index.php");
    exit; // exit est utilisé pour s'assurer que le script s'arrête après la redirection
}

// POST
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['username'], $_POST['password'])) {
        $username = $_POST['username'];
        $password = $_POST['password'];

        // Tente de connecter l'utilisateur
        if (login($pdo, $username, $password)) {
            header("Location: index.php");
            exit;
        } else {
            $error = "Identifiants incorrects";
        }
    } else {
        $error = "Veuillez remplir tous les champs.";
    }
}
?>

<h1>Connexion</h1>
<form method="post">
    <input name="username" placeholder="Nom d'utilisateur" required>
    <input type="password" name="password" placeholder="Mot de passe" required>
    <button>Connexion</button>
</form>
<p><a href="register.php">S'inscrire</a></p>

<!--  message d'erreur si nécessaire -->
<?php if(isset($error)) echo '<p style="color:red;">' . htmlspecialchars($error, ENT_QUOTES, 'UTF-8') . '</p>'; ?>

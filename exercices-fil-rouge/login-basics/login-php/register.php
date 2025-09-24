<?php
require 'db.php';
require 'functions.php';

// Renvoyer vers index si déjà connecté
if (isset($_SESSION['user_id'])) {
    header("Location: index.php");
    exit;
}

// POST
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'];
    $email = $_POST['email'];
    $password = $_POST['password'];

    if (get_user_by_email($pdo, $email) || get_user_by_username($pdo, $username)) {
        $error = "Nom d'utilisateur ou email déjà utilisé.";
    } else {
        if (register($pdo, $username, $email, $password)) {
            $_SESSION['user_id'] = $pdo->lastInsertId();
            $_SESSION['username'] = $username;
            header("Location: index.php");
            exit;
        } else {
            $error = "Impossible de s'inscrire";
        }
    }
}
?>

<h1>S'inscrire</h1>

<form method="post">
    <input name="username" placeholder="Nom d'utilisateur" required>
    <input type="email" name="email" placeholder="Email" required>
    <input type="password" name="password" placeholder="Mot de passe" required>
    <button>S'inscrire</button>
</form>
<p><a href="login.php">Se connecter</a></p>

<!--  message d'erreur si nécessaire -->
<?php if(isset($error)) echo '<p style="color:red;">' . htmlspecialchars($error, ENT_QUOTES, 'UTF-8') . '</p>'; ?>

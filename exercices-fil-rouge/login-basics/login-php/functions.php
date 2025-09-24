<?php
function register($pdo, $username, $email, $password) {
    $hash = password_hash($password, PASSWORD_DEFAULT);
    $stmt = $pdo->prepare("INSERT INTO user (user_login, user_mail, user_password) VALUES (?, ?, ?)");
    return $stmt->execute([$username, $email, $hash]);
}

function login($pdo, $username, $password) {
    $stmt = $pdo->prepare("SELECT * FROM user WHERE user_login = ?");
    $stmt->execute([$username]);
    $user = $stmt->fetch();
    if ($user && password_verify($password, $user['user_password'])) {
        $_SESSION['user_id'] = $user['user_id'];
        $_SESSION['username'] = $user['user_login'];
        return true;
    }
    return false;
}

function get_user_by_username($pdo, $username) {
    $stmt = $pdo->prepare("SELECT * FROM user WHERE user_login = ?");
    $stmt->execute([$username]);
    return $stmt->fetch();
}

function get_user_by_email($pdo, $email) {
    $stmt = $pdo->prepare("SELECT * FROM user WHERE user_mail = ?");
    $stmt->execute([$email]);
    return $stmt->fetch();
}

function check_login() {
    return isset($_SESSION['user_id']);
}

function logout() {
    session_unset();
    session_destroy();
}
?>

<?php
// INTENTIONALLY VULNERABLE TRAINING SAMPLE — never deploy.
$username = $_POST['username'] ?? '';
$password = $_POST['password'] ?? '';
$db_password = "demo-password-12345";
$sql = "SELECT * FROM users WHERE username = '" . $username . "'";
// Unsafe SQL construction and direct output are shown for review practice only.
echo $_GET['message'] ?? '';
?>
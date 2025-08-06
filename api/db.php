<?php
$host = "localhost";       // or your server name (e.g., "127.0.0.1")
$dbname = "chatbot"; // change to your database name
$username = "root";        // your DB username
$password = "root";            // your DB password (set this securely)

$conn = new mysqli($host, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>

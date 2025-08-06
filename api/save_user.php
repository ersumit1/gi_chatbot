<?php
include "db.php";  // your DB connection file

$name = $_POST['name'];
$mobile = $_POST['mobile'];

if (!preg_match("/^[6-9][0-9]{9}$/", $mobile)) {
    echo json_encode(["error" => "Invalid mobile number"]);
    exit;
}

$stmt = $conn->prepare("INSERT IGNORE INTO users (name, mobile) VALUES (?, ?)");
$stmt->bind_param("ss", $name, $mobile);
$stmt->execute();

// Get the user_id back
$stmt2 = $conn->prepare("SELECT user_id FROM users WHERE mobile = ?");
$stmt2->bind_param("s", $mobile);
$stmt2->execute();
$result = $stmt2->get_result();
$user = $result->fetch_assoc();

echo json_encode(["user_id" => $user["user_id"]]);
?>

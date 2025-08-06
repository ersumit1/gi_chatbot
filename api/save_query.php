<?php
include "db.php";

$user_id = $_POST['user_id'];
$question = $_POST['question'];
$response = $_POST['response'];

$stmt = $conn->prepare("INSERT INTO queries (user_id, question, response) VALUES (?, ?, ?)");
$stmt->bind_param("iss", $user_id, $question, $response);
$stmt->execute();

echo json_encode(["status" => "saved"]);
?>
<?php
include "db.php";

$mobile = $_GET['mobile'];
$stmt = $conn->prepare("SELECT user_id FROM users WHERE mobile = ?");
$stmt->bind_param("s", $mobile);
$stmt->execute();
$result = $stmt->get_result();

if ($row = $result->fetch_assoc()) {
    echo json_encode(["user_id" => $row["user_id"]]);
} else {
    echo json_encode(["user_id" => null]);
}
?>

<?php
class SQLiteDatabase {
    private $pdo;

    public function __construct($dbPath) {
        $this->pdo = new PDO("sqlite:" . $dbPath);
        $this->pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    }

    public function getAllKeys($table, $keyColumn) {
        $stmt = $this->pdo->query("SELECT $keyColumn FROM $table");
        return $stmt->fetchAll(PDO::FETCH_COLUMN);
    }

    public function getRecord($table, $keyColumn, $keyValue) {
        $stmt = $this->pdo->prepare("SELECT * FROM $table WHERE $keyColumn = :keyValue");
        $stmt->execute(['keyValue' => $keyValue]);
        return $stmt->fetch(PDO::FETCH_ASSOC);
    }

    public function executeQuery($query, $params = []) {
        $stmt = $this->pdo->prepare($query);
        $stmt->execute($params);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
}

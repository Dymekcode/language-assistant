-- 1. Wyłączamy sprawdzanie kluczy, żeby baza pozwoliła nam usunąć tabele
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS conversation_logs;
DROP TABLE IF EXISTS users;

-- 2. Włączamy sprawdzanie z powrotem, żeby nowe tabele były bezpieczne
SET FOREIGN_KEY_CHECKS = 1;

-- 3. Tworzymy tabelę użytkowników
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(50)
);

-- 4. Tworzymy tabelę logów
CREATE TABLE conversation_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    original_text TEXT,
    corrected_text TEXT,
    error_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 5. Wpisujemy dane
INSERT INTO users (user_name) VALUES ('Szymon');
INSERT INTO conversation_logs (user_id, original_text, corrected_text, error_type) 
VALUES (1, 'I has a dog', 'I have a dog', 'Grammar');

-- 6. Sprawdzamy wynik
SELECT * FROM users;
SELECT * FROM conversation_logs;
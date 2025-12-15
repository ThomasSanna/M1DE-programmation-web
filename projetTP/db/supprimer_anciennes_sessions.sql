-- à titre de visualisation seulement
SELECT * FROM game_sessions
WHERE start_time < NOW() - INTERVAL 1 DAY AND is_completed = 0;

-- Suppression des anciennes sessions de jeu incomplètes
DELETE FROM game_sessions
WHERE start_time < NOW() - INTERVAL 1 DAY AND is_completed = 0;
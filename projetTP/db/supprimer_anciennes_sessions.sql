SELECT * FROM game_sessions
WHERE start_time < NOW() - INTERVAL 1 DAY AND is_completed = 0;

DELETE FROM game_sessions
WHERE start_time < NOW() - INTERVAL 1 DAY AND is_completed = 0;
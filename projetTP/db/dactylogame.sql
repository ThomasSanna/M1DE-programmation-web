- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : lun. 17 nov. 2025 à 18:53
-- Version du serveur : 10.4.32-MariaDB
-- Version de PHP : 8.1.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `dactylogame`
--

-- --------------------------------------------------------

--
-- Structure de la table `game_sessions`
--

CREATE TABLE `game_sessions` (
  `id` int(11) NOT NULL,
  `user_id` int(11),
  `session_token` varchar(64) NOT NULL,
  `words_sequence` text NOT NULL,
  `seed` varchar(32) NOT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp(),
  `expected_end_time` timestamp NOT NULL DEFAULT current_timestamp(),
  `is_completed` tinyint(1) DEFAULT 0,
  `score_id` int(11) DEFAULT NULL,
  `words_correct_count` int(11) NOT NULL DEFAULT 0 COMMENT 'Compteur sécurisé côté serveur',
  `words_wrong_count` int(11) NOT NULL DEFAULT 0 COMMENT 'Compteur sécurisé côté serveur'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `scores`
--

CREATE TABLE `scores` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `score` int(11) NOT NULL DEFAULT 0,
  `words_correct` int(11) NOT NULL DEFAULT 0,
  `words_wrong` int(11) NOT NULL DEFAULT 0,
  `duration` int(11) NOT NULL DEFAULT 30 COMMENT 'Durée en secondes',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `created_at`, `updated_at`) VALUES
(1, 'admin', 'admin@dactylogame.fr', 'test_hash_1', '2025-11-16 12:22:47', '2025-11-16 12:22:47'),
(2, 'player1', 'player1@example.com', 'test_hash_2', '2025-11-16 12:22:47', '2025-11-16 12:22:47'),
(3, 'player2', 'player2@example.com', 'test_hash_3', '2025-11-16 12:22:47', '2025-11-16 12:22:47'),
(4, 'testest', 'testest@gmail.com', '6fb83b387310f99a97627e51fd4589f9$9e4c69c89306fdc6782bae530bdf868378659e6ce364e16a4a3aff21e69fd507', '2025-11-16 12:26:12', '2025-11-16 12:26:12');

-- --------------------------------------------------------

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `game_sessions`
--
ALTER TABLE `game_sessions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `session_token` (`session_token`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `score_id` (`score_id`);

--
-- Index pour la table `scores`
--
ALTER TABLE `scores`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_score` (`score`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- Index pour la table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `idx_username` (`username`),
  ADD KEY `idx_email` (`email`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `game_sessions`
--
ALTER TABLE `game_sessions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `scores`
--
ALTER TABLE `scores`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT pour la table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `game_sessions`
--
ALTER TABLE `game_sessions`
  ADD CONSTRAINT `game_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `game_sessions_ibfk_2` FOREIGN KEY (`score_id`) REFERENCES `scores` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `scores`
--
ALTER TABLE `scores`
  ADD CONSTRAINT `scores_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

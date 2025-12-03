-- --------------------------------------------------------
-- Host:                                127.0.0.1
-- Versión del servidor:                10.4.32-MariaDB - mariadb.org binary distribution
-- SO del servidor:                     Win64
-- HeidiSQL Versión:                    12.13.0.7147
--
-- ESQUEMA DEFINITIVO VERSIÓN 2.0 (SINCRONIZADO CON REGISTRO.HTML)
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Eliminando base de datos y volviendo a crear para un inicio limpio
DROP DATABASE IF EXISTS `izakaya`; 
CREATE DATABASE IF NOT EXISTS `izakaya` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
USE `izakaya`;

-- Volcando estructura para la tabla izakaya.usuario
-- Estructura FINAL con los 12 campos de datos del formulario.
CREATE TABLE IF NOT EXISTS `usuario` (
  `user_ID` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `apellidos` varchar(50) NOT NULL,
  `dia` tinyint(4) NOT NULL,
  `mes` tinyint(4) NOT NULL,
  `anio` int(11) NOT NULL,
  `genero` enum('H','M','O','P') NOT NULL,  -- H: Hombre, M: Mujer, O: Otro, P: Prefiero no decirlo
  `actFisica` enum('Y','N') NOT NULL,      -- CAMPO SINCRONIZADO: Y: Sí, N: No
  
  -- CAMPOS OPCIONALES AÑADIDOS DESDE EL FORMULARIO
  `objetivo` varchar(255) DEFAULT NULL,    -- Objetivo principal (Opcional, puede ser NULL)
  `dieta` varchar(255) DEFAULT NULL,       -- Tipo de dieta (Opcional, puede ser NULL)
  `alergias` varchar(500) DEFAULT NULL,    -- Alergias o restricciones (Opcional, puede ser NULL)

  `correo` varchar(50) NOT NULL UNIQUE,    -- Correo electrónico (único)
  `contrasena` varchar(255) NOT NULL,      -- Hash de contraseña
  
  PRIMARY KEY (`user_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla `usuario` (vacío por ahora)
DELETE FROM `usuario`;

-- Restaurar las configuraciones previas
/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
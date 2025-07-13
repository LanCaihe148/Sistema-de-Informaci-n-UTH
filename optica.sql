-- phpMyAdmin SQL Dump
-- version 4.7.9
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1:3307
-- Tiempo de generación: 10-07-2025 a las 18:25:11
-- Versión del servidor: 10.2.14-MariaDB
-- Versión de PHP: 5.6.35

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `optica`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

DROP TABLE IF EXISTS `clientes`;
CREATE TABLE IF NOT EXISTS `clientes` (
  `id_cliente` bigint(20) NOT NULL AUTO_INCREMENT,
  `cliente` varchar(40) DEFAULT NULL,
  `celular` varchar(20) DEFAULT NULL,
  `domicilio` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`id_cliente`)
) ENGINE=MyISAM AUTO_INCREMENT=17 DEFAULT CHARSET=latin1;

--
-- Volcado de datos para la tabla `clientes`
--

INSERT INTO `clientes` (`id_cliente`, `cliente`, `celular`, `domicilio`) VALUES
(1, 'efrain sandoval', '6624006571', 'colonia Altamira, cosahui #47'),
(2, 'logan pitsakis', '6621126545', 'colonia altares, carta blanca #65'),
(3, 'ian carlo', '6622057890', 'colonia la nuevo, tejones #66'),
(4, 'luis arraez', '6625374821', 'colonia La nuevo, jecota corriosa #34'),
(5, 'jonathan beltran', '6625435462', 'colonia Los encinos etapa 2, efrain huerta #132'),
(9, 'jose altuve', '6635263522', 'colonia Amapola, semilla #2'),
(13, 'victor arriola', '6621525526', 'colonia Altares, retorno jesus hdz saucedo #5'),
(16, 'manny machado', '6621736621', 'colonia Rio bravo, agua azul #87');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `lentes`
--

DROP TABLE IF EXISTS `lentes`;
CREATE TABLE IF NOT EXISTS `lentes` (
  `id_lente` bigint(20) NOT NULL AUTO_INCREMENT,
  `lente` varchar(40) DEFAULT NULL,
  `precio` decimal(15,2) DEFAULT NULL,
  `disponibilidad` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_lente`)
) ENGINE=MyISAM AUTO_INCREMENT=14 DEFAULT CHARSET=latin1;

--
-- Volcado de datos para la tabla `lentes`
--

INSERT INTO `lentes` (`id_lente`, `lente`, `precio`, `disponibilidad`) VALUES
(1, 'RayBan eclipse', '1800.00', 44),
(2, 'Carlo Marioni', '3600.00', 32),
(3, 'Lv', '10000.00', 47),
(4, 'RayBan aviator', '4700.00', 43),
(12, 'Nike Runner', '3400.00', 50);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id_usuario` bigint(20) NOT NULL AUTO_INCREMENT,
  `usuario` varchar(40) DEFAULT NULL,
  `cuenta` varchar(20) DEFAULT NULL,
  `clave` varchar(128) DEFAULT NULL,
  `nivel` int(11) DEFAULT NULL,
  `idioma` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_usuario`)
) ENGINE=MyISAM AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuario`, `usuario`, `cuenta`, `clave`, `nivel`, `idioma`) VALUES
(1, 'Luis Ortega', 'admin', '0000', 1, 1),
(2, 'Jose Martinez', 'operador', '1111', 2, 2),
(3, 'Ian Carlo', 'ian', '2222', 2, 1),
(7, 'Maria Benitez', 'mrbntz', '1234', 2, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ventas`
--

DROP TABLE IF EXISTS `ventas`;
CREATE TABLE IF NOT EXISTS `ventas` (
  `id_venta` bigint(20) NOT NULL AUTO_INCREMENT,
  `id_cliente` bigint(20) DEFAULT NULL,
  `id_lente` bigint(20) DEFAULT NULL,
  `id_usuario` bigint(20) DEFAULT NULL,
  `total` decimal(15,2) DEFAULT NULL,
  `fechahora` datetime DEFAULT NULL,
  PRIMARY KEY (`id_venta`)
) ENGINE=MyISAM AUTO_INCREMENT=19 DEFAULT CHARSET=latin1;

--
-- Volcado de datos para la tabla `ventas`
--

INSERT INTO `ventas` (`id_venta`, `id_cliente`, `id_lente`, `id_usuario`, `total`, `fechahora`) VALUES
(1, 1, 1, 1, '1800.00', '2025-05-19 08:21:33'),
(2, 2, 2, 1, '3600.00', '2025-05-19 09:00:00'),
(3, 3, 3, 1, '10000.00', '2025-05-19 10:15:00'),
(4, 2, 1, 1, '1800.00', '2025-06-23 10:06:55'),
(5, 2, 3, 1, '10000.00', '2025-06-23 11:28:33'),
(6, 4, 2, 2, '3600.00', '2025-06-24 11:32:50'),
(7, 5, 3, 1, '10000.00', '2025-06-24 11:20:50');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

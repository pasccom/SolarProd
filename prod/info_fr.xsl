<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:import href="info.xsl" />

    <xsl:variable name="lang" select="document('')/*/xsl:variable[substring(@name, 1, 5)='lang.']" />
    <xsl:variable name="lang.plant">Installation</xsl:variable>
    <xsl:variable name="lang.characteristics">Caractéristiques</xsl:variable>
    <xsl:variable name="lang.inverters">Onduleurs</xsl:variable>
    <xsl:variable name="lang.solar_log">SolarLog</xsl:variable>
    <xsl:variable name="lang.software">Logiciel</xsl:variable>

    <xsl:variable name="lang.name">Nom</xsl:variable>
    <xsl:variable name="lang.orientation">Orientation</xsl:variable>
    <xsl:variable name="lang.panels">Panneaux</xsl:variable>
    <xsl:variable name="lang.city">Ville</xsl:variable>
    <xsl:variable name="lang.lang">Pays</xsl:variable>
    <xsl:variable name="lang.owner">Propriétaire</xsl:variable>

    <xsl:variable name="lang.date_start">Date de mise en service</xsl:variable>
    <xsl:variable name="lang.current">Temps actuel</xsl:variable>
    <xsl:variable name="lang.interval">Intervalle de sauvegarde</xsl:variable>
    <xsl:variable name="lang.online">En ligne</xsl:variable>
    <xsl:variable name="lang.temp">Température</xsl:variable>
    <xsl:variable name="lang.maximum_power">Puissance maximale</xsl:variable>
    <xsl:variable name="lang.reward">Gain estimé</xsl:variable>
    <xsl:variable name="lang.production_hours">Horaires de production</xsl:variable>
    <xsl:variable name="lang.months">Janvier Février Mars Avril Mai Juin Juillet Août Septembre Octobre Novembre Décembre</xsl:variable>

    <xsl:variable name="lang.model">Modèle</xsl:variable>
    <xsl:variable name="lang.serial_number">Numéro de série</xsl:variable>
    <xsl:variable name="lang.rated_power">Puissance nominale</xsl:variable>
    <xsl:variable name="lang.fw_version">Version du firmware</xsl:variable>
    <xsl:variable name="lang.fw_date">Date du firmware</xsl:variable>
    <xsl:variable name="lang.config">Configuration</xsl:variable>

    <xsl:variable name="lang.prod">Page web</xsl:variable>
    <xsl:variable name="lang.distribution">Distribution</xsl:variable>
    <xsl:variable name="lang.uname">Linux</xsl:variable>
    <xsl:variable name="lang.web">Serveur Web</xsl:variable>
    <xsl:variable name="lang.ftp">Serveur FTP</xsl:variable>
    <xsl:variable name="lang.ssh">Serveur SSH</xsl:variable>

    <xsl:variable name="lang.version">Version</xsl:variable>
    <xsl:variable name="lang.arch">Architecture</xsl:variable>

    <xsl:variable name="lang.True">Oui</xsl:variable>
    <xsl:variable name="lang.False">Non</xsl:variable>

    <xsl:variable name="lang.send_mail">Enoyer un courriel à</xsl:variable>
    <xsl:variable name="lang.web_site">Site Web de</xsl:variable>
    <xsl:variable name="lang.plant_picture">Photo de l'installation</xsl:variable>
</xsl:stylesheet>

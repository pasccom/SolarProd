<?xml version="1.0" encoding="UTF-8"?>
<!-- Copyright 2018-2020 Pascal COMBES <pascom@orange.fr>
     
     This file is part of SolarProd.
     
     SolarProd is free software: you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation, either version 3 of the License, or
     (at your option) any later version.
     
     SolarProd is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
     GNU General Public License for more details.
     
     You should have received a copy of the GNU General Public License
     along with SolarProd. If not, see <http://www.gnu.org/licenses/>
-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:exsl="http://exslt.org/common">
    <xsl:import href="info.xsl" />

    <xsl:variable name="dict">
        <tr name="plant">Installation</tr>
        <tr name="characteristics">Caractéristiques</tr>
        <tr name="inverters">Onduleurs</tr>
        <tr name="solar_log">SolarLog</tr>
        <tr name="software">Logiciel</tr>

        <tr name="name">Nom</tr>
        <tr name="orientation">Orientation</tr>
        <tr name="panels">Panneaux</tr>
        <tr name="city">Ville</tr>
        <tr name="lang">Pays</tr>
        <tr name="owner">Propriétaire</tr>

        <tr name="date_start">Date de mise en service</tr>
        <tr name="current">Temps actuel</tr>
        <tr name="interval">Intervalle de sauvegarde</tr>
        <tr name="online">En ligne</tr>
        <tr name="temp">Température</tr>
        <tr name="maximum_power">Puissance maximale</tr>
        <tr name="reward">Gain estimé</tr>
        <tr name="production_hours">Horaires de production</tr>
        <tr name="months">Janvier Février Mars Avril Mai Juin Juillet Août Septembre Octobre Novembre Décembre</tr>

        <tr name="model">Modèle</tr>
        <tr name="serial_number">Numéro de série</tr>
        <tr name="rated_power">Puissance nominale</tr>
        <tr name="fw_version">Version du firmware</tr>
        <tr name="fw_date">Date du firmware</tr>
        <tr name="config">Configuration</tr>

        <tr name="prod">Page web</tr>
        <tr name="distribution">Distribution</tr>
        <tr name="uname">Linux</tr>
        <tr name="web">Serveur Web</tr>
        <tr name="ftp">Serveur FTP</tr>
        <tr name="ssh">Serveur SSH</tr>

        <tr name="version">Version</tr>
        <tr name="arch">Architecture</tr>

        <tr name="True">Oui</tr>
        <tr name="False">Non</tr>

        <tr name="send_mail">Enoyer un courriel à</tr>
        <tr name="web_site">Site Web de</tr>
        <tr name="plant_picture">Photo de l'installation</tr>
    </xsl:variable>

    <!-- Store all translations as a node list in "lang" variable -->
    <xsl:variable name="lang" select="exsl:node-set($dict)/tr" />
</xsl:stylesheet>

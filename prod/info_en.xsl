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
        <tr name="plant">Plant</tr>
        <tr name="characteristics">Characteristics</tr>
        <tr name="inverters">Inverters</tr>
        <tr name="solar_log">SolarLog</tr>
        <tr name="software">Software</tr>

        <tr name="name">Name</tr>
        <tr name="orientation">Orientation</tr>
        <tr name="panels">Panels</tr>
        <tr name="city">City</tr>
        <tr name="lang">Country</tr>
        <tr name="owner">Owner</tr>

        <tr name="date_start">Start date</tr>
        <tr name="current">Current time</tr>
        <tr name="interval">Transmission interval</tr>
        <tr name="online">Online</tr>
        <tr name="temp">Temperature</tr>
        <tr name="maximum_power">Maximum power</tr>
        <tr name="reward">Estimated reward</tr>
        <tr name="production_hours">Production hours</tr>
        <tr name="months">January February March April May June July August September October November Décember</tr>

        <tr name="model">Model</tr>
        <tr name="serial_number">Serial number</tr>
        <tr name="rated_power">Rated power</tr>
        <tr name="fw_version">Firmware version</tr>
        <tr name="fw_date">Firmware date</tr>
        <tr name="config">Configuration</tr>

        <tr name="prod">Web page</tr>
        <tr name="distribution">Distribution</tr>
        <tr name="uname">Linux</tr>
        <tr name="web">Web Server</tr>
        <tr name="ftp">FTP Server</tr>
        <tr name="ssh">SSH Server</tr>

        <tr name="version">Version</tr>
        <tr name="arch">Architecture</tr>

        <tr name="True">Yes</tr>
        <tr name="False">No</tr>

        <tr name="send_mail">Send an email to</tr>
        <tr name="web_site">Website of</tr>
        <tr name="plant_picture">Photo of the plant</tr>
    </xsl:variable>

    <!-- Store all translations as a node list in "lang" variable -->
    <xsl:variable name="lang" select="exsl:node-set($dict)/tr" />
</xsl:stylesheet>

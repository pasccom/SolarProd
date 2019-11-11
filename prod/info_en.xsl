<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:import href="info.xsl" />

    <xsl:variable name="lang" select="document('')/*/xsl:variable[substring(@name, 1, 5)='lang.']" />
    <xsl:variable name="lang.plant">Plant</xsl:variable>
    <xsl:variable name="lang.characteristics">Characteristics</xsl:variable>
    <xsl:variable name="lang.inverters">Inverters</xsl:variable>
    <xsl:variable name="lang.solar_log">SolarLog</xsl:variable>
    <xsl:variable name="lang.software">Software</xsl:variable>

    <xsl:variable name="lang.name">Name</xsl:variable>
    <xsl:variable name="lang.orientation">Orientation</xsl:variable>
    <xsl:variable name="lang.panels">Panels</xsl:variable>
    <xsl:variable name="lang.city">City</xsl:variable>
    <xsl:variable name="lang.lang">Country</xsl:variable>
    <xsl:variable name="lang.owner">Owner</xsl:variable>

    <xsl:variable name="lang.date_start">Start date</xsl:variable>
    <xsl:variable name="lang.current">Current time</xsl:variable>
    <xsl:variable name="lang.interval">Transmission interval</xsl:variable>
    <xsl:variable name="lang.online">Online</xsl:variable>
    <xsl:variable name="lang.temp">Temperature</xsl:variable>
    <xsl:variable name="lang.maximum_power">Maximum power</xsl:variable>
    <xsl:variable name="lang.reward">Estimated reward</xsl:variable>
    <xsl:variable name="lang.production_hours">Production hours</xsl:variable>
    <xsl:variable name="lang.months">January February March April May June July August September October November Décember</xsl:variable>

    <xsl:variable name="lang.model">Model</xsl:variable>
    <xsl:variable name="lang.serial_number">Serial number</xsl:variable>
    <xsl:variable name="lang.rated_power">Rated power</xsl:variable>
    <xsl:variable name="lang.fw_version">Firmware version</xsl:variable>
    <xsl:variable name="lang.fw_date">Firmware date</xsl:variable>
    <xsl:variable name="lang.config">Configuration</xsl:variable>

    <xsl:variable name="lang.prod">Web page</xsl:variable>
    <xsl:variable name="lang.distribution">Distribution</xsl:variable>
    <xsl:variable name="lang.uname">Linux</xsl:variable>
    <xsl:variable name="lang.web">Web Server</xsl:variable>
    <xsl:variable name="lang.ftp">FTP Server</xsl:variable>
    <xsl:variable name="lang.ssh">SSH Server</xsl:variable>

    <xsl:variable name="lang.version">Version</xsl:variable>
    <xsl:variable name="lang.arch">Architecture</xsl:variable>

    <xsl:variable name="lang.True">Yes</xsl:variable>
    <xsl:variable name="lang.False">No</xsl:variable>

    <xsl:variable name="lang.send_mail">Send an email to</xsl:variable>
    <xsl:variable name="lang.web_site">Website of</xsl:variable>
    <xsl:variable name="lang.plant_picture">Photo of the plant</xsl:variable>
</xsl:stylesheet>

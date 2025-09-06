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

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html" encoding="UTF-8" />

    <!-- Template used for translations -->
    <xsl:template name="translated_text">
        <xsl:param name="prefix" />
        <xsl:param name="name" />
        <xsl:param name="suffix" />
        <xsl:choose>
            <xsl:when test="$lang[@name = concat('lang.', $name)]">
                <xsl:value-of select="$prefix" />
                <xsl:if test="$prefix != ''">
                    <xsl:text> </xsl:text>
                </xsl:if>
                <xsl:value-of select="$lang[@name = concat('lang.', $name)]" />
                <xsl:if test="$suffix != ''">
                    <xsl:text> </xsl:text>
                </xsl:if>
                <xsl:value-of select="$suffix" />
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$prefix" />
                <xsl:if test="$prefix != ''">
                    <xsl:text> </xsl:text>
                </xsl:if>
                <xsl:value-of select="$name" />
                <xsl:if test="$suffix != ''">
                    <xsl:text> </xsl:text>
                </xsl:if>
                <xsl:value-of select="$suffix" />
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <!-- Bad template for a datum of type "graph" in the XML -->
    <xsl:template match="datum[@type='graph']">
        <bad><xsl:value-of select="@name" /></bad>
    </xsl:template>

    <!-- Template for a datum of type "bool" in the XML -->
    <xsl:template match="datum[@type='bool']">
        <dt><xsl:call-template name="translated_text">
            <xsl:with-param name="name" select="@name" />
        </xsl:call-template></dt>
        <xsl:variable name="value" select="." />
        <dd><img src="img/{.}-20x20.png">
            <xsl:attribute name="alt">
                <xsl:call-template name="translated_text">
                    <xsl:with-param name="name" select="." />
                </xsl:call-template>
            </xsl:attribute>
        </img></dd>
    </xsl:template>

    <!-- Template for a datum of type "email" in the XML -->
    <xsl:template match="datum[@type='email']">
        <dt><xsl:call-template name="translated_text">
            <xsl:with-param name="name" select="@name" />
        </xsl:call-template></dt>
        <dd><a href="mailto:{.}">
            <xsl:attribute name="title">
                <xsl:call-template name="translated_text">
                    <xsl:with-param name="name">send_mail</xsl:with-param>
                    <xsl:with-param name="suffix" select="." />
                </xsl:call-template>
            </xsl:attribute>
            <xsl:value-of select="../datum[@type='name' and @name=./@name]" />
        </a></dd>
    </xsl:template>

    <!-- Template for a datum of type "home_url" in the XML -->
    <xsl:template match="datum[@type='home_url']">
        <dt><xsl:call-template name="translated_text">
            <xsl:with-param name="name" select="@name" />
        </xsl:call-template></dt>
        <dd><a href="{.}">
            <xsl:attribute name="title">
                <xsl:call-template name="translated_text">
                    <xsl:with-param name="name">web_site</xsl:with-param>
                    <xsl:with-param name="suffix" select="../datum[@type='name' and @name=./@name]" />
                </xsl:call-template>
            </xsl:attribute>
            <xsl:value-of select="../datum[@type='name' and @name=./@name]" />
        </a></dd>
    </xsl:template>

    <!-- Template for a datum of type "time" in the XML -->
    <xsl:template match="datum[@type='time']">
        <dt><xsl:call-template name="translated_text">
            <xsl:with-param name="name" select="@name" />
        </xsl:call-template></dt>
        <dd><xsl:value-of select="../datum[@type='date' and @name=./@name]" />&#160;<xsl:value-of select="." /></dd>
    </xsl:template>

    <!-- Empty template for a datum of type "name" in the XML -->
    <xsl:template match="datum[@type='name']" />
    <!-- Empty template for a datum of type "date" in the XML -->
    <xsl:template match="datum[@type='date']" />

    <!-- Template for:
       - a datum (fallback, not one one the above types), or
       - a list item without children
    in the XML -->
    <xsl:template match="datum | item[not(child::*)]">
        <dt><xsl:call-template name="translated_text">
            <xsl:with-param name="name" select="@name" />
        </xsl:call-template></dt>
        <dd><xsl:value-of select="." /><xsl:value-of select="@unit" /></dd>
    </xsl:template>

    <!-- Template for a list item (with children) in the XML -->
    <xsl:template match="item">
        <li><xsl:call-template name="translated_text">
            <xsl:with-param name="name" select="@name" />
        </xsl:call-template></li>
        <dl>
            <xsl:apply-templates />
        </dl>
    </xsl:template>

    <!-- Template for a list in the XML -->
    <xsl:template match="list">
        <xsl:if test="item[not(child::*)]">
            <dl>
                <xsl:apply-templates select="item[not(child::*)]" />
            </dl>
        </xsl:if>
        <xsl:if test="item[child::*]">
            <ul>
                <xsl:apply-templates select="item[child::*]" />
            </ul>
        </xsl:if>
    </xsl:template>

    <!-- Template for a graph in the XML -->
    <xsl:template match="graph">
        <svg id="prodChart"
             width="100%"
             height="300"
             xlabel="Heure"
             xstart="{@start}"
             xend="{@end}">
            <xsl:attribute name="title">
                <xsl:call-template name="translated_text">
                    <xsl:with-param name="name" select="@name" />
                </xsl:call-template>
            </xsl:attribute>
            <xsl:attribute name="ydata">
                <xsl:call-template name="translated_text">
                    <xsl:with-param name="name">months</xsl:with-param>
                </xsl:call-template>
            </xsl:attribute>
        </svg>
    </xsl:template>

    <!-- Template for an image in the XML -->
    <xsl:template match="img">
        <img src="{@src}">
            <xsl:attribute name="alt">
                <xsl:call-template name="translated_text">
                    <xsl:with-param name="name" select="@name" />
                </xsl:call-template>
            </xsl:attribute>
        </img>
    </xsl:template>

    <!-- Template for a section in the XML -->
    <xsl:template match="section">
        <div class="about" id="{@name}">
            <xsl:attribute name="title">
                <xsl:call-template name="translated_text">
                    <xsl:with-param name="name" select="@name" />
                </xsl:call-template>
            </xsl:attribute>
            <xsl:apply-templates select="img" />
            <xsl:if test="datum">
                <dl>
                    <xsl:apply-templates select="datum" />
                </dl>
            </xsl:if>
            <xsl:apply-templates select="list|graph" />
        </div>
    </xsl:template>

    <!-- Template for the root of the XML -->
    <xsl:template match="/info">
        <html>
            <head>
                <meta charset='utf-8' />
                <title>Ducomquet: Production solaire</title>
                <style type="text/css">
div {
    border: 1px solid black;
    border-radius: 4px;
    margin-bottom: 8px;
    padding: 4px;
}

.about ul {
    padding-left: 20px;
    margin: 0;
}

.about li {
    margin-left: -20px;
    display: inline-block;
}

.about dl {
    margin: 0;
    padding-left: 20px;
    overflow-x: hidden;
}

.about dl dl {
    clear: both;
}

.about dt {
    margin-left: -20px;
    display: block;
    clear: both;
    float: left;
    width: -moz-fit-content;
    width: fit-content;
    white-space: nowrap;
}

.about dt::after {
    display: block;
    float: right;
    width: 0;
    white-space: nowrap;
    content: " . . . . . . . . . . . . . . . . . . . "
             ". . . . . . . . . . . . . . . . . . . . "
             ". . . . . . . . . . . . . . . . . . . . "
             ". . . . . . . . . . . . . . . . . . . . "
             ". . . . . . . . . . . . . . . . . . . . "
             ". . . . . . . . . . . . . . . . . . . . "
             ". . . . . . . . . . . . . . . . . . . . "
             ". . . . . . . . . . . . . . . . . . . . "
             ". . . . . . . . . . . . . . . . . . . . "
             ". . . . . . . . . . . . . . . . . . . . "
             ". . . . . . . . . . . . . . . . . . . . "
             ". . . . . . . . . . . . . . . . . . . . ";
}

.about dd {
    background-color: white;
    background-color: -moz-default-background-color;
    margin-left: 0;
    float: right;
    clear: right;
    display: block;
    height: 21px;
}

.about img {
    width: 100%;
}
                </style>
            </head>
            <body>
                <xsl:apply-templates />
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>

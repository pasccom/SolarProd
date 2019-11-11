<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html" encoding="UTF-8" />

    <xsl:template name="translated_text">
        <xsl:param name="name" />
        <xsl:choose>
            <xsl:when test="$lang[@name = concat('lang.', $name)]">
                <xsl:value-of select="$lang[@name = concat('lang.', $name)]" />
            </xsl:when>
            <xsl:otherwise>
                 <xsl:value-of select="$name" />
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="datum[@type!='graph'] | datum[not(@type)] | item[not(child::*)]">
        <xsl:variable name="name" select="@name" />
        <xsl:choose>
            <xsl:when test="@type='bool'">
                <dt><xsl:call-template name="translated_text">
                    <xsl:with-param name="name" select="@name" />
                </xsl:call-template></dt>
                <xsl:variable name="value" select="." />
                <dd><img src="img/{.}-20x20.png" alt="{$lang[@name = concat('lang.', $value)]}" /></dd>
            </xsl:when>
            <xsl:when test="@type='email'">
                <dt><xsl:call-template name="translated_text">
                    <xsl:with-param name="name" select="@name" />
                </xsl:call-template></dt>
                <dd><a href="mailto:{.}" title="{$lang[@name='lang.send_mail']} {.}"><xsl:value-of select="../datum[@type='name' and @name=./@name]" /></a></dd>
            </xsl:when>
            <xsl:when test="@type='home_url'">
                <dt><xsl:call-template name="translated_text">
                    <xsl:with-param name="name" select="@name" />
                </xsl:call-template></dt>
                <dd><a href="{.}" title="{$lang[@name='lang.web_site']} {../datum[@type='name' and @name=./@name]}">
                    <xsl:value-of select="../datum[@type='name' and @name=./@name]" />
                </a></dd>
            </xsl:when>
            <xsl:when test="@type='time'">
                <dt><xsl:call-template name="translated_text">
                    <xsl:with-param name="name" select="@name" />
                </xsl:call-template></dt>
                <dd><xsl:value-of select="../datum[@type='date' and @name=./@name]" />&#160;<xsl:value-of select="." /></dd>
            </xsl:when>
            <xsl:when test="@type='name'" />
            <xsl:when test="@type='date'" />
            <xsl:otherwise>
                <dt><xsl:call-template name="translated_text">
                    <xsl:with-param name="name" select="@name" />
                </xsl:call-template></dt>
                <dd><xsl:value-of select="." /><xsl:value-of select="@unit" /></dd>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="datum[@type='graph']">
        <bad><xsl:value-of select="@name" /></bad>
    </xsl:template>

    <xsl:template match="item">
        <li><xsl:call-template name="translated_text">
            <xsl:with-param name="name" select="@name" />
        </xsl:call-template></li>
        <dl>
            <xsl:apply-templates />
        </dl>
    </xsl:template>

    <xsl:template match="list">
        <dl>
            <xsl:apply-templates select="item[not(child::*)]" />
        </dl>
        <ul>
            <xsl:apply-templates select="item[child::*]" />
        </ul>
    </xsl:template>

    <xsl:template match="graph">
        <xsl:variable name="name" select="@name" />
        <svg id="prodChart"
             width="100%"
             height="300"
             title="{$lang[@name=concat('lang.', $name)]}"
             xlabel="Heure"
             xstart="{@start}"
             xend="{@end}"
             ydata="{$lang.months}"/>
    </xsl:template>

    <xsl:template match="img">
        <xsl:variable name="name" select="@name" />
        <img src="{@src}" alt="{$lang[@name=concat('lang.', $name)]}" />
    </xsl:template>

    <xsl:template match="section">
        <xsl:variable name="name" select="@name" />
        <div class="about" id="{@name}" title="{$lang[@name=concat('lang.', $name)]}">
            <xsl:apply-templates select="img" />
            <dl>
                <xsl:apply-templates select="datum" />
            </dl>
            <xsl:apply-templates select="list|graph" />
        </div>
    </xsl:template>


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
